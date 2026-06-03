"""
CortexHire - Bulk Resume Upload & Candidate Ingestion

POST /api/candidates/bulk-upload
  Accepts multiple resume files (PDF, DOCX, TXT).
  For each file:
    1. Extracts raw text (pypdf / python-docx / utf-8)
    2. Uses LLM to parse structured candidate profile
    3. Saves Candidate record to DB
    4. Returns per-file status

POST /api/candidates/  (single)
  Create a single candidate from JSON.

GET /api/candidates/
GET /api/candidates/count/total
GET /api/candidates/{id}
"""
from __future__ import annotations

import json
import logging
import tempfile
import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.postgres import get_session
from db.models import Candidate
from core.llm_router import llm_chat
from core.temporal import compute_temporal_profile

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

# ── In-memory import job tracker ──────────────────────────────
_import_jobs: dict[str, dict] = {}


# ── LLM prompt for extracting candidate profile from resume text ──

RESUME_PARSE_PROMPT = """
You are an AI recruiter assistant that extracts structured candidate profiles from raw resume text.

Given the resume text below, extract a complete structured profile.
Be intelligent — infer years of experience from dates, estimate capability scores from evidence.

Return ONLY valid JSON with EXACTLY this structure:
{
  "name": "<full name>",
  "email": "<email or null>",
  "headline": "<one-line professional headline, e.g. 'Senior Backend Engineer | Payments & FinTech'>",
  "location": "<city, country or null>",
  "summary": "<2-3 sentence professional summary>",
  "years_experience": <number, float>,
  "education_tier": "<tier1|tier2|tier3|bootcamp|self-taught>",
  "education_detail": "<degree, institution, year>",
  "skills": [
    {"name": "<skill name>", "level": "<expert|proficient|familiar>", "years": <number>}
  ],
  "achievements": [
    "<one-line achievement with quantified impact if possible>"
  ],
  "career_history": [
    {
      "title": "<job title>",
      "company": "<company name>",
      "start_year": <year>,
      "end_year": <year or null for current>,
      "description": "<2-3 sentence description of impact and scope>",
      "team_size": <estimated team size, integer>,
      "impact_score": <0.0-1.0, your assessment of impact>
    }
  ],
  "capability_profile": {
    "technical_depth": <0.0-1.0>,
    "adaptability": <0.0-1.0>,
    "leadership": <0.0-1.0>,
    "execution": <0.0-1.0>,
    "systems_thinking": <0.0-1.0>,
    "creativity": <0.0-1.0>,
    "resilience": <0.0-1.0>,
    "communication": <0.0-1.0>
  }
}

Education tier guide:
- tier1: IIT, IIM, IISc, Ivy League, MIT, Stanford, Oxford, Cambridge, NIT top 5
- tier2: Other reputed universities, top state universities
- tier3: Private colleges, lesser-known universities
- bootcamp: Coding bootcamp, online certification programs
- self-taught: No formal CS degree, self-taught developer

Be generous but honest with capability scores. Base them on evidence in the resume.
"""


def _extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract plain text from PDF, DOCX, or TXT file."""
    fn = filename.lower()

    if fn.endswith(".pdf"):
        import io
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

    elif fn.endswith(".docx"):
        import io
        from docx import Document
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

    elif fn.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore").strip()

    raise ValueError(f"Unsupported file type: {filename}")


async def _parse_candidate_from_text(resume_text: str, filename: str) -> dict:
    """Use LLM to parse structured candidate profile from resume text."""
    truncated = " ".join(resume_text.split()[:2500])  # ~3000 word cap
    messages = [
        {"role": "system", "content": RESUME_PARSE_PROMPT},
        {"role": "user", "content": f"Resume text (from file: {filename}):\n\n{truncated}"},
    ]
    raw = await llm_chat(
        messages=messages,
        temperature=0.2,
        max_tokens=2000,
        json_mode=True,
        task_name="resume_parse_candidate",
    )
    return json.loads(raw)


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


# ── Endpoints ────────────────────────────────────────────────

@router.post("/bulk-upload")
async def bulk_upload_resumes(
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_session),
):
    """
    Gap 2: Upload multiple resumes — each is parsed by LLM into a structured Candidate profile.
    Accepts: PDF, DOCX, TXT (up to 20 files, 10 MB each).
    """
    if len(files) > 20:
        raise HTTPException(400, "Maximum 20 files per upload batch.")

    results = []
    for file in files:
        filename = file.filename or "unknown"
        try:
            content = await file.read()
            if len(content) > 10 * 1024 * 1024:
                results.append({"filename": filename, "status": "error", "error": "File too large (max 10 MB)"})
                continue

            # 1. Extract text
            resume_text = _extract_text_from_file(content, filename)
            if not resume_text or len(resume_text.strip()) < 50:
                results.append({"filename": filename, "status": "error", "error": "Could not extract enough text from file"})
                continue

            # 2. LLM parse → structured profile
            profile = await _parse_candidate_from_text(resume_text, filename)

            # 3. Save to DB
            cand = Candidate(
                name=profile.get("name", filename.rsplit(".", 1)[0]),
                email=profile.get("email"),
                headline=profile.get("headline"),
                location=profile.get("location"),
                summary=profile.get("summary"),
                years_experience=profile.get("years_experience"),
                education_tier=profile.get("education_tier"),
                education_detail=profile.get("education_detail"),
                raw_profile=resume_text[:5000],
            )
            cand.skills = profile.get("skills", [])
            cand.achievements = profile.get("achievements", [])
            cand.career_history = profile.get("career_history", [])
            cand.capability_profile = profile.get("capability_profile", {})

            # Compute temporal profile from career history
            try:
                temporal = compute_temporal_profile({
                    "career_history": profile.get("career_history", []),
                    "years_experience": profile.get("years_experience", 0),
                })
                cand.temporal_profile = temporal
            except Exception:
                pass

            session.add(cand)
            await session.commit()
            await session.refresh(cand)

            results.append({
                "filename": filename,
                "status": "success",
                "candidate_id": cand.id,
                "name": cand.name,
                "headline": cand.headline,
                "years_experience": cand.years_experience,
                "skills_count": len(profile.get("skills", [])),
            })

        except Exception as e:
            logger.error(f"Failed to process resume {filename}: {e}", exc_info=True)
            results.append({"filename": filename, "status": "error", "error": str(e)[:200]})

    success_count = sum(1 for r in results if r["status"] == "success")
    return {
        "total": len(files),
        "succeeded": success_count,
        "failed": len(files) - success_count,
        "results": results,
    }


@router.get("/")
async def list_candidates(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Candidate).order_by(col(Candidate.created_at).desc()))
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


# ── Dataset Import ────────────────────────────────────────────

async def _run_dataset_import(import_id: str, tmp_path: str, limit: int, file_ext: str):
    """Background task: run dataset_importer and update the job tracker."""
    import os
    _import_jobs[import_id]["status"] = "running"
    try:
        from data.dataset_importer import import_candidates
        count = await import_candidates(file_path=tmp_path, limit=limit, skip_existing=True)
        _import_jobs[import_id].update({"status": "complete", "imported": count})
        logger.info(f"Dataset import {import_id} complete: {count} imported")
    except Exception as e:
        logger.error(f"Dataset import {import_id} failed: {e}", exc_info=True)
        _import_jobs[import_id].update({"status": "failed", "error": str(e)[:300]})
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


@router.post("/import-dataset")
async def import_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    limit: int = 500,
):
    """
    Upload a .jsonl or .json candidate dataset file and import up to `limit` candidates.

    The import runs in the background. Poll GET /api/candidates/import-status/{import_id}
    to check progress.

    Args:
        file:   .jsonl or .json dataset file (e.g. candidates.jsonl)
        limit:  Maximum candidates to import (default 500, max 10000)
    """
    filename = file.filename or "upload"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ".json"
    if ext not in (".json", ".jsonl"):
        raise HTTPException(400, "Only .json and .jsonl files are supported")
    if limit < 1 or limit > 10_000:
        raise HTTPException(400, "limit must be between 1 and 10000")

    content = await file.read()
    if len(content) > 200 * 1024 * 1024:  # 200 MB max
        raise HTTPException(400, "File too large (max 200 MB)")

    # Write to temp file so dataset_importer can stream it
    with tempfile.NamedTemporaryFile(mode="wb", suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    import_id = str(uuid.uuid4())
    _import_jobs[import_id] = {
        "import_id": import_id,
        "status": "queued",
        "filename": filename,
        "limit": limit,
        "imported": 0,
        "error": None,
    }

    background_tasks.add_task(_run_dataset_import, import_id, tmp_path, limit, ext)
    return {
        "import_id": import_id,
        "status": "queued",
        "filename": filename,
        "limit": limit,
        "message": f"Import started — up to {limit} candidates will be imported in the background.",
    }


@router.get("/import-status/{import_id}")
async def get_import_status(import_id: str):
    """Poll the status of a background dataset import."""
    job = _import_jobs.get(import_id)
    if not job:
        raise HTTPException(404, "Import job not found")
    return job
