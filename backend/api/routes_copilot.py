"""
CortexHire — Recruiter Copilot API Routes (SQLite compatible)
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import CandidateRanking, CopilotMessage, Job, RankingRun, Candidate
from core.llm_router import llm_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/copilot", tags=["Copilot"])


class CopilotRequest(BaseModel):
    message: str
    job_id: str
    run_id: Optional[str] = None


COPILOT_SYSTEM_PROMPT = """
You are the CortexHire Recruiter Copilot — an elite AI recruiting assistant.

You have access to a complete AI-generated ranking of candidates for a specific job.
You help recruiters understand the ranking, explore tradeoffs, and make better decisions.

Your responses should be:
- Direct and evidence-based
- Reference specific candidates by name and rank
- Highlight key differences between candidates
- Be honest about risks and limitations
- Avoid HR corporate speak
- Sound like a trusted senior recruiter, not a chatbot

Never make up facts. If you don't have information, say so.
"""


@router.post("/chat")
async def copilot_chat(
    request: CopilotRequest,
    session: AsyncSession = Depends(get_session),
):
    job = await session.get(Job, request.job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    run_id = request.run_id
    if not run_id:
        result = await session.execute(
            select(RankingRun)
            .where(RankingRun.job_id == request.job_id, RankingRun.status == "complete")
            .order_by(col(RankingRun.created_at).desc())
            .limit(1)
        )
        run = result.scalars().first()
        if run:
            run_id = run.id

    ranking_context = ""
    if run_id:
        rankings_result = await session.execute(
            select(CandidateRanking)
            .where(CandidateRanking.run_id == run_id)
            .order_by(CandidateRanking.rank_position)
        )
        rankings = rankings_result.scalars().all()

        ranking_lines = []
        for r in rankings:
            candidate = await session.get(Candidate, r.candidate_id)
            name = candidate.name if candidate else "Unknown"
            headline = (candidate.headline or "")[:60] if candidate else ""
            explanation_snippet = (r.explanation or "")[:250]
            shortlist_tag = " [SHORTLISTED]" if r.shortlisted else ""
            ranking_lines.append(
                f"#{r.rank_position}{shortlist_tag} {name} | {headline}\n"
                f"  Fit: {r.fit_score:.0f}/100 | Risk: {r.risk_score:.0f}/100 | "
                f"Growth: {r.growth_score:.0f}/100 | Success: {r.success_probability:.0f}%\n"
                f"  Assessment: {explanation_snippet}"
            )
        ranking_context = "\n\n".join(ranking_lines)

    genome = job.role_genome or {}

    def _pct(key: str) -> str:
        v = genome.get(key)
        return f"{v:.0%}" if isinstance(v, (int, float)) else "N/A"

    context_message = f"""
JOB: {job.title} at {job.company}
LOCATION: {job.location or "Not specified"} | SENIORITY: {job.seniority or "Not specified"}
ROLE GENOME: Technical depth {_pct("technical_depth")} | Ownership {_pct("ownership")} | Startup readiness {_pct("startup_readiness")}

RANKED CANDIDATES:
{ranking_context if ranking_context else "No ranking data yet. I can still answer general questions about this job, discuss what to look for in candidates, or help you think through the role requirements."}
    """.strip()

    history_result = await session.execute(
        select(CopilotMessage)
        .where(CopilotMessage.job_id == request.job_id)
        .order_by(col(CopilotMessage.created_at).desc())
        .limit(6)
    )
    history = list(reversed(history_result.scalars().all()))

    messages = [
        {"role": "system", "content": COPILOT_SYSTEM_PROMPT},
        {"role": "system", "content": f"Current ranking context:\n{context_message}"},
    ]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": request.message})

    response = await llm_chat(
        messages=messages,
        temperature=0.5,
        max_tokens=800,
        json_mode=False,
        task_name="copilot_chat",
    )

    user_msg = CopilotMessage(job_id=request.job_id, role="user", content=request.message, context_run_id=run_id)
    assistant_msg = CopilotMessage(job_id=request.job_id, role="assistant", content=response, context_run_id=run_id)
    session.add(user_msg)
    session.add(assistant_msg)
    await session.commit()

    return {"response": response, "job_id": request.job_id, "run_id": run_id}


@router.get("/history/{job_id}")
async def get_history(job_id: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(CopilotMessage)
        .where(CopilotMessage.job_id == job_id)
        .order_by(col(CopilotMessage.created_at).asc())
    )
    messages = result.scalars().all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in messages]
