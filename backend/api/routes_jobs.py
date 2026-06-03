"""
CortexHire — Jobs API Routes
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import Job, JobCreate, JobRead
from core.role_cognition import extract_role_genome

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


def _job_to_read(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location,
        "employment_type": job.employment_type,
        "seniority": job.seniority,
        "created_at": job.created_at,
        "status": job.status,
        "role_genome": job.role_genome,  # uses property
    }


@router.get("/")
async def list_jobs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Job).order_by(col(Job.created_at).desc()))
    return [_job_to_read(j) for j in result.scalars().all()]


@router.get("/{job_id}")
async def get_job(job_id: str, session: AsyncSession = Depends(get_session)):
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return _job_to_read(job)


@router.post("/", status_code=201)
async def create_job(
    data: JobCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    job = Job(
        title=data.title,
        company=data.company,
        description=data.description,
        location=data.location,
        employment_type=data.employment_type,
        seniority=data.seniority,
        status="pending",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    background_tasks.add_task(_process_role_genome, job.id, data.description, data.title, data.company)
    return _job_to_read(job)


async def _process_role_genome(job_id: str, description: str, title: str, company: str):
    from db.postgres import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            job = await session.get(Job, job_id)
            if not job:
                return
            job.status = "processing"
            await session.commit()
            genome = await extract_role_genome(description, title, company)
            job.role_genome = genome  # uses setter
            job.status = "ready"
            await session.commit()
            logger.info(f"Role genome extracted for job {job_id}")
        except Exception as e:
            logger.error(f"Role genome processing failed for {job_id}: {e}")


@router.post("/{job_id}/analyze")
async def analyze_job(job_id: str, session: AsyncSession = Depends(get_session)):
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    genome = await extract_role_genome(job.description, job.title, job.company)
    job.role_genome = genome
    job.status = "ready"
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return _job_to_read(job)
