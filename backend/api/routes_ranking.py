"""
CortexHire — Ranking API Routes (SQLite compatible)
"""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import Candidate, CandidateRanking, Job, RankingRun
from core.multi_agent import run_all_agents
from core.embeddings import (
    generate_candidate_embeddings,
    generate_role_embeddings,
    compute_dimension_similarity,
    aggregate_similarity_score,
)
from core.temporal import compute_temporal_profile
from core.bias_correction import detect_bias_signals
from core.ranking import compute_consensus_score, generate_explanation, rank_candidates

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ranking", tags=["Ranking"])


@router.post("/run/{job_id}")
async def run_ranking(
    job_id: str,
    background_tasks: BackgroundTasks,
    shortlist_size: int = 10,
    session: AsyncSession = Depends(get_session),
):
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if not job.role_genome:
        raise HTTPException(400, "Job must be analyzed first. Call /api/jobs/{id}/analyze")

    run = RankingRun(job_id=job_id, status="pending", shortlist_size=shortlist_size)
    session.add(run)
    await session.commit()
    await session.refresh(run)

    background_tasks.add_task(_execute_ranking_pipeline, run.id, job_id, shortlist_size)
    return {"run_id": run.id, "status": "processing", "message": "Ranking pipeline started"}


@router.get("/run/{run_id}/status")
async def get_run_status(run_id: str, session: AsyncSession = Depends(get_session)):
    run = await session.get(RankingRun, run_id)
    if not run:
        raise HTTPException(404, "Ranking run not found")
    return {"run_id": run.id, "status": run.status, "total_candidates": run.total_candidates, "created_at": run.created_at}


@router.get("/results/{run_id}")
async def get_ranking_results(run_id: str, session: AsyncSession = Depends(get_session)):
    run = await session.get(RankingRun, run_id)
    if not run:
        raise HTTPException(404, "Ranking run not found")
    if run.status != "complete":
        return {"status": run.status, "results": [], "run_id": run_id, "job_id": run.job_id, "total_candidates": run.total_candidates}

    result = await session.execute(
        select(CandidateRanking)
        .where(CandidateRanking.run_id == run_id)
        .order_by(CandidateRanking.rank_position)
    )
    rankings = result.scalars().all()

    output = []
    for ranking in rankings:
        candidate = await session.get(Candidate, ranking.candidate_id)
        c_dict = None
        if candidate:
            c_dict = {
                "id": candidate.id,
                "name": candidate.name,
                "headline": candidate.headline,
                "location": candidate.location,
                "years_experience": candidate.years_experience,
                "education_tier": candidate.education_tier,
                "education_detail": candidate.education_detail,
                "skills": candidate.skills or [],
                "achievements": candidate.achievements or [],
                "capability_profile": candidate.capability_profile or {},
                "temporal_profile": candidate.temporal_profile,
                "career_history": candidate.career_history or [],
            }
        output.append({
            "rank_position": ranking.rank_position,
            "fit_score": ranking.fit_score,
            "risk_score": ranking.risk_score,
            "growth_score": ranking.growth_score,
            "confidence_score": ranking.confidence_score,
            "success_probability": ranking.success_probability,
            "explanation": ranking.explanation,
            "agent_scores": ranking.agent_scores,  # uses property
            "bias_report": ranking.bias_report,    # uses property
            "candidate": c_dict,
        })

    return {"run_id": run_id, "job_id": run.job_id, "status": run.status, "total_candidates": run.total_candidates, "results": output}


@router.get("/job/{job_id}/latest")
async def get_latest_ranking(job_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(RankingRun)
        .where(RankingRun.job_id == job_id, RankingRun.status == "complete")
        .order_by(col(RankingRun.created_at).desc())
        .limit(1)
    )
    run = result.scalars().first()
    if not run:
        return {"status": "no_results", "results": [], "job_id": job_id}
    return await get_ranking_results(run.id, session)


async def _execute_ranking_pipeline(run_id: str, job_id: str, shortlist_size: int):
    from db.postgres import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        try:
            run = await session.get(RankingRun, run_id)
            job = await session.get(Job, job_id)
            if not run or not job:
                return

            run.status = "processing"
            await session.commit()

            result = await session.execute(select(Candidate))
            candidates = result.scalars().all()
            run.total_candidates = len(candidates)
            await session.commit()

            job_dict = {"id": job.id, "title": job.title, "company": job.company, "description": job.description, "seniority": job.seniority}
            role_genome = job.role_genome or {}

            role_embeddings = await generate_role_embeddings(role_genome, job.description)

            scored = []
            for candidate in candidates:
                candidate_dict = {
                    "id": candidate.id,
                    "name": candidate.name,
                    "headline": candidate.headline,
                    "location": candidate.location,
                    "summary": candidate.summary,
                    "years_experience": candidate.years_experience,
                    "education_tier": candidate.education_tier,
                    "education_detail": candidate.education_detail,
                    "career_history": candidate.career_history or [],
                    "skills": candidate.skills or [],
                    "achievements": candidate.achievements or [],
                    "capability_profile": candidate.capability_profile or {},
                }

                agent_results, candidate_embeddings = await asyncio.gather(
                    run_all_agents(candidate_dict, job_dict, role_genome),
                    generate_candidate_embeddings(candidate_dict),
                )

                dimension_sims = compute_dimension_similarity(candidate_embeddings, role_embeddings, role_genome)
                embedding_similarity = aggregate_similarity_score(dimension_sims, role_genome)
                temporal_profile = compute_temporal_profile(candidate_dict)
                bias_analysis = detect_bias_signals(candidate_dict)

                consensus = compute_consensus_score(
                    agent_results=agent_results,
                    embedding_similarity=embedding_similarity,
                    temporal_profile=temporal_profile,
                    bias_analysis=bias_analysis,
                    role_genome=role_genome,
                )

                scored.append({
                    "candidate": candidate_dict,
                    "candidate_db": candidate,
                    "agent_results": agent_results,
                    "consensus": consensus,
                    "bias_analysis": bias_analysis,
                    "temporal_profile": temporal_profile,
                })

            ranked = rank_candidates(scored, shortlist_size)

            for ranked_item in ranked:
                explanation = await generate_explanation(
                    candidate=ranked_item["candidate"],
                    job=job_dict,
                    consensus=ranked_item["consensus"],
                    agent_results=ranked_item["agent_results"],
                    bias_analysis=ranked_item["bias_analysis"],
                )

                consensus = ranked_item["consensus"]
                ranking = CandidateRanking(
                    run_id=run_id,
                    job_id=job_id,
                    candidate_id=ranked_item["candidate"]["id"],
                    rank_position=ranked_item["rank_position"],
                    fit_score=consensus["fit_score"],
                    risk_score=consensus["risk_score"],
                    growth_score=consensus["growth_score"],
                    confidence_score=consensus["confidence_score"],
                    success_probability=consensus["success_probability"],
                    explanation=explanation,
                    shortlisted=True,
                )
                # Set JSON fields via properties
                ranking.agent_scores = {
                    "agent_results": ranked_item["agent_results"],
                    "embedding_similarity": consensus["embedding_similarity"],
                    "trajectory": consensus["trajectory"],
                    "raw_agent_score": consensus["raw_agent_score"],
                }
                ranking.bias_report = ranked_item["bias_analysis"]
                session.add(ranking)

                c_db = ranked_item["candidate_db"]
                c_db.temporal_profile = ranked_item["temporal_profile"]
                session.add(c_db)

            run.status = "complete"
            await session.commit()
            logger.info(f"Ranking run {run_id} complete. {len(ranked)} candidates ranked.")

        except Exception as e:
            logger.error(f"Ranking pipeline failed for run {run_id}: {e}", exc_info=True)
            try:
                run = await session.get(RankingRun, run_id)
                if run:
                    run.status = "failed"
                    await session.commit()
            except Exception:
                pass
