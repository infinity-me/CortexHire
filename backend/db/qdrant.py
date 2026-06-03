"""
CortexHire — Qdrant vector store (in-memory mode, no Docker needed)
Uses QdrantClient with :memory: when QDRANT_IN_MEMORY=true.
Falls back gracefully if connection fails.
"""
from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger(__name__)

# Capability vector dimensions
CAPABILITY_DIMENSIONS = [
    "technical_depth",
    "adaptability",
    "leadership",
    "execution",
    "systems_thinking",
    "creativity",
    "resilience",
    "communication",
]

VECTOR_SIZE = settings.qdrant_vector_size


class QdrantStore:
    def __init__(self) -> None:
        self._client = None
        self._available = False

    async def connect(self) -> None:
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            if settings.qdrant_in_memory:
                # In-memory mode — no server needed!
                self._client = QdrantClient(":memory:")
                logger.info("Qdrant started in IN-MEMORY mode (no Docker needed)")
            else:
                self._client = QdrantClient(
                    host=settings.qdrant_host,
                    port=settings.qdrant_port,
                )
                logger.info(f"Qdrant connected to {settings.qdrant_host}:{settings.qdrant_port}")

            # Create collections
            named_vectors = {
                dim: VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
                for dim in CAPABILITY_DIMENSIONS
            }

            for name in [
                settings.qdrant_collection_candidates,
                settings.qdrant_collection_roles,
            ]:
                existing = self._client.get_collections()
                col_names = {c.name for c in existing.collections}
                if name not in col_names:
                    self._client.create_collection(
                        collection_name=name,
                        vectors_config=named_vectors,
                    )
                    logger.info(f"Created Qdrant collection: {name}")

            self._available = True

        except Exception as e:
            logger.warning(f"Qdrant not available (vector search disabled): {e}")
            self._available = False

    def upsert_candidate_sync(
        self,
        candidate_id: str,
        vectors: dict[str, list[float]],
        payload: dict[str, Any],
    ) -> None:
        if not self._available or not self._client:
            return
        try:
            from qdrant_client.models import PointStruct
            point = PointStruct(id=candidate_id, vector=vectors, payload=payload)
            self._client.upsert(
                collection_name=settings.qdrant_collection_candidates,
                points=[point],
            )
        except Exception as e:
            logger.warning(f"Qdrant upsert failed: {e}")

    def search_candidates_sync(
        self,
        query_vector: list[float],
        dimension: str = "technical_depth",
        limit: int = 20,
    ) -> list:
        if not self._available or not self._client:
            return []
        try:
            from qdrant_client.models import NamedVector
            return self._client.search(
                collection_name=settings.qdrant_collection_candidates,
                query_vector=NamedVector(name=dimension, vector=query_vector),
                limit=limit,
                with_payload=True,
            )
        except Exception as e:
            logger.warning(f"Qdrant search failed: {e}")
            return []

    async def upsert_candidate(
        self,
        candidate_id: str,
        vectors: dict[str, list[float]],
        payload: dict[str, Any],
    ) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self.upsert_candidate_sync(candidate_id, vectors, payload))

    async def close(self) -> None:
        pass  # In-memory client cleans up automatically


# Singleton
qdrant_store = QdrantStore()
