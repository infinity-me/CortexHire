"""
CortexHire — Challenge API Routes

Supports:
  - Local file mode (dev): server-side candidates.jsonl
  - Upload mode (production/Render): upload candidates file + optional JD
  - JD parsing: extract structured scoring profile from any JD file or text

Routes:
  GET  /api/challenge/info              — dataset status + JD info
  POST /api/challenge/parse-jd          — extract JD profile from file/text
  POST /api/challenge/run               — run on local file (dev mode)
  POST /api/challenge/upload-and-run    — upload candidates + optional JD (production)
  GET  /api/challenge/status/{run_id}   — poll progress
  GET  /api/challenge/download/{run_id} — download submission CSV
  GET  /api/challenge/results/{run_id}  — full ranked results JSON
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

# ── In-memory run tracker ─────────────────────────────────────────────────────
_runs: dict[str, dict] = {}


# ── JD Text Extraction ────────────────────────────────────────────────────────

def _extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from uploaded file (docx, txt, md, pdf)."""
    filename_lower = (filename or "").lower()

    if filename_lower.endswith(".docx"):
        try:
            from docx import Document
            import io as _io
            doc = Document(_io.BytesIO(file_bytes))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            logger.warning(f"docx parse failed: {e}. Falling back to raw text.")
            return file_bytes.decode("utf-8", errors="replace")

    elif filename_lower.endswith(".pdf"):
        try:
            import pdfplumber
            import io as _io
            text_parts = []
            with pdfplumber.open(_io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
            return "\n".join(text_parts)
        except Exception as e:
            logger.warning(f"PDF parse failed: {e}. Trying raw decode.")
            return file_bytes.decode("utf-8", errors="replace")

    else:  # .txt, .md, or anything else
        for enc in ("utf-8", "utf-16", "latin-1"):
            try:
                return file_bytes.decode(enc)
            except Exception:
                continue
        return file_bytes.decode("utf-8", errors="replace")


# ── Dataset path detection ────────────────────────────────────────────────────

def _find_dataset() -> Optional[str]:
    backend_dir = Path(__file__).resolve().parent.parent
    search_paths = [
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        backend_dir / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        Path("India_runs_data_and_ai_challenge") / "candidates.jsonl",
        Path("candidates.jsonl"),
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    return None


def _find_sample() -> Optional[str]:
    backend_dir = Path(__file__).resolve().parent.parent
    search_paths = [
        backend_dir / "data" / "sample_challenge_candidates.json",
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        backend_dir / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/info")
async def get_challenge_info():
    """Return info about available dataset files and default JD summary."""
    dataset_path = _find_dataset()
    sample_path = _find_sample()

    result = {
        "full_dataset": None,
        "sample_dataset": None,
        "upload_supported": True,
        "job_description_summary": _get_default_jd_summary(),
        "scoring_info": {
            "skills_weight": "40%",
            "career_weight": "30%",
            "behavioral_weight": "20%",
            "engagement_weight": "10%",
        },
    }

    if dataset_path:
        try:
            size_mb = Path(dataset_path).stat().st_size / (1024 * 1024)
            result["full_dataset"] = {
                "path": dataset_path,
                "size_mb": round(size_mb, 1),
                "estimated_candidates": 100000,
                "available": True,
            }
        except OSError:
            pass

    if sample_path:
        try:
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else 1
            result["sample_dataset"] = {
                "path": sample_path,
                "candidate_count": count,
                "available": True,
            }
        except Exception:
            pass

    return result


def _get_default_jd_summary() -> dict:
    return {
        "title": "Senior AI Engineer — Founding Team",
        "company": "Redrob AI (Series A)",
        "experience": "5–9 years",
        "must_have": [
            "Embeddings-based retrieval (sentence-transformers, BGE, E5)",
            "Vector databases (Qdrant, FAISS, Pinecone, Weaviate, Milvus)",
            "Ranking evaluation (NDCG, MRR, MAP, A/B testing)",
            "Strong Python + production ML systems",
        ],
        "disqualifiers": [
            "All-consulting career (TCS/Infosys/Wipro-only)",
            "Pure research (no production deployments)",
            "CV/speech domains without NLP/IR exposure",
            "Title-chaser pattern (<18mo avg tenure)",
        ],
        "is_default": True,
    }


@router.post("/parse-jd")
async def parse_jd(
    file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
):
    """
    Parse an uploaded JD file or raw JD text.
    Returns a structured JD profile with extracted skills, experience range, etc.
    Accepts: .docx, .txt, .md, .pdf or raw text in form body.
    """
    import sys
    backend_dir = str(Path(__file__).resolve().parent.parent)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    from run_challenge import build_jd_profile

    text = ""
    source = "text"

    if file and file.filename:
        content = await file.read()
        text = _extract_text_from_file(content, file.filename)
        source = file.filename
    elif jd_text:
        text = jd_text
    else:
        raise HTTPException(400, "Provide either a JD file upload or jd_text form field")

    if len(text.strip()) < 30:
        raise HTTPException(400, "JD text too short to parse (minimum 30 characters)")

    profile = build_jd_profile(text)

    return {
        "source": source,
        "parsed_title": profile.title,
        "experience_range": {
            "ideal_min": profile.exp_ideal_min,
            "ideal_max": profile.exp_ideal_max,
            "good_min": profile.exp_good_min,
            "good_max": profile.exp_good_max,
        },
        "core_skills_count": len(profile.core_skills),
        "secondary_skills_count": len(profile.secondary_skills),
        "required_skills_preview": profile.required_skills_preview,
        "disqualifiers_preview": profile.disqualifiers_preview,
        "locations": profile.locations,
        "parsed_summary": profile.parsed_summary,
        "jd_text": text[:5000],  # Return first 5000 chars so frontend can use it
    }


@router.post("/run")
async def start_challenge_run(
    background_tasks: BackgroundTasks,
    use_sample: bool = False,
    sample_limit: int = 0,
    jd_text: Optional[str] = None,
):
    """Start ranking on a server-side file (dev mode). Optionally pass jd_text."""
    if use_sample:
        file_path = _find_sample()
        if not file_path:
            raise HTTPException(404, "No sample file found. Use upload-and-run instead.")
        is_sample = True
        limit = 0
    else:
        file_path = _find_dataset()
        if not file_path:
            raise HTTPException(404, "candidates.jsonl not found. Use upload-and-run.")
        is_sample = False
        limit = sample_limit

    run_id = _create_run(file_path, is_sample, limit)
    background_tasks.add_task(
        _run_challenge_background, run_id, file_path, limit, is_sample,
        jd_text=jd_text
    )
    return {
        "run_id": run_id, "status": "queued",
        "file": file_path, "is_sample": is_sample,
        "jd_provided": bool(jd_text),
        "message": "Ranking started. Poll /api/challenge/status/{run_id}",
    }


@router.post("/upload-and-run")
async def upload_and_run(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
    limit: int = Form(default=0),
):
    """
    Upload candidates file + optional JD file/text, then rank.
    Works in production (Render) — no local files needed.

    - file: candidates .json or .jsonl
    - jd_file: job description .docx, .txt, .md, .pdf (optional)
    - jd_text: raw JD text as form string (optional, used if jd_file not provided)
    - limit: cap number of candidates (0 = all)
    """
    filename = file.filename or "candidates"
    suffix = ".jsonl" if filename.endswith(".jsonl") else ".json"

    # Save candidates to temp file
    tmp = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix, delete=False, prefix="challenge_")
    try:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    finally:
        tmp.close()

    file_size_mb = len(content) / (1024 * 1024)
    logger.info(f"Upload: {filename} ({file_size_mb:.1f} MB) → {tmp_path}")

    # Validate candidates file
    try:
        if suffix == ".json":
            data = json.loads(content.decode("utf-8"))
            candidate_count = len(data) if isinstance(data, list) else 1
        else:
            lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
            candidate_count = len(lines)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(400, f"Invalid candidates file: {e}")

    if candidate_count == 0:
        os.unlink(tmp_path)
        raise HTTPException(400, "Candidates file is empty")

    # Extract JD text
    extracted_jd_text = jd_text or ""
    if jd_file and jd_file.filename:
        jd_content = await jd_file.read()
        extracted_jd_text = _extract_text_from_file(jd_content, jd_file.filename)
        logger.info(f"JD file: {jd_file.filename} ({len(extracted_jd_text)} chars)")

    is_sample = candidate_count <= 500
    actual_limit = limit if limit > 0 else candidate_count

    run_id = _create_run(tmp_path, is_sample, actual_limit, uploaded_filename=filename)
    background_tasks.add_task(
        _run_challenge_background, run_id, tmp_path, actual_limit, is_sample,
        cleanup_file=tmp_path, jd_text=extracted_jd_text or None,
    )

    return {
        "run_id": run_id,
        "status": "queued",
        "filename": filename,
        "candidate_count": candidate_count,
        "is_sample": is_sample,
        "jd_provided": bool(extracted_jd_text),
        "message": f"Uploaded {candidate_count:,} candidates. Ranking started.",
    }


@router.get("/status/{run_id}")
async def get_run_status(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    return {
        "run_id": run["run_id"],
        "status": run["status"],
        "total_candidates": run["total_candidates"],
        "processed": run["processed"],
        "honeypots_detected": run["honeypots_detected"],
        "started_at": run["started_at"],
        "completed_at": run["completed_at"],
        "elapsed_seconds": run["elapsed_seconds"],
        "error": run["error"],
        "top_10_preview": run["results"][:10] if run["results"] else [],
        "is_sample": run.get("is_sample", False),
        "uploaded_filename": run.get("uploaded_filename"),
        "jd_title": run.get("jd_title"),
        "jd_provided": run.get("jd_provided", False),
    }


@router.get("/download/{run_id}")
async def download_challenge_csv(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    if run["status"] != "complete":
        raise HTTPException(400, f"Run not complete (status: {run['status']})")
    if not run["csv_content"]:
        raise HTTPException(500, "No CSV content generated")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"cortexhire_submission_{timestamp}.csv"
    return StreamingResponse(
        iter([run["csv_content"]]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/results/{run_id}")
async def get_run_results(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    return {
        "run_id": run_id,
        "status": run["status"],
        "results": run["results"],
        "total_candidates": run["total_candidates"],
        "honeypots_detected": run["honeypots_detected"],
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _create_run(file_path, is_sample, limit, uploaded_filename=None):
    run_id = str(uuid.uuid4())
    _runs[run_id] = {
        "run_id": run_id, "status": "queued",
        "file_path": file_path, "is_sample": is_sample,
        "uploaded_filename": uploaded_filename,
        "total_candidates": limit if limit > 0 else 100000,
        "processed": 0, "honeypots_detected": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None, "elapsed_seconds": None,
        "error": None, "results": [], "csv_content": None,
        "jd_title": None, "jd_provided": False,
    }
    return run_id


def _run_challenge_background(
    run_id: str, file_path: str, sample_limit: int, is_sample: bool,
    cleanup_file: Optional[str] = None,
    jd_text: Optional[str] = None,
):
    run = _runs[run_id]
    run["status"] = "running"
    t_start = time.time()

    try:
        import sys
        backend_dir = str(Path(__file__).resolve().parent.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from run_challenge import stream_candidates, score_candidate, build_jd_profile

        # Build JD profile from uploaded JD text
        jd_profile = None
        if jd_text and len(jd_text.strip()) >= 30:
            jd_profile = build_jd_profile(jd_text)
            run["jd_title"] = jd_profile.title[:80]
            run["jd_provided"] = True
            logger.info(f"Run {run_id}: using custom JD — {jd_profile.parsed_summary}")
        else:
            logger.info(f"Run {run_id}: using default Redrob JD profile")

        # Handle JSON vs JSONL
        if Path(file_path).suffix == ".json":
            with open(file_path, "r", encoding="utf-8") as f:
                all_records = json.load(f)
            candidates_iter = iter(all_records if isinstance(all_records, list) else [all_records])
            total_est = len(all_records) if isinstance(all_records, list) else 1
        else:
            candidates_iter = stream_candidates(file_path, limit=sample_limit)
            total_est = sample_limit if sample_limit > 0 else 100000

        run["total_candidates"] = total_est

        top_buffer: list[dict] = []
        BUFFER = 400
        processed = 0
        honeypots = 0

        for candidate in candidates_iter:
            result = score_candidate(candidate, jd_profile)
            if result is None:
                honeypots += 1
                processed += 1
                continue

            processed += 1
            top_buffer.append(result)

            if len(top_buffer) > BUFFER * 4:
                top_buffer.sort(key=lambda x: x["total_score"], reverse=True)
                top_buffer = top_buffer[:BUFFER]

            if processed % 5000 == 0:
                run["processed"] = processed
                run["honeypots_detected"] = honeypots

        top_buffer.sort(key=lambda x: x["total_score"], reverse=True)
        top_n = min(100, len(top_buffer))
        top_results = top_buffer[:top_n]

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        results_list = []
        prev_score = 1.0
        for rank, item in enumerate(top_results, start=1):
            score = min(prev_score, item["normalized_score"])
            prev_score = score
            writer.writerow([item["candidate_id"], rank, f"{score:.4f}", item["reasoning"]])
            results_list.append({
                "rank": rank,
                "candidate_id": item["candidate_id"],
                "score": score,
                "title": item.get("title", ""),
                "name": item.get("name", ""),
                "skills_score": item.get("skills_score", 0),
                "career_score": item.get("career_score", 0),
                "behavioral_score": item.get("behavioral_score", 0),
                "engagement_score": item.get("engagement_score", 0),
                "total_score": item.get("total_score", 0),
                "reasoning": item["reasoning"],
            })

        elapsed = time.time() - t_start
        run.update({
            "status": "complete",
            "processed": processed,
            "total_candidates": processed + honeypots,
            "honeypots_detected": honeypots,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "results": results_list,
            "csv_content": output.getvalue(),
        })
        logger.info(f"Run {run_id} complete: {processed:,} in {elapsed:.1f}s")

    except Exception as e:
        logger.error(f"Run {run_id} failed: {e}", exc_info=True)
        run.update({
            "status": "failed",
            "error": str(e)[:500],
            "elapsed_seconds": round(time.time() - t_start, 1),
        })
    finally:
        if cleanup_file:
            try:
                os.unlink(cleanup_file)
            except Exception:
                pass
