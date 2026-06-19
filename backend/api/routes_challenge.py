"""
CortexHire — Challenge API Routes

Supports both local-file mode (development) and file-upload mode (production/Render).

Routes:
  GET  /api/challenge/info              — dataset status
  POST /api/challenge/run               — run on local file (dev)
  POST /api/challenge/upload-and-run    — upload file + run (production)
  GET  /api/challenge/status/{run_id}   — poll progress
  GET  /api/challenge/download/{run_id} — download submission CSV
  GET  /api/challenge/results/{run_id}  — full results JSON
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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

# ── In-memory run tracker ─────────────────────────────────────────────────────
_runs: dict[str, dict] = {}

# ── Dataset path detection ────────────────────────────────────────────────────

def _find_dataset() -> Optional[str]:
    """Auto-detect candidates.jsonl — local dev only."""
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
    """
    Find sample candidates JSON.
    Priority:
    1. backend/data/sample_challenge_candidates.json  (committed — works on Render)
    2. India_runs_data_and_ai_challenge/sample_candidates.json (local only)
    """
    backend_dir = Path(__file__).resolve().parent.parent
    search_paths = [
        # Committed embedded sample (always works)
        backend_dir / "data" / "sample_challenge_candidates.json",
        # Local challenge folder
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        backend_dir / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        Path("India_runs_data_and_ai_challenge") / "sample_candidates.json",
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    return None


def _count_jsonl_lines(path: str, max_count: int = 100001) -> int:
    """Count lines in a JSONL file (capped to avoid blocking on huge files)."""
    count = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for _ in f:
                count += 1
                if count >= max_count:
                    break
    except Exception:
        pass
    return count


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/info")
async def get_challenge_info():
    """Return info about available dataset files."""
    dataset_path = _find_dataset()
    sample_path = _find_sample()

    result = {
        "full_dataset": None,
        "sample_dataset": None,
        "upload_supported": True,
        "job_description_summary": _get_jd_summary(),
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


def _get_jd_summary() -> dict:
    return {
        "title": "Senior AI Engineer — Founding Team",
        "company": "Redrob AI (Series A)",
        "location": "Pune/Noida, India (Hybrid)",
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
        "key_behavioral_signals": [
            "Active on platform (last_active_date recency)",
            "Open to work flag",
            "Short notice period (<30 days preferred)",
            "High recruiter response rate",
        ],
    }


@router.post("/run")
async def start_challenge_run(
    background_tasks: BackgroundTasks,
    use_sample: bool = False,
    sample_limit: int = 0,
):
    """Start ranking on a locally-detected file (dev mode)."""
    if use_sample:
        file_path = _find_sample()
        if not file_path:
            raise HTTPException(404, "No sample file found. Use upload-and-run instead.")
        is_sample = True
        limit = 0
    else:
        file_path = _find_dataset()
        if not file_path:
            raise HTTPException(
                404,
                "candidates.jsonl not found on server. "
                "Use POST /api/challenge/upload-and-run to upload your file."
            )
        is_sample = False
        limit = sample_limit

    run_id = _create_run(file_path, is_sample, limit)
    background_tasks.add_task(_run_challenge_background, run_id, file_path, limit, is_sample)

    return {
        "run_id": run_id,
        "status": "queued",
        "file": file_path,
        "is_sample": is_sample,
        "message": "Ranking started. Poll /api/challenge/status/{run_id} for progress.",
    }


@router.post("/upload-and-run")
async def upload_and_run(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    limit: int = Form(default=0),
):
    """
    Accept an uploaded candidates file (JSON or JSONL) and start ranking.
    Works in production (Render) — no local file needed.
    """
    filename = file.filename or "candidates"
    suffix = ".jsonl" if filename.endswith(".jsonl") else ".json"

    # Save upload to a temp file
    tmp = tempfile.NamedTemporaryFile(
        mode="wb", suffix=suffix, delete=False, prefix="challenge_upload_"
    )
    try:
        content = await file.read()
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name
    finally:
        tmp.close()

    file_size_mb = len(content) / (1024 * 1024)
    logger.info(f"Received upload: {filename} ({file_size_mb:.1f} MB) → {tmp_path}")

    # Quick validation
    try:
        if suffix == ".json":
            data = json.loads(content.decode("utf-8"))
            candidate_count = len(data) if isinstance(data, list) else 1
        else:
            lines = [l for l in content.decode("utf-8").splitlines() if l.strip()]
            candidate_count = len(lines)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(400, f"Invalid file format: {e}")

    if candidate_count == 0:
        os.unlink(tmp_path)
        raise HTTPException(400, "Uploaded file contains no candidates.")

    is_sample = candidate_count <= 500
    actual_limit = limit if limit > 0 else candidate_count

    run_id = _create_run(tmp_path, is_sample, actual_limit, uploaded_filename=filename)
    background_tasks.add_task(
        _run_challenge_background, run_id, tmp_path, actual_limit, is_sample,
        cleanup_file=tmp_path
    )

    return {
        "run_id": run_id,
        "status": "queued",
        "filename": filename,
        "candidate_count": candidate_count,
        "is_sample": is_sample,
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

def _create_run(
    file_path: str,
    is_sample: bool,
    limit: int,
    uploaded_filename: Optional[str] = None,
) -> str:
    run_id = str(uuid.uuid4())
    _runs[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "file_path": file_path,
        "is_sample": is_sample,
        "uploaded_filename": uploaded_filename,
        "total_candidates": limit if limit > 0 else 100000,
        "processed": 0,
        "honeypots_detected": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "elapsed_seconds": None,
        "error": None,
        "results": [],
        "csv_content": None,
    }
    return run_id


def _run_challenge_background(
    run_id: str,
    file_path: str,
    sample_limit: int,
    is_sample: bool,
    cleanup_file: Optional[str] = None,
):
    """Score candidates in background thread and store results."""
    run = _runs[run_id]
    run["status"] = "running"
    t_start = time.time()

    try:
        import sys
        backend_dir = str(Path(__file__).resolve().parent.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from run_challenge import stream_candidates, score_candidate

        # Handle JSON vs JSONL
        path = Path(file_path)
        if path.suffix == ".json":
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
            result = score_candidate(candidate)
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

        # Final sort
        top_buffer.sort(key=lambda x: x["total_score"], reverse=True)
        top_n = min(100, len(top_buffer))
        top_results = top_buffer[:top_n]

        # Generate CSV
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
        logger.info(f"Challenge run {run_id}: {processed:,} processed in {elapsed:.1f}s")

    except Exception as e:
        logger.error(f"Challenge run {run_id} failed: {e}", exc_info=True)
        run.update({
            "status": "failed",
            "error": str(e)[:500],
            "elapsed_seconds": round(time.time() - t_start, 1),
        })
    finally:
        # Clean up temp upload file
        if cleanup_file:
            try:
                os.unlink(cleanup_file)
            except Exception:
                pass
