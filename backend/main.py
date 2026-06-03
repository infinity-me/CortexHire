"""
CortexHire - FastAPI Main Application
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.postgres import init_db
from db.neo4j_client import neo4j_store
from api.routes_jobs import router as jobs_router
from api.routes_candidates import router as candidates_router
from api.routes_ranking import router as ranking_router
from api.routes_copilot import router as copilot_router
from api.routes_interview import router as interview_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def _seed_jobs_if_empty():
    """Insert the 5 synthetic jobs on first run (or after a DB wipe)."""
    from sqlmodel import select
    from db.postgres import AsyncSessionLocal
    from db.models import Job
    from data.synthetic_jobs import SYNTHETIC_JOBS

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Job).limit(1))
        if result.scalars().first() is not None:
            logger.info("Jobs table already has data - skipping seed.")
            return

        logger.info(f"Seeding {len(SYNTHETIC_JOBS)} synthetic jobs...")
        for job_data in SYNTHETIC_JOBS:
            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                location=job_data.get("location", ""),
                employment_type=job_data.get("employment_type", "full-time"),
                seniority=job_data.get("seniority", ""),
                status="pending",
            )
            session.add(job)
        await session.commit()
        logger.info("Synthetic jobs seeded successfully.")


async def _seed_demo_data():
    """Seed demo candidates, rankings, and interview sessions if tables are empty."""
    from datetime import datetime, timezone, timedelta
    from sqlmodel import select
    from db.postgres import AsyncSessionLocal
    from db.models import (
        Candidate, RankingRun, CandidateRanking,
        InterviewSession, InterviewAnswer, Job
    )
    from data.synthetic_demo import SYNTHETIC_CANDIDATES, RANKING_RESULTS, INTERVIEW_SESSIONS

    async with AsyncSessionLocal() as session:
        # Skip if candidates already exist
        cand_check = await session.execute(select(Candidate).limit(1))
        if cand_check.scalars().first() is not None:
            logger.info("Demo data already seeded - skipping.")
            return

        # Fetch seeded jobs (need their IDs)
        jobs_result = await session.execute(select(Job).order_by(Job.created_at))
        jobs = jobs_result.scalars().all()
        if not jobs:
            logger.warning("No jobs found - skipping demo data seed.")
            return

        logger.info(f"Seeding {len(SYNTHETIC_CANDIDATES)} demo candidates...")

        # Seed Candidates
        candidate_records = []
        for cd in SYNTHETIC_CANDIDATES:
            cand = Candidate(
                name=cd["name"],
                email=cd.get("email"),
                headline=cd.get("headline"),
                location=cd.get("location"),
                summary=cd.get("summary"),
                years_experience=cd.get("years_experience"),
                education_tier=cd.get("education_tier"),
                education_detail=cd.get("education_detail"),
            )
            cand.skills = cd.get("skills", [])
            cand.career_history = cd.get("career_history", [])
            cand.capability_profile = cd.get("capability_profile", {})
            session.add(cand)
            candidate_records.append(cand)

        await session.commit()
        for c in candidate_records:
            await session.refresh(c)

        logger.info(f"{len(candidate_records)} candidates seeded.")

        # Seed Ranking Run (for ZetaPay job - index 0)
        if jobs:
            zetapay_job = jobs[0]
            run = RankingRun(
                job_id=zetapay_job.id,
                status="complete",
                total_candidates=len(SYNTHETIC_CANDIDATES),
                shortlist_size=3,
            )
            session.add(run)
            await session.commit()
            await session.refresh(run)

            for (cand_idx, rank, fit, risk, growth, conf, success_prob, shortlisted, explanation) in RANKING_RESULTS:
                if cand_idx < len(candidate_records):
                    cr = CandidateRanking(
                        run_id=run.id,
                        job_id=zetapay_job.id,
                        candidate_id=candidate_records[cand_idx].id,
                        rank_position=rank,
                        fit_score=fit,
                        risk_score=risk,
                        growth_score=growth,
                        confidence_score=conf,
                        success_probability=success_prob,
                        shortlisted=shortlisted,
                        explanation=explanation,
                    )
                    cr.agent_scores = {
                        "technical_fit": round(fit * 0.95, 1),
                        "culture_fit": round(fit * 0.90, 1),
                        "execution_evidence": round(fit * 0.88, 1),
                        "growth_trajectory": round(growth * 0.92, 1),
                    }
                    cr.bias_report = {
                        "flags": [],
                        "assessment": "No significant bias detected in evaluation.",
                    }
                    session.add(cr)

            await session.commit()
            logger.info(f"Ranking run seeded for {zetapay_job.title}.")

        # Seed Interview Sessions
        base_time = datetime.now(timezone.utc) - timedelta(days=14)

        for i, sd in enumerate(INTERVIEW_SESSIONS):
            job_idx = int(sd["job_index"])
            job = jobs[job_idx] if job_idx < len(jobs) else jobs[0]
            session_time = base_time + timedelta(days=i * 2, hours=i % 3)

            isession = InterviewSession(
                job_id=job.id,
                candidate_name=sd["candidate_name"],
                candidate_email=sd.get("candidate_email"),
                status=sd["status"],
                created_at=session_time,
                completed_at=session_time + timedelta(minutes=30 + i * 5),
                total_score=sd.get("total_score"),
                answer_quality_score=sd.get("answer_quality_score"),
                communication_score=sd.get("communication_score"),
                posture_score=sd.get("posture_score"),
                engagement_score=sd.get("engagement_score"),
                confidence_score=sd.get("confidence_score"),
            )
            isession.questions = sd.get("questions", [])
            session.add(isession)
            await session.commit()
            await session.refresh(isession)

            for q_idx, ans_data in enumerate(list(sd.get("answers", []))):
                ans = InterviewAnswer(
                    session_id=isession.id,
                    question_index=q_idx,
                    question_text=ans_data["q"],
                    transcript=ans_data.get("transcript", ""),
                    answer_quality=ans_data.get("answer_quality"),
                    communication=ans_data.get("communication"),
                    posture=ans_data.get("posture"),
                    engagement=ans_data.get("engagement"),
                    confidence=ans_data.get("confidence"),
                    created_at=session_time + timedelta(minutes=q_idx * 5),
                )
                ans.feedback = ans_data.get("feedback", {})
                session.add(ans)

            await session.commit()

        logger.info(f"{len(INTERVIEW_SESSIONS)} interview sessions seeded.")


async def _seed_dataset_candidates():
    """
    Import real candidates from the competition dataset on first startup.
    Uses sample_candidates.json (50 records) if the dataset file exists.
    The full candidates.jsonl (500k records) can be imported via CLI.
    """
    import os
    from pathlib import Path
    from sqlmodel import select
    from db.postgres import AsyncSessionLocal
    from db.models import Candidate

    # Check if real dataset candidates already exist
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Candidate).where(Candidate.raw_profile.contains("CAND_")).limit(1)  # type: ignore
        )
        if result.scalars().first():
            logger.info("Dataset candidates already seeded — skipping.")
            return

    # Find dataset file relative to this file's location
    backend_dir = Path(__file__).resolve().parent
    dataset_paths = [
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        Path("India_runs_data_and_ai_challenge") / "sample_candidates.json",
        Path("sample_candidates.json"),
    ]

    dataset_file = None
    for p in dataset_paths:
        if p.exists():
            dataset_file = str(p)
            break

    if not dataset_file:
        logger.info("Competition dataset not found — skipping dataset seed (OK for production).")
        return

    logger.info(f"Seeding real candidates from competition dataset: {dataset_file}")
    from data.dataset_importer import import_candidates
    count = await import_candidates(file_path=dataset_file, limit=50, skip_existing=True)
    logger.info(f"Dataset seed complete: {count} real candidates imported.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("CortexHire API starting up...")
    logger.info(f"   LLM Provider: {settings.active_llm}")
    logger.info(f"   Environment: {settings.app_env}")


    # Initialize databases
    try:
        await init_db()
        logger.info("PostgreSQL initialized")
    except Exception as e:
        logger.error(f"PostgreSQL initialization failed: {e}")

    try:
        await neo4j_store.connect()
        logger.info("Neo4j connected")
    except Exception as e:
        logger.warning(f"Neo4j not available (graph features disabled): {e}")

    # Seed synthetic jobs if the table is empty
    try:
        await _seed_jobs_if_empty()
    except Exception as e:
        logger.warning(f"Job seeding skipped: {e}")

    # Seed demo candidates, rankings, and interview sessions
    try:
        await _seed_demo_data()
    except Exception as e:
        logger.warning(f"Demo data seeding skipped: {e}")

    # Seed real candidates from competition dataset (sample_candidates.json)
    try:
        await _seed_dataset_candidates()
    except Exception as e:
        logger.warning(f"Dataset candidates seeding skipped: {e}")


    yield

    # Cleanup
    await neo4j_store.close()
    logger.info("CortexHire API shutting down.")


app = FastAPI(
    title="CortexHire API",
    description="AI Recruitment Intelligence System - Think like an elite recruiter",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(jobs_router)
app.include_router(candidates_router)
app.include_router(ranking_router)
app.include_router(copilot_router)
app.include_router(interview_router)


@app.get("/")
async def root():
    return {
        "service": "CortexHire API",
        "tagline": "Don't hire resumes. Hire potential.",
        "version": "1.0.0",
        "llm_provider": settings.active_llm,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "llm": settings.active_llm,
        "environment": settings.app_env,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=settings.app_env == "development",
    )
