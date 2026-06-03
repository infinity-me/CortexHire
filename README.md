<div align="center">

# 🧠 CortexHire
### AI Recruitment Intelligence System

**Don't hire resumes. Hire potential.**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-cortexhire.vercel.app-7c3aed?style=for-the-badge)](https://cortexhire.vercel.app)
[![Backend API](https://img.shields.io/badge/⚡_Backend_API-Render-10b981?style=for-the-badge)](https://cortexhire.onrender.com/docs)
[![Built for](https://img.shields.io/badge/Built_for-India_Runs_Data_%26_AI_Challenge-f59e0b?style=for-the-badge)](https://indiarunsdataandai.com)

</div>

---

## 🎯 The Problem

Traditional hiring is broken in three fundamental ways:

1. **Keyword matching is not intelligence.** ATS systems reject great candidates who don't use the "right" words.
2. **Human bias is systematic.** IIT pedigree, FAANG logos, and resume formatting influence decisions more than capability.
3. **Resumes are backward-looking.** They show where someone has been — not where they're going.

CortexHire is an AI-native recruitment platform that thinks the way the best human recruiters think — with full context, zero bias, and deep pattern recognition — at the scale and speed that humans simply cannot.

---

## 💡 The Solution

CortexHire introduces **5 novel AI innovations** that collectively solve the hiring problem from multiple dimensions:

### Innovation 1 — Role Cognition Engine 🧬
Instead of keyword-matching against a job description, CortexHire extracts a **"Role Genome"** — a structured multidimensional model of what a role *actually* needs, beyond its surface-level keywords.

The Role Genome scores 8 dimensions (0–1):

| Dimension | What It Measures |
|---|---|
| `technical_depth` | Complexity of technical work required |
| `ambiguity_tolerance` | Comfort with unclear requirements |
| `ownership` | Independence and outcome-orientation |
| `communication` | Cross-functional & stakeholder needs |
| `startup_readiness` | Speed vs. process bias |
| `leadership_potential` | People or technical influence expected |
| `creativity` | Novel problem-solving vs. defined execution |
| `execution_speed` | Pace and delivery expectations |

Plus extracted narrative intelligence: `hidden_needs`, `functional_needs`, `team_dynamics`, `risk_profile`, `cognitive_style`, `role_summary`.

---

### Innovation 2 — 5-Agent Recruiter Simulation 🤖
Every candidate is evaluated in **parallel by 5 specialized AI recruiter agents**, each with a distinct expertise and independent rubric:

| Agent | Expertise |
|---|---|
| 🔧 **Technical Recruiter** | System complexity, architecture depth, scale of problems solved |
| 📋 **Hiring Manager** | Ownership signals, delivery track record, execution under pressure |
| 🧠 **Organizational Psychologist** | Behavioral patterns, resilience, cultural alignment |
| ⚖️ **Diversity & Bias Corrector** | Detects and corrects pedigree, gap, and geographic bias |
| 🔮 **Future Potential Predictor** | Career trajectory, learning velocity, 2-year projection |

Each agent returns a `score (0–100)`, `confidence (0–1)`, `key_signals`, `risks`, and `reasoning`. Their assessments are aggregated by a **Consensus Ranking Engine** into a final fit score.

---

### Innovation 3 — Human Capability Embeddings 📐
Candidates and roles are both embedded into **8-dimensional semantic vectors**, one per capability dimension. Cosine similarity is computed per-dimension, weighted by role genome importance — enabling semantic matching that goes beyond keyword overlap.

This powers the **Phase 1 Pre-Filter**: scoring 10,000+ candidates in seconds (no LLM), shortlisting the top N for deep analysis.

---

### Innovation 4 — Temporal Intelligence Engine ⏳
Career data is analyzed as a **time series** to detect:
- Scope expansion velocity (are they growing faster than peers?)
- Company stage transitions (startup → scale-up → enterprise)
- Role change patterns (promotion vs. lateral vs. regressive)
- Gap analysis (context-aware, not penalized)
- Momentum classification: `accelerating / steady / plateauing / declining`

---

### Innovation 5 — Ethical AI Layer ⚖️
A dedicated Bias Corrector agent detects and corrects for:
- **College prestige bias** — IIT/FAANG halo effect
- **Career gap penalization** — Caregiving, health, personal reasons
- **Geographic bias** — City/country-based quality assumptions
- **Company name halo** — Previous employer prestige vs. actual work
- **Resume formatting bias** — Presentation vs. content

Bias adjustment: `-10 to +15` applied to raw capability score.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Frontend                      │
│  Jobs · Candidates · Rankings · Live Interview · Copilot│
└────────────────────┬────────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                          │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │Role Cognition│  │ 5-Agent Sim  │  │  Embeddings    │  │
│  │   Engine    │  │   Pipeline   │  │  (8-dim vec)   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  Temporal   │  │Bias Corrector│  │Consensus Ranker│  │
│  │Intelligence │  │   Agent      │  │  + Explainer   │  │
│  └─────────────┘  └──────────────┘  └────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │           LLM Router (Groq → OpenAI → Mock)       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────┐  ┌──────────────────────────────────┐   │
│  │ SQLite DB  │  │     Live Interview Engine         │   │
│  │(SQLModel)  │  │ WebRTC + Gemini Vision + STT     │   │
│  └────────────┘  └──────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### 2-Phase Ranking Pipeline (scales to 500K+ candidates)

```
All Candidates (any size)
        │
        ▼
Phase 1 — Fast Pre-Filter (seconds, no LLM)
  Embedding similarity scored per candidate
  → Keep top N (configurable: 25–500)
        │
        ▼
Phase 2 — Deep Analysis (minutes, LLM)
  5 agents × top N candidates (parallel batches of 3)
  → Consensus score + explanation
        │
        ▼
Final Ranked Results
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** | Async REST API framework |
| **SQLModel + SQLite** | ORM + embedded database (no Docker needed) |
| **Groq (LLaMA 3.3 70B)** | Primary LLM — ultra-fast inference |
| **OpenAI GPT-4o** | Fallback LLM + embedding generation |
| **Google Gemini Flash** | Vision model — posture/body language in interviews |
| **tenacity** | Retry logic with exponential backoff |
| **pypdf + python-docx** | Resume text extraction (PDF, DOCX) |
| **asyncio** | Parallel agent execution |

### Frontend
| Technology | Purpose |
|---|---|
| **Next.js 15 (App Router)** | Full-stack React framework |
| **TypeScript** | Type safety across API surface |
| **Framer Motion** | Animations and micro-interactions |
| **Recharts / SVG** | Role Genome radar chart, score visualizations |
| **Web Speech API** | Real-time interview answer transcription |
| **MediaStream API** | Webcam capture for live interview panel |
| **Axios** | HTTP client with timeout handling |

### Infrastructure
| Service | Role |
|---|---|
| **Vercel** | Frontend deployment (edge CDN) |
| **Render** | Backend deployment (persistent disk for SQLite) |
| **GitHub** | Source control + CI/CD trigger |

---

## 📁 Project Structure

```
CortexHire/
├── backend/
│   ├── api/
│   │   ├── routes_jobs.py           # CRUD + JD analysis endpoint
│   │   ├── routes_candidates.py     # Resume upload, dataset import, bulk ops
│   │   ├── routes_ranking.py        # 2-phase ranking pipeline + results
│   │   ├── routes_interview.py      # Live AI interview engine
│   │   └── routes_copilot.py        # Recruiter Q&A copilot
│   ├── core/
│   │   ├── llm_router.py            # Groq → OpenAI → Mock fallback chain
│   │   ├── role_cognition.py        # Role Genome extraction (Innovation #1)
│   │   ├── multi_agent.py           # 5-Agent Simulation (Innovation #4)
│   │   ├── embeddings.py            # 8-dim capability vectors (Innovation #3)
│   │   ├── temporal.py              # Career trajectory engine (Innovation #2)
│   │   ├── bias_correction.py       # Bias detection + correction (Innovation #5)
│   │   └── ranking.py               # Consensus scoring + explanation generation
│   ├── db/
│   │   ├── models.py                # SQLModel ORM: Job, Candidate, RankingRun, ...
│   │   └── postgres.py              # Async DB session management
│   ├── data/
│   │   ├── dataset_importer.py      # Competition dataset ingestion (JSONL/JSON)
│   │   ├── embedded_candidates.py   # 50-record seed data (committed to repo)
│   │   ├── synthetic_jobs.py        # 5 rich JDs for demo/cold-start
│   │   └── gen_embedded.py          # Regenerate embedded_candidates.py
│   ├── config.py                    # Env config via pydantic-settings
│   ├── main.py                      # App entrypoint + lifespan seeding
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Command Center dashboard
│   │   ├── jobs/
│   │   │   ├── page.tsx             # Jobs list + "+ New Job" modal
│   │   │   └── [id]/page.tsx        # Job detail + Role Genome + Run Ranking
│   │   ├── candidates/
│   │   │   └── page.tsx             # Candidate list + resume upload + dataset import
│   │   ├── ranking/
│   │   │   └── [runId]/page.tsx     # Ranked results + agent scores + bias report
│   │   ├── interview/
│   │   │   ├── page.tsx             # Interview setup
│   │   │   ├── [sessionId]/page.tsx # Live webcam + STT interview panel
│   │   │   └── report/[sessionId]/  # Detailed interview scorecard
│   │   └── copilot/page.tsx         # Recruiter AI copilot chat
│   ├── components/
│   │   ├── layout/Sidebar.tsx       # Navigation sidebar
│   │   └── jobs/RoleGenomeChart.tsx # SVG radar chart for Role Genome
│   └── lib/
│       ├── api.ts                   # Typed API client (all endpoints)
│       └── types.ts                 # TypeScript interfaces
├── render.yaml                      # Render deployment config
├── docker-compose.yml               # Local dev with Qdrant
└── .env.example                     # Required environment variables
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Groq API key](https://console.groq.com) (for LLM)

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
# Edit .env and add your GROQ_API_KEY at minimum
uvicorn main:app --reload --port 8000
```

The backend auto-seeds 5 synthetic jobs (with AI-extracted role genomes) and 50 real candidate records on first startup.

**API Docs:** http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🔑 Environment Variables

```env
# Required
GROQ_API_KEY=gsk_...              # Free at console.groq.com — powers all LLM calls

# Optional (enhances specific features)
OPENAI_API_KEY=sk-...             # Fallback LLM + real semantic embeddings
GEMINI_API_KEY=AIza...            # Vision model for interview posture analysis
```

Without `OPENAI_API_KEY`, embeddings fall back to a deterministic TF-IDF mock (still works).  
Without `GEMINI_API_KEY`, posture scoring uses smart mock values.

---

## 🔄 Complete Hiring Workflow

### For a new job requirement with a large dataset:

```
1. Jobs → "+ New Job"
   Fill in: title, company, location, seniority, JD text
   → AI auto-extracts Role Genome (8 dimensions + narrative)

2. Candidates → "Bulk Dataset Import"
   Upload: candidates.jsonl or sample_candidates.json
   Set limit: 50 – 5,000 candidates
   → Background import (no LLM needed, fast field mapping)

3. Jobs → [Your Job] → Set pre-filter slider
   "Analyze top N candidates" (25–500)
   → Phase 1 embedding pre-filter runs on ALL candidates (seconds)
   → Phase 2 deep 5-agent analysis on top N only (minutes)

4. View Results → /ranking/[runId]
   Full ranked list with: fit score, agent consensus,
   bias-corrected scores, trajectory, hiring explanation

5. Recruiter Copilot → Ask anything
   "Why is candidate #3 ranked above #5?"
   "Who has the strongest system design background?"
```

---

## 🎥 Live Interview Panel

The AI interview panel is a complete webcam-based assessment tool:

| Feature | Technology |
|---|---|
| Real-time answer transcription | Web Speech API (browser-native) |
| Periodic body language analysis | Gemini Flash Vision (every 10s) |
| Answer quality + communication scoring | Groq LLaMA 3.3 70B |
| Webcam capture (no plugins) | MediaStream API |
| Session persistence | SQLite (interview answers + scores) |

**Scoring rubric (out of 100):**

| Metric | Weight |
|---|---|
| Answer Quality | 40% |
| Posture & Body Language | 20% |
| Communication Clarity | 15% |
| Engagement | 15% |
| Confidence | 10% |

---

## 📊 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/jobs/` | List all jobs |
| `POST` | `/api/jobs/` | Create a new job |
| `POST` | `/api/jobs/{id}/analyze` | Extract Role Genome from JD |
| `GET` | `/api/candidates/` | List all candidates |
| `POST` | `/api/candidates/bulk-upload` | Upload PDF/DOCX resumes (LLM-parsed) |
| `POST` | `/api/candidates/import-dataset` | Import from JSONL/JSON dataset file |
| `GET` | `/api/candidates/import-status/{id}` | Poll dataset import progress |
| `POST` | `/api/ranking/run/{job_id}` | Start 2-phase ranking pipeline |
| `GET` | `/api/ranking/run/{run_id}/status` | Poll ranking status |
| `GET` | `/api/ranking/results/{run_id}` | Get full ranked results |
| `GET` | `/api/ranking/job/{job_id}/latest` | Get most recent ranking for a job |
| `POST` | `/api/interview/start` | Start AI interview session |
| `POST` | `/api/interview/evaluate-answer` | Score a single answer |
| `POST` | `/api/interview/analyze-frame` | Vision analysis of webcam frame |
| `POST` | `/api/interview/report/{session_id}` | Generate full interview report |
| `POST` | `/api/copilot/chat` | Ask the Recruiter Copilot |
| `GET` | `/health` | Health check + LLM provider status |

Full interactive docs: **[https://cortexhire.onrender.com/docs](https://cortexhire.onrender.com/docs)**

---

## 🌐 Deployment

### Frontend — Vercel

```bash
vercel --prod
# Set env: NEXT_PUBLIC_API_URL=https://cortexhire.onrender.com
```

### Backend — Render

Configured via `render.yaml`. Key settings:
- **Persistent disk** at `/data` for SQLite (`cortexhire.db`)
- Auto-seeds candidates + jobs on cold start
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🏆 Built for India Runs Data & AI Challenge

CortexHire was built as a submission for the **India Runs Data & AI Challenge**, using the competition's candidate dataset (500K records from the Redrob platform).

The dataset is gitignored due to size. The system includes:
- A 50-record embedded seed (`data/embedded_candidates.py`) for cold-start demo
- Full CLI import: `python -m data.dataset_importer --file candidates.jsonl --limit 500`
- UI import: Candidates page → "Bulk Dataset Import"

---

<div align="center">

Built with ❤️ — *AI that thinks like a recruiter, not a keyword matcher.*

**[🌐 Live Demo](https://cortexhire.vercel.app)** · **[📖 API Docs](https://cortexhire.onrender.com/docs)** · **[⭐ Star on GitHub](https://github.com/infinity-me/CortexHire)**

</div>
