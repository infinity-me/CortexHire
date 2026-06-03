"""
CortexHire — Dataset Importer for India Runs Data & AI Challenge

Reads the competition's candidate data (sample_candidates.json or candidates.jsonl)
and maps it to CortexHire's Candidate model. Also stores Redrob signals so the
ranking engine can use platform activity as a scoring signal.

Usage:
    python -m data.dataset_importer --file sample_candidates.json --limit 50
    python -m data.dataset_importer --file candidates.jsonl --limit 500
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import math
import os
import sys
from pathlib import Path

# ensure backend root is on path when run directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db.postgres import AsyncSessionLocal, init_db
from db.models import Candidate, Job
from core.role_cognition import extract_role_genome

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ── Education tier mapping ─────────────────────────────────────

TIER_MAP = {
    "tier_1": "tier1",
    "tier_2": "tier2",
    "tier_3": "tier3",
    "tier_4": "tier3",   # fold tier4 into tier3
    "unknown": "tier3",
}


def _map_education_tier(education_list: list) -> str:
    """Use the best (lowest number = highest prestige) tier from education history."""
    tiers = [e.get("tier", "unknown") for e in education_list]
    priority = {"tier_1": 0, "tier_2": 1, "tier_3": 2, "tier_4": 3, "unknown": 4}
    best = min(tiers, key=lambda t: priority.get(t, 4), default="unknown")
    return TIER_MAP.get(best, "tier3")


def _education_detail(education_list: list) -> str:
    if not education_list:
        return ""
    e = education_list[0]
    parts = [e.get("degree", ""), e.get("field_of_study", ""), e.get("institution", "")]
    return ", ".join(p for p in parts if p)


def _map_career_history(career: list) -> list:
    """Convert dataset career format → CortexHire career_history format."""
    result = []
    for role in career:
        start_date = role.get("start_date", "")
        start_year = int(start_date[:4]) if start_date and len(start_date) >= 4 else None
        end_date = role.get("end_date")
        end_year = int(end_date[:4]) if end_date and len(end_date) >= 4 else None

        # Estimate team size from company size
        company_size_str = role.get("company_size", "51-200")
        size_to_team = {
            "1-10": 5, "11-50": 10, "51-200": 20, "201-500": 40,
            "501-1000": 60, "1001-5000": 80, "5001-10000": 100, "10001+": 150,
        }
        team_size = size_to_team.get(company_size_str, 20)

        # Impact score: senior-sounding title + larger company = higher
        title = role.get("title", "").lower()
        impact_base = 0.5
        if any(w in title for w in ["senior", "lead", "staff", "principal", "manager", "head", "director"]):
            impact_base += 0.2
        if any(w in title for w in ["vp", "president", "cto", "ceo", "founder"]):
            impact_base += 0.35
        if company_size_str in ("5001-10000", "10001+"):
            impact_base += 0.1
        impact_score = min(1.0, impact_base)

        result.append({
            "company": role.get("company", ""),
            "title": role.get("title", ""),
            "start_year": start_year,
            "end_year": end_year,
            "description": role.get("description", ""),
            "team_size": team_size,
            "impact_score": round(impact_score, 2),
            "duration_months": role.get("duration_months", 0),
            "industry": role.get("industry", ""),
            "is_current": role.get("is_current", False),
        })
    return result


def _map_skills(skills_list: list) -> list:
    """Convert dataset skills format → CortexHire skills format."""
    level_map = {"beginner": "familiar", "intermediate": "proficient", "advanced": "expert", "expert": "expert"}
    return [
        {
            "name": s.get("name", ""),
            "level": level_map.get(s.get("proficiency", "intermediate"), "proficient"),
            "years": round(s.get("duration_months", 12) / 12, 1),
            "endorsements": s.get("endorsements", 0),
        }
        for s in skills_list
    ]


def _infer_capability_profile(candidate_data: dict) -> dict:
    """
    Derive 8-dimension capability profile from structured dataset signals.
    Uses skills, career, redrob signals — no LLM needed.
    """
    profile = candidate_data.get("profile", {})
    career = candidate_data.get("career_history", [])
    skills = candidate_data.get("skills", [])
    redrob = candidate_data.get("redrob_signals", {})
    education = candidate_data.get("education", [])

    years_exp = profile.get("years_of_experience", 0) or 0

    # Technical skills scoring
    tech_skill_names = {s.get("name", "").lower() for s in skills}
    tech_keywords = {
        "python", "java", "go", "rust", "c++", "kubernetes", "docker", "spark", "kafka",
        "pytorch", "tensorflow", "react", "node", "sql", "postgresql", "redis", "aws",
        "gcp", "azure", "terraform", "airflow", "mlops", "llm", "nlp", "ml", "ai",
        "machine learning", "deep learning", "microservices", "distributed systems",
    }
    tech_overlap = len(tech_skill_names & tech_keywords)
    tech_depth = min(1.0, 0.3 + (tech_overlap * 0.06) + (years_exp * 0.02))

    # GitHub activity
    github_score = redrob.get("github_activity_score", -1)
    if github_score >= 0:
        tech_depth = min(1.0, tech_depth + github_score / 400)

    # Skill assessment scores
    assessment_scores = redrob.get("skill_assessment_scores", {})
    if assessment_scores:
        avg_assessment = sum(assessment_scores.values()) / len(assessment_scores) / 100
        tech_depth = min(1.0, (tech_depth * 0.7) + (avg_assessment * 0.3))

    # Leadership signals from career
    leadership_keywords = {"manager", "lead", "head", "director", "vp", "founder", "cto", "principal", "staff"}
    has_leadership = any(
        any(w in r.get("title", "").lower() for w in leadership_keywords)
        for r in career
    )
    leadership = 0.3 + (0.4 if has_leadership else 0.0) + min(0.3, years_exp * 0.02)

    # Execution: interview completion rate, offer acceptance
    interview_rate = redrob.get("interview_completion_rate", 0.5)
    offer_rate = redrob.get("offer_acceptance_rate", -1)
    execution = min(1.0, 0.5 + interview_rate * 0.3 + (offer_rate * 0.2 if offer_rate >= 0 else 0))

    # Adaptability: domain diversity across career
    industries = {r.get("industry", "") for r in career}
    adaptability = min(1.0, 0.4 + len(industries) * 0.08 + years_exp * 0.015)

    # Communication: connections, profile completeness, response rate
    connections = min(500, redrob.get("connection_count", 100))
    completeness = redrob.get("profile_completeness_score", 50) / 100
    response_rate = redrob.get("recruiter_response_rate", 0.5)
    communication = min(1.0, 0.3 + (connections / 2000) + (completeness * 0.3) + (response_rate * 0.2))

    # Systems thinking: senior roles + large companies + tech depth proxy
    max_company_size = max(
        ({"1-10": 10, "11-50": 50, "51-200": 200, "201-500": 500,
          "501-1000": 1000, "1001-5000": 5000, "5001-10000": 10000, "10001+": 20000}
         .get(r.get("company_size", "51-200"), 200) for r in career),
        default=200
    )
    systems_thinking = min(1.0, 0.3 + (math.log10(max_company_size + 1) / 5) + (tech_depth * 0.3))

    # Resilience: years_exp + platform tenure + notice period discipline
    resilience = min(1.0, 0.4 + min(years_exp, 15) * 0.03 + (0.1 if redrob.get("verified_email") else 0))

    # Creativity: open source activity + diverse skills
    creativity = min(1.0, 0.4 + (github_score / 300 if github_score >= 0 else 0) + (len(skills) * 0.01))

    return {
        "technical_depth": round(tech_depth, 3),
        "adaptability": round(adaptability, 3),
        "leadership": round(leadership, 3),
        "execution": round(execution, 3),
        "systems_thinking": round(systems_thinking, 3),
        "creativity": round(creativity, 3),
        "resilience": round(resilience, 3),
        "communication": round(communication, 3),
    }


def _extract_achievements(candidate_data: dict) -> list:
    """Pull notable signals into achievement strings."""
    redrob = candidate_data.get("redrob_signals", {})
    profile = candidate_data.get("profile", {})
    certs = candidate_data.get("certifications", [])

    achievements = []

    # Platform signals
    github = redrob.get("github_activity_score", -1)
    if github >= 60:
        achievements.append(f"High GitHub activity score: {github}/100 (active OSS contributor)")
    elif github >= 30:
        achievements.append(f"Active GitHub contributor: score {github}/100")

    endorsements = redrob.get("endorsements_received", 0)
    if endorsements >= 30:
        achievements.append(f"Highly endorsed by peers: {endorsements} endorsements received")

    saved = redrob.get("saved_by_recruiters_30d", 0)
    if saved >= 5:
        achievements.append(f"In-demand candidate: saved by {saved} recruiters in last 30 days")

    if redrob.get("interview_completion_rate", 0) >= 0.85:
        achievements.append("Reliable interview candidate: 85%+ completion rate")

    # Certifications
    for cert in certs[:3]:
        achievements.append(f"Certified: {cert.get('name', '')} ({cert.get('issuer', '')}, {cert.get('year', '')})")

    # Skill assessments
    assessment_scores = redrob.get("skill_assessment_scores", {})
    top_assessments = sorted(assessment_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for skill, score in top_assessments:
        if score >= 70:
            achievements.append(f"Platform-verified {skill} skill: {score:.0f}/100 assessment score")

    return achievements[:8]


def map_dataset_candidate(candidate_data: dict) -> dict:
    """
    Map a competition dataset candidate record → CortexHire Candidate fields dict.
    """
    profile = candidate_data.get("profile", {})
    redrob = candidate_data.get("redrob_signals", {})
    education = candidate_data.get("education", [])
    skills = candidate_data.get("skills", [])
    career = candidate_data.get("career_history", [])

    # Salary range as a readable summary
    salary = redrob.get("expected_salary_range_inr_lpa", {})
    salary_str = f"₹{salary.get('min', 0):.1f}–{salary.get('max', 0):.1f} LPA" if salary else ""

    work_mode = redrob.get("preferred_work_mode", "")
    notice = redrob.get("notice_period_days", 0)

    # Build rich summary incorporating redrob signals
    base_summary = profile.get("summary", "")
    platform_context = []
    if redrob.get("open_to_work_flag"):
        platform_context.append("actively open to opportunities")
    if redrob.get("willing_to_relocate"):
        platform_context.append("willing to relocate")
    if salary_str:
        platform_context.append(f"expected salary {salary_str}")
    if notice:
        platform_context.append(f"notice period {notice} days")
    if work_mode:
        platform_context.append(f"preferred work mode: {work_mode}")

    full_summary = base_summary
    if platform_context:
        full_summary = base_summary + " [Platform signals: " + "; ".join(platform_context) + "]"

    return {
        "name": profile.get("anonymized_name", "Unknown"),
        "email": None,  # anonymized dataset
        "headline": profile.get("headline", ""),
        "location": f"{profile.get('location', '')}, {profile.get('country', '')}".strip(", "),
        "summary": full_summary,
        "years_experience": profile.get("years_of_experience", 0),
        "education_tier": _map_education_tier(education),
        "education_detail": _education_detail(education),
        "career_history": _map_career_history(career),
        "skills": _map_skills(skills),
        "achievements": _extract_achievements(candidate_data),
        "capability_profile": _infer_capability_profile(candidate_data),
        # Store raw redrob signals for ranking engine
        "raw_profile": json.dumps({
            "candidate_id": candidate_data.get("candidate_id"),
            "redrob_signals": redrob,
            "current_title": profile.get("current_title"),
            "current_company": profile.get("current_company"),
            "current_industry": profile.get("current_industry"),
        }),
    }


async def import_candidates(file_path: str, limit: int = 100, skip_existing: bool = True) -> int:
    """Import candidates from dataset file into the DB."""
    await init_db()

    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return 0

    # Load records
    records: list[dict] = []
    if path.suffix == ".jsonl":
        logger.info(f"Streaming JSONL file (limit={limit})...")
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                try:
                    records.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    elif path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data[:limit] if isinstance(data, list) else [data]
    else:
        logger.error(f"Unsupported file type: {path.suffix}")
        return 0

    logger.info(f"Loaded {len(records)} records from {path.name}")

    imported = 0
    skipped = 0
    failed = 0

    async with AsyncSessionLocal() as session:
        for i, record in enumerate(records):
            try:
                cand_id = record.get("candidate_id", f"UNKNOWN_{i}")

                # Skip if already imported (check by raw_profile containing candidate_id)
                if skip_existing:
                    from sqlmodel import select, col
                    existing_check = await session.execute(
                        select(Candidate).where(
                            Candidate.raw_profile.contains(cand_id)  # type: ignore
                        ).limit(1)
                    )
                    if existing_check.scalars().first():
                        skipped += 1
                        continue

                mapped = map_dataset_candidate(record)

                cand = Candidate(
                    name=mapped["name"],
                    email=mapped["email"],
                    headline=mapped["headline"],
                    location=mapped["location"],
                    summary=mapped["summary"],
                    years_experience=mapped["years_experience"],
                    education_tier=mapped["education_tier"],
                    education_detail=mapped["education_detail"],
                    raw_profile=mapped["raw_profile"],
                )
                cand.career_history = mapped["career_history"]
                cand.skills = mapped["skills"]
                cand.achievements = mapped["achievements"]
                cand.capability_profile = mapped["capability_profile"]

                session.add(cand)
                imported += 1

                if (i + 1) % 50 == 0:
                    await session.commit()
                    logger.info(f"Progress: {i+1}/{len(records)} — {imported} imported, {skipped} skipped")

            except Exception as e:
                logger.error(f"Failed to import {record.get('candidate_id', i)}: {e}")
                failed += 1

        await session.commit()

    logger.info(f"Import complete: {imported} imported, {skipped} skipped, {failed} failed")
    return imported


async def seed_job_from_dataset(job_description_text: str) -> None:
    """Seed the competition job description as a Job record and extract role genome."""
    await init_db()

    # The challenge job is for an AI/ML role at a company
    JOB_TITLE = "AI/ML Engineer — Intelligent Candidate Discovery"
    JOB_COMPANY = "India Runs Data & AI Challenge"

    async with AsyncSessionLocal() as session:
        from sqlmodel import select
        existing = await session.execute(
            select(Job).where(Job.company == JOB_COMPANY).limit(1)
        )
        if existing.scalars().first():
            logger.info("Challenge job already seeded, skipping.")
            return

        logger.info("Extracting role genome from challenge job description...")
        genome = await extract_role_genome(job_description_text, JOB_TITLE, JOB_COMPANY)

        job = Job(
            title=JOB_TITLE,
            company=JOB_COMPANY,
            description=job_description_text,
            location="India (Remote)",
            employment_type="full-time",
            seniority="mid-senior",
            status="ready",
        )
        job.role_genome = genome
        session.add(job)
        await session.commit()
        logger.info(f"Seeded challenge job with genome: {json.dumps(genome, indent=2)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import competition dataset into CortexHire")
    parser.add_argument("--file", default="India_runs_data_and_ai_challenge/sample_candidates.json",
                        help="Path to candidates.json or candidates.jsonl")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max candidates to import")
    parser.add_argument("--no-skip", action="store_true",
                        help="Re-import even if candidate_id already exists")
    args = parser.parse_args()

    asyncio.run(import_candidates(
        file_path=args.file,
        limit=args.limit,
        skip_existing=not args.no_skip,
    ))
