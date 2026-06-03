"""
CortexHire — Live Interview Panel API Routes

Endpoints:
  POST /api/interview/start           — Generate questions + create session
  POST /api/interview/evaluate-answer — Score a candidate's answer (text)
  POST /api/interview/analyze-frame   — Analyze posture/body language from image
  POST /api/interview/report/{id}     — Aggregate all scores into final report
  GET  /api/interview/sessions        — List past interview sessions
  GET  /api/interview/session/{id}    — Get session details + answers
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import InterviewSession, InterviewAnswer, Job
from core.llm_router import llm_chat, llm_vision_chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/interview", tags=["Interview"])


# ─── Request / Response Models ───────────────────────────────

class StartInterviewRequest(BaseModel):
    job_id: str
    candidate_name: str
    candidate_email: Optional[str] = None
    num_questions: int = 6


class EvaluateAnswerRequest(BaseModel):
    session_id: str
    question_index: int
    question_text: str
    transcript: str
    # Optional posture scores already collected for this question
    posture_score: Optional[float] = None
    engagement_score: Optional[float] = None
    confidence_score: Optional[float] = None


class AnalyzeFrameRequest(BaseModel):
    session_id: str
    question_index: int
    image_base64: str          # base64 JPEG
    image_mime: str = "image/jpeg"
    current_question: str = ""


# ─── Question Generation Prompt ─────────────────────────────

QUESTION_GEN_PROMPT = """
You are an elite technical interviewer preparing a live video interview for a specific job role.

Job Title: {title}
Company: {company}
Job Description: {description}
Role Genome (AI-extracted traits): {genome}

Generate exactly {num_questions} interview questions for this role. The questions must:
1. Be specific to this job — not generic HR questions
2. Cover: technical depth (2 questions), ownership/execution (1), problem-solving (1), behavioral (1), situational/culture (1)
3. Be concise (1-2 sentences each) — clearly worded, no ambiguity
4. Be genuinely challenging — not softballs
5. Be ordered from warm-up → hard → behavioral → closing

Return ONLY a valid JSON array of strings. No extra text, no numbering, no markdown.
Example: ["Question 1?", "Question 2?", ...]
"""

ANSWER_EVAL_PROMPT = """
You are an honest, experienced technical interviewer evaluating a candidate's answer.

Job: {job_title} at {company}
Question: {question}
Candidate's Answer (transcript): {transcript}

Score this answer honestly across two dimensions (0-100 each):

1. answer_quality (0-100): How well did the candidate actually answer the question?
   - 0-40: Vague, off-topic, or shows major knowledge gaps
   - 41-65: Partial answer, some relevant points but missing depth
   - 66-80: Solid answer with relevant specifics
   - 81-100: Excellent — specific, structured, demonstrates mastery

2. communication (0-100): How clearly did they communicate?
   - 0-40: Very hard to follow, no structure
   - 41-65: Understandable but rambling or unclear
   - 66-80: Clear and organized
   - 81-100: Excellent structure (STAR method or similar), very articulate

Also provide:
- strength: One specific thing they did well (be specific, quote their words if possible)
- weakness: One specific gap or missed opportunity (be honest, don't sugarcoat)
- suggested_followup: A good follow-up question the interviewer could ask

Return ONLY valid JSON:
{{
  "answer_quality": <number 0-100>,
  "communication": <number 0-100>,
  "strength": "<string>",
  "weakness": "<string>",
  "suggested_followup": "<string>",
  "overall_comment": "<2-3 sentence honest assessment>"
}}
"""

VISION_ANALYSIS_PROMPT = """
You are analyzing a video frame from a live job interview. Assess the candidate's body language and non-verbal communication.

Current interview question: {question}

Look at this image and score the candidate on these dimensions (0-100 each):

1. posture_score (0-100): Is the candidate sitting upright? Shoulders back? Not slouching?
   - 0-40: Clearly slouching, leaning back, or poor posture
   - 41-65: Somewhat upright but could be better
   - 66-80: Good posture maintained
   - 81-100: Excellent — confident, upright, professional

2. eye_contact_score (0-100): Are they looking at the camera (making "eye contact")?
   - 0-40: Mostly looking away, down at notes, or to the side
   - 41-65: Some eye contact but frequently looking away
   - 66-80: Good eye contact most of the time
   - 81-100: Excellent — consistent camera engagement

3. engagement_score (0-100): Overall energy, attentiveness, facial expression
   - 0-40: Appears disengaged, bored, or distracted
   - 41-65: Neutral/passive engagement
   - 66-80: Engaged and attentive
   - 81-100: Highly engaged, expressive, enthusiastic

4. confidence_score (0-100): Physical confidence signals (posture, expression, stillness vs fidgeting)
   - 0-40: Appears nervous — fidgeting, looking down, tense
   - 41-65: Some confidence signals mixed with nervousness
   - 66-80: Mostly confident
   - 81-100: Highly confident, composed, calm

Be HONEST. Not all candidates score highly. If the image is low-quality or unclear, note that.

Return ONLY valid JSON:
{{
  "posture_score": <0-100>,
  "eye_contact_score": <0-100>,
  "engagement_score": <0-100>,
  "confidence_score": <0-100>,
  "observations": ["<observation 1>", "<observation 2>"],
  "overall_body_language": <average 0-100>,
  "source": "gemini"
}}
"""

REPORT_SUMMARY_PROMPT = """
You are writing a final, honest interview assessment report for a recruiter.

Candidate: {candidate_name}
Job: {job_title} at {company}

Interview Performance Summary:
- Answer Quality Score: {answer_quality}/100
- Communication Score: {communication}/100
- Posture Score: {posture}/100
- Engagement Score: {engagement}/100
- Confidence Score: {confidence}/100
- OVERALL SCORE: {total}/100

Per-Question Performance:
{qa_summary}

Write an honest assessment. Do NOT inflate scores or give empty praise.
Be direct, specific, and reference actual answers where possible.

Return ONLY valid JSON:
{{
  "verdict": "strong_hire" | "hire" | "maybe" | "no_hire" | "strong_no_hire",
  "headline": "<one punchy sentence summarizing the candidate>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "concerns": ["<concern 1>", "<concern 2>"],
  "body_language_summary": "<2 sentences about non-verbal communication>",
  "recommendation": "<2-3 sentences — what should the recruiter do next?>"
}}
"""


# ─── Endpoints ──────────────────────────────────────────────

@router.post("/start")
async def start_interview(
    req: StartInterviewRequest,
    session: AsyncSession = Depends(get_session),
):
    """Start a new interview session and generate tailored questions."""
    job = await session.get(Job, req.job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    genome = job.role_genome or {}
    genome_summary = ", ".join(
        f"{k}: {v:.0%}" for k, v in genome.items()
        if isinstance(v, float)
    ) if genome else "Not available"

    prompt = QUESTION_GEN_PROMPT.format(
        title=job.title,
        company=job.company,
        description=(job.description or "")[:800],
        genome=genome_summary,
        num_questions=req.num_questions,
    )

    raw = await llm_chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=1000,
        json_mode=False,
        task_name="interview_questions",
    )

    # Parse question list
    try:
        # Strip markdown fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])
        questions = json.loads(cleaned)
        if not isinstance(questions, list):
            raise ValueError("Not a list")
    except Exception:
        # Fallback: extract JSON array manually
        import re
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            questions = json.loads(match.group())
        else:
            questions = _fallback_questions(job.title, req.num_questions)

    # Create session in DB
    interview_session = InterviewSession(
        job_id=req.job_id,
        candidate_name=req.candidate_name,
        candidate_email=req.candidate_email,
        status="active",
    )
    interview_session.questions = questions[:req.num_questions]
    session.add(interview_session)
    await session.commit()
    await session.refresh(interview_session)

    return {
        "session_id": interview_session.id,
        "questions": questions[:req.num_questions],
        "job_title": job.title,
        "company": job.company,
        "candidate_name": req.candidate_name,
    }


@router.post("/evaluate-answer")
async def evaluate_answer(
    req: EvaluateAnswerRequest,
    session: AsyncSession = Depends(get_session),
):
    """Score a candidate's spoken answer using LLM evaluation."""
    interview = await session.get(InterviewSession, req.session_id)
    if not interview:
        raise HTTPException(404, "Interview session not found")

    job = await session.get(Job, interview.job_id)
    job_title = job.title if job else "Unknown Role"
    company = job.company if job else "Unknown Company"

    if not req.transcript or len(req.transcript.strip()) < 10:
        # No answer given — score it harshly
        scores = {
            "answer_quality": 5.0,
            "communication": 5.0,
            "strength": "No answer provided",
            "weakness": "Candidate did not answer this question",
            "suggested_followup": "Please try again and provide a response",
            "overall_comment": "No answer was given for this question.",
        }
    else:
        prompt = ANSWER_EVAL_PROMPT.format(
            job_title=job_title,
            company=company,
            question=req.question_text,
            transcript=req.transcript,
        )
        raw = await llm_chat(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
            json_mode=True,
            task_name="interview_answer_eval",
        )
        try:
            scores = json.loads(raw)
        except Exception:
            scores = {"answer_quality": 50.0, "communication": 50.0,
                      "strength": "N/A", "weakness": "N/A",
                      "suggested_followup": "N/A", "overall_comment": "Parse error"}

    # Use vision scores if provided, else defaults
    posture = req.posture_score if req.posture_score is not None else 55.0
    engagement = req.engagement_score if req.engagement_score is not None else 55.0
    confidence = req.confidence_score if req.confidence_score is not None else 55.0

    # Upsert answer record
    existing_result = await session.execute(
        select(InterviewAnswer)
        .where(InterviewAnswer.session_id == req.session_id,
               InterviewAnswer.question_index == req.question_index)
    )
    existing = existing_result.scalars().first()

    if existing:
        existing.transcript = req.transcript
        existing.answer_quality = float(scores.get("answer_quality", 50))
        existing.communication = float(scores.get("communication", 50))
        existing.posture = posture
        existing.engagement = engagement
        existing.confidence = confidence
        existing.feedback = scores
        session.add(existing)
    else:
        answer = InterviewAnswer(
            session_id=req.session_id,
            question_index=req.question_index,
            question_text=req.question_text,
            transcript=req.transcript,
            answer_quality=float(scores.get("answer_quality", 50)),
            communication=float(scores.get("communication", 50)),
            posture=posture,
            engagement=engagement,
            confidence=confidence,
        )
        answer.feedback = scores
        session.add(answer)

    await session.commit()

    return {
        "question_index": req.question_index,
        "answer_quality": float(scores.get("answer_quality", 50)),
        "communication": float(scores.get("communication", 50)),
        "posture": posture,
        "engagement": engagement,
        "confidence": confidence,
        "feedback": scores,
    }


@router.post("/analyze-frame")
async def analyze_frame(
    req: AnalyzeFrameRequest,
    session: AsyncSession = Depends(get_session),
):
    """Analyze a webcam frame for posture and body language using Gemini Vision."""
    interview = await session.get(InterviewSession, req.session_id)
    if not interview:
        raise HTTPException(404, "Interview session not found")

    prompt = VISION_ANALYSIS_PROMPT.format(
        question=req.current_question or "General interview question"
    )

    raw = await llm_vision_chat(
        prompt=prompt,
        image_base64=req.image_base64,
        image_mime=req.image_mime,
        task_name="interview_frame_analysis",
    )

    try:
        result = json.loads(raw)
    except Exception:
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group()) if match else {
            "posture_score": 55, "eye_contact_score": 55,
            "engagement_score": 55, "confidence_score": 55,
            "observations": [], "overall_body_language": 55, "source": "error"
        }

    return result


@router.post("/report/{session_id}")
async def generate_report(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Aggregate all answer scores + body language → final interview report."""
    interview = await session.get(InterviewSession, session_id)
    if not interview:
        raise HTTPException(404, "Interview session not found")

    job = await session.get(Job, interview.job_id)

    answers_result = await session.execute(
        select(InterviewAnswer)
        .where(InterviewAnswer.session_id == session_id)
        .order_by(InterviewAnswer.question_index)
    )
    answers = answers_result.scalars().all()

    if not answers:
        raise HTTPException(400, "No answers recorded yet")

    # Aggregate scores
    def avg(vals): return round(sum(vals) / len(vals), 1) if vals else 0.0

    aq_scores = [a.answer_quality for a in answers if a.answer_quality is not None]
    comm_scores = [a.communication for a in answers if a.communication is not None]
    posture_scores = [a.posture for a in answers if a.posture is not None]
    engagement_scores = [a.engagement for a in answers if a.engagement is not None]
    confidence_scores = [a.confidence for a in answers if a.confidence is not None]

    answer_quality_avg = avg(aq_scores)
    communication_avg = avg(comm_scores)
    posture_avg = avg(posture_scores)
    engagement_avg = avg(engagement_scores)
    confidence_avg = avg(confidence_scores)

    # Weighted total: 40% AQ + 15% Comm + 20% Posture + 15% Engagement + 10% Confidence
    total = round(
        answer_quality_avg * 0.40 +
        communication_avg * 0.15 +
        posture_avg * 0.20 +
        engagement_avg * 0.15 +
        confidence_avg * 0.10,
        1
    )

    # Build Q&A summary for LLM
    qa_lines = []
    for a in answers:
        fb = a.feedback or {}
        qa_lines.append(
            f"Q{a.question_index + 1}: {a.question_text}\n"
            f"  Transcript: {(a.transcript or 'No answer')[:200]}\n"
            f"  Scores: AQ={a.answer_quality:.0f}, Comm={a.communication:.0f}, "
            f"Posture={a.posture:.0f}, Engagement={a.engagement:.0f}\n"
            f"  Comment: {fb.get('overall_comment', '')}"
        )
    qa_summary = "\n\n".join(qa_lines)

    prompt = REPORT_SUMMARY_PROMPT.format(
        candidate_name=interview.candidate_name,
        job_title=job.title if job else "Unknown",
        company=job.company if job else "Unknown",
        answer_quality=answer_quality_avg,
        communication=communication_avg,
        posture=posture_avg,
        engagement=engagement_avg,
        confidence=confidence_avg,
        total=total,
        qa_summary=qa_summary,
    )

    raw = await llm_chat(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=800,
        json_mode=True,
        task_name="interview_report",
    )

    try:
        ai_summary = json.loads(raw)
    except Exception:
        ai_summary = {
            "verdict": "maybe",
            "headline": "Interview completed",
            "strengths": [],
            "concerns": [],
            "body_language_summary": "",
            "recommendation": "Review the individual question scores for details.",
        }

    # Persist final scores
    interview.status = "complete"
    interview.completed_at = datetime.utcnow()
    interview.total_score = total
    interview.answer_quality_score = answer_quality_avg
    interview.communication_score = communication_avg
    interview.posture_score = posture_avg
    interview.engagement_score = engagement_avg
    interview.confidence_score = confidence_avg
    session.add(interview)
    await session.commit()

    # Build per-question breakdown for response
    per_question = []
    for a in answers:
        fb = a.feedback or {}
        per_question.append({
            "question_index": a.question_index,
            "question_text": a.question_text,
            "transcript": a.transcript or "",
            "answer_quality": a.answer_quality,
            "communication": a.communication,
            "posture": a.posture,
            "engagement": a.engagement,
            "confidence": a.confidence,
            "feedback": fb,
        })

    return {
        "session_id": session_id,
        "candidate_name": interview.candidate_name,
        "job_title": job.title if job else "",
        "company": job.company if job else "",
        "total_score": total,
        "scores": {
            "answer_quality": answer_quality_avg,
            "communication": communication_avg,
            "posture": posture_avg,
            "engagement": engagement_avg,
            "confidence": confidence_avg,
        },
        "ai_summary": ai_summary,
        "per_question": per_question,
    }


@router.get("/sessions")
async def list_sessions(session: AsyncSession = Depends(get_session)):
    """List all past interview sessions."""
    result = await session.execute(
        select(InterviewSession).order_by(col(InterviewSession.created_at).desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "job_id": s.job_id,
            "candidate_name": s.candidate_name,
            "status": s.status,
            "total_score": s.total_score,
            "created_at": s.created_at,
        }
        for s in sessions
    ]


@router.get("/session/{session_id}")
async def get_session_detail(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get full interview session details including per-question answers."""
    interview = await session.get(InterviewSession, session_id)
    if not interview:
        raise HTTPException(404, "Session not found")

    answers_result = await session.execute(
        select(InterviewAnswer)
        .where(InterviewAnswer.session_id == session_id)
        .order_by(InterviewAnswer.question_index)
    )
    answers = answers_result.scalars().all()

    return {
        "id": interview.id,
        "job_id": interview.job_id,
        "candidate_name": interview.candidate_name,
        "status": interview.status,
        "total_score": interview.total_score,
        "created_at": interview.created_at,
        "questions": interview.questions or [],
        "answers": [
            {
                "question_index": a.question_index,
                "question_text": a.question_text,
                "transcript": a.transcript,
                "answer_quality": a.answer_quality,
                "communication": a.communication,
                "posture": a.posture,
                "engagement": a.engagement,
                "confidence": a.confidence,
                "feedback": a.feedback,
            }
            for a in answers
        ],
    }


# ─── Helpers ─────────────────────────────────────────────────

def _fallback_questions(job_title: str, n: int) -> list[str]:
    """Fallback questions if LLM parsing fails."""
    base = [
        f"Walk me through the most technically complex project you've led that's relevant to this {job_title} role.",
        "Describe a situation where you had to make a critical technical decision with incomplete information. What was the outcome?",
        "Tell me about a time you disagreed strongly with a technical direction. How did you handle it?",
        "What does 'ownership' mean to you in an engineering context? Give me a concrete example.",
        "If you joined this team tomorrow, what would you spend your first 30 days doing?",
        "What's a skill gap you're actively working on right now?",
    ]
    return base[:n]
