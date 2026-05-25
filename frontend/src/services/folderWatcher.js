/**
 * Frontend Folder Watcher — uses File System Access API to detect new images
 * in locally-selected folders, enabling cloud-deployed backends to work with
 * local folders via browser-side polling.
 *
 * Directory handles are persisted in IndexedDB so watching can survive page
 * reloads (the browser will prompt for permission on first access after reload).
 */

const DB_NAME = 'ak_lumora_handles'
const STORE_NAME = 'dir_handles'
const DB_VERSION = 1
const POLL_INTERVAL_MS = 3000

// ── IndexedDB helpers ─────────────────────────────────────────────

function openDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      if (!req.result.objectStoreNames.contains(STORE_NAME)) {
        req.result.createObjectStore(STORE_NAME)
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

export async function saveDirHandle(folderId, handle) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).put(handle, String(folderId))
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

export async function getDirHandle(folderId) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const req = tx.objectStore(STORE_NAME).get(String(folderId))
    req.onsuccess = () => resolve(req.result || null)
    req.onerror = () => reject(req.error)
  })
}

export async function removeDirHandle(folderId) {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    tx.objectStore(STORE_NAME).delete(String(folderId))
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

// ── Supported image formats ───────────────────────────────────────

const IMAGE_EXTENSIONS = new Set([
  // Standard
  'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 'webp',
  'svg', 'ico', 'heic', 'heif', 'avif',
  // RAW / DSLR
  'raw', 'cr2', 'cr3', 'nef', 'nrw', 'arw', 'srf', 'sr2',
  'dng', 'orf', 'pef', 'rw2', 'raf', 'srw', 'x3f',
])

function isImageFile(name) {
  const ext = name.split('.').pop()?.toLowerCase() || ''
  return IMAGE_EXTENSIONS.has(ext)
}

// ── Folder Watcher Class ──────────────────────────────────────────

export class FolderWatcher {
  constructor() {
    /** @type {Map<number, {handle: FileSystemDirectoryHandle, interval: number, knownFiles: Set<string>, uploading: Set<string>}>} */
    this._watchers = new Map()
    /** @type {((folderId: number, file: File, fileName: string) => void)|null} */
    this._onNewFile = null
  }

  /**
   * Set the callback for when a new image file is detected.
   * @param {(folderId: number, file: File, fileName: string) => void} fn
   */
  setCallback(fn) {
    this._onNewFile = fn
  }

  /**
   * Start watching a folder.
   * @param {number} folderId
   * @param {FileSystemDirectoryHandle|null} handle — pass null to restore from IndexedDB
   * @returns {Promise<boolean>} true if watching started
   */
  async startWatching(folderId, handle = null) {
    if (!handle) {
      handle = await getDirHandle(folderId)
    }
    if (!handle) return false

    // Verify / request permission
    try {
      let perm = await handle.queryPermission({ mode: 'read' })
      if (perm !== 'granted') {
        perm = await handle.requestPermission({ mode: 'read' })
        if (perm !== 'granted') return false
      }
    } catch (e) {
      console.warn(`[FolderWatcher] Permission check failed for folder ${folderId}:`, e)
      return false
    }

    // Persist handle for future sessions
    try {
      await saveDirHandle(folderId, handle)
    } catch (e) {
      console.warn('[FolderWatcher] Could not persist handle:', e)
    }

    // Stop any existing watcher for this folder
    this.stopWatching(folderId)

    // Initial scan: record all existing files so we don't re-upload them
    const knownFiles = new Set()
    try {
      for await (const entry of handle.values()) {
        if (entry.kind === 'file' && isImageFile(entry.name)) {
          knownFiles.add(entry.name)
        }
      }
    } catch (e) {
      console.error('[FolderWatcher] Initial scan failed:', e)
      return false
    }

    console.log(`[FolderWatcher] Started watching folder ${folderId} — ${knownFiles.size} existing files`)

    // Start polling interval
    const interval = setInterval(() => this._poll(folderId), POLL_INTERVAL_MS)
    this._watchers.set(folderId, { handle, interval, knownFiles, uploading: new Set() })
    return true
  }

  /**
   * Stop watching a folder.
   */
  stopWatching(folderId) {
    const w = this._watchers.get(folderId)
    if (w) {
      clearInterval(w.interval)
      this._watchers.delete(folderId)
      console.log(`[FolderWatcher] Stopped watching folder ${folderId}`)
    }
  }

  stopAll() {
    for (const id of this._watchers.keys()) {
      this.stopWatching(id)
    }
  }

  isWatching(folderId) {
    return this._watchers.has(folderId)
  }

  /** @private */
  async _poll(folderId) {
    const w = this._watchers.get(folderId)
    if (!w) return

    try {
      for await (const entry of w.handle.values()) {
        if (entry.kind === 'file' && isImageFile(entry.name)) {
          if (!w.knownFiles.has(entry.name) && !w.uploading.has(entry.name)) {
            // Mark as uploading to prevent duplicate processing
            w.uploading.add(entry.name)
            w.knownFiles.add(entry.name)

            try {
              const file = await entry.getFile()
              console.log(`[FolderWatcher] New image detected: ${entry.name} (${(file.size / 1024).toFixed(1)} KB)`)
              if (this._onNewFile) {
                this._onNewFile(folderId, file, entry.name)
              }
            } catch (fileErr) {
              console.warn(`[FolderWatcher] Could not read file ${entry.name}:`, fileErr)
              w.knownFiles.delete(entry.name)
            } finally {
              w.uploading.delete(entry.name)
            }
          }
        }
      }
    } catch (e) {
      console.error(`[FolderWatcher] Poll failed for folder ${folderId}:`, e)
      // Directory may have been deleted or permission revoked
      this.stopWatching(folderId)
    }
  }
}

// Global singleton
export const folderWatcher = new FolderWatcher()
