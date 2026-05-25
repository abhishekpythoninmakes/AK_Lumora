"""Qdrant-based vector store for face embeddings.

Uses *local file mode* — no Docker or separate server required.
Data is persisted to ``settings.QDRANT_STORAGE_PATH`` (default ``./qdrant_data``).
"""

import logging
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

COLLECTION_NAME = "face_embeddings"
EMBEDDING_DIM = 512


class VectorStore:
    """Thin wrapper around qdrant-client in local file-storage mode."""

    def __init__(self, storage_path: str):
        from qdrant_client import QdrantClient
        import threading

        self._path = storage_path
        self.client = QdrantClient(path=storage_path)
        self._write_lock = threading.Lock()
        self._ensure_collection()
        logger.info("VectorStore: opened at %s", storage_path)

    # ── Collection bootstrap ──────────────────────────────────────────

    def _ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        collections = [c.name for c in self.client.get_collections().collections]
        if COLLECTION_NAME not in collections:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("VectorStore: created collection '%s'", COLLECTION_NAME)

    # ── Write ─────────────────────────────────────────────────────────

    def add_embedding(
        self,
        point_id: int,
        embedding: np.ndarray,
        metadata: dict,
    ) -> None:
        """Insert or update a single face embedding."""
        from qdrant_client.models import PointStruct

        vec = embedding.astype(np.float32).flatten().tolist()
        with self._write_lock:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(id=point_id, vector=vec, payload=metadata),
                ],
            )

    def add_embeddings_batch(
        self,
        points: List[dict],
    ) -> None:
        """Batch insert.  Each dict: {id, embedding, metadata}."""
        from qdrant_client.models import PointStruct

        structs = []
        for p in points:
            vec = np.asarray(p["embedding"], dtype=np.float32).flatten().tolist()
            structs.append(
                PointStruct(id=p["id"], vector=vec, payload=p["metadata"])
            )
        if structs:
            with self._write_lock:
                self.client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=structs,
                )

    # ── Search ────────────────────────────────────────────────────────

    def search(
        self,
        query_embedding: np.ndarray,
        user_id: int,
        limit: int = 50,
        threshold: float = 0.45,
        folder_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        """Search for similar faces, filtered by *user_id* and optionally
        by *folder_ids*.  Returns list of ``{id, score, payload}``."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        must = [FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        if folder_ids:
            # Use should conditions (OR) across folder_ids
            from qdrant_client.models import MatchAny
            must.append(
                FieldCondition(key="folder_id", match=MatchAny(any=folder_ids))
            )

        vec = query_embedding.astype(np.float32).flatten().tolist()
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vec,
            query_filter=Filter(must=must),
            limit=limit,
            score_threshold=threshold,
            with_payload=True,
        )

        out: List[dict] = []
        for hit in results.points:
            out.append(
                {
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload,
                }
            )
        return out

    def search_by_person(
        self, person_id: int, user_id: int, limit: int = 200
    ) -> List[dict]:
        """Fast lookup: return all embeddings for a known person cluster."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        filt = Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="person_id", match=MatchValue(value=person_id)),
            ]
        )
        results = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=filt,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [
            {"id": p.id, "score": 1.0, "payload": p.payload}
            for p in results[0]
        ]

    # ── Update / Delete ───────────────────────────────────────────────

    def update_person_ids(self, face_id_to_person: Dict[int, int]) -> None:
        """Batch-update ``person_id`` payload field after clustering."""
        from qdrant_client.models import SetPayload

        with self._write_lock:
            for face_id, person_id in face_id_to_person.items():
                self.client.set_payload(
                    collection_name=COLLECTION_NAME,
                    payload={"person_id": int(person_id)},
                    points=[int(face_id)],
                )

    def delete_by_upload(self, upload_log_id: int) -> None:
        """Remove all embeddings for a deleted upload."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        with self._write_lock:
            self.client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="upload_log_id",
                            match=MatchValue(value=upload_log_id),
                        )
                    ]
                ),
            )

    def set_payload(self, payload: dict, points: List[int]) -> None:
        """Thread-safe update of payload for specific points."""
        with self._write_lock:
            self.client.set_payload(
                collection_name=COLLECTION_NAME,
                payload=payload,
                points=points,
            )

    def get_all_embeddings_for_user(
        self, user_id: int, limit: int = 10000
    ) -> List[dict]:
        """Fetch all embeddings+payloads for a user (used by clustering)."""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        filt = Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        )
        results = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter=filt,
            limit=limit,
            with_payload=True,
            with_vectors=True,
        )
        return [
            {
                "id": p.id,
                "vector": p.vector,
                "payload": p.payload,
            }
            for p in results[0]
        ]

    def count(self, user_id: Optional[int] = None) -> int:
        """Count total embeddings, optionally filtered by user."""
        if user_id is None:
            info = self.client.get_collection(COLLECTION_NAME)
            return info.points_count or 0

        from qdrant_client.models import FieldCondition, Filter, MatchValue

        return self.client.count(
            collection_name=COLLECTION_NAME,
            count_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id", match=MatchValue(value=user_id)
                    )
                ]
            ),
        ).count

    def close(self) -> None:
        """Close qdrant client explicitly during app shutdown."""
        try:
            self.client.close()
        except Exception as exc:
            logger.debug("VectorStore close warning: %s", exc)


# Module-level singleton — set during lifespan startup
vector_store: Optional[VectorStore] = None
