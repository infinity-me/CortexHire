<div align="center">

# 🧠 CortexHire
### AI Recruitment Intelligence System

**Don't hire resumes. Hire potential.**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-cortexhire.vercel.app-7c3aed?style=for-the-badge)](https://cortexhire.vercel.app)
[![API Docs](https://img.shields.io/badge/⚡_API_Docs-Render-10b981?style=for-the-badge)](https://cortexhire.onrender.com/docs)
[![Hackathon](https://img.shields.io/badge/🏆_Built_for-India_Runs_Data_%26_AI_Challenge-f59e0b?style=for-the-badge)](https://indiarunsdataandai.com)

> Built for the **India Runs Data & AI Challenge** — ranking 500K+ real candidates from the Redrob platform using zero LLM calls, zero keyword stuffing, and genuine multi-dimensional intelligence.

</div>

---

## 🎯 The Problem

Traditional ATS systems reject great engineers because they didn't write "Kubernetes" in the right font. CortexHire replaces that with a system that thinks like an elite recruiter — with full context, zero bias, and 100,000 candidates per minute.

---

## 🏗️ How It Works

### Two Modes

| Mode | Use Case | Speed |
|---|---|---|
| **Challenge Ranker** | Upload any candidates file + optional JD → instant ranked CSV | No LLM, seconds |
| **Full Pipeline** | Jobs + Candidates DB → 2-phase AI ranking with 5 agents | LLM, minutes |

### Scoring Breakdown (Challenge Ranker)

Every candidate is scored across 4 dimensions — **no keyword stuffing, no resume gaming:**

| Dimension | Weight | What It Measures |
|---|---|---|
| **Skills Depth** | 40 pts | Core skill match × proficiency level × duration × endorsements |
| **Career Quality** | 30 pts | Experience range, product company ratio, seniority trajectory |
| **Behavioral Signals** | 20 pts | Open-to-work, recency, notice period, recruiter response rate |
| **Platform Engagement** | 10 pts | GitHub activity, profile completeness, recruiter saves |

**Anti-gaming filters built in:**
- 🛡️ Honeypot detection — impossible profiles auto-excluded
- 🔻 Consulting-only career penalty (−15 pts)
- 🔻 Wrong-domain title penalty (−18 pts)
- 🔻 Title-chaser pattern (avg tenure < 18mo) penalty (−5 pts)

---

## ✨ Features

### 🏆 Challenge Ranker
- Upload **any** candidates `.jsonl` / `.json` file
- Upload **any** JD (`.docx` / `.txt` / `.md` / `.pdf`) — or paste text
- JD auto-parsed offline: extracts skills, experience range, seniority, locations
- Scoring adapts dynamically to the uploaded JD — no hardcoding
- Streams large files in 4 MB chunks — handles 700 MB+ without RAM blow-up
- Outputs ranked CSV in the exact competition submission format
- Full run history saved to disk — re-downloadable after server restart

### 📊 Full Ranking Pipeline (Jobs Module)
- Create jobs with AI-extracted **Role Genome** (8-dimension capability vector)
- Import candidates from the 500K dataset via UI or CLI
- 2-phase ranking: embedding pre-filter → 5-agent deep analysis
- Results with fit scores, bias reports, trajectory, hiring explanations
- Recruiter Copilot: ask "Why is candidate #3 ranked above #5?"

### 🎤 Live AI Interview Panel
- Real-time webcam interview with answer transcription (Web Speech API)
- Periodic body-language analysis via Gemini Vision (every 10s)
- Per-answer scoring: quality, communication, posture, engagement, confidence
- Full interview report with scorecard

### 🤖 AI Innovations
1. **Role Cognition Engine** — extracts 8-dim Role Genome from any JD
2. **5-Agent Recruiter Simulation** — Technical, Hiring Manager, Psychologist, Bias Corrector, Future Predictor
3. **Human Capability Embeddings** — 8-dim semantic vectors, cosine similarity per dimension
4. **Temporal Intelligence** — career trajectory as time-series (accelerating / plateauing / declining)
5. **Ethical AI Layer** — detects + corrects pedigree, gap, and geographic bias

---

## 🛠️ Tech Stack

### Backend
| | Technology | Purpose |
|---|---|---|
| 🐍 | **FastAPI** | Async REST API |
| 🗄️ | **SQLModel + SQLite** | ORM + embedded DB (no Docker) |
| ⚡ | **Groq LLaMA 3.3 70B** | Primary LLM — ultra-fast inference |
| 🤖 | **OpenAI GPT-4o** | Fallback LLM + semantic embeddings |
| 👁️ | **Google Gemini Flash** | Vision — posture analysis in interviews |
| 🔢 | **NumPy + scikit-learn** | TF-IDF embeddings, cosine similarity |
| 📄 | **pdfplumber + python-docx** | JD/resume text extraction |
| 🔁 | **tenacity** | Retry with exponential backoff |

### Frontend
| | Technology | Purpose |
|---|---|---|
| ⚛️ | **Next.js 16 (App Router)** | Full-stack React framework |
| 🔷 | **TypeScript** | End-to-end type safety |
| 🎞️ | **Framer Motion** | Animations & micro-interactions |
| 📡 | **Axios** | API client with 2-min ranking timeout |
| 🎙️ | **Web Speech API** | Browser-native STT for interviews |
| 📷 | **MediaStream API** | Webcam capture (no plugins) |

### Infrastructure
| | Service | Role |
|---|---|---|
| 🌐 | **Vercel** | Frontend (edge CDN) |
| 🖥️ | **Render** | Backend (persistent disk for SQLite) |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Groq API key](https://console.groq.com) — free, powers all LLM calls

### 1. Clone

```bash
git clone https://github.com/infinity-me/CortexHire.git
cd CortexHire
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload --port 8000
```

On first startup the backend auto-seeds **5 synthetic jobs** (with AI role genomes) and **50 real candidate records**.

### 3. Frontend

```bash
cd frontend
npm install
# Make sure .env.local points to local backend:
# NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open → **http://localhost:3000**

---

## 🔑 Environment Variables

```env
# .env in /backend

# Required
GROQ_API_KEY=gsk_...          # Free at console.groq.com

# Optional — enhances specific features
OPENAI_API_KEY=sk-...         # Real semantic embeddings (falls back to TF-IDF without this)
GEMINI_API_KEY=AIza...        # Vision posture scoring in interviews (mocked without this)
```

---

## 🏆 Shortlisting Candidates for a Job — Step by Step

### Path A — Challenge Ranker (fastest, no DB needed)

> Best for: ranking uploaded files, hackathon submission, any custom JD

```
localhost:3000/challenge
```

1. **Upload JD** *(optional)* — drop any `.docx / .txt / .md / .pdf` file, or paste text
   → System auto-extracts: skills, experience range, seniority, locations
   → Scoring profile adapts to YOUR job — not hardcoded

2. **Upload Candidates** *(required)* — drop `candidates.jsonl` or `sample_candidates.json`

3. **Hit "Run Ranking"**
   → Progress bar shows candidates processed in real time
   → Honeypots detected and excluded automatically

4. **View Results** — top 100 ranked with scores, reasoning, skill breakdown

5. **Download CSV** — `submission.csv` in the exact competition format:
   ```
   candidate_id, rank, score, reasoning
   ```

---

### Path B — Full AI Pipeline (deep analysis with LLM agents)

> Best for: real hiring decisions, multi-agent scoring, bias-corrected results

```
1. Jobs → "+ New Job"
   Fill in title, company, JD text
   → Role Genome extracted (8 capability dimensions)

2. Candidates → "Bulk Dataset Import"
   Upload candidates.jsonl, set limit (50–5000)
   → Background async import, no LLM needed

3. Jobs → [Your Job] → "Run Ranking"
   Set shortlist size (25–500)
   → Phase 1: embedding pre-filter on ALL candidates (seconds)
   → Phase 2: 5-agent deep analysis on top N (minutes)

4. Rankings → View results
   Fit score · Agent consensus · Bias report · Career trajectory

5. Recruiter Copilot → Ask anything
   "Why is candidate #3 above #5?"
   "Who has the strongest RAG background?"
```

---

## 📦 Working with Large Candidate Files Locally

The competition dataset (`candidates.jsonl`) is ~500K records and is **gitignored** due to size. Here's how to use it:

### Option A — UI Upload (recommended for files up to ~200 MB)

1. Place your `candidates.jsonl` anywhere on your machine
2. Go to **Challenge Ranker** → drop the file in the Candidates section
3. The backend streams it in 4 MB chunks — never loads the full file into RAM
4. Works for files up to **700 MB** (hard limit)

> ⚠️ For cloud (Render), the 2-min request timeout kicks in for files > ~50 MB. **Use local backend for large files.**

### Option B — Local File Mode (fastest, no upload needed)

Place the dataset in the expected path:

```
CortexHire/
└── India_runs_data_and_ai_challenge/
    └── candidates.jsonl          ← full 500K dataset
    └── sample_candidates.json   ← 50-record sample (included in repo)
```

The backend detects this automatically. In Challenge Ranker you'll see the file listed as available — click it to run without uploading.

### Option C — CLI (for headless / scripted runs)

```bash
# Run on full dataset, output submission.csv
python backend/run_challenge.py

# Custom file + output path
python backend/run_challenge.py \
  --candidates ../India_runs_data_and_ai_challenge/candidates.jsonl \
  --out submission.csv

# Fast test on first 1000 records
python backend/run_challenge.py --sample 1000

# With a custom JD file
python backend/run_challenge.py \
  --candidates candidates.jsonl \
  --jd my_job_description.docx \
  --out ranked.csv
```

### Option D — Import into DB (for Full Pipeline mode)

```bash
# Import 500 real candidates into SQLite (background, no LLM)
python -m data.dataset_importer --file candidates.jsonl --limit 500

# Or via UI: Candidates → "Bulk Dataset Import" → upload file → set limit
```

---

## 📁 Project Structure

```
CortexHire/
├── backend/
│   ├── api/
│   │   ├── routes_challenge.py      # Challenge Ranker API (upload + rank + history)
│   │   ├── routes_jobs.py           # Job CRUD + Role Genome analysis
│   │   ├── routes_candidates.py     # Resume upload, dataset import
│   │   ├── routes_ranking.py        # 2-phase ranking pipeline
│   │   ├── routes_interview.py      # Live AI interview engine
│   │   └── routes_copilot.py        # Recruiter Q&A copilot
│   ├── core/
│   │   ├── llm_router.py            # Groq → OpenAI → Mock fallback chain
│   │   ├── role_cognition.py        # Role Genome extraction
│   │   ├── multi_agent.py           # 5-Agent Simulation
│   │   ├── embeddings.py            # 8-dim capability vectors
│   │   ├── temporal.py              # Career trajectory engine
│   │   ├── bias_correction.py       # Bias detection + correction
│   │   └── ranking.py               # Consensus scoring + explanations
│   ├── db/
│   │   ├── models.py                # SQLModel ORM models
│   │   └── postgres.py              # Async session management
│   ├── data/
│   │   ├── dataset_importer.py      # JSONL/JSON dataset ingestion
│   │   ├── embedded_candidates.py   # 50-record seed (committed, works on Render)
│   │   └── synthetic_jobs.py        # 5 rich demo JDs for cold-start
│   ├── run_challenge.py             # Standalone CLI ranker (zero-dependency scoring)
│   ├── config.py                    # Env config via pydantic-settings
│   ├── main.py                      # App entrypoint + lifespan seeding
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Command Center dashboard
│   │   ├── challenge/page.tsx       # Challenge Ranker UI
│   │   ├── jobs/[id]/page.tsx       # Job detail + Role Genome radar + Run Ranking
│   │   ├── candidates/page.tsx      # Candidate list + upload + dataset import
│   │   ├── ranking/[runId]/page.tsx # Ranked results + agent scores + bias report
│   │   ├── interview/               # Live webcam interview + report
│   │   └── challenge/page.tsx       # Challenge Ranker + history
│   ├── lib/
│   │   ├── api.ts                   # Typed API client
│   │   └── types.ts                 # TypeScript interfaces
│   └── .env.local                   # NEXT_PUBLIC_API_URL (localhost or Render)
├── India_runs_data_and_ai_challenge/ # ← gitignored, place dataset here
│   ├── candidates.jsonl             # Full 500K dataset
│   └── sample_candidates.json       # 50-record sample
├── render.yaml                      # Render deployment config
└── .env.example                     # Environment variable template
```

---

## 🌐 Deployment

### Frontend → Vercel

```bash
vercel --prod
# Set env var: NEXT_PUBLIC_API_URL=https://cortexhire.onrender.com
```

### Backend → Render

Configured via `render.yaml`:
- Persistent disk at `/data` for SQLite
- Auto-seeds jobs + candidates on cold start
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

> ⚠️ **Large file uploads on Render** time out after ~2 minutes. For the full 500K dataset, run the backend locally and use the local file mode or CLI.

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/challenge/upload-and-run` | Upload candidates + optional JD → start ranking |
| `GET` | `/api/challenge/status/{run_id}` | Poll ranking progress |
| `GET` | `/api/challenge/results/{run_id}` | Full ranked results JSON |
| `GET` | `/api/challenge/download/{run_id}` | Download submission CSV |
| `GET` | `/api/challenge/history` | All past runs (persisted to disk) |
| `POST` | `/api/challenge/parse-jd` | Extract JD profile from file or text |
| `GET` | `/api/jobs/` | List all jobs |
| `POST` | `/api/ranking/run/{job_id}` | Start 2-phase AI ranking |
| `GET` | `/api/ranking/run/{run_id}/status` | Poll ranking status |
| `GET` | `/api/ranking/results/{run_id}` | Full ranked results |
| `POST` | `/api/interview/start` | Start AI interview session |
| `POST` | `/api/copilot/chat` | Recruiter Copilot Q&A |
| `GET` | `/health` | Health check + LLM provider |

Full interactive docs: **http://localhost:8000/docs** or **[Render API Docs](https://cortexhire.onrender.com/docs)**

---

<div align="center">

Built with ❤️ for the **India Runs Data & AI Challenge**

*AI that thinks like a recruiter, not a keyword matcher.*

**[🌐 Live Demo](https://cortexhire.vercel.app)** · **[📖 API Docs](https://cortexhire.onrender.com/docs)** · **[⭐ Star on GitHub](https://github.com/infinity-me/CortexHire)**

</div>
