# CortexHire — AI Recruitment Intelligence System

> **Don't hire resumes. Hire potential.**

CortexHire is a full-stack AI recruitment platform that ranks candidates the way an elite recruiter thinks — with full context, zero bias, and deep intelligence.

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| 🧠 **Role Cognition Engine** | Extracts a "Role Genome" from job descriptions using LLMs |
| 🤖 **5-Agent Simulation** | Technical Recruiter, Hiring Manager, Org Psychologist, Bias Corrector, Future Predictor |
| 📊 **Explainable Rankings** | Every rank is backed by evidence-based AI reasoning |
| ⚖️ **Ethical AI Layer** | Bias detection and correction built into the pipeline |
| 💬 **Recruiter Copilot** | Conversational AI to ask anything about the rankings |
| 🎥 **Live Interview Panel** | Real-time AI interviews with posture analysis (Gemini Vision) and honest /100 scoring |
| 📈 **Temporal Intelligence** | Career momentum and trajectory analysis |
| 🌐 **Semantic Matching** | Multi-vector capability embeddings via Qdrant |

---

## 🏗️ Tech Stack

**Backend**
- FastAPI + SQLModel (SQLite, no Docker needed)
- Groq (LLaMA 3.3 70B) + OpenAI GPT-4o + Google Gemini Flash
- Qdrant (in-memory vector DB)
- Python 3.11+

**Frontend**
- Next.js 15 (App Router)
- TypeScript + Framer Motion
- Web Speech API (live transcription)
- MediaStream API (webcam for interview panel)

---

## ⚡ Quick Start

### 1. Clone & setup

```bash
git clone https://github.com/infinity-me/CortexHire.git
cd CortexHire
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example .env   # fill in your API keys
python main.py
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

---

## 🔑 API Keys Required

| Key | Purpose | Free? |
|-----|---------|-------|
| `GROQ_API_KEY` | Primary LLM (Llama 3.3) | ✅ Free at console.groq.com |
| `OPENAI_API_KEY` | Fallback + embeddings | Paid |
| `GEMINI_API_KEY` | Vision analysis in interviews | ✅ Free at aistudio.google.com |

---

## 📁 Project Structure

```
CortexHire/
├── backend/
│   ├── api/          # FastAPI route handlers
│   ├── core/         # LLM router, ranking, agents, embeddings
│   ├── db/           # SQLModel models + DB setup
│   ├── data/         # Synthetic data generation
│   └── main.py
├── frontend/
│   ├── app/          # Next.js App Router pages
│   ├── components/   # Reusable UI components
│   └── lib/          # API client + TypeScript types
└── docker-compose.yml
```

---

## 🎥 Live Interview Panel

The interview panel uses:
- **Browser MediaStream API** — webcam + microphone capture (no installs)
- **Web Speech API** — real-time answer transcription
- **Gemini Flash Vision** — periodic frame analysis for posture/body language
- **Groq LLaMA** — answer quality and communication scoring

Scoring is out of **100 points**:
- Answer Quality: 40%
- Communication: 15%
- Posture: 20%
- Engagement: 15%
- Confidence: 10%

---

*Built with ❤️ — AI that thinks like a recruiter, not a keyword matcher.*
