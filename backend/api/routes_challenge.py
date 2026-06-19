"""
CortexHire — Challenge API Routes

Exposes the India Runs hackathon ranking as a web API so the frontend
Challenge page can trigger runs, poll progress, and download results.

Routes:
  GET  /api/challenge/info            — dataset file info & status
  POST /api/challenge/run             — start a background ranking run
  GET  /api/challenge/status/{run_id} — poll run progress
  GET  /api/challenge/download/{run_id} — download submission CSV
"""
from __future__ import annotations

import csv
import io
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/challenge", tags=["Challenge"])

# ── In-memory run tracker ─────────────────────────────────────────────────────
_runs: dict[str, dict] = {}

# ── Dataset path detection ────────────────────────────────────────────────────

def _find_dataset() -> Optional[str]:
    """Auto-detect the candidates.jsonl file location."""
    backend_dir = Path(__file__).resolve().parent.parent
    search_paths = [
        backend_dir / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        Path("India_runs_data_and_ai_challenge") / "candidates.jsonl",
        Path("candidates.jsonl"),
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    return None


def _find_sample() -> Optional[str]:
    """Find sample_candidates.json for quick runs."""
    backend_dir = Path(__file__).resolve().parent.parent
    search_paths = [
        backend_dir / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
    ]
    for p in search_paths:
        if p.exists():
            return str(p)
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/info")
async def get_challenge_info():
    """
    Return info about the available challenge dataset files.
    Used by the frontend to show what's available before running.
    """
    dataset_path = _find_dataset()
    sample_path = _find_sample()

    result = {
        "full_dataset": None,
        "sample_dataset": None,
        "job_description_summary": _get_jd_summary(),
        "scoring_info": {
            "skills_weight": "40%",
            "career_weight": "30%",
            "behavioral_weight": "20%",
            "engagement_weight": "10%",
            "output_format": "candidate_id, rank, score, reasoning",
            "top_n": 100,
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
            import json as _json
            with open(sample_path, "r", encoding="utf-8") as f:
                data = _json.load(f)
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
    """Return a summary of the job description for the frontend."""
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
    """
    Start a background challenge ranking run.

    Args:
        use_sample: If True, use sample_candidates.json instead of full dataset.
        sample_limit: Limit number of candidates (0 = all). For testing.

    Returns:
        run_id to poll with GET /api/challenge/status/{run_id}
    """
    # Determine which file to use
    if use_sample:
        file_path = _find_sample()
        if not file_path:
            raise HTTPException(404, "sample_candidates.json not found")
        is_sample = True
        limit = 0  # read all sample records
    else:
        file_path = _find_dataset()
        if not file_path:
            raise HTTPException(
                404,
                "candidates.jsonl not found. Expected at: "
                "India_runs_data_and_ai_challenge/candidates.jsonl"
            )
        is_sample = False
        limit = sample_limit

    run_id = str(uuid.uuid4())
    _runs[run_id] = {
        "run_id": run_id,
        "status": "queued",
        "file_path": file_path,
        "is_sample": is_sample,
        "total_candidates": 0,
        "processed": 0,
        "honeypots_detected": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "elapsed_seconds": None,
        "error": None,
        "results": [],  # top 100 results stored here
        "csv_content": None,  # generated CSV string
    }

    background_tasks.add_task(_run_challenge_background, run_id, file_path, limit, is_sample)

    return {
        "run_id": run_id,
        "status": "queued",
        "file": file_path,
        "is_sample": is_sample,
        "message": "Challenge ranking started. Poll /api/challenge/status/{run_id} for progress.",
    }


@router.get("/status/{run_id}")
async def get_run_status(run_id: str):
    """Poll the status of a challenge ranking run."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")

    # Return safe copy without full results (too large)
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
    }


@router.get("/download/{run_id}")
async def download_challenge_csv(run_id: str):
    """Download the submission CSV for a completed run."""
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    if run["status"] != "complete":
        raise HTTPException(400, f"Run is not complete (status: {run['status']})")
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
    """Get full ranked results for a completed run."""
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


# ── Background Task ───────────────────────────────────────────────────────────

def _run_challenge_background(
    run_id: str,
    file_path: str,
    sample_limit: int,
    is_sample: bool,
):
    """Run the scoring pipeline in a background thread."""
    run = _runs[run_id]
    run["status"] = "running"
    t_start = time.time()

    try:
        # Import scoring functions from run_challenge.py
        import sys
        backend_dir = str(Path(__file__).resolve().parent.parent)
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        from run_challenge import stream_candidates, score_candidate

        # For sample JSON files, convert to streaming format
        if is_sample and file_path.endswith(".json"):
            import json as _json
            with open(file_path, "r", encoding="utf-8") as f:
                all_records = _json.load(f)
            candidates_iter = iter(all_records if isinstance(all_records, list) else [all_records])
            run["total_candidates"] = len(all_records) if isinstance(all_records, list) else 1
        else:
            candidates_iter = stream_candidates(file_path, limit=sample_limit)
            run["total_candidates"] = sample_limit if sample_limit > 0 else 100000

        top_buffer: list[dict] = []
        BUFFER_SIZE = 300
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

            # Trim buffer periodically
            if len(top_buffer) > BUFFER_SIZE * 4:
                top_buffer.sort(key=lambda x: x["total_score"], reverse=True)
                top_buffer = top_buffer[:BUFFER_SIZE]

            # Update progress every 5000
            if processed % 5000 == 0:
                run["processed"] = processed
                run["honeypots_detected"] = honeypots

        # Final sort
        top_buffer.sort(key=lambda x: x["total_score"], reverse=True)
        top_100 = top_buffer[:100]

        # Generate CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        results_list = []
        prev_score = 1.0
        for rank, item in enumerate(top_100, start=1):
            # Enforce non-increasing scores
            score = min(prev_score, item["normalized_score"])
            prev_score = score
            item["final_score"] = score
            item["rank"] = rank

            writer.writerow([
                item["candidate_id"],
                rank,
                f"{score:.4f}",
                item["reasoning"],
            ])
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
            "honeypots_detected": honeypots,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed, 1),
            "results": results_list,
            "csv_content": output.getvalue(),
        })
        logger.info(
            f"Challenge run {run_id} complete: {processed:,} processed, "
            f"{honeypots} honeypots, {elapsed:.1f}s"
        )

    except Exception as e:
        logger.error(f"Challenge run {run_id} failed: {e}", exc_info=True)
        run.update({
            "status": "failed",
            "error": str(e)[:500],
            "elapsed_seconds": round(time.time() - t_start, 1),
        })
