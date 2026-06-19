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
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

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


# ── JD Profile (dynamic — built from uploaded JD text) ────────────────────────

@dataclass
class JDProfile:
    """Scoring parameters extracted from a job description."""
    title: str = "Senior AI Engineer"
    company: str = ""
    # Skills
    core_skills: set = field(default_factory=lambda: set(CORE_AI_SKILLS))
    secondary_skills: set = field(default_factory=lambda: set(SECONDARY_AI_SKILLS))
    penalised_domains: set = field(default_factory=lambda: set(CV_SPEECH_ONLY))
    neg_title_keywords: set = field(default_factory=lambda: set(NEGATIVE_TITLE_KEYWORDS))
    # Experience range
    exp_ideal_min: float = 6.0
    exp_ideal_max: float = 8.0
    exp_good_min: float = 5.0
    exp_good_max: float = 9.0
    exp_ok_min: float = 4.0
    exp_ok_max: float = 12.0
    # Seniority
    senior_keywords: set = field(default_factory=lambda: {
        "senior", "lead", "staff", "principal", "head", "director",
        "architect", "manager", "vp", "founder", "cto", "chief"
    })
    # Location (informational only — no hard scoring)
    locations: list = field(default_factory=list)
    # Raw summary for display
    parsed_summary: str = ""
    required_skills_preview: list = field(default_factory=list)
    disqualifiers_preview: list = field(default_factory=list)


# Broad tech vocabulary used when parsing any JD text
_ALL_TECH_VOCAB: dict[str, str] = {
    # key = keyword to search, value = category ("core" or "secondary")
    # Embeddings & Retrieval
    "embeddings": "core", "sentence-transformers": "core", "sentence transformers": "core",
    "bge": "core", "e5": "core", "text-embedding": "core",
    # Vector DBs
    "qdrant": "core", "pinecone": "core", "weaviate": "core", "milvus": "core",
    "faiss": "core", "elasticsearch": "core", "opensearch": "core", "chromadb": "core",
    "chroma": "core", "pgvector": "core", "redis vector": "core", "vespa": "core",
    "vector search": "core", "vector database": "core", "hybrid search": "core",
    "ann": "core", "approximate nearest neighbour": "core",
    # NLP / IR
    "nlp": "core", "natural language processing": "core",
    "information retrieval": "core", "semantic search": "core",
    "dense retrieval": "core", "sparse retrieval": "core",
    "bm25": "core", "tf-idf": "core", "tfidf": "core", "full-text search": "core",
    # LLM / GenAI
    "llm": "core", "large language model": "core", "gpt": "core",
    "claude": "core", "gemini": "core", "llama": "core", "mistral": "core",
    "rag": "core", "retrieval augmented": "core",
    "langchain": "core", "llamaindex": "core", "llama index": "core",
    "fine-tuning": "core", "fine tuning": "core", "finetuning": "core",
    "lora": "core", "qlora": "core", "peft": "core", "rlhf": "core", "dpo": "core",
    # Ranking / RecSys
    "ranking": "core", "learning to rank": "core", "ltr": "core",
    "reranking": "core", "reranker": "core", "cross-encoder": "core",
    "recommendation system": "core", "recommender": "core",
    "collaborative filtering": "core", "matrix factorization": "core",
    "ndcg": "core", "mrr": "core", "map@k": "core",
    # ML / DL Frameworks
    "pytorch": "core", "tensorflow": "core", "jax": "core",
    "huggingface": "core", "transformers": "core",
    "scikit-learn": "secondary", "sklearn": "secondary",
    "xgboost": "secondary", "lightgbm": "secondary", "catboost": "secondary",
    # ML Production
    "mlops": "core", "ml pipeline": "core", "model serving": "core",
    "triton": "secondary", "feature store": "secondary", "model deployment": "secondary",
    # Core Languages
    "python": "core", "golang": "secondary", "rust": "secondary", "scala": "secondary",
    "java": "secondary", "typescript": "secondary", "javascript": "secondary",
    # Data Engineering
    "kafka": "secondary", "spark": "secondary", "airflow": "secondary",
    "dbt": "secondary", "data pipeline": "secondary", "distributed systems": "secondary",
    # Cloud / Infra
    "kubernetes": "secondary", "docker": "secondary",
    "aws": "secondary", "gcp": "secondary", "azure": "secondary",
    # Web / API
    "fastapi": "secondary", "flask": "secondary", "rest api": "secondary",
    # General ML
    "machine learning": "secondary", "deep learning": "secondary",
    "neural network": "secondary", "bert": "secondary",
    "data science": "secondary", "statistics": "secondary",
    "sql": "secondary", "nosql": "secondary",
    # CV / Speech (penalised for AI-text roles)
    "computer vision": "penalised", "object detection": "penalised",
    "image classification": "penalised", "cnn": "penalised",
    "speech recognition": "penalised", "text to speech": "penalised",
    "audio processing": "penalised", "robotics": "penalised",
    # Open source signals
    "open source": "core", "github": "secondary", "research paper": "secondary",
    "numpy": "secondary", "pandas": "secondary",
}

_DEFAULT_DISQUALIFIER_TITLES = [
    "marketing", "sales", "human resources", "accountant", "finance",
    "civil engineer", "mechanical engineer", "graphic designer",
    "content writer", "customer support", "operations manager",
    "supply chain", "logistics", "real estate", "teacher", "nurse",
    "business analyst", "project manager", "business development",
    "product manager", "scrum master", "ui designer", "ux designer",
    "digital marketer", "seo specialist", "social media",
]


def build_jd_profile(jd_text: str) -> JDProfile:
    """
    Parse raw JD text (from .txt/.docx/.md) into a JDProfile that
    drives dynamic, JD-specific candidate scoring.
    Works entirely offline — no LLM required.
    """
    if not jd_text or len(jd_text.strip()) < 30:
        return JDProfile()  # fall back to defaults

    text = jd_text.lower()

    # ── 1. Extract experience range ──────────────────────────────────────────
    # Patterns: "5-9 years", "5 to 9 years", "minimum 5 years", "5+ years"
    range_matches = re.findall(r'(\d+)\s*[-–to]+\s*(\d+)\s*year', text)
    min_matches = re.findall(r'(?:minimum|at least|min(?:imum)?)\s*(\d+)\s*year', text)
    plus_matches = re.findall(r'(\d+)\+\s*year', text)

    exp_ideal_min, exp_ideal_max = 5.0, 9.0
    exp_good_min, exp_good_max = 4.0, 11.0
    exp_ok_min, exp_ok_max = 3.0, 15.0

    if range_matches:
        vals = [(int(a), int(b)) for a, b in range_matches if int(a) < int(b)]
        if vals:
            exp_ideal_min = min(v[0] for v in vals)
            exp_ideal_max = max(v[1] for v in vals)
            exp_good_min = max(0, exp_ideal_min - 1)
            exp_good_max = exp_ideal_max + 2
            exp_ok_min = max(0, exp_ideal_min - 2)
            exp_ok_max = exp_ideal_max + 4
    elif min_matches:
        mn = int(min_matches[0])
        exp_ideal_min = mn
        exp_ideal_max = mn + 5
        exp_good_min = max(0, mn - 1)
        exp_good_max = mn + 8
    elif plus_matches:
        mn = int(plus_matches[0])
        exp_ideal_min = mn
        exp_ideal_max = mn + 6
        exp_good_min = max(0, mn - 1)
        exp_good_max = mn + 8

    # ── 2. Extract skills from JD text ──────────────────────────────────────
    # Split into "required" vs "nice-to-have" sections if possible
    required_marker = re.search(
        r'(?:must.have|required|mandatory|essential|you.will.need|minimum qualification)',
        text
    )
    nice_marker = re.search(
        r'(?:nice.to.have|bonus|preferred|plus|advantage|good.to.have)',
        text
    )

    req_text = text
    nice_text = ""
    if required_marker and nice_marker and required_marker.start() < nice_marker.start():
        req_text = text[required_marker.start():nice_marker.start()]
        nice_text = text[nice_marker.start():]

    core_skills: set[str] = set()
    secondary_skills: set[str] = set()
    penalised: set[str] = set()

    for kw, category in _ALL_TECH_VOCAB.items():
        in_req = kw in req_text
        in_nice = kw in nice_text

        if category == "penalised":
            if in_req or in_nice:
                penalised.add(kw)
        elif category == "core":
            if in_req:
                core_skills.add(kw)
            elif in_nice or kw in text:  # mentioned anywhere → at least secondary
                secondary_skills.add(kw)
        else:  # secondary
            if in_req:
                secondary_skills.add(kw)
            elif in_nice or kw in text:
                secondary_skills.add(kw)

    # Ensure python is always core if mentioned anywhere (it's in every tech JD)
    if "python" in text:
        core_skills.add("python")

    # Fall back to default constants if JD is very sparse
    if len(core_skills) < 3:
        core_skills = set(CORE_AI_SKILLS)
        secondary_skills = set(SECONDARY_AI_SKILLS)

    # ── 3. Detect seniority level ────────────────────────────────────────────
    senior_kws = {"senior", "lead", "staff", "principal", "head", "director",
                  "architect", "vp", "founder", "cto", "chief"}
    if any(k in text for k in ["junior", "entry level", "associate engineer", "fresher"]):
        senior_kws = {"junior", "associate", "entry"}
    elif any(k in text for k in ["manager", "director", "vp ", "head of"]):
        senior_kws.update({"manager", "director", "vp", "head"})

    # ── 4. Detect disqualifiers ──────────────────────────────────────────────
    # Start from defaults; keep them — JD-specific disqualifiers are hard to infer
    neg_titles = set(_DEFAULT_DISQUALIFIER_TITLES)

    # ── 5. Extract location ──────────────────────────────────────────────────
    loc_re = r'\b(bangalore|bengaluru|mumbai|delhi|ncr|pune|hyderabad|chennai|noida|gurgaon|gurugram|kolkata|ahmedabad|remote)\b'
    locations = list(dict.fromkeys(re.findall(loc_re, text)))  # deduplicated

    # ── 6. Extract role title ────────────────────────────────────────────────
    title_line = jd_text.strip().splitlines()[0][:80]

    # ── 7. Build preview lists for UI display ───────────────────────────────
    req_preview = sorted(core_skills)[:10]
    disq_preview = sorted(neg_titles)[:6]

    exp_str = f"{int(exp_ideal_min)}–{int(exp_ideal_max)} years"
    skills_preview = ", ".join(sorted(core_skills)[:6])
    parsed_summary = f"Experience: {exp_str} | Skills detected: {len(core_skills)} core, {len(secondary_skills)} secondary"
    if locations:
        parsed_summary += f" | Location: {', '.join(locations[:3])}"

    return JDProfile(
        title=title_line,
        core_skills=core_skills,
        secondary_skills=secondary_skills,
        penalised_domains=penalised if penalised else set(CV_SPEECH_ONLY),
        neg_title_keywords=neg_titles,
        exp_ideal_min=exp_ideal_min,
        exp_ideal_max=exp_ideal_max,
        exp_good_min=exp_good_min,
        exp_good_max=exp_good_max,
        exp_ok_min=exp_ok_min,
        exp_ok_max=exp_ok_max,
        senior_keywords=senior_kws,
        locations=locations,
        parsed_summary=parsed_summary,
        required_skills_preview=req_preview,
        disqualifiers_preview=disq_preview,
    )


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

def score_skills(
    candidate: dict,
    jd_profile: Optional[JDProfile] = None,
) -> tuple[float, list[str]]:
    """
    Score 0–40 based on skill alignment with the JD.
    Uses JDProfile if provided, otherwise falls back to hardcoded Redrob JD constants.
    Returns (score, matched_skills_list).
    """
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0, []

    p = jd_profile
    core_kws = p.core_skills if p else CORE_AI_SKILLS
    secondary_kws = p.secondary_skills if p else SECONDARY_AI_SKILLS
    penalised_kws = p.penalised_domains if p else CV_SPEECH_ONLY
    neg_title_kws = p.neg_title_keywords if p else NEGATIVE_TITLE_KEYWORDS

    redrob = candidate.get("redrob_signals", {})
    assessment_scores = redrob.get("skill_assessment_scores", {})

    level_weight = {"expert": 1.0, "advanced": 0.75, "intermediate": 0.5, "beginner": 0.25}

    core_matches: list[tuple[str, float]] = []
    secondary_matches: list[tuple[str, float]] = []
    penalised_count = 0

    for skill in skills:
        name = (skill.get("name") or "").lower().strip()
        level = skill.get("proficiency", "intermediate")
        weight = level_weight.get(level, 0.5)
        duration_months = skill.get("duration_months", 12)
        endorsements = skill.get("endorsements", 0)

        duration_bonus = min(0.3, duration_months / 120)
        endorsement_bonus = min(0.2, endorsements / 100)
        effective_weight = weight + duration_bonus + endorsement_bonus

        matched_core = False
        for keyword in core_kws:
            if keyword in name or name in keyword:
                core_matches.append((keyword, effective_weight))
                matched_core = True
                break

        if not matched_core:
            for keyword in secondary_kws:
                if keyword in name or name in keyword:
                    secondary_matches.append((keyword, effective_weight * 0.4))
                    break

        for keyword in penalised_kws:
            if keyword in name:
                penalised_count += 1
                break

    assessment_bonus = 0.0
    if assessment_scores:
        avg = sum(assessment_scores.values()) / len(assessment_scores)
        assessment_bonus = (avg / 100) * 3.0

    core_score = min(30.0, sum(w for _, w in core_matches[:12]) * 3.5)
    secondary_score = min(7.0, sum(w for _, w in secondary_matches[:6]) * 2.0)
    raw = core_score + secondary_score + assessment_bonus
    raw -= penalised_count * 0.5  # gentle penalty per penalised-domain skill

    # Title mismatch: heavily discount skills from wrong-domain candidates
    profile = candidate.get("profile", {})
    current_title = (profile.get("current_title") or "").lower()
    if any(kw in current_title for kw in neg_title_kws):
        raw *= 0.25

    if not core_matches:
        raw *= 0.2

    matched_names = list({kw for kw, _ in core_matches[:5]})
    return round(min(40.0, max(0.0, raw)), 2), matched_names


# ── Career Quality Scoring ─────────────────────────────────────────────────────

def score_career(
    candidate: dict,
    jd_profile: Optional[JDProfile] = None,
) -> tuple[float, str]:
    """
    Score 0–30 based on career trajectory, company types, and experience range.
    Uses JDProfile experience ranges if provided.
    Returns (score, career_reasoning).
    """
    p = jd_profile
    neg_title_kws = p.neg_title_keywords if p else NEGATIVE_TITLE_KEYWORDS
    senior_kws = p.senior_keywords if p else {"senior", "lead", "staff", "principal",
        "head", "director", "architect", "manager", "vp", "founder", "cto", "chief"}
    ideal_min = p.exp_ideal_min if p else 6.0
    ideal_max = p.exp_ideal_max if p else 8.0
    good_min = p.exp_good_min if p else 5.0
    good_max = p.exp_good_max if p else 9.0
    ok_min = p.exp_ok_min if p else 4.0
    ok_max = p.exp_ok_max if p else 12.0

    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])

    years_exp = profile.get("years_of_experience", 0) or 0
    current_title = (profile.get("current_title") or "").lower()

    score = 0.0
    reasoning_parts = []

    # 1. Experience range (JD-specific thresholds)
    if ideal_min <= years_exp <= ideal_max:
        score += 10.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (ideal)")
    elif good_min <= years_exp <= good_max:
        score += 8.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (good range)")
    elif ok_min <= years_exp <= ok_max:
        score += 5.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (acceptable)")
    elif years_exp > 0:
        score += 1.0
        reasoning_parts.append(f"{years_exp:.1f}yrs (out of range)")

    # 2. Consulting firm penalty
    if career:
        consulting_count = sum(
            1 for r in career
            if any(firm in (r.get("company") or "").lower() for firm in CONSULTING_FIRMS)
        )
        if consulting_count == len(career) and len(career) >= 2:
            score -= 15.0
            reasoning_parts.append("consulting-only career")
        elif consulting_count > 0:
            score -= (consulting_count / len(career)) * 6.0

    # 3. Wrong-domain title penalty
    if any(kw in current_title for kw in neg_title_kws):
        score -= 18.0
        reasoning_parts.append(f"wrong-domain title: {profile.get('current_title')}")

    # 4. Senior role trajectory
    senior_count = sum(
        1 for r in career
        if any(kw in (r.get("title") or "").lower() for kw in senior_kws)
    )
    score += min(8.0, senior_count * 2.5)
    if senior_count > 0:
        reasoning_parts.append(f"{senior_count} senior roles")

    # 5. Product company experience
    product_industries = {"software", "saas", "fintech", "ai", "ml", "tech",
                          "startup", "product", "platform", "marketplace"}
    product_count = sum(
        1 for r in career
        if any(ind in (r.get("industry") or "").lower() for ind in product_industries)
        and not any(firm in (r.get("company") or "").lower() for firm in CONSULTING_FIRMS)
    )
    score += min(8.0, product_count * 2.5)

    # 6. Title-chaser detection
    if len(career) >= 3:
        durations = [r.get("duration_months", 0) for r in career if not r.get("is_current")]
        if durations and (sum(durations) / len(durations)) < 18:
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

def score_candidate(
    candidate: dict,
    jd_profile: Optional[JDProfile] = None,
) -> dict | None:
    """Score a single candidate against the JD profile. Returns None if honeypot."""
    if is_honeypot(candidate):
        return None

    candidate_id = candidate.get("candidate_id", "UNKNOWN")
    profile = candidate.get("profile", {})

    skills_score, matched_skills = score_skills(candidate, jd_profile)
    career_score, career_reasoning = score_career(candidate, jd_profile)
    behavioral_score, behavioral_signals = score_behavioral(candidate)
    engagement_score = score_engagement(candidate)

    total = skills_score + career_score + behavioral_score + engagement_score
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


def run_ranking(
    candidates_file: str,
    out_file: str,
    sample: int = 0,
    jd_profile: Optional[JDProfile] = None,
) -> None:
    """Full ranking pipeline. Outputs top-100 CSV."""
    logger.info(f"Starting ranking: {candidates_file}")
    logger.info(f"Output: {out_file}")

    t_start = time.time()

    top_k: list[dict] = []  # keep top 200 buffer to ensure we have 100 after dedup
    total_processed = 0
    honeypots_detected = 0
    BUFFER_SIZE = 200  # keep top 200, output top 100

    for candidate in stream_candidates(candidates_file, limit=sample):
        result = score_candidate(candidate, jd_profile)
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
