"""
Helper script: generates embedded_candidates.py from the local sample_candidates.json.
Run from the repo root:
    python backend/data/gen_embedded.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "India_runs_data_and_ai_challenge" / "sample_candidates.json"
OUT = Path(__file__).resolve().parent / "embedded_candidates.py"

with open(SRC, "r", encoding="utf-8") as f:
    data = json.load(f)

header = '''\
"""
CortexHire -- Embedded Competition Dataset (50 sample candidates)

This file contains the 50-record sample from the India Runs Data and AI Challenge,
embedded directly in the codebase so the deployed backend (Render) can seed
candidates on first startup without needing the gitignored data folder.

DO NOT EDIT manually -- regenerate from gen_embedded.py if needed.
"""

SAMPLE_CANDIDATES = \
'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(header)
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")

print(f"Written {len(data)} records to {OUT}")
