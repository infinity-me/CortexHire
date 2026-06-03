"""
CortexHire — FastAPI Main Application
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
            logger.info("Jobs table already has data — skipping seed.")
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
        logger.info("✅ Synthetic jobs seeded successfully.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 CortexHire API starting up...")
    logger.info(f"   LLM Provider: {settings.active_llm}")
    logger.info(f"   Environment: {settings.app_env}")

    # Initialize databases
    try:
        await init_db()
        logger.info("✅ PostgreSQL initialized")
    except Exception as e:
        logger.error(f"❌ PostgreSQL initialization failed: {e}")

    try:
        await neo4j_store.connect()
        logger.info("✅ Neo4j connected")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j not available (graph features disabled): {e}")

    # Seed synthetic jobs if the table is empty (e.g. fresh deploy or DB wipe)
    try:
        await _seed_jobs_if_empty()
        logger.info("✅ Job seed check complete")
    except Exception as e:
        logger.warning(f"⚠️ Job seeding skipped: {e}")

    yield

    # Cleanup
    await neo4j_store.close()
    logger.info("CortexHire API shutting down.")


app = FastAPI(
    title="CortexHire API",
    description="AI Recruitment Intelligence System — Think like an elite recruiter",
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
