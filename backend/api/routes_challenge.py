"""
CortexHire — Challenge API Routes

Supports:
  - Local file mode (dev): server-side candidates.jsonl
  - Upload mode (production/Render): upload candidates file + optional JD
  - JD parsing: extract structured scoring profile from any JD file or text
  - History: all completed runs persisted to disk, re-downloadable anytime

Routes:
  GET  /api/challenge/info                    — dataset status + JD info
  POST /api/challenge/parse-jd                — extract JD profile from file/text
  POST /api/challenge/run                     — run on local file (dev mode)
  POST /api/challenge/upload-and-run          — upload candidates + optional JD
  GET  /api/challenge/status/{run_id}         — poll progress
  GET  /api/challenge/download/{run_id}       — download CSV (in-memory)
  GET  /api/challenge/results/{run_id}        — full ranked results JSON
  GET  /api/challenge/history                 — list all saved runs
  GET  /api/challenge/history/{run_id}/download — download saved CSV from disk
  DELETE /api/challenge/history/{run_id}      — delete a history entry
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

# ── History directory ─────────────────────────────────────────────────────────
_HISTORY_DIR = Path(__file__).resolve().parent.parent / "data" / "challenge_history"
_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


# ── History Persistence ───────────────────────────────────────────────────────

def _history_meta_path(run_id: str) -> Path:
    return _HISTORY_DIR / f"{run_id}.json"

def _history_csv_path(run_id: str) -> Path:
    return _HISTORY_DIR / f"{run_id}.csv"


def _save_run_to_history(run: dict) -> None:
    """Persist a completed run's metadata and CSV to disk."""
    run_id = run["run_id"]
    try:
        meta = {
            "run_id": run_id,
            "status": run["status"],
            "uploaded_filename": run.get("uploaded_filename") or "server_file",
            "total_candidates": run.get("total_candidates", 0),
            "processed": run.get("processed", 0),
            "honeypots_detected": run.get("honeypots_detected", 0),
            "elapsed_seconds": run.get("elapsed_seconds"),
            "started_at": run.get("started_at"),
            "completed_at": run.get("completed_at"),
            "jd_title": run.get("jd_title"),
            "jd_provided": run.get("jd_provided", False),
            "is_sample": run.get("is_sample", False),
            "ranked_count": len(run.get("results", [])),
            "top_5": run.get("results", [])[:5],
            "error": run.get("error"),
        }
        with open(_history_meta_path(run_id), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        if run.get("csv_content"):
            with open(_history_csv_path(run_id), "w", encoding="utf-8", newline="") as f:
                f.write(run["csv_content"])

        logger.info(f"History saved: {run_id}")
    except Exception as e:
        logger.error(f"Failed to save history for {run_id}: {e}")


def _load_history() -> list[dict]:
    """Load all history metadata from disk, newest first."""
    entries = []
    for meta_file in sorted(_HISTORY_DIR.glob("*.json"), reverse=True):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                entries.append(json.load(f))
        except Exception:
            continue
    return entries


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
            logger.warning(f"docx parse failed: {e}")
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
            logger.warning(f"PDF parse failed: {e}")
            return file_bytes.decode("utf-8", errors="replace")

    else:
        for enc in ("utf-8", "utf-16", "latin-1"):
            try:
                return file_bytes.decode(enc)
            except Exception:
                continue
        return file_bytes.decode("utf-8", errors="replace")


# ── Dataset path detection ────────────────────────────────────────────────────

def _find_dataset() -> Optional[str]:
    backend_dir = Path(__file__).resolve().parent.parent
    for p in [
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        backend_dir / "India_runs_data_and_ai_challenge" / "candidates.jsonl",
        Path("India_runs_data_and_ai_challenge") / "candidates.jsonl",
        Path("candidates.jsonl"),
    ]:
        if p.exists():
            return str(p)
    return None


def _find_sample() -> Optional[str]:
    backend_dir = Path(__file__).resolve().parent.parent
    for p in [
        backend_dir / "data" / "sample_challenge_candidates.json",
        backend_dir.parent / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
        backend_dir / "India_runs_data_and_ai_challenge" / "sample_candidates.json",
    ]:
        if p.exists():
            return str(p)
    return None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/info")
async def get_challenge_info():
    dataset_path = _find_dataset()
    sample_path = _find_sample()
    result = {
        "full_dataset": None,
        "sample_dataset": None,
        "upload_supported": True,
        "job_description_summary": _get_default_jd_summary(),
        "scoring_info": {
            "skills_weight": "40%", "career_weight": "30%",
            "behavioral_weight": "20%", "engagement_weight": "10%",
        },
    }
    if dataset_path:
        try:
            size_mb = Path(dataset_path).stat().st_size / (1024 * 1024)
            result["full_dataset"] = {"path": dataset_path, "size_mb": round(size_mb, 1), "estimated_candidates": 100000, "available": True}
        except OSError:
            pass
    if sample_path:
        try:
            with open(sample_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result["sample_dataset"] = {"path": sample_path, "candidate_count": len(data) if isinstance(data, list) else 1, "available": True}
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
    import sys
    backend_dir = str(Path(__file__).resolve().parent.parent)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from run_challenge import build_jd_profile

    text, source = "", "text"
    if file and file.filename:
        text = _extract_text_from_file(await file.read(), file.filename)
        source = file.filename
    elif jd_text:
        text = jd_text
    else:
        raise HTTPException(400, "Provide a JD file or jd_text")

    if len(text.strip()) < 30:
        raise HTTPException(400, "JD text too short (minimum 30 characters)")

    profile = build_jd_profile(text)
    return {
        "source": source,
        "parsed_title": profile.title,
        "experience_range": {
            "ideal_min": profile.exp_ideal_min, "ideal_max": profile.exp_ideal_max,
            "good_min": profile.exp_good_min, "good_max": profile.exp_good_max,
        },
        "core_skills_count": len(profile.core_skills),
        "secondary_skills_count": len(profile.secondary_skills),
        "required_skills_preview": profile.required_skills_preview,
        "disqualifiers_preview": profile.disqualifiers_preview,
        "locations": profile.locations,
        "parsed_summary": profile.parsed_summary,
        "jd_text": text[:5000],
    }


@router.post("/run")
async def start_challenge_run(
    background_tasks: BackgroundTasks,
    use_sample: bool = False,
    sample_limit: int = 0,
    jd_text: Optional[str] = None,
):
    if use_sample:
        file_path = _find_sample()
        if not file_path:
            raise HTTPException(404, "No sample file found. Use upload-and-run.")
        is_sample, limit = True, 0
    else:
        file_path = _find_dataset()
        if not file_path:
            raise HTTPException(404, "candidates.jsonl not found. Use upload-and-run.")
        is_sample, limit = False, sample_limit

    run_id = _create_run(file_path, is_sample, limit)
    background_tasks.add_task(_run_challenge_background, run_id, file_path, limit, is_sample, jd_text=jd_text)
    return {"run_id": run_id, "status": "queued", "file": file_path, "is_sample": is_sample, "jd_provided": bool(jd_text), "message": "Ranking started."}


@router.post("/upload-and-run")
async def upload_and_run(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
    limit: int = Form(default=0),
):
    """
    Stream candidates file to disk (never reads entire file into RAM).
    Supports files of any size as long as disk space allows.
    """
    filename = file.filename or "candidates"
    suffix = ".jsonl" if filename.endswith(".jsonl") else ".json"

    # ── Stream to disk in 4 MB chunks ─────────────────────────────────────────
    MAX_BYTES = 700 * 1024 * 1024  # 700 MB hard limit
    CHUNK = 4 * 1024 * 1024       # 4 MB chunks

    tmp = tempfile.NamedTemporaryFile(mode="wb", suffix=suffix, delete=False, prefix="challenge_")
    tmp_path = tmp.name
    total_bytes = 0
    candidate_count = 0
    leftover = b""

    try:
        while True:
            chunk = await file.read(CHUNK)
            if not chunk:
                break
            total_bytes += len(chunk)
            if total_bytes > MAX_BYTES:
                tmp.close()
                os.unlink(tmp_path)
                raise HTTPException(413, f"File too large (>{MAX_BYTES//1024//1024} MB). Upload a smaller batch or run locally.")
            tmp.write(chunk)

            # Count newlines (approximate candidate count) during streaming
            if suffix == ".jsonl":
                combined = leftover + chunk
                lines = combined.split(b"\n")
                leftover = lines[-1]          # might be partial line
                candidate_count += sum(1 for l in lines[:-1] if l.strip())

        # flush the leftover
        if suffix == ".jsonl" and leftover.strip():
            candidate_count += 1
    finally:
        tmp.close()
    file_size_mb = total_bytes / (1024 * 1024)
    logger.info(f"Upload streamed: {filename} ({file_size_mb:.1f} MB) → {tmp_path}")

    # For JSON files, count properly (small files only)
    if suffix == ".json":
        try:
            with open(tmp_path, "r", encoding="utf-8") as f_in:
                data = json.load(f_in)
            candidate_count = len(data) if isinstance(data, list) else 1
        except Exception as e:
            os.unlink(tmp_path)
            raise HTTPException(400, f"Invalid JSON candidates file: {e}")

    if candidate_count == 0:
        os.unlink(tmp_path)
        raise HTTPException(400, "Candidates file appears empty")

    extracted_jd = jd_text or ""
    if jd_file and jd_file.filename:
        extracted_jd = _extract_text_from_file(await jd_file.read(), jd_file.filename)

    is_sample = candidate_count <= 500
    actual_limit = limit if limit > 0 else candidate_count

    run_id = _create_run(tmp_path, is_sample, actual_limit, uploaded_filename=filename)
    background_tasks.add_task(
        _run_challenge_background, run_id, tmp_path, actual_limit, is_sample,
        cleanup_file=tmp_path, jd_text=extracted_jd or None,
    )
    return {
        "run_id": run_id, "status": "queued",
        "filename": filename, "candidate_count": candidate_count,
        "is_sample": is_sample, "jd_provided": bool(extracted_jd),
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
    """Download from in-memory (current session run)."""
    run = _runs.get(run_id)
    # Fallback to disk if not in memory
    if not run:
        csv_path = _history_csv_path(run_id)
        if csv_path.exists():
            return StreamingResponse(
                iter([csv_path.read_text(encoding="utf-8")]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=submission_{run_id[:8]}.csv"},
            )
        raise HTTPException(404, f"Run {run_id} not found")
    if run["status"] != "complete":
        raise HTTPException(400, f"Run not complete (status: {run['status']})")
    if not run.get("csv_content"):
        raise HTTPException(500, "No CSV content generated")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    return StreamingResponse(
        iter([run["csv_content"]]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=submission_{timestamp}.csv"},
    )


@router.get("/results/{run_id}")
async def get_run_results(run_id: str):
    run = _runs.get(run_id)
    if not run:
        raise HTTPException(404, f"Run {run_id} not found")
    return {
        "run_id": run_id, "status": run["status"],
        "results": run["results"],
        "total_candidates": run["total_candidates"],
        "honeypots_detected": run["honeypots_detected"],
    }


# ── History endpoints ─────────────────────────────────────────────────────────

@router.get("/history")
async def get_history():
    """Return all completed ranking runs (newest first), loaded from disk."""
    return {"runs": _load_history()}


@router.get("/history/{run_id}/download")
async def download_history_csv(run_id: str):
    """Download a saved CSV from disk (persists across server restarts)."""
    # Security: run_id is a UUID, sanitise it
    safe_id = "".join(c for c in run_id if c.isalnum() or c == "-")[:36]
    csv_path = _history_csv_path(safe_id)
    meta_path = _history_meta_path(safe_id)

    if not csv_path.exists():
        raise HTTPException(404, "CSV not found in history. It may have been deleted.")

    meta = {}
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    filename_hint = meta.get("uploaded_filename", "candidates").replace(".jsonl", "").replace(".json", "")
    ts = meta.get("completed_at", "")[:10].replace("-", "")
    download_name = f"submission_{filename_hint}_{ts or safe_id[:8]}.csv"

    return StreamingResponse(
        iter([csv_path.read_text(encoding="utf-8")]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={download_name}"},
    )


@router.delete("/history/{run_id}")
async def delete_history_entry(run_id: str):
    """Delete a history entry and its CSV from disk."""
    safe_id = "".join(c for c in run_id if c.isalnum() or c == "-")[:36]
    deleted = []
    for path in [_history_meta_path(safe_id), _history_csv_path(safe_id)]:
        if path.exists():
            path.unlink()
            deleted.append(path.name)
    if not deleted:
        raise HTTPException(404, "History entry not found")
    return {"deleted": deleted, "run_id": safe_id}


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

        jd_profile = None
        if jd_text and len(jd_text.strip()) >= 30:
            jd_profile = build_jd_profile(jd_text)
            run["jd_title"] = jd_profile.title[:80]
            run["jd_provided"] = True

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
        top_results = top_buffer[:min(100, len(top_buffer))]

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

        # ✅ Persist to history on disk
        _save_run_to_history(run)
        logger.info(f"Run {run_id} complete: {processed:,} in {elapsed:.1f}s")

    except Exception as e:
        logger.error(f"Run {run_id} failed: {e}", exc_info=True)
        run.update({"status": "failed", "error": str(e)[:500], "elapsed_seconds": round(time.time() - t_start, 1)})
        _save_run_to_history(run)  # save failed runs too for audit trail
    finally:
        if cleanup_file:
            try:
                os.unlink(cleanup_file)
            except Exception:
                pass
