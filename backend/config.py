"""
CortexHire — Central Configuration
Loads from .env file. Handles Groq → OpenAI → Mock fallback chain.
No-Docker mode: SQLite + Qdrant in-memory.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    secret_key: str = "dev-secret-key"

    # LLM
    groq_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    llm_provider: Literal["groq", "openai", "mock"] = "groq"
    llm_fallback: Literal["openai", "mock"] = "openai"
    offline_mode: bool = False
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4o"
    gemini_model: str = "gemini-1.5-flash"
    embedding_model: str = "text-embedding-3-small"

    # Database — SQLite by default (no Docker needed)
    database_url: str = "sqlite+aiosqlite:///./cortexhire.db"
    use_sqlite: bool = True

    # Qdrant — in-memory by default (no Docker needed)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_candidates: str = "candidate_capabilities"
    qdrant_collection_roles: str = "role_genomes"
    qdrant_vector_size: int = 1536
    qdrant_in_memory: bool = True

    # Neo4j — disabled by default (requires Docker)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "cortexhire_secret"
    neo4j_enabled: bool = False

    # Frontend
    next_public_api_url: str = "http://localhost:8000"

    @property
    def active_llm(self) -> str:
        """Return the first available LLM provider."""
        if self.offline_mode:
            return "mock"
        if self.llm_provider == "groq" and self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            return "groq"
        if self.llm_provider == "openai" and self.openai_api_key and self.openai_api_key != "your_openai_api_key_here":
            return "openai"
        if self.llm_fallback == "openai" and self.openai_api_key and self.openai_api_key != "your_openai_api_key_here":
            return "openai"
        return "mock"

    @property
    def has_gemini_vision(self) -> bool:
        """True if Gemini API key is available for vision analysis."""
        return bool(self.gemini_api_key and self.gemini_api_key != "your_gemini_api_key_here")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
