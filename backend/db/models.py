"""
CortexHire — SQLModel schemas (SQLite compatible)
All structured app data: jobs, candidates, rankings, agents, audit.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text
import json


def new_uuid() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.utcnow()


# ─── JSON helper for SQLite ──────────────────────────────────
# SQLite stores JSON as TEXT; we serialize/deserialize manually via properties.
# We use a simple text field with JSON encoding.

class JSONField:
    """Store a Python dict/list as a JSON text in SQLite."""
    pass


# ─── Job ────────────────────────────────────────────────────

class Job(SQLModel, table=True):
    __tablename__ = "jobs"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    title: str
    company: str
    description: str
    location: Optional[str] = None
    employment_type: Optional[str] = "full-time"
    seniority: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    role_genome_json: Optional[str] = Field(default=None)  # JSON stored as text
    org_dna_json: Optional[str] = Field(default=None)
    status: str = "pending"

    @property
    def role_genome(self) -> Optional[dict]:
        if self.role_genome_json:
            try:
                return json.loads(self.role_genome_json)
            except Exception:
                return None
        return None

    @role_genome.setter
    def role_genome(self, value: Optional[dict]) -> None:
        self.role_genome_json = json.dumps(value) if value is not None else None


class JobCreate(SQLModel):
    title: str
    company: str
    description: str
    location: Optional[str] = None
    employment_type: Optional[str] = "full-time"
    seniority: Optional[str] = None


class JobRead(SQLModel):
    id: str
    title: str
    company: str
    description: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    created_at: datetime
    role_genome: Optional[dict] = None
    status: str


# ─── Candidate ──────────────────────────────────────────────

class Candidate(SQLModel, table=True):
    __tablename__ = "candidates"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    name: str
    email: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    years_experience: Optional[float] = None
    education_tier: Optional[str] = None
    education_detail: Optional[str] = None
    raw_profile: Optional[str] = None
    created_at: datetime = Field(default_factory=now)

    # JSON stored as text for SQLite compatibility
    career_history_json: Optional[str] = Field(default=None)
    skills_json: Optional[str] = Field(default=None)
    achievements_json: Optional[str] = Field(default=None)
    capability_profile_json: Optional[str] = Field(default=None)
    temporal_profile_json: Optional[str] = Field(default=None)
    bias_flags_json: Optional[str] = Field(default=None)

    qdrant_synced: bool = False
    neo4j_synced: bool = False

    @property
    def career_history(self) -> Optional[list]:
        return json.loads(self.career_history_json) if self.career_history_json else None

    @career_history.setter
    def career_history(self, v):
        self.career_history_json = json.dumps(v) if v is not None else None

    @property
    def skills(self) -> Optional[list]:
        return json.loads(self.skills_json) if self.skills_json else None

    @skills.setter
    def skills(self, v):
        self.skills_json = json.dumps(v) if v is not None else None

    @property
    def achievements(self) -> Optional[list]:
        return json.loads(self.achievements_json) if self.achievements_json else None

    @achievements.setter
    def achievements(self, v):
        self.achievements_json = json.dumps(v) if v is not None else None

    @property
    def capability_profile(self) -> Optional[dict]:
        return json.loads(self.capability_profile_json) if self.capability_profile_json else None

    @capability_profile.setter
    def capability_profile(self, v):
        self.capability_profile_json = json.dumps(v) if v is not None else None

    @property
    def temporal_profile(self) -> Optional[dict]:
        return json.loads(self.temporal_profile_json) if self.temporal_profile_json else None

    @temporal_profile.setter
    def temporal_profile(self, v):
        self.temporal_profile_json = json.dumps(v) if v is not None else None

    @property
    def bias_flags(self) -> Optional[list]:
        return json.loads(self.bias_flags_json) if self.bias_flags_json else None

    @bias_flags.setter
    def bias_flags(self, v):
        self.bias_flags_json = json.dumps(v) if v is not None else None


class CandidateRead(SQLModel):
    id: str
    name: str
    headline: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    years_experience: Optional[float] = None
    education_tier: Optional[str] = None
    education_detail: Optional[str] = None
    created_at: datetime
    career_history: Optional[list] = None
    skills: Optional[list] = None
    capability_profile: Optional[dict] = None
    temporal_profile: Optional[dict] = None


# ─── Ranking Run ────────────────────────────────────────────

class RankingRun(SQLModel, table=True):
    __tablename__ = "ranking_runs"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    job_id: str = Field(foreign_key="jobs.id", index=True)
    created_at: datetime = Field(default_factory=now)
    status: str = "pending"
    total_candidates: int = 0
    shortlist_size: int = 10
    config_json: Optional[str] = Field(default=None)


# ─── Candidate Ranking ──────────────────────────────────────

class CandidateRanking(SQLModel, table=True):
    __tablename__ = "candidate_rankings"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    run_id: str = Field(foreign_key="ranking_runs.id", index=True)
    job_id: str = Field(foreign_key="jobs.id", index=True)
    candidate_id: str = Field(foreign_key="candidates.id", index=True)
    rank_position: int
    fit_score: float
    risk_score: float
    growth_score: float
    confidence_score: float
    success_probability: float
    agent_scores_json: Optional[str] = Field(default=None)
    explanation: Optional[str] = None
    bias_report_json: Optional[str] = Field(default=None)
    shortlisted: bool = False

    @property
    def agent_scores(self) -> Optional[dict]:
        return json.loads(self.agent_scores_json) if self.agent_scores_json else None

    @agent_scores.setter
    def agent_scores(self, v):
        self.agent_scores_json = json.dumps(v) if v is not None else None

    @property
    def bias_report(self) -> Optional[dict]:
        return json.loads(self.bias_report_json) if self.bias_report_json else None

    @bias_report.setter
    def bias_report(self, v):
        self.bias_report_json = json.dumps(v) if v is not None else None


# ─── Copilot Session ────────────────────────────────────────

class CopilotMessage(SQLModel, table=True):
    __tablename__ = "copilot_messages"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    job_id: str = Field(foreign_key="jobs.id", index=True)
    created_at: datetime = Field(default_factory=now)
    role: str
    content: str
    context_run_id: Optional[str] = None


class CopilotMessageRead(SQLModel):
    id: str
    role: str
    content: str
    created_at: datetime


# ─── Interview Session ───────────────────────────────────────

class InterviewSession(SQLModel, table=True):
    __tablename__ = "interview_sessions"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    job_id: str = Field(foreign_key="jobs.id", index=True)
    candidate_name: str = ""
    candidate_email: Optional[str] = None
    created_at: datetime = Field(default_factory=now)
    completed_at: Optional[datetime] = None
    status: str = "active"   # active | complete | abandoned

    # Final aggregated scores (stored after report generation)
    total_score: Optional[float] = None
    answer_quality_score: Optional[float] = None
    communication_score: Optional[float] = None
    posture_score: Optional[float] = None
    engagement_score: Optional[float] = None
    confidence_score: Optional[float] = None

    # JSON blob: list of questions used
    questions_json: Optional[str] = Field(default=None)

    @property
    def questions(self) -> Optional[list]:
        return json.loads(self.questions_json) if self.questions_json else None

    @questions.setter
    def questions(self, v):
        self.questions_json = json.dumps(v) if v is not None else None


class InterviewAnswer(SQLModel, table=True):
    __tablename__ = "interview_answers"
    id: str = Field(default_factory=new_uuid, primary_key=True)
    session_id: str = Field(foreign_key="interview_sessions.id", index=True)
    question_index: int
    question_text: str
    transcript: Optional[str] = None
    created_at: datetime = Field(default_factory=now)

    # Per-answer dimension scores (0-100 each)
    answer_quality: Optional[float] = None
    communication: Optional[float] = None
    posture: Optional[float] = None
    engagement: Optional[float] = None
    confidence: Optional[float] = None

    # LLM feedback text per answer
    feedback_json: Optional[str] = Field(default=None)

    @property
    def feedback(self) -> Optional[dict]:
        return json.loads(self.feedback_json) if self.feedback_json else None

    @feedback.setter
    def feedback(self, v):
        self.feedback_json = json.dumps(v) if v is not None else None

