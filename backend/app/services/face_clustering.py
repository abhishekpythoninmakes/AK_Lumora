"""Person clustering service using DBSCAN.

Groups detected faces into person clusters so that face-search can
compare the query against a handful of cluster centroids rather than
every single embedding.
"""

import json
import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class PersonClusteringService:
    """Run DBSCAN on a user's face embeddings → assign person_ids."""

    async def cluster_faces(self, user_id: int) -> int:
        """Cluster all face embeddings for *user_id*.

        Returns the number of clusters (persons) found.
        """
        from app.services import vector_store as vs_mod
        from app.database import async_session
        from app.models.face import FaceEmbedding, PersonCluster
        from sqlalchemy import select, delete
        import asyncio

        store = vs_mod.vector_store
        if store is None:
            logger.warning("Clustering: vector_store not ready")
            return 0

        # 1. Fetch all embeddings for this user from Qdrant
        records = await asyncio.to_thread(
            store.get_all_embeddings_for_user, user_id
        )
        if len(records) < 2:
            logger.info("Clustering: user %d has <2 faces, skipping", user_id)
            return 0

        face_ids = [r["id"] for r in records]
        embeddings = np.array(
            [r["vector"] for r in records], dtype=np.float32
        )

        # 2. Normalize for cosine distance
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings_norm = embeddings / norms

        # 3. Run DBSCAN
        from sklearn.cluster import DBSCAN

        # eps=0.5 in cosine-distance space (1 - cosine_sim); min 2 photos
        clustering = DBSCAN(
            eps=0.5,
            min_samples=2,
            metric="cosine",
            n_jobs=1,
        ).fit(embeddings_norm)

        labels = clustering.labels_  # -1 = noise (unclustered)
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        logger.info(
            "Clustering: user %d → %d persons from %d faces",
            user_id,
            n_clusters,
            len(face_ids),
        )

        if n_clusters == 0:
            return 0

        # 4. Build face_id → person_id mapping & centroids
        cluster_map: dict[int, list] = {}  # label → [indices]
        for idx, label in enumerate(labels):
            if label == -1:
                continue
            cluster_map.setdefault(label, []).append(idx)

        # 5. Persist to SQLite + update Qdrant payloads
        async with async_session() as db:
            # Clear previous clusters for this user
            await db.execute(
                delete(PersonCluster).where(PersonCluster.user_id == user_id)
            )

            face_id_to_person: dict[int, int] = {}

            for label, indices in cluster_map.items():
                # Compute centroid
                centroid = embeddings_norm[indices].mean(axis=0)
                centroid = centroid / (np.linalg.norm(centroid) or 1.0)

                pc = PersonCluster(
                    user_id=user_id,
                    centroid_json=json.dumps(centroid.tolist()),
                    face_count=len(indices),
                )
                db.add(pc)
                await db.flush()
                await db.refresh(pc)

                person_id = pc.id

                # Update FaceEmbedding rows
                for idx in indices:
                    fid = face_ids[idx]
                    face_id_to_person[fid] = person_id
                    result = await db.execute(
                        select(FaceEmbedding).where(FaceEmbedding.id == fid)
                    )
                    fe = result.scalar_one_or_none()
                    if fe:
                        fe.person_id = person_id

            await db.commit()

        # 6. Update Qdrant payloads with person_ids
        if face_id_to_person:
            await asyncio.to_thread(
                store.update_person_ids, face_id_to_person
            )

        logger.info(
            "Clustering: updated %d face embeddings with person_ids",
            len(face_id_to_person),
        )
        return n_clusters

    async def get_person_centroid(
        self, person_id: int
    ) -> Optional[np.ndarray]:
        """Retrieve a cached centroid for quick matching."""
        from app.database import async_session
        from app.models.face import PersonCluster
        from sqlalchemy import select

        async with async_session() as db:
            result = await db.execute(
                select(PersonCluster).where(PersonCluster.id == person_id)
            )
            pc = result.scalar_one_or_none()
            if pc and pc.centroid_json:
                return np.array(json.loads(pc.centroid_json), dtype=np.float32)
        return None


# Module-level singleton
clustering_service = PersonClusteringService()
