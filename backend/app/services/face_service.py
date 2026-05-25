"""Face detection and embedding service using InsightFace + ONNX.

Dynamically selects the face model (buffalo_l or buffalo_s) based on
available system RAM.  Falls back gracefully if the preferred model
cannot be loaded.
"""

import logging
import os
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import cv2
import numpy as np
import psutil
from PIL import Image

logger = logging.getLogger(__name__)

# Minimum RAM (GB) to use the large model
_LARGE_MODEL_RAM_THRESHOLD = 3.0  # buffalo_l needs ~1.5 GB; keep headroom


@dataclass
class FaceResult:
    """Result for a single detected face."""
    bbox: List[int]               # [x1, y1, x2, y2]
    confidence: float
    embedding: np.ndarray         # 512-dim float32
    face_index: int = 0


class FaceService:
    """Singleton InsightFace service with dynamic model selection.

    * ``auto`` — picks ``buffalo_l`` when ≥ 3 GB RAM free, else ``buffalo_s``
    * ``large`` — always ``buffalo_l``
    * ``small`` — always ``buffalo_s``

    The service is thread-safe; detection runs inside a lock so the ONNX
    session is never called concurrently (InsightFace is *not* thread-safe).
    """

    _instance: Optional["FaceService"] = None
    _init_lock = threading.Lock()

    def __new__(cls, preference: str = "auto"):
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    inst = super().__new__(cls)
                    inst._initialized = False
                    cls._instance = inst
        return cls._instance

    # ── Initialization ────────────────────────────────────────────────

    def initialize(self, preference: str = "auto") -> None:
        """Load the model (idempotent)."""
        if self._initialized:
            return
        with self._init_lock:
            if self._initialized:
                return
            self._preference = preference
            self._model_name: Optional[str] = None
            self._app = None
            self._detect_lock = threading.Lock()
            self._load_model()
            self._initialized = True

    def _pick_model(self) -> str:
        if self._preference == "large":
            return "buffalo_l"
        if self._preference == "small":
            return "buffalo_s"

        # Check for persisted selection to guarantee embedding consistency across reboots
        from app.config import settings
        storage_path = getattr(settings, "QDRANT_STORAGE_PATH", "./qdrant_data")
        os.makedirs(storage_path, exist_ok=True)
        model_file = os.path.join(storage_path, "chosen_model.txt")
        
        if os.path.exists(model_file):
            try:
                with open(model_file, "r") as f:
                    saved_model = f.read().strip()
                if saved_model in ("buffalo_l", "buffalo_s"):
                    logger.info("FaceService: using persisted auto-selected model: %s", saved_model)
                    return saved_model
            except Exception as e:
                logger.warning("FaceService: failed to read persisted model file: %s", e)

        # auto — check available RAM
        avail_gb = psutil.virtual_memory().available / (1024 ** 3)
        chosen = "buffalo_l" if avail_gb >= _LARGE_MODEL_RAM_THRESHOLD else "buffalo_s"
        logger.info(
            "FaceService auto-select: %.1f GB available → %s", avail_gb, chosen
        )

        # Persist choice for future boots
        try:
            with open(model_file, "w") as f:
                f.write(chosen)
            logger.info("FaceService: persisted auto-selected model '%s' to %s", chosen, model_file)
        except Exception as e:
            logger.warning("FaceService: failed to write persisted model file: %s", e)

        return chosen

    def _load_model(self) -> None:
        """Load InsightFace model with automatic fallback."""
        from insightface.app import FaceAnalysis  # deferred import

        model = self._pick_model()
        try:
            app = FaceAnalysis(name=model, providers=["CPUExecutionProvider"])
            app.prepare(ctx_id=0, det_size=(640, 640))
            self._app = app
            self._model_name = model
            logger.info("FaceService: loaded model '%s'", model)
        except Exception:
            logger.warning("FaceService: failed to load '%s', trying fallback", model)
            fallback = "buffalo_s" if model == "buffalo_l" else "buffalo_l"
            try:
                app = FaceAnalysis(name=fallback, providers=["CPUExecutionProvider"])
                app.prepare(ctx_id=0, det_size=(640, 640))
                self._app = app
                self._model_name = fallback
                logger.info("FaceService: loaded fallback model '%s'", fallback)
            except Exception:
                logger.exception("FaceService: could not load any model")
                self._app = None
                self._model_name = None

    @property
    def ready(self) -> bool:
        return self._app is not None

    @property
    def model_name(self) -> Optional[str]:
        return self._model_name

    # ── Image Loading ─────────────────────────────────────────────────

    @staticmethod
    def extract_preview_from_raw(file_path: str) -> Optional[np.ndarray]:
        """Extract embedded JPEG preview from a RAW file.

        This avoids decoding the full 40 MB+ Bayer data — the embedded
        preview is typically a 1–3 MP JPEG that is more than enough for
        face detection.
        """
        try:
            import rawpy  # deferred — only needed for RAW files

            with rawpy.imread(file_path) as raw:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    buf = np.frombuffer(thumb.data, dtype=np.uint8)
                    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
                    if img is not None:
                        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                elif thumb.format == rawpy.ThumbFormat.BITMAP:
                    return thumb.data  # already RGB
        except Exception as exc:
            logger.debug("RAW preview extraction failed for %s: %s", file_path, exc)
        return None

    @staticmethod
    def load_image(file_path: str) -> Optional[np.ndarray]:
        """Load an image from disk, returning an RGB numpy array."""
        raw_exts = {
            ".raw", ".cr2", ".cr3", ".nef", ".nrw", ".arw", ".srf", ".sr2",
            ".dng", ".orf", ".pef", ".rw2", ".raf", ".srw", ".x3f",
            ".3fr", ".ari", ".bay", ".cap", ".iiq", ".eip", ".dcs",
            ".dcr", ".drf", ".k25", ".kdc", ".mdc", ".mef", ".mos",
            ".mrw", ".obm", ".ptx", ".pxn", ".r3d", ".rwl", ".rwz",
        }
        ext = os.path.splitext(file_path)[1].lower()

        if ext in raw_exts:
            img = FaceService.extract_preview_from_raw(file_path)
            if img is not None:
                return img
            # Fallback: try rawpy full postprocess (slow but works)
            try:
                import rawpy

                with rawpy.imread(file_path) as raw:
                    return raw.postprocess(use_camera_wb=True)
            except Exception:
                pass

        # Standard image formats
        try:
            img = cv2.imread(file_path)
            if img is not None:
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception:
            pass

        # PIL fallback (HEIC, AVIF, etc.)
        try:
            pil_img = Image.open(file_path).convert("RGB")
            return np.array(pil_img)
        except Exception:
            pass

        logger.warning("FaceService: unable to load image %s", file_path)
        return None

    @staticmethod
    def load_image_from_bytes(data: bytes) -> Optional[np.ndarray]:
        """Load an image from raw bytes (e.g. an uploaded selfie)."""
        try:
            buf = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
            if img is not None:
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception:
            pass
        try:
            from io import BytesIO

            pil_img = Image.open(BytesIO(data)).convert("RGB")
            return np.array(pil_img)
        except Exception:
            pass
        return None

    # ── Pre-processing ────────────────────────────────────────────────

    @staticmethod
    def resize_for_detection(
        image: np.ndarray, max_dim: int = 1024
    ) -> np.ndarray:
        """Resize keeping aspect ratio so the largest dimension ≤ max_dim."""
        h, w = image.shape[:2]
        if max(h, w) <= max_dim:
            return image
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # ── Detection ─────────────────────────────────────────────────────

    def detect_and_embed(self, image: np.ndarray) -> List[FaceResult]:
        """Detect faces and generate 512-dim embeddings.

        Thread-safe: acquires an internal lock so the ONNX session is
        never invoked concurrently.
        """
        if not self.ready:
            logger.warning("FaceService: model not loaded, skipping detection")
            return []

        with self._detect_lock:
            faces = self._app.get(image)

        results: List[FaceResult] = []
        for idx, face in enumerate(faces):
            bbox = face.bbox.astype(int).tolist()
            x1 = max(0, bbox[0])
            y1 = max(0, bbox[1])
            x2 = min(image.shape[1], bbox[2])
            y2 = min(image.shape[0], bbox[3])

            embedding = face.normed_embedding
            if embedding is None:
                embedding = np.zeros(512, dtype=np.float32)
            else:
                embedding = np.asarray(embedding, dtype=np.float32).flatten()

            results.append(
                FaceResult(
                    bbox=[x1, y1, x2, y2],
                    confidence=float(face.det_score),
                    embedding=embedding,
                    face_index=idx,
                )
            )
        return results

    # ── Full Pipeline ─────────────────────────────────────────────────

    def process_image_file(self, file_path: str) -> List[FaceResult]:
        """Full pipeline: load → (extract preview if RAW) → resize → detect."""
        image = self.load_image(file_path)
        if image is None:
            return []
        image = self.resize_for_detection(image)
        return self.detect_and_embed(image)

    def process_image_bytes(self, data: bytes) -> List[FaceResult]:
        """Process an in-memory image (e.g. uploaded selfie)."""
        image = self.load_image_from_bytes(data)
        if image is None:
            return []
        image = self.resize_for_detection(image)
        return self.detect_and_embed(image)


# Convenience accessor (instantiate but don't load model until .initialize())
face_service = FaceService()
