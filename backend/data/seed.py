"""
CortexHire — Database Seed Script (No-Docker, SQLite + in-memory Qdrant)
"""
from __future__ import annotations

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.postgres import init_db, AsyncSessionLocal
from db.qdrant import qdrant_store
from db.models import Candidate, Job
from data.synthetic_candidates import SYNTHETIC_CANDIDATES
from data.synthetic_jobs import SYNTHETIC_JOBS
from core.role_cognition import extract_role_genome
from core.temporal import compute_temporal_profile
from core.bias_correction import detect_bias_signals

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_database():
    logger.info("🌱 Starting CortexHire database seed (SQLite + in-memory Qdrant)...")

    await init_db()
    logger.info("✅ SQLite tables created")

    await qdrant_store.connect()
    logger.info("✅ Qdrant in-memory started")

    from sqlmodel import select
    async with AsyncSessionLocal() as session:
        # ── Seed Candidates ──────────────────────────────────
        logger.info("📋 Seeding 20 synthetic candidates...")
        seeded = 0
        for c_data in SYNTHETIC_CANDIDATES:
            result = await session.execute(select(Candidate).where(Candidate.name == c_data["name"]))
            if result.scalars().first():
                logger.info(f"  ↩  {c_data['name']} already exists, skipping")
                continue

            temporal = compute_temporal_profile(c_data)
            bias = detect_bias_signals(c_data)

            candidate = Candidate(
                name=c_data["name"],
                email=c_data.get("email"),
                headline=c_data.get("headline"),
                location=c_data.get("location"),
                summary=c_data.get("summary"),
                years_experience=c_data.get("years_experience"),
                education_tier=c_data.get("education_tier"),
                education_detail=c_data.get("education_detail"),
            )
            # Use property setters for JSON fields
            candidate.career_history = c_data.get("career_history", [])
            candidate.skills = c_data.get("skills", [])
            candidate.achievements = c_data.get("achievements", [])
            candidate.capability_profile = c_data.get("capability_profile", {})
            candidate.temporal_profile = temporal
            candidate.bias_flags = bias.get("bias_flags", [])

            session.add(candidate)
            seeded += 1
            logger.info(f"  ✅ {c_data['name']} | trajectory: {temporal['trajectory']} | bias: {bias['bias_flags'] or 'none'}")

        await session.commit()
        logger.info(f"✅ {seeded} new candidates seeded")

        # ── Seed Jobs ────────────────────────────────────────
        logger.info("💼 Seeding 5 synthetic jobs...")
        seeded_jobs = 0
        for j_data in SYNTHETIC_JOBS:
            result = await session.execute(select(Job).where(Job.title == j_data["title"]))
            if result.scalars().first():
                logger.info(f"  ↩  Job '{j_data['title']}' already exists, skipping")
                continue

            job = Job(
                title=j_data["title"],
                company=j_data["company"],
                description=j_data["description"],
                location=j_data.get("location"),
                employment_type=j_data.get("employment_type", "full-time"),
                seniority=j_data.get("seniority"),
                status="pending",
            )
            session.add(job)
            await session.flush()  # Get ID before role genome

            logger.info(f"  🧠 Extracting role genome for: {j_data['title']}...")
            try:
                genome = await extract_role_genome(j_data["description"], j_data["title"], j_data["company"])
                job.role_genome = genome  # uses setter
                job.status = "ready"
                logger.info(
                    f"  ✅ {j_data['title']} | technical: {genome.get('technical_depth', 0):.2f} | "
                    f"ownership: {genome.get('ownership', 0):.2f} | startup: {genome.get('startup_readiness', 0):.2f}"
                )
            except Exception as e:
                logger.warning(f"  ⚠️  Role genome extraction failed: {e}")
                job.status = "pending"

            seeded_jobs += 1

        await session.commit()
        logger.info(f"✅ {seeded_jobs} new jobs seeded")

    logger.info("\n🚀 Seed complete! Now run:")
    logger.info("   uvicorn main:app --reload --port 8000")


if __name__ == "__main__":
    asyncio.run(seed_database())
