"""Background queue for face-embedding generation.

Dynamically sizes the worker pool based on CPU cores and available RAM.
Applies back-pressure when the system is under heavy load so the FastAPI
event loop is never blocked and the server never OOMs.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class FaceTask:
    """A unit of work: generate face embeddings for one image file."""
    upload_log_id: int
    user_id: int
    folder_id: int
    file_path: str
    drive_file_id: Optional[str] = None
    enqueued_at: float = field(default_factory=time.time)


@dataclass
class QueueStats:
    """Cumulative counters — safe for concurrent reads."""
    images_processed: int = 0
    faces_found: int = 0
    new_faces_since_cluster: int = 0
    errors: int = 0


class FaceQueueManager:
    """Adaptive async queue that scales workers to system resources.

    * ``max_workers`` is computed once at init from CPU cores / RAM.
    * Each worker runs face detection in ``asyncio.to_thread`` so the
      event loop stays unblocked.
    * If CPU > 90 % or RAM > 85 %, the worker sleeps briefly before
      picking up the next task (back-pressure).
    """

    def __init__(self, max_workers: int = 0):
        self.queue: asyncio.Queue[FaceTask] = asyncio.Queue()
        self._workers: List[asyncio.Task] = []
        self._max_workers = max_workers or self._calculate_max_workers()
        self._running = False
        self.stats = QueueStats()
        logger.info(
            "FaceQueueManager: max_workers=%d", self._max_workers
        )

    # ── Auto-scale ────────────────────────────────────────────────────

    @staticmethod
    def _calculate_max_workers() -> int:
        cpu = psutil.cpu_count(logical=False) or 2
        avail_gb = psutil.virtual_memory().available / (1024 ** 3)
        ram_based = max(1, int(avail_gb / 0.5))  # ~500 MB per worker
        return max(1, min(cpu - 1, ram_based, 4))

    @property
    def max_workers(self) -> int:
        return self._max_workers

    @property
    def active_workers(self) -> int:
        return sum(1 for w in self._workers if not w.done())

    # ── Lifecycle ─────────────────────────────────────────────────────

    def start(self) -> None:
        """Spawn worker tasks (call from inside a running event loop)."""
        if self._running:
            return
        self._running = True
        for i in range(self._max_workers):
            task = asyncio.create_task(self._worker(i))
            self._workers.append(task)
        logger.info("FaceQueueManager: started %d workers", self._max_workers)

    async def stop(self) -> None:
        """Drain the queue and cancel workers."""
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        logger.info("FaceQueueManager: stopped")

    # ── Enqueue ───────────────────────────────────────────────────────

    async def enqueue(self, task: FaceTask) -> None:
        """Add an image to the processing queue (non-blocking)."""
        # Light back-pressure: if queue is very large, log a warning
        qsize = self.queue.qsize()
        if qsize > 100:
            logger.warning(
                "FaceQueue: %d items pending — system may be overloaded", qsize
            )
        await self.queue.put(task)
        logger.debug(
            "FaceQueue: enqueued upload_log_id=%d (queue_size=%d)",
            task.upload_log_id,
            self.queue.qsize(),
        )

    # ── Worker loop ───────────────────────────────────────────────────

    async def _worker(self, worker_id: int) -> None:
        from app.services.face_service import face_service
        from app.services import vector_store as vs_mod
        from app.database import async_session
        from app.models.face import FaceEmbedding
        from sqlalchemy import select

        logger.info("FaceQueue worker-%d: started", worker_id)
        while self._running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=2.0)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            try:
                # Throttle when system is stressed
                await self._throttle_if_needed()

                # ── Run face detection in thread pool ────────────────
                results = []
                import os
                file_exists = os.path.exists(task.file_path) if (task.file_path and not task.file_path.startswith("browser://")) else False

                if file_exists:
                    results = await asyncio.to_thread(
                        face_service.process_image_file, task.file_path
                    )
                else:
                    # File doesn't exist locally (cloud deployment or browser upload)
                    # Try downloading from Google Drive if we have a drive_file_id
                    drive_file_id = task.drive_file_id

                    if not drive_file_id:
                        async with async_session() as db:
                            from app.models.upload import UploadLog
                            result = await db.execute(
                                select(UploadLog.drive_file_id).where(UploadLog.id == task.upload_log_id)
                            )
                            drive_file_id = result.scalar_one_or_none()

                    if drive_file_id:
                        task.drive_file_id = drive_file_id
                        logger.info("FaceQueue: downloading image %s from Google Drive for face detection", drive_file_id)
                        from app.services.drive_service import download_drive_file
                        async with async_session() as db:
                            from app.models.folder import WatchedFolder
                            folder_result = await db.execute(
                                select(WatchedFolder.drive_config_id).where(WatchedFolder.id == task.folder_id)
                            )
                            drive_config_id = folder_result.scalar_one_or_none()

                            file_bytes = await download_drive_file(db, task.user_id, drive_file_id, drive_config_id)

                        if file_bytes:
                            results = await asyncio.to_thread(
                                face_service.process_image_bytes, file_bytes
                            )
                        else:
                            logger.error("FaceQueue: failed to download file %s from Google Drive", drive_file_id)
                    else:
                        logger.warning("FaceQueue: no local file or Google Drive file ID available for upload_log_id=%d", task.upload_log_id)

                if not results:
                    self.stats.images_processed += 1
                    self.queue.task_done()
                    continue

                # ── Store embeddings in Qdrant + SQLite ──────────────
                store = vs_mod.vector_store
                if store is None:
                    logger.warning("FaceQueue: vector_store not initialized")
                    self.queue.task_done()
                    continue

                async with async_session() as db:
                    batch_points = []
                    for face in results:
                        fe = FaceEmbedding(
                            upload_log_id=task.upload_log_id,
                            user_id=task.user_id,
                            folder_id=task.folder_id,
                            face_index=face.face_index,
                            bbox_json=json.dumps(face.bbox),
                            confidence=face.confidence,
                            drive_file_id=task.drive_file_id,
                            embedding_stored=True,
                        )
                        db.add(fe)
                        await db.flush()
                        await db.refresh(fe)

                        batch_points.append(
                            {
                                "id": int(fe.id),
                                "embedding": face.embedding,
                                "metadata": {
                                    "upload_log_id": int(task.upload_log_id),
                                    "user_id": int(task.user_id),
                                    "folder_id": int(task.folder_id),
                                    "face_index": int(face.face_index),
                                    "confidence": float(face.confidence),
                                    "drive_file_id": str(task.drive_file_id or ""),
                                    "public_link": f"https://drive.google.com/uc?export=view&id={task.drive_file_id}" if task.drive_file_id else "",
                                    "thumbnail_url": f"https://drive.google.com/thumbnail?id={task.drive_file_id}&sz=w800" if task.drive_file_id else "",
                                    "person_id": 0,  # not clustered yet
                                },
                            }
                        )

                    await db.commit()

                    # Qdrant upsert (sync call, fast for small batches)
                    await asyncio.to_thread(
                        store.add_embeddings_batch, batch_points
                    )

                self.stats.images_processed += 1
                self.stats.faces_found += len(results)
                self.stats.new_faces_since_cluster += len(results)

                logger.info(
                    "FaceQueue worker-%d: processed upload_log_id=%d → %d faces",
                    worker_id,
                    task.upload_log_id,
                    len(results),
                )

                # ── Trigger clustering if threshold reached ──────────
                from app.config import settings

                if (
                    self.stats.new_faces_since_cluster
                    >= settings.FACE_CLUSTER_INTERVAL
                ):
                    asyncio.create_task(
                        self._trigger_clustering(task.user_id)
                    )
                    self.stats.new_faces_since_cluster = 0

            except Exception:
                self.stats.errors += 1
                logger.exception(
                    "FaceQueue worker-%d: error processing upload_log_id=%d",
                    worker_id,
                    task.upload_log_id,
                )
            finally:
                self.queue.task_done()

    # ── Clustering trigger ────────────────────────────────────────────

    async def _trigger_clustering(self, user_id: int) -> None:
        try:
            from app.services.face_clustering import clustering_service

            await clustering_service.cluster_faces(user_id)
        except Exception:
            logger.exception("FaceQueue: clustering failed for user %d", user_id)

    # ── Throttling ────────────────────────────────────────────────────

    @staticmethod
    async def _throttle_if_needed() -> None:
        """Sleep if the system is under heavy load."""
        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory().percent
        if cpu > 90 or ram > 85:
            delay = 2.0 if ram > 90 else 1.0
            logger.debug(
                "FaceQueue: throttling %.1fs (cpu=%.0f%%, ram=%.0f%%)",
                delay,
                cpu,
                ram,
            )
            await asyncio.sleep(delay)


# Module-level singleton — instantiated during lifespan startup
face_queue: Optional[FaceQueueManager] = None
