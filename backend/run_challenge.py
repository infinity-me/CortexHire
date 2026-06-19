"""
CortexHire — India Runs Hackathon Ranker
========================================
Reads candidates.jsonl (100k records), scores each candidate for the
Senior AI Engineer role at Redrob AI, and outputs the top-100 as submission.csv.

Rules (from submission_spec.md):
  - Exactly 100 rows (ranks 1–100)
  - Scores non-increasing with rank
  - No network / GPU / LLM API calls during ranking
  - Must complete in < 5 minutes on CPU

Usage:
    python backend/run_challenge.py
    python backend/run_challenge.py --candidates ../India_runs_data_and_ai_challenge/candidates.jsonl --out submission.csv
    python backend/run_challenge.py --sample 1000   # fast test on first 1000 records
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

# Consulting-heavy companies (penalty if ALL career is here)
CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "mphasis", "hexaware", "mindtree", "l&t infotech",
    "ltimindtree", "persistent", "mastech", "niit technologies",
}

# Core skills that directly match the JD requirements
CORE_AI_SKILLS = {
    # Embeddings & Retrieval (MUST-HAVE from JD)
    "embeddings", "sentence-transformers", "sentence transformers", "bge", "e5",
    "openai embeddings", "cohere embeddings", "ada", "text-embedding",
    # Vector DBs (MUST-HAVE)
    "qdrant", "pinecone", "weaviate", "milvus", "faiss", "elasticsearch", "opensearch",
    "chroma", "chromadb", "pgvector", "redis vector", "weaviate", "vespa",
    "hybrid search", "vector search", "vector database", "ann",
    # NLP / Retrieval (MUST-HAVE)
    "nlp", "natural language processing", "information retrieval", "ir",
    "text retrieval", "semantic search", "dense retrieval", "sparse retrieval",
    "bm25", "tf-idf", "tfidf", "full-text search",
    # LLMs (nice to have but signals AI alignment)
    "llm", "large language model", "gpt", "claude", "gemini", "llama", "mistral",
    "rag", "retrieval augmented", "langchain", "llamaindex", "llama index",
    "fine-tuning", "fine tuning", "finetuning", "lora", "qlora", "peft",
    "rlhf", "dpo", "instruction tuning",
    # Ranking / RecSys
    "ranking", "learning to rank", "ltr", "lambdamart", "xgboost ranking",
    "reranking", "reranker", "cross-encoder", "biencoder", "bi-encoder",
    "recommendation system", "recommender", "collaborative filtering",
    "ndcg", "mrr", "map@k", "precision@k", "recall@k", "a/b testing",
    # ML Production
    "mlops", "ml pipeline", "feature store", "model serving", "triton",
    "model deployment", "online learning", "ml platform",
    # Python & Core Tools
    "python", "pytorch", "tensorflow", "jax", "huggingface", "transformers",
    "scikit-learn", "sklearn", "numpy", "pandas", "spark ml",
    # Data Infra (signals production experience)
    "kafka", "spark", "airflow", "dbt", "data pipeline", "data engineering",
    "distributed systems", "microservices", "kubernetes", "docker",
    # Open Source signal
    "open source", "github", "research paper", "arxiv",
}

# Secondary skills (nice to have)
SECONDARY_AI_SKILLS = {
    "machine learning", "deep learning", "neural network", "bert", "gpt-2",
    "data science", "statistics", "sql", "cloud", "aws", "gcp", "azure",
    "rest api", "fastapi", "flask", "golang", "scala",
}

# Negative signals — heavily penalizes for JD mismatch
NEGATIVE_TITLE_KEYWORDS = {
    "marketing", "sales", "hr ", "human resources", "accountant", "finance",
    "civil engineer", "mechanical engineer", "graphic designer", "content writer",
    "customer support", "operations manager", "supply chain", "logistics",
    "real estate", "teacher", "nurse", "business analyst", "project manager",
    "business development", "product manager", "scrum master", "agile coach",
    "ui designer", "ux designer", "digital marketer", "seo", "social media",
}

# Skills from other domains that are NOT a fit here
CV_SPEECH_ONLY = {
    "object detection", "image classification", "computer vision", "cnn",
    "convolutional", "yolo", "resnet", "opencv", "speech recognition",
    "text to speech", "tts", "automatic speech recognition", "asr",
    "audio processing", "robotics", "slam", "lidar",
}

# Reference date for recency calculations
_NOW = datetime(2026, 6, 19, tzinfo=timezone.utc)


# ── Candidate Streaming ────────────────────────────────────────────────────────

def stream_candidates(file_path: str, limit: int = 0) -> Iterator[dict]:
    """Memory-efficient line-by-line JSONL reader."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")
    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
                count += 1
                if limit and count >= limit:
                    break
            except json.JSONDecodeError:
                continue


# ── Honeypot Detection ─────────────────────────────────────────────────────────

def is_honeypot(candidate: dict) -> bool:
    """
    Detect candidates with impossible/contradictory profiles.
    These are forced to relevance tier 0 in the ground truth.
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])
    skills = candidate.get("skills", [])

    years_exp = profile.get("years_of_experience", 0) or 0

    # 1. Expert proficiency with 0 duration AND 0 endorsements on many skills
    expert_zero_count = sum(
        1 for s in skills
        if s.get("proficiency") == "expert"
        and s.get("duration_months", 1) == 0
        and s.get("endorsements", 0) == 0
    )
    if expert_zero_count >= 5:
        return True

    # 2. Claimed years_of_experience >> sum of all career durations
    if career:
        total_months = sum(r.get("duration_months", 0) for r in career)
        total_years_from_career = total_months / 12
        if years_exp > 0 and total_years_from_career > 0:
            # If claimed exp is more than 3x the career history, suspicious
            if years_exp > total_years_from_career * 3 and years_exp > 15:
                return True

    # 3. Impossible skill: 60+ months usage for a skill but 0 endorsements AND beginner level
    impossible_skills = sum(
        1 for s in skills
        if s.get("duration_months", 0) >= 60
        and s.get("proficiency") == "beginner"
        and s.get("endorsements", 0) == 0
    )
    if impossible_skills >= 6:
        return True

    return False


# ── Skills Scoring ─────────────────────────────────────────────────────────────

def score_skills(candidate: dict) -> tuple[float, list[str]]:
    """
    Score 0–40 based on skill alignment with the AI Engineer JD.
    Returns (score, matched_skills_list).
    """
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0, []

    redrob = candidate.get("redrob_signals", {})
    assessment_scores = redrob.get("skill_assessment_scores", {})

    level_weight = {"expert": 1.0, "advanced": 0.75, "intermediate": 0.5, "beginner": 0.25}

    core_matches = []
    secondary_matches = []
    cv_speech_penalty = 0

    for skill in skills:
        name = (skill.get("name") or "").lower().strip()
        level = skill.get("proficiency", "intermediate")
        weight = level_weight.get(level, 0.5)
        duration_months = skill.get("duration_months", 12)
        endorsements = skill.get("endorsements", 0)

        # Duration bonus (more years = more credible)
        duration_bonus = min(0.3, duration_months / 120)
        endorsement_bonus = min(0.2, endorsements / 100)

        effective_weight = weight + duration_bonus + endorsement_bonus

        # Check core AI skills
        matched_core = False
        for keyword in CORE_AI_SKILLS:
            if keyword in name or name in keyword:
                core_matches.append((keyword, effective_weight))
                matched_core = True
                break

        # Check secondary skills
        if not matched_core:
            for keyword in SECONDARY_AI_SKILLS:
                if keyword in name or name in keyword:
                    secondary_matches.append((keyword, effective_weight * 0.4))
                    break

        # CV/Speech penalty
        for keyword in CV_SPEECH_ONLY:
            if keyword in name:
                cv_speech_penalty += 0.1
                break

    # Assessment score bonus
    assessment_bonus = 0.0
    if assessment_scores:
        avg = sum(assessment_scores.values()) / len(assessment_scores)
        assessment_bonus = (avg / 100) * 3.0  # up to +3 pts

    # Calculate raw score
    core_score = min(30.0, sum(w for _, w in core_matches[:12]) * 3.5)
    secondary_score = min(7.0, sum(w for _, w in secondary_matches[:6]) * 2.0)
    raw = core_score + secondary_score + assessment_bonus
    raw -= cv_speech_penalty * 5.0  # penalize CV/speech-only profiles

    # Check if current title is non-tech — heavily discount skills score
    # (Marketing Manager with Pinecone in skills is a trap candidate)
    profile = candidate.get("profile", {})
    current_title = (profile.get("current_title") or "").lower()
    is_wrong_domain = any(kw in current_title for kw in NEGATIVE_TITLE_KEYWORDS)
    if is_wrong_domain:
        raw *= 0.25  # skills don't matter if core title is wrong domain

    # Penalty if no core AI skills found
    if not core_matches:
        raw *= 0.2

    matched_names = list({kw for kw, _ in core_matches[:5]})
    return round(min(40.0, max(0.0, raw)), 2), matched_names


# ── Career Quality Scoring ─────────────────────────────────────────────────────

def score_career(candidate: dict) -> tuple[float, str]:
    """
    Score 0–30 based on career trajectory, company types, and experience range.
    Returns (score, career_reasoning).
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])

    years_exp = profile.get("years_of_experience", 0) or 0
    current_title = (profile.get("current_title") or "").lower()
    current_industry = (profile.get("current_industry") or "").lower()

    score = 0.0
    reasoning_parts = []

    # 1. Experience range alignment (0–10 pts)
    # JD: 5–9 years ideal, 6–8 sweet spot
    if 6 <= years_exp <= 8:
        score += 10.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (ideal)")
    elif 5 <= years_exp <= 9:
        score += 8.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (good range)")
    elif 4 <= years_exp < 5 or 9 < years_exp <= 12:
        score += 5.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (acceptable)")
    elif 3 <= years_exp < 4:
        score += 2.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (junior)")
    else:
        reasoning_parts.append(f"{years_exp:.1f}yrs (out of range)")

    # 2. Consulting firm penalty (–15 if ALL career is consulting)
    if career:
        consulting_count = sum(
            1 for r in career
            if any(firm in (r.get("company") or "").lower() for firm in CONSULTING_FIRMS)
        )
        if consulting_count == len(career) and len(career) >= 2:
            score -= 15.0
            reasoning_parts.append("consulting-only career")
        elif consulting_count > 0:
            consulting_ratio = consulting_count / len(career)
            score -= consulting_ratio * 6.0  # partial penalty

    # 3. Negative title signals (-18 pts for clearly wrong domain — strong penalty)
    neg_hit = any(kw in current_title for kw in NEGATIVE_TITLE_KEYWORDS)
    if neg_hit:
        score -= 18.0
        reasoning_parts.append(f"wrong-domain title: {profile.get('current_title')}")

    # 4. Senior role trajectory (0–8 pts)
    senior_keywords = {"senior", "lead", "staff", "principal", "head", "director",
                       "architect", "manager", "vp", "founder", "cto", "chief"}
    senior_count = sum(
        1 for r in career
        if any(kw in (r.get("title") or "").lower() for kw in senior_keywords)
    )
    score += min(8.0, senior_count * 2.5)
    if senior_count > 0:
        reasoning_parts.append(f"{senior_count} senior roles")

    # 5. Product company experience (0–8 pts)
    # Detect non-consulting industry signals
    product_industries = {"software", "saas", "fintech", "ai", "ml", "tech",
                          "startup", "product", "platform", "marketplace"}
    product_count = sum(
        1 for r in career
        if any(ind in (r.get("industry") or "").lower() for ind in product_industries)
        and not any(firm in (r.get("company") or "").lower() for firm in CONSULTING_FIRMS)
    )
    score += min(8.0, product_count * 2.5)

    # 6. Title-chaser detection (avg tenure < 18 months across 3+ jobs = penalty)
    if len(career) >= 3:
        durations = [r.get("duration_months", 0) for r in career if not r.get("is_current")]
        if durations:
            avg_tenure = sum(durations) / len(durations)
            if avg_tenure < 18:
                score -= 5.0
                reasoning_parts.append("short avg tenure (<18mo)")

    reasoning = ", ".join(reasoning_parts) if reasoning_parts else "standard career"
    return round(min(30.0, max(0.0, score)), 2), reasoning


# ── Behavioral Signals Scoring ─────────────────────────────────────────────────

def score_behavioral(candidate: dict) -> tuple[float, list[str]]:
    """
    Score 0–20 based on Redrob platform behavioral signals.
    These signals indicate actual availability and engagement.
    Returns (score, signal_list).
    """
    redrob = candidate.get("redrob_signals", {})
    signals = []
    score = 0.0

    # 1. Open to work (0 or +4)
    if redrob.get("open_to_work_flag"):
        score += 4.0
        signals.append("open to work")

    # 2. Recency of last activity (0–4 pts)
    last_active_str = redrob.get("last_active_date", "")
    if last_active_str:
        try:
            last_active = datetime.fromisoformat(last_active_str).replace(tzinfo=timezone.utc)
            days_since = (_NOW - last_active).days
            if days_since <= 7:
                score += 4.0
                signals.append("active this week")
            elif days_since <= 30:
                score += 3.0
                signals.append("active this month")
            elif days_since <= 90:
                score += 2.0
                signals.append("active <90d")
            elif days_since <= 180:
                score += 1.0
            else:
                signals.append(f"inactive {days_since}d")
        except (ValueError, TypeError):
            pass

    # 3. Recruiter response rate (0–4 pts)
    response_rate = redrob.get("recruiter_response_rate", -1)
    if response_rate >= 0:
        score += response_rate * 4.0
        if response_rate >= 0.7:
            signals.append(f"high response rate ({response_rate:.0%})")

    # 4. Notice period (0–4 pts)
    notice = redrob.get("notice_period_days", 90)
    if notice <= 0:
        score += 4.0
        signals.append("immediate joiner")
    elif notice <= 30:
        score += 4.0
        signals.append(f"notice {notice}d (ideal)")
    elif notice <= 60:
        score += 2.5
        signals.append(f"notice {notice}d")
    elif notice <= 90:
        score += 1.0
    else:
        score -= 1.0  # long notice = risk

    # 5. Interview completion rate (0–4 pts)
    icr = redrob.get("interview_completion_rate", 0)
    score += icr * 4.0

    return round(min(20.0, max(0.0, score)), 2), signals


# ── Platform Engagement Scoring ────────────────────────────────────────────────

def score_engagement(candidate: dict) -> float:
    """
    Score 0–10 based on platform engagement signals.
    """
    redrob = candidate.get("redrob_signals", {})
    score = 0.0

    # GitHub activity (0–4 pts)
    github = redrob.get("github_activity_score", -1)
    if github >= 0:
        score += (github / 100) * 4.0

    # Saved by recruiters (0–3 pts)
    saved = redrob.get("saved_by_recruiters_30d", 0)
    score += min(3.0, saved * 0.4)

    # Profile completeness (0–3 pts)
    completeness = redrob.get("profile_completeness_score", 50) / 100
    score += completeness * 3.0

    return round(min(10.0, max(0.0, score)), 2)


# ── Reasoning Generator ────────────────────────────────────────────────────────

def generate_reasoning(
    candidate: dict,
    skills_score: float,
    career_score: float,
    behavioral_score: float,
    engagement_score: float,
    total_score: float,
    matched_skills: list[str],
    behavioral_signals: list[str],
    career_reasoning: str,
) -> str:
    """Generate a concise, specific reasoning string for the CSV."""
    profile = candidate.get("profile", {})
    redrob = candidate.get("redrob_signals", {})

    name = profile.get("anonymized_name", "Candidate")
    title = profile.get("current_title", "")
    years = profile.get("years_of_experience", 0)
    company = profile.get("current_company", "")
    edu = candidate.get("education", [{}])
    edu_tier = edu[0].get("tier", "unknown") if edu else "unknown"

    parts = []

    # Core profile
    if title and years:
        parts.append(f"{title} with {years:.1f}yrs experience")

    # Top matched skills
    if matched_skills:
        parts.append(f"AI/ML skills: {', '.join(matched_skills[:4])}")

    # Career context
    if career_reasoning and career_reasoning != "standard career":
        parts.append(career_reasoning)

    # Behavioral availability
    if behavioral_signals:
        parts.append("; ".join(behavioral_signals[:2]))

    # Education
    if edu_tier in ("tier_1", "tier_2"):
        parts.append(f"strong academic background ({edu_tier.replace('_', ' ')})")

    # Notice period summary
    notice = redrob.get("notice_period_days", 90)
    if notice <= 30:
        parts.append(f"available soon (notice: {notice}d)")

    if not parts:
        parts.append(f"Score {total_score:.2f}/100 across skills, career, and engagement signals")

    return "; ".join(parts)[:400]


# ── Main Scoring Pipeline ──────────────────────────────────────────────────────

def score_candidate(candidate: dict) -> dict | None:
    """Score a single candidate. Returns None if honeypot detected."""
    if is_honeypot(candidate):
        return None

    candidate_id = candidate.get("candidate_id", "UNKNOWN")
    profile = candidate.get("profile", {})

    skills_score, matched_skills = score_skills(candidate)
    career_score, career_reasoning = score_career(candidate)
    behavioral_score, behavioral_signals = score_behavioral(candidate)
    engagement_score = score_engagement(candidate)

    total = skills_score + career_score + behavioral_score + engagement_score
    # Normalize to 0–1 for the competition format
    normalized_score = round(total / 100.0, 4)

    reasoning = generate_reasoning(
        candidate=candidate,
        skills_score=skills_score,
        career_score=career_score,
        behavioral_score=behavioral_score,
        engagement_score=engagement_score,
        total_score=total,
        matched_skills=matched_skills,
        behavioral_signals=behavioral_signals,
        career_reasoning=career_reasoning,
    )

    return {
        "candidate_id": candidate_id,
        "total_score": total,
        "normalized_score": normalized_score,
        "skills_score": skills_score,
        "career_score": career_score,
        "behavioral_score": behavioral_score,
        "engagement_score": engagement_score,
        "reasoning": reasoning,
        "name": profile.get("anonymized_name", ""),
        "title": profile.get("current_title", ""),
    }


def run_ranking(candidates_file: str, out_file: str, sample: int = 0) -> None:
    """Full ranking pipeline. Outputs top-100 CSV."""
    logger.info(f"Starting ranking: {candidates_file}")
    logger.info(f"Output: {out_file}")

    t_start = time.time()

    top_k: list[dict] = []  # keep top 200 buffer to ensure we have 100 after dedup
    total_processed = 0
    honeypots_detected = 0
    BUFFER_SIZE = 200  # keep top 200, output top 100

    for candidate in stream_candidates(candidates_file, limit=sample):
        result = score_candidate(candidate)
        if result is None:
            honeypots_detected += 1
            total_processed += 1
            continue

        total_processed += 1

        # Maintain a top-N buffer (faster than sorting everything)
        top_k.append(result)
        if len(top_k) > BUFFER_SIZE * 3:
            top_k.sort(key=lambda x: x["total_score"], reverse=True)
            top_k = top_k[:BUFFER_SIZE * 2]

        if total_processed % 10000 == 0:
            elapsed = time.time() - t_start
            rate = total_processed / elapsed
            logger.info(
                f"Progress: {total_processed:,} processed | "
                f"{honeypots_detected} honeypots | "
                f"{elapsed:.1f}s elapsed | {rate:.0f} cands/sec"
            )

    # Final sort — get top 100
    top_k.sort(key=lambda x: x["total_score"], reverse=True)
    top_100 = top_k[:100]

    elapsed = time.time() - t_start
    logger.info(
        f"Scoring complete: {total_processed:,} candidates in {elapsed:.1f}s "
        f"({total_processed/elapsed:.0f} cands/sec)"
    )
    logger.info(f"Honeypots detected and excluded: {honeypots_detected}")

    if len(top_100) < 100:
        logger.warning(f"Only {len(top_100)} candidates scored — padding not possible, check dataset.")

    # Write CSV
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for rank, item in enumerate(top_100, start=1):
            # Enforce non-increasing scores (cap at previous score)
            if rank > 1:
                prev_score = float(top_100[rank - 2]["normalized_score"])
                if item["normalized_score"] > prev_score:
                    item["normalized_score"] = prev_score

            writer.writerow([
                item["candidate_id"],
                rank,
                f"{item['normalized_score']:.4f}",
                item["reasoning"],
            ])

    logger.info(f"✅ Submission CSV written: {out_file}")
    logger.info(f"Top 5 candidates:")
    for i, item in enumerate(top_100[:5], start=1):
        logger.info(
            f"  #{i}: {item['candidate_id']} | {item['title']} | "
            f"Score={item['total_score']:.1f} | {item['reasoning'][:80]}..."
        )


# ── CLI Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CortexHire — India Runs Hackathon Ranker"
    )
    parser.add_argument(
        "--candidates",
        default=None,
        help="Path to candidates.jsonl (auto-detected if not specified)",
    )
    parser.add_argument(
        "--out",
        default="submission.csv",
        help="Output CSV path (default: submission.csv)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="Limit to first N candidates (0 = all). Use for testing.",
    )
    args = parser.parse_args()

    # Auto-detect candidates file
    candidates_file = args.candidates
    if not candidates_file:
        search_paths = [
            Path(__file__).parent.parent / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
            Path("India_runs_data_and_ai_challenge") / "candidates.jsonl",
            Path("candidates.jsonl"),
        ]
        for p in search_paths:
            if p.exists():
                candidates_file = str(p)
                break

    if not candidates_file or not Path(candidates_file).exists():
        logger.error(
            "candidates.jsonl not found. Pass --candidates /path/to/candidates.jsonl"
        )
        sys.exit(1)

    logger.info(f"Dataset: {candidates_file}")
    count_str = "ALL" if args.sample == 0 else f"{args.sample:,}"
    logger.info(f"Candidates to process: {count_str}")

    run_ranking(candidates_file, args.out, sample=args.sample)
