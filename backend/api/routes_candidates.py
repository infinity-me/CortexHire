"""
CortexHire — Candidates API Routes (SQLite compatible)
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import Candidate
from core.temporal import compute_temporal_profile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/candidates", tags=["Candidates"])


def _candidate_to_dict(c: Candidate) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "headline": c.headline,
        "location": c.location,
        "summary": c.summary,
        "years_experience": c.years_experience,
        "education_tier": c.education_tier,
        "education_detail": c.education_detail,
        "created_at": c.created_at,
        "career_history": c.career_history or [],
        "skills": c.skills or [],
        "achievements": c.achievements or [],
        "capability_profile": c.capability_profile or {},
        "temporal_profile": c.temporal_profile,
    }


@router.get("/")
async def list_candidates(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Candidate).order_by(Candidate.created_at.desc()))
    return [_candidate_to_dict(c) for c in result.scalars().all()]


@router.get("/count/total")
async def count_candidates(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Candidate))
    candidates = result.scalars().all()
    return {"total": len(candidates)}


@router.get("/{candidate_id}")
async def get_candidate(candidate_id: str, session: AsyncSession = Depends(get_session)):
    candidate = await session.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(404, "Candidate not found")
    d = _candidate_to_dict(candidate)
    if not d["temporal_profile"]:
        d["temporal_profile"] = compute_temporal_profile({
            "career_history": d["career_history"],
            "years_experience": d["years_experience"] or 0,
        })
    return d
