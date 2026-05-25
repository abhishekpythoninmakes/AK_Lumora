"""File monitoring service using watchdog for detecting new images."""

import os
import asyncio
import logging
import time
from typing import Dict, Set, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# Supported image formats (DSLR + professional + standard)
SUPPORTED_FORMATS = {
    # Standard formats
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp",
    ".svg", ".ico", ".heic", ".heif", ".avif",
    # RAW formats (DSLR / professional cameras)
    ".raw", ".cr2", ".cr3", ".nef", ".nrw", ".arw", ".srf", ".sr2",
    ".dng", ".orf", ".pef", ".rw2", ".raf", ".srw", ".x3f",
    ".3fr", ".ari", ".bay", ".cap", ".iiq", ".eip", ".dcs",
    ".dcr", ".drf", ".k25", ".kdc", ".mdc", ".mef", ".mos",
    ".mrw", ".obm", ".ptx", ".pxn", ".r3d", ".rwl", ".rwz",
}


def is_supported_image(filename: str) -> bool:
    """Check if file extension is a supported image format."""
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_FORMATS


class ImageFileHandler(FileSystemEventHandler):
    """Handles filesystem events for new/modified image files."""

    def __init__(self, folder_id: int, callback: Callable, delete_callback: Callable = None):
        self.folder_id = folder_id
        self.callback = callback
        self.delete_callback = delete_callback
        self._processed: Set[str] = set()
        self._last_event_at: Dict[str, float] = {}
        self._debounce_seconds = 1.5

    def on_created(self, event):
        if event.is_directory:
            return
        if is_supported_image(event.src_path):
            now = time.time()
            last = self._last_event_at.get(event.src_path, 0.0)
            if (now - last) < self._debounce_seconds:
                return
            self._last_event_at[event.src_path] = now
            self._processed.add(event.src_path)
            logger.info(f"New image detected: {event.src_path}")
            self.callback(self.folder_id, event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        if is_supported_image(event.src_path):
            now = time.time()
            last = self._last_event_at.get(event.src_path, 0.0)
            if (now - last) < self._debounce_seconds:
                return
            self._last_event_at[event.src_path] = now
            self._processed.add(event.src_path)
            logger.info(f"Modified image detected: {event.src_path}")
            self.callback(self.folder_id, event.src_path)

    def on_deleted(self, event):
        if event.is_directory:
            return
        if is_supported_image(event.src_path):
            self._processed.discard(event.src_path)
            self._last_event_at.pop(event.src_path, None)
            if self.delete_callback:
                logger.info(f"Deleted image detected: {event.src_path}")
                self.delete_callback(self.folder_id, event.src_path)


class FileMonitorManager:
    """Manages multiple folder watchers."""

    def __init__(self):
        self._observers: Dict[int, Observer] = {}
        self._callback: Optional[Callable] = None
        self._delete_callback: Optional[Callable] = None

    def set_callback(self, callback: Callable, delete_callback: Callable = None):
        """Set the callback functions for events."""
        self._callback = callback
        self._delete_callback = delete_callback

    def start_watching(self, folder_id: int, path: str, callback: Callable = None, delete_callback: Callable = None) -> bool:
        """Start watching a folder and call callback when new images are found."""
        if not os.path.exists(path):
            logger.error(f"Cannot watch non-existent path: {path}")
            return False

        if folder_id in self._observers:
            self.stop_watching(folder_id)

        try:
            handler_callback = callback or self._callback
            handler_delete_callback = delete_callback or self._delete_callback
            if not handler_callback:
                logger.error("No callback provided or set for file monitor")
                return False
                
            handler = ImageFileHandler(folder_id, handler_callback, handler_delete_callback)
            observer = Observer()
            observer.schedule(handler, path, recursive=False)
            observer.start()
            self._observers[folder_id] = observer
            logger.info(f"Started watching folder {folder_id}: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to start watching: {e}")
            return False

    def stop_watching(self, folder_id: int) -> bool:
        """Stop watching a folder."""
        if folder_id not in self._observers:
            return False

        try:
            observer = self._observers[folder_id]
            observer.stop()
            observer.join(timeout=5)
            del self._observers[folder_id]
            logger.info(f"Stopped watching folder {folder_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop watching: {e}")
            return False

    def stop_all(self):
        """Stop all watchers."""
        for folder_id in list(self._observers.keys()):
            self.stop_watching(folder_id)


# Global singleton
file_monitor = FileMonitorManager()
