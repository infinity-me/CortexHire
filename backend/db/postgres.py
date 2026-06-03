"""
CortexHire — Database engine (SQLite via aiosqlite, no Docker needed)
Falls back gracefully — SQLite file created automatically on first run.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from config import settings

# SQLite needs special pool config for async
_connect_args = {}
_pool_kwargs = {}

if "sqlite" in settings.database_url:
    _connect_args = {"check_same_thread": False}
    _pool_kwargs = {
        "poolclass": StaticPool,
        "connect_args": _connect_args,
    }
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        **_pool_kwargs,
    )
else:
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """FastAPI dependency — yields a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
