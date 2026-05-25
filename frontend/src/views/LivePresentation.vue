<template>
  <div class="app live-page">
    <!-- Ambient Lens Flares -->
    <div class="ambient-glows" aria-hidden="true">
      <div class="flare flare-1"></div>
      <div class="flare flare-2"></div>
    </div>

    <!-- Premium Glass Card Topbar -->
    <div class="topbar glass-card">
      <div class="topbar-left">
        <h2 @click="showStudioDetailsModal = true" class="studio-trigger-title" title="View Studio Profile Details">
          <span class="pulse-dot"></span>
          <span class="gradient-text-branding studio-glow-text">{{ currentUser?.studio_name || 'Live Studio' }}</span>
        </h2>
        <p>Real-time photo presentation</p>
      </div>
      <div class="topbar-right">
        <div class="select-wrapper">
          <select v-model="selectedFolderId" class="input input-neu" style="min-width: 150px;">
            <option value="">All Folders</option>
            <option v-for="f in watchedTargetFolders" :key="f.id" :value="String(f.id)">{{ f.name }}</option>
          </select>
        </div>
        <div class="watching-indicator" style="display:inline-flex;" v-if="isWatching">
          <span class="watching-dot"></span>
          <span>Live Sync Active</span>
        </div>
        <span class="count-badge" id="galleryCount">{{ images.length }} image{{ images.length !== 1 ? 's' : '' }}</span>
      </div>
    </div>


    <div class="dashboard-grid">
      <div class="dashboard-left">
        <div class="card live-preview-card" v-if="featuredImage">
          <div class="card-header">
            <h3><span style="color:#10b981;">●</span> Live Preview</h3>
            <span class="live-badge">Latest</span>
          </div>
          <div class="live-image-wrap" @click="openModal(featuredImage)">
            <div v-if="!featuredImageLoaded" class="img-skeleton"></div>
            <img
              :src="featuredImageDisplayUrl"
              :alt="featuredImage.name"
              :class="{ 'img-hidden': !featuredImageLoaded }"
              @load="onFeaturedImageLoad"
              @error="onFeaturedImageError"
            >
            <div class="live-overlay">
              <span>Click to expand & scan QR</span>
            </div>
          </div>
          <div class="live-meta">
            <span class="meta-name">{{ featuredImage.name }}</span>
            <span class="meta-dot">•</span>
            <span>{{ formatBytes(featuredImage.size) }}</span>
            <span class="meta-dot">•</span>
            <span class="folder-badge">{{ featuredImage.folder }}</span>
            <span class="meta-dot">•</span>
            <span>{{ featuredImage.time }}</span>
          </div>
        </div>
        
        <div class="empty-gallery" v-else>
          <div class="empty-icon">📸</div>
          <p>Waiting for photos... Start watching a folder in the Dashboard.</p>
        </div>

        <section class="gallery-section-full" v-if="images.length > 0">
          <div class="section-header">
            <h3>All Photos</h3>
          </div>
          <div class="gallery-grid">
            <div class="gallery-card" v-for="(img, idx) in images" :key="img.downloadUrl || img.url" @click="openModal(img)" :style="{ animationDelay: `${Math.min(idx * 0.03, 0.6)}s` }">
              <div class="gallery-img-wrap">
                <div v-if="!isImageLoaded(img, 'gallery')" class="img-skeleton"></div>
                <img
                  :src="img.url"
                  :alt="img.name"
                  loading="lazy"
                  :class="{ 'img-hidden': !isImageLoaded(img, 'gallery') }"
                  @load="onImageLoad(img, 'gallery')"
                  @error="onImageError(img, 'gallery')"
                >
              </div>
              <div class="gallery-info">
                <div class="gallery-name">{{ img.name }}</div>
                <div class="gallery-meta">
                  <span>{{ formatBytes(img.size) }}</span>
                  <span class="folder-badge">{{ img.folder }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <div class="pagination flex-center" style="margin-top: 24px; gap: 16px;">
            <button class="btn btn-secondary btn-sm" @click="goPrevPage" :disabled="page === 1">← Prev</button>
            <span class="page-info">Page {{ page }}</span>
            <button class="btn btn-secondary btn-sm" @click="goNextPage" :disabled="!nextPageToken">Next →</button>
          </div>
        </section>
      </div>

      <div class="dashboard-right">
        <div class="card">
          <div class="card-header">
            <h3>🔴 Recent Photos</h3>
          </div>
          <div class="recent-grid" v-if="recentImages.length > 0">
            <div class="recent-thumb" v-for="(img, idx) in recentImages" :key="img.downloadUrl || img.url" @click="openModal(img)" :style="{ animation: `fadeInUp 0.4s ease ${idx * 0.05}s both` }">
              <div v-if="!isImageLoaded(img, 'recent')" class="img-skeleton"></div>
              <img
                :src="img.url"
                :alt="img.name"
                loading="lazy"
                :class="{ 'img-hidden': !isImageLoaded(img, 'recent') }"
                @load="onImageLoad(img, 'recent')"
                @error="onImageError(img, 'recent')"
              >
            </div>
          </div>
          <div class="recent-grid" v-else>
             <div class="empty-recent">No recent photos</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Toast Notification -->
    <div id="toast" class="toast" :class="{ show: toastMessage }">{{ toastMessage }}</div>

    <!-- Preview Modal with QR -->
    <div class="modal" :class="{ active: showModal }" v-if="selectedImage">
      <div class="modal-backdrop" @click="closeModal"></div>
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">×</button>
        <div class="modal-body">
          <div class="modal-image-section">
            <img :src="selectedImage.url" :alt="selectedImage.name">
          </div>
          <div class="modal-info-section">
            <div class="modal-title">{{ selectedImage.name }}</div>
            <div class="modal-meta">
              <span class="modal-badge">{{ selectedImage.folder }}</span>
              <span>{{ formatBytes(selectedImage.size) }}</span>
              <span>{{ selectedImage.time }}</span>
            </div>
            
            <div class="qr-container">
              <div class="qr-section">
                <div class="qr-label">Scan to Download</div>
                
                <!-- QR Code Canvas -->
                <canvas ref="modalQrCanvas" v-show="selectedImage.downloadUrl"></canvas>
                
                <!-- Loading Spinner (shown when downloadUrl is missing) -->
                <div v-if="!selectedImage.downloadUrl" class="qr-loading">
                  <div class="spinner"></div>
                  <span>Uploading & Generating Link...</span>
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════ FACE SCAN FAB ═══════════ -->
    <button class="face-scan-fab" id="faceScanFab" @click="openFaceScan" :class="{ 'fab-hidden': showFaceScanModal }">
      <svg class="fab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 3H5a2 2 0 00-2 2v4"/>
        <path d="M15 3h4a2 2 0 012 2v4"/>
        <path d="M9 21H5a2 2 0 01-2-2v-4"/>
        <path d="M15 21h4a2 2 0 002-2v-4"/>
        <circle cx="12" cy="10" r="3"/>
        <path d="M12 13c-2.67 0-8 1.34-8 4v1h16v-1c0-2.66-5.33-4-8-4z"/>
      </svg>
      <span class="fab-label">Face Scan</span>
      <span class="fab-pulse"></span>
    </button>

    <!-- ═══════════ FACE SCAN MODAL ═══════════ -->
    <Teleport to="body">
      <div class="fs-overlay" v-if="showFaceScanModal" @click.self="closeFaceScanIfNotProcessing">
        <!-- Search progress overlay -->
        <div class="fs-progress-overlay" v-if="fsSearching">
          <div class="fs-progress-card">
            <div class="fs-progress-icon">
              <svg class="fs-scan-anim" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="none" stroke="url(#fsg1)" stroke-width="4" stroke-dasharray="120 60" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0 32 32" to="360 32 32" dur="1.2s" repeatCount="indefinite"/></circle><defs><linearGradient id="fsg1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#10b981"/></linearGradient></defs></svg>
            </div>
            <div class="fs-progress-text">Scanning {{ fsProgressText }}...</div>
            <div class="fs-progress-bar-wrap">
              <div class="fs-progress-bar" :style="{ width: fsProgressPercent + '%' }"></div>
            </div>
            <div class="fs-progress-detail">{{ fsProgressDetail }}</div>
          </div>
        </div>

        <div class="fs-modal" v-if="!fsSearching || fsResults.length > 0">
          <button class="fs-close" @click="closeFaceScan">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>

          <!-- ── Step 1: Choose Method ── -->
          <div class="fs-step fs-step-choose" v-if="fsStep === 'choose'">
            <div class="fs-header">
              <div class="fs-header-icon">
                <svg viewBox="0 0 48 48" fill="none">
                  <rect x="6" y="6" width="36" height="36" rx="8" stroke="url(#fsh1)" stroke-width="2.5"/>
                  <circle cx="24" cy="20" r="6" stroke="url(#fsh1)" stroke-width="2"/>
                  <path d="M14 36c0-5.523 4.477-10 10-10s10 4.477 10 10" stroke="url(#fsh1)" stroke-width="2" stroke-linecap="round"/>
                  <path d="M6 12V8a2 2 0 012-2h4" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
                  <path d="M42 12V8a2 2 0 00-2-2h-4" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
                  <path d="M6 36v4a2 2 0 002 2h4" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/>
                  <path d="M42 36v4a2 2 0 01-2 2h-4" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/>
                  <defs><linearGradient id="fsh1" x1="6" y1="6" x2="42" y2="42"><stop stop-color="#6366f1"/><stop offset="1" stop-color="#10b981"/></linearGradient></defs>
                </svg>
              </div>
              <h2>Find Your Photos</h2>
              <p>Scan your face to find all photos of you</p>
            </div>
            <div class="fs-options">
              <button class="fs-option-btn" @click="startCamera" id="fsCameraBtn">
                <div class="fs-option-icon">
                  <svg viewBox="0 0 40 40" fill="none">
                    <rect x="4" y="10" width="32" height="22" rx="4" stroke="currentColor" stroke-width="2"/>
                    <circle cx="20" cy="21" r="6" stroke="currentColor" stroke-width="2"/>
                    <circle cx="20" cy="21" r="2.5" fill="currentColor" opacity="0.3"/>
                    <path d="M14 10l2-4h8l2 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="30" cy="15" r="1.5" fill="currentColor"/>
                  </svg>
                </div>
                <span class="fs-option-title">Open Camera</span>
                <span class="fs-option-desc">Take a selfie using your camera</span>
              </button>
              <button class="fs-option-btn" @click="triggerUpload" id="fsUploadBtn">
                <div class="fs-option-icon">
                  <svg viewBox="0 0 40 40" fill="none">
                    <rect x="6" y="4" width="28" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
                    <path d="M20 14v10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    <path d="M15 18l5-5 5 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="12" y1="30" x2="28" y2="30" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                  </svg>
                </div>
                <span class="fs-option-title">Upload Photo</span>
                <span class="fs-option-desc">Choose a selfie from your device</span>
              </button>
            </div>
            <input type="file" ref="fsSelfieInput" accept="image/*" class="fs-hidden-input" @change="onSelfieSelected" />
          </div>

          <!-- ── Step 2: Camera ── -->
          <div class="fs-step fs-step-camera" v-if="fsStep === 'camera'">
            <div class="fs-camera-container">
              <video ref="fsCameraVideo" autoplay playsinline muted class="fs-camera-video"></video>
              <div class="fs-camera-overlay">
                <div class="fs-face-guide"></div>
              </div>
              <div class="fs-camera-controls">
                <button class="fs-cam-btn fs-cam-back" @click="fsStep = 'choose'; stopCamera()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
                </button>
                <button class="fs-cam-btn fs-cam-capture" @click="capturePhoto" id="fsCaptureBtn">
                  <div class="fs-shutter-ring"></div>
                </button>
                <div style="width:48px;"></div>
              </div>
            </div>
          </div>

          <!-- ── Step 3: Preview Captured ── -->
          <div class="fs-step fs-step-preview" v-if="fsStep === 'preview'">
            <div class="fs-preview-wrap">
              <img :src="fsCapturedImage" alt="Captured face" class="fs-preview-img" />
              <div class="fs-face-bbox" v-if="fsFaceDetected" :style="fsBboxStyle"></div>
            </div>
            <div class="fs-preview-actions">
              <button class="fs-action-btn fs-retake" @click="retakePhoto">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 105.13-11.74L1 10"/></svg>
                Retake
              </button>
              <button class="fs-action-btn fs-search" @click="searchByFace" id="fsSearchBtn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                Find My Photos
              </button>
            </div>
          </div>

          <!-- ── Step 4: Results ── -->
          <div class="fs-step fs-step-results" v-if="fsStep === 'results'">
            <div class="fs-results-header">
              <h3>
                <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" style="width:22px;height:22px;vertical-align:middle;margin-right:6px;"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                {{ fsResults.length }} Photo{{ fsResults.length !== 1 ? 's' : '' }} Found
              </h3>
              <span class="fs-search-time">{{ fsSearchTime }}ms</span>
            </div>

            <!-- Threshold Slider -->
            <div class="fs-threshold-row">
              <label class="fs-threshold-label">Similarity: <strong>{{ (fsThreshold * 100).toFixed(0) }}%</strong></label>
              <input type="range" class="fs-threshold-slider" min="10" max="95" :value="fsThreshold * 100" @input="onThresholdChange" />
            </div>

            <div class="fs-results-grid" v-if="fsResults.length > 0">
              <div class="fs-result-card" v-for="(res, idx) in fsResults" :key="res.drive_file_id || idx" @click="openFsResultModal(res)" :style="{ animationDelay: `${Math.min(idx * 0.04, 0.8)}s` }">
                <div class="fs-result-img-wrap">
                  <div v-if="!isFsImageLoaded(res)" class="img-skeleton"></div>
                  <img :src="getFsResultThumbnail(res)" :alt="res.file_name" loading="lazy" :class="{ 'img-hidden': !isFsImageLoaded(res) }" @load="onFsImageLoad(res)" @error="onFsImageLoad(res)" />
                  <div class="fs-similarity-badge" :class="getSimilarityClass(res.similarity)">{{ (res.similarity * 100).toFixed(0) }}%</div>
                </div>
                <div class="fs-result-info">
                  <div class="fs-result-name">{{ res.file_name }}</div>
                  <div class="fs-result-meta">
                    <span class="folder-badge">{{ res.drive_folder_name || res.folder_name || 'Folder' }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="fs-no-results" v-else>
              <svg viewBox="0 0 48 48" fill="none" style="width:48px;height:48px;opacity:0.4;">
                <circle cx="24" cy="24" r="20" stroke="#6b7280" stroke-width="2"/>
                <path d="M16 30s2-4 8-4 8 4 8 4" stroke="#6b7280" stroke-width="2" stroke-linecap="round"/>
                <circle cx="18" cy="20" r="2" fill="#6b7280"/>
                <circle cx="30" cy="20" r="2" fill="#6b7280"/>
              </svg>
              <p>No matching photos found. Try adjusting the similarity threshold or scan again.</p>
            </div>
            <div class="fs-results-actions">
              <button class="fs-action-btn fs-retake" @click="resetFaceScan">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 105.13-11.74L1 10"/></svg>
                Scan Again
              </button>
            </div>
          </div>

        </div>

        <!-- ── Face Search Result Detail Modal ── -->
        <div class="fs-detail-overlay" v-if="fsSelectedResult" @click.self="fsSelectedResult = null">
          <div class="fs-detail-card">
            <button class="fs-close fs-detail-close" @click="fsSelectedResult = null">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
            <div class="fs-detail-img">
              <img :src="getFsResultFullImage(fsSelectedResult)" :alt="fsSelectedResult.file_name" />
            </div>
            <div class="fs-detail-info">
              <div class="fs-detail-name">{{ fsSelectedResult.file_name }}</div>
              <div class="fs-detail-meta">
                <span class="fs-similarity-badge" :class="getSimilarityClass(fsSelectedResult.similarity)">{{ (fsSelectedResult.similarity * 100).toFixed(0) }}% match</span>
                <span class="folder-badge">{{ fsSelectedResult.drive_folder_name || fsSelectedResult.folder_name }}</span>
              </div>
              <div class="fs-detail-qr" v-if="fsSelectedResult.public_link || fsSelectedResult.drive_file_id">
                <div class="qr-label">Scan to Download</div>
                <canvas ref="fsDetailQrCanvas"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ═══════════ STUDIO PROFILE DETAILS OVERLAY ═══════════ -->
    <Transition name="fade">
      <div v-if="showStudioDetailsModal" class="studio-details-overlay" @click.self="showStudioDetailsModal = false">
        <div class="studio-details-card glass-strong">
          <button class="studio-close-btn" @click="showStudioDetailsModal = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
          
          <!-- Scrollable inner container -->
          <div class="studio-details-scroll">
            <!-- Hero Header -->
            <div class="studio-profile-header">
              <div class="studio-avatar-ring">
                <div class="studio-avatar-large">
                  <img 
                    v-if="currentUser?.profile_image && !studioImgError" 
                    :src="resolveLogoUrl(currentUser.profile_image)" 
                    alt="Studio Profile"
                    @error="studioImgError = true"
                  />
                  <div v-else class="studio-initial-large">
                    {{ (currentUser?.email || 'S')[0].toUpperCase() }}
                  </div>
                </div>
              </div>
              <h3 class="studio-brand-title gradient-text-branding">{{ currentUser?.studio_name || 'Studio Profile' }}</h3>
              <p class="studio-brand-subtitle">AK Lumora Registered Creative Studio</p>
              <p v-if="currentUser?.bio" class="studio-bio">{{ currentUser.bio }}</p>
            </div>

            <!-- Contact Info Section -->
            <div class="studio-section">
              <div class="studio-section-title">Contact Information</div>
              <div class="studio-info-grid">
                <!-- Owner Name -->
                <div class="studio-info-item">
                  <div class="studio-info-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  </div>
                  <div class="studio-info-content">
                    <span class="studio-info-label">Owner</span>
                    <span class="studio-info-value">{{ currentUser?.name || 'Photographer' }}</span>
                  </div>
                </div>

                <!-- Email -->
                <div class="studio-info-item">
                  <div class="studio-info-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                  </div>
                  <div class="studio-info-content">
                    <span class="studio-info-label">Email</span>
                    <span class="studio-info-value studio-info-truncate">{{ currentUser?.email || 'N/A' }}</span>
                  </div>
                </div>

                <!-- Phone Number -->
                <div class="studio-info-item" v-if="currentUser?.phone">
                  <div class="studio-info-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                  </div>
                  <div class="studio-info-content">
                    <span class="studio-info-label">Phone</span>
                    <span class="studio-info-value">{{ currentUser?.phone }}</span>
                  </div>
                </div>

                <!-- Alternate Contacts -->
                <div class="studio-info-item" v-if="currentUser?.contact_numbers">
                  <div class="studio-info-icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                  </div>
                  <div class="studio-info-content">
                    <span class="studio-info-label">Alt. Phone</span>
                    <span class="studio-info-value studio-info-truncate">{{ currentUser?.contact_numbers }}</span>
                  </div>
                </div>

                <!-- WhatsApp -->
                <div class="studio-info-item" v-if="currentUser?.whatsapp_number">
                  <div class="studio-info-icon" style="background: rgba(37, 211, 102, 0.1);">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#25D366" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                  </div>
                  <div class="studio-info-content">
                    <span class="studio-info-label">WhatsApp</span>
                    <span class="studio-info-value">{{ currentUser.whatsapp_number }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Website & Address Section -->
            <div class="studio-section" v-if="currentUser?.website_link || currentUser?.address">
              <div class="studio-section-title">Location & Web</div>

              <!-- Website -->
              <div class="studio-website-row" v-if="currentUser?.website_link">
                <a :href="websiteUrl" target="_blank" class="studio-website-btn">
                  <div class="studio-website-btn-left">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                    <span>{{ websiteDomain }}</span>
                  </div>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                </a>
              </div>

              <!-- Address -->
              <div class="studio-address-row" v-if="currentUser?.address">
                <div class="studio-info-icon">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                </div>
                <div class="studio-info-content">
                  <span class="studio-info-label">Studio Address</span>
                  <span class="studio-info-value" style="font-size: 12px; line-height: 1.45;">{{ currentUser?.address }}</span>
                </div>
              </div>
            </div>

            <!-- Social Channels & QR Codes Section -->
            <div class="studio-section" v-if="currentUser?.instagram_link || currentUser?.facebook_link">
              <div class="studio-section-title">Scan to Connect</div>

              <div class="studio-social-grid">
                <!-- Instagram Card -->
                <div class="studio-social-card" v-if="currentUser?.instagram_link">
                  <div class="studio-social-badge" style="color: #E1306C;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/></svg>
                    <span>Instagram</span>
                  </div>
                  <div class="studio-qr-box">
                    <img :src="getQrCodeUrl(instagramUrl)" alt="Instagram QR Code" />
                  </div>
                  <a :href="instagramUrl" target="_blank" class="studio-social-handle">{{ instagramUsername }}</a>
                </div>

                <!-- Facebook Card -->
                <div class="studio-social-card" v-if="currentUser?.facebook_link">
                  <div class="studio-social-badge" style="color: #1877F2;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>
                    <span>Facebook</span>
                  </div>
                  <div class="studio-qr-box">
                    <img :src="getQrCodeUrl(facebookUrl)" alt="Facebook QR Code" />
                  </div>
                  <a :href="facebookUrl" target="_blank" class="studio-social-handle">{{ facebookUsername }}</a>
                </div>
              </div>
            </div>
          </div>

          <!-- Pinned footer -->
          <div class="studio-profile-footer">
            <button class="btn btn-primary btn-sm btn-full" @click="showStudioDetailsModal = false">Close Profile</button>
          </div>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import QRCode from 'qrcode'
import api from '../utils/api'
import imageCompression from 'browser-image-compression'
import exifr from 'exifr'
import axios from 'axios'

// State
const selectedFolderId = ref('')
const syncQueue = ref([])
const isSyncingDrive = computed(() => syncQueue.value.some(item => item.stage !== 'completed' && item.stage !== 'failed'))
const syncingFileName = computed(() => {
  const activeItem = syncQueue.value.find(item => item.stage !== 'completed' && item.stage !== 'failed')
  return activeItem ? activeItem.name : ''
})
const activeSyncCount = computed(() => syncQueue.value.filter(item => ['analyzing', 'compressing', 'resuming', 'uploading'].includes(item.stage)).length)
const queuedSyncCount = computed(() => syncQueue.value.filter(item => item.stage === 'detected').length)
const currentUser = ref(null)
const showStudioDetailsModal = ref(false)
const studioImgError = ref(false)
const page = ref(1)
const perPage = 6
const watchedTargetFolders = ref([])
const images = ref([])
const isWatching = ref(false)
const nextPageToken = ref(null)
const pageTokens = ref([])
const cacheBustSeed = ref(Date.now())
const backendUnavailable = ref(false)
const driveAuthInvalid = ref(false)

// Social & Website URL computed properties for Live Presentation Studio details
const instagramUrl = computed(() => {
  const link = currentUser.value?.instagram_link
  if (!link) return ''
  const clean = link.trim()
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    return clean
  }
  return `https://instagram.com/${clean.replace(/^@/, '')}`
})

const instagramUsername = computed(() => {
  const link = currentUser.value?.instagram_link
  if (!link) return ''
  const clean = link.trim().replace(/^@/, '')
  // Extract username from full instagram URL
  if (clean.includes('instagram.com/')) {
    const parts = clean.split('instagram.com/')
    const lastPart = parts[parts.length - 1]
    const username = lastPart.split('/')[0].split('?')[0]
    return username ? '@' + username : '@studio'
  }
  // If it looks like any other URL, just show a clean version
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    try {
      const url = new URL(clean)
      const path = url.pathname.replace(/^\//, '').split('/')[0]
      return '@' + (path || url.hostname.split('.')[0])
    } catch {
      return '@studio'
    }
  }
  return '@' + clean
})

const facebookUrl = computed(() => {
  const link = currentUser.value?.facebook_link
  if (!link) return ''
  const clean = link.trim()
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    return clean
  }
  return `https://facebook.com/${clean}`
})

const facebookUsername = computed(() => {
  const link = currentUser.value?.facebook_link
  if (!link) return ''
  const clean = link.trim()
  // Extract username from full facebook URL
  if (clean.includes('facebook.com/')) {
    const parts = clean.split('facebook.com/')
    const lastPart = parts[parts.length - 1]
    const username = lastPart.split('/')[0].split('?')[0]
    return username || 'Studio'
  }
  // If it looks like any other URL, extract meaningful part
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    try {
      const url = new URL(clean)
      const path = url.pathname.replace(/^\//, '').split('/')[0]
      return path || url.hostname.split('.')[0]
    } catch {
      return 'Studio'
    }
  }
  return clean
})

const websiteUrl = computed(() => {
  const link = currentUser.value?.website_link
  if (!link) return ''
  const clean = link.trim()
  if (clean.startsWith('http://') || clean.startsWith('https://')) {
    return clean
  }
  return `https://${clean}`
})

const websiteDomain = computed(() => {
  const link = currentUser.value?.website_link
  if (!link) return ''
  return link.trim().replace(/^(https?:\/\/)?(www\.)?/, '').split('/')[0]
})

function getQrCodeUrl(url) {
  if (!url) return ''
  return `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(url)}`
}
const BACKEND_RETRY_MS = 15000
const featuredImageUseThumbnail = ref(false)
const featuredHighResReady = ref(false)
const featuredImageLoaded = ref(false)
const loadedImageKeys = ref(new Set())
const driveBlobCache = new Map() // driveFileId -> objectUrl

// Modal State
const showModal = ref(false)
const selectedImage = ref(null)
const modalQrCanvas = ref(null)

// Toast State
const toastMessage = ref('')
let toastTimeout = null

function showToast(message) {
  toastMessage.value = message
  if (toastTimeout) clearTimeout(toastTimeout)
  toastTimeout = setTimeout(() => { toastMessage.value = '' }, 3000)
}

// Computed Data
const filteredImages = computed(() => [...images.value].sort((a, b) => b.timestamp - a.timestamp))

const featuredImage = computed(() => filteredImages.value[0] || null)
const featuredImageDisplayUrl = computed(() => {
  if (!featuredImage.value) return ''
  if (featuredImageUseThumbnail.value) return featuredImage.value.url || ''
  if (featuredHighResReady.value && featuredImage.value.previewUrl) return featuredImage.value.previewUrl
  return featuredImage.value.url || featuredImage.value.previewUrl || ''
})
const recentImages = computed(() => filteredImages.value.slice(0, 6))

watch(() => featuredImage.value?.id, () => {
  featuredImageUseThumbnail.value = false
  featuredHighResReady.value = false
  featuredImageLoaded.value = false
})

function onFeaturedImageError() {
  featuredImageUseThumbnail.value = true
  featuredImageLoaded.value = false
}

function onFeaturedImageLoad() {
  featuredImageLoaded.value = true
}

function getImageRenderKey(img, section) {
  return `${section}:${img.id || img.uploadLogId || img.name}:${img.url}`
}

function isImageLoaded(img, section) {
  return loadedImageKeys.value.has(getImageRenderKey(img, section))
}

function onImageLoad(img, section) {
  loadedImageKeys.value.add(getImageRenderKey(img, section))
}

function onImageError(img, section) {
  loadedImageKeys.value.add(getImageRenderKey(img, section))
}

function preloadFeaturedHighResImage() {
  if (!featuredImage.value?.previewUrl) return
  const probe = new Image()
  probe.onload = () => {
    featuredHighResReady.value = true
  }
  probe.onerror = () => {
    featuredHighResReady.value = false
  }
  probe.src = featuredImage.value.previewUrl
}

// Formatters
function resolveLogoUrl(path) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('blob:')) {
    return path
  }
  const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const base = apiBase.endsWith('/') ? apiBase.slice(0, -1) : apiBase
  const relative = path.startsWith('/') ? path : '/' + path
  return `${base}${relative}`
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const idx = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, idx)).toFixed(1)) + ' ' + sizes[idx]
}

function getDriveImageViewUrl(driveFileId) {
  if (!driveFileId) return ''
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
  return `${baseUrl}/api/uploads/public-image/${driveFileId}?v=${cacheBustSeed.value}`
}

function getDriveThumbnailUrl(driveFileId) {
  if (!driveFileId) return ''
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
  return `${baseUrl}/api/uploads/public-thumbnail/${driveFileId}?v=${cacheBustSeed.value}`
}

// Modal Actions
function openModal(img) {
  selectedImage.value = img
  showModal.value = true
  document.body.style.overflow = 'hidden'
  
  nextTick(() => {
    if (modalQrCanvas.value && img.downloadUrl) {
      QRCode.toCanvas(modalQrCanvas.value, img.downloadUrl, {
        width: 200,
        margin: 2,
        color: { dark: '#111827', light: '#ffffff' }
      }, (err) => {
        if (err) console.error(err)
      })
    } else if (modalQrCanvas.value) {
      // Clear canvas if no download URL
      const ctx = modalQrCanvas.value.getContext('2d')
      ctx.clearRect(0, 0, modalQrCanvas.value.width, modalQrCanvas.value.height)
    }
  })
}

function closeModal() {
  showModal.value = false
  selectedImage.value = null
  document.body.style.overflow = ''
}

// Watch for downloadUrl changes while modal is open (e.g. if upload completes while viewing)
watch(() => selectedImage.value?.downloadUrl, (newUrl) => {
  if (showModal.value && newUrl && modalQrCanvas.value) {
    QRCode.toCanvas(modalQrCanvas.value, newUrl, {
      width: 200,
      margin: 2,
      color: { dark: '#111827', light: '#ffffff' }
    }, (err) => {
      if (err) console.error(err)
    })
  }
})

watch(
  () => featuredImage.value?.id,
  () => {
    featuredImageLoaded.value = false
    preloadFeaturedHighResImage()
  },
  { immediate: true }
)

// Data Loading and WebSockets
let ws = null
let pollTimer = null

function startPollingUploads() {
  stopPollingUploads()
  pollTimer = setInterval(loadRecentUploads, backendUnavailable.value ? 7000 : 5000)
}

function markBackendOffline() {
  backendUnavailable.value = true
  localStorage.setItem('ak_backend_offline', '1')
  localStorage.setItem('ak_backend_offline_since', String(Date.now()))
}

function markBackendOnline() {
  backendUnavailable.value = false
  localStorage.removeItem('ak_backend_offline')
  localStorage.removeItem('ak_backend_offline_since')
}

function shouldAttemptBackendNow() {
  if (backendUnavailable.value) return false
  const isOffline = localStorage.getItem('ak_backend_offline') === '1'
  if (!isOffline) return true
  const since = Number(localStorage.getItem('ak_backend_offline_since') || '0')
  if (!since) return true
  return (Date.now() - since) >= BACKEND_RETRY_MS
}

function stopPollingUploads() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function findJpegEnd(bytes, start) {
  let pos = start + 2; // skip FF D8
  while (pos < bytes.length - 4) {
    if (bytes[pos] !== 0xFF) {
      return -1; // Not a valid marker
    }
    const marker = bytes[pos + 1];
    if (marker === 0xD9) {
      return pos + 2; // EOI
    }
    if (marker === 0xDA) {
      // Start of Scan
      const len = (bytes[pos + 2] << 8) | bytes[pos + 3];
      pos += 2 + len;
      
      // Scan entropy-coded data for EOI (FF D9)
      while (pos < bytes.length - 1) {
        if (bytes[pos] === 0xFF) {
          const m = bytes[pos + 1];
          if (m === 0xD9) {
            return pos + 2; // True EOI
          }
          if (m === 0x00 || (m >= 0xD0 && m <= 0xD7)) {
            pos += 2; // Stuffed byte or restart marker
          } else if (m === 0xFF) {
            pos += 1;
          } else {
            pos += 2;
          }
        } else {
          pos++;
        }
      }
      return -1;
    }
    
    if (marker === 0xD8 || marker === 0x01 || (marker >= 0xD0 && marker <= 0xD7)) {
      pos += 2;
    } else {
      const len = (bytes[pos + 2] << 8) | bytes[pos + 3];
      if (len < 2) return -1;
      pos += 2 + len;
    }
  }
  return -1;
}

async function extractLargestJpegFromRaw(blob) {
  try {
    const buffer = await blob.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    
    // Find all FF D8 FF occurrences
    const candidates = [];
    let pos = 0;
    while (true) {
      const idx = bytes.indexOf(0xFF, pos);
      if (idx === -1 || idx > bytes.length - 3) break;
      if (bytes[idx+1] === 0xD8 && bytes[idx+2] === 0xFF) {
        candidates.push(idx);
        pos = idx + 3;
      } else {
        pos = idx + 1;
      }
    }
    
    let largestSize = 0;
    let bestStart = -1;
    let bestEnd = -1;
    
    for (const start of candidates) {
      const end = findJpegEnd(bytes, start);
      if (end !== -1) {
        const size = end - start;
        if (size > largestSize) {
          largestSize = size;
          bestStart = start;
          bestEnd = end;
        }
      }
    }
    
    if (bestStart !== -1 && largestSize > 20000) {
      const jpegBytes = bytes.slice(bestStart, bestEnd);
      return new Blob([jpegBytes], { type: 'image/jpeg' });
    }
  } catch (err) {
    console.warn("Failed to scan raw buffer for JPEG:", err);
  }
  return null;
}

// ─── Frontend-driven Google Drive upload ───
// ─── Frontend-driven Google Drive Parallel Upload Queue ───
const MAX_CONCURRENT_UPLOADS = 3

function getStageLabel(stage) {
  const labels = {
    detected: 'Detected',
    analyzing: 'Analyzing Image',
    compressing: 'Compressing Preview',
    resuming: 'Creating Drive Link',
    uploading: 'Uploading to Drive',
    completed: 'Completed',
    failed: 'Sync Failed'
  }
  return labels[stage] || 'Syncing...'
}

// Watch syncQueue and process pending uploads
watch(syncQueue, () => {
  processNextInQueue()
}, { deep: true })

async function processNextInQueue() {
  const activeCount = syncQueue.value.filter(item => 
    ['analyzing', 'compressing', 'resuming', 'uploading'].includes(item.stage)
  ).length

  if (activeCount >= MAX_CONCURRENT_UPLOADS) return

  const nextItem = syncQueue.value.find(item => item.stage === 'detected')
  if (!nextItem) return

  // Transition to active state
  nextItem.stage = 'analyzing'
  nextItem.progress = 10
  
  // Launch upload asynchronously
  runUploadWorker(nextItem)
  
  // Recurse to see if we can trigger more parallel uploads
  processNextInQueue()
}

async function runUploadWorker(queueItem) {
  const startTime = performance.now()
  try {
    // 1. Fetch file blob from backend
    const blobResp = await fetch(queueItem.url, { cache: 'no-store' })
    if (!blobResp.ok) throw new Error('Failed to fetch stream')
    let blob = await blobResp.blob()
    let mimeType = blob.type || 'image/png'
    let finalFileName = queueItem.name

    queueItem.stage = 'analyzing'
    queueItem.progress = 20
    await new Promise(resolve => setTimeout(resolve, 200))

    // 2. Compressing stage
    const isRaw = /\.(arw|cr2|nef|dng|raw|orf|raf)$/i.test(finalFileName);
    let compressibleBlob = blob;

    if (isRaw) {
      queueItem.stage = 'compressing'
      queueItem.progress = 30
      
      let extractedBlob = null;
      try {
        extractedBlob = await extractLargestJpegFromRaw(blob);
      } catch (e) {
        console.warn("Binary raw JPEG extraction failed:", e);
      }

      if (extractedBlob) {
        compressibleBlob = extractedBlob;
        finalFileName = finalFileName.replace(/\.[^/.]+$/, "") + ".jpg";
        mimeType = 'image/jpeg';
      } else {
        try {
          const thumbData = await exifr.thumbnail(blob);
          if (thumbData) {
            compressibleBlob = new Blob([thumbData], { type: 'image/jpeg' });
            finalFileName = finalFileName.replace(/\.[^/.]+$/, "") + ".jpg";
            mimeType = 'image/jpeg';
          } else {
            throw new Error("Could not extract JPEG preview from RAW file via exifr");
          }
        } catch (exifrErr) {
          console.warn("Exifr extraction failed:", exifrErr);
          throw new Error("Could not extract JPEG preview from RAW file");
        }
      }
    }

    queueItem.stage = 'compressing'
    queueItem.progress = 40

    try {
      const options = {
        maxSizeMB: 1.5,
        maxWidthOrHeight: 2560,
        useWebWorker: true,
        initialQuality: 0.88,
        fileType: 'image/jpeg',
        exifOrientation: true
      };

      const compressedBlob = await imageCompression(compressibleBlob, options);
      blob = compressedBlob;
      mimeType = 'image/jpeg';
      
      if (!finalFileName.toLowerCase().endsWith('.jpg') && !finalFileName.toLowerCase().endsWith('.jpeg')) {
        finalFileName = finalFileName.replace(/\.[^/.]+$/, "") + ".jpg";
      }
    } catch (compressErr) {
      console.warn('Compression failed, falling back to original:', compressErr);
    }
    
    queueItem.progress = 55
    await new Promise(resolve => setTimeout(resolve, 150))

    // 3. Creating Drive Link stage
    queueItem.stage = 'resuming'
    queueItem.progress = 60
    
    const { data: resumable } = await api.post('/api/uploads/resumable', {
      file_name: finalFileName,
      file_size: blob.size,
      mime_type: mimeType,
      folder_id: queueItem.folderId,
    })

    // 4. Uploading directly from browser to Google Drive with dynamic progress
    queueItem.stage = 'uploading'
    queueItem.progress = 65

    const driveResp = await axios.put(resumable.upload_url, blob, {
      headers: {
        'Content-Type': mimeType,
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        // Animate smoothly between 65% and 92%
        queueItem.progress = 65 + Math.round((percentCompleted * 27) / 100);
      }
    })

    if (driveResp.status !== 200 && driveResp.status !== 201) {
      throw new Error(`Drive upload failed with status ${driveResp.status}`)
    }
    
    const fileId = driveResp.data.id
    queueItem.progress = 95
    const uploadTime = Math.round((performance.now() - startTime) / 1000 * 100) / 100

    // 5. Finalize upload
    queueItem.progress = 97
    await api.post('/api/uploads/finalize', {
      upload_log_id: queueItem.uploadLogId,
      drive_file_id: fileId,
      upload_time_sec: uploadTime,
    })

    queueItem.stage = 'completed'
    queueItem.progress = 100
    showToast(`✓ ${queueItem.name} uploaded to Drive!`)
  } catch (err) {
    console.error('Queue upload failed:', err)
    queueItem.stage = 'failed'
    queueItem.error = err.message || 'Upload failed'
    showToast(`✕ Sync failed for ${queueItem.name}`)
  }
}

async function getDriveAccessTokenDirect(userId) {
  const cached = localStorage.getItem('ak_drive_access_token')
  if (cached) return cached
  if (!shouldAttemptBackendNow()) return null
  try {
    const { data } = await api.get(`/api/drive/token?user_id=${userId}`)
    const token = data?.access_token
    if (token) {
      localStorage.setItem('ak_drive_access_token', token)
      markBackendOnline()
      return token
    }
  } catch {
    markBackendOffline()
    return null
  }
  return null
}

async function refreshDriveAccessToken(userId) {
  if (!shouldAttemptBackendNow()) return null
  try {
    const { data } = await api.get(`/api/drive/token?user_id=${userId}`)
    const token = data?.access_token
    if (token) {
      localStorage.setItem('ak_drive_access_token', token)
      markBackendOnline()
      driveAuthInvalid.value = false
      return token
    }
  } catch {
    markBackendOffline()
  }
  return null
}

function getHighResDriveThumbnail(thumbnailLink) {
  if (!thumbnailLink) return ''
  const scaled = thumbnailLink.replace(/=s\d+(-c)?$/, '=s1600').replace(/=w\d+(-c)?$/, '=s1600')
  if (scaled === thumbnailLink) {
    if (thumbnailLink.includes('=')) {
      return thumbnailLink.substring(0, thumbnailLink.lastIndexOf('=')) + '=s1600'
    } else {
      return thumbnailLink + '=s1600'
    }
  }
  return scaled
}

async function mapDriveFilesToImages(files, watchedByDriveFolderId, token) {
  return Promise.all(files.map(async (file) => {
    const driveFileId = file.id
    const parentId = (file.parents || [])[0] || null
    const watched = watchedByDriveFolderId.get(parentId)
    const isRaw = /\.(arw|cr2|nef|dng|raw|orf|raf)$/i.test(file.name)
    
    let objectUrl = ''
    
    // For RAW files or when we have a thumbnailLink, we use the high-res thumbnail link.
    // This uses Google's high-speed CDN to serve standard web JPEGs, resolving rendering
    // compatibility and avoiding multi-megabyte browser download bottlenecks.
    if (file.thumbnailLink) {
      objectUrl = getHighResDriveThumbnail(file.thumbnailLink)
    }
    
    // Fallback only if no thumbnail link is available
    if (!objectUrl) {
      const mediaUrl = `https://www.googleapis.com/drive/v3/files/${driveFileId}?alt=media`
      if (driveBlobCache.has(driveFileId)) {
        objectUrl = driveBlobCache.get(driveFileId)
      } else {
        try {
          const imgResp = await fetch(mediaUrl, {
            headers: { Authorization: `Bearer ${token}` },
          })
          if (imgResp.ok) {
            const blob = await imgResp.blob()
            objectUrl = URL.createObjectURL(blob)
            driveBlobCache.set(driveFileId, objectUrl)
          }
        } catch {}
      }
      if (!objectUrl) {
        objectUrl = mediaUrl
      }
    }

    return {
      id: driveFileId,
      uploadLogId: null,
      watchedFolderId: watched?.id || null,
      driveFileId,
      name: file.name,
      url: objectUrl,
      previewUrl: objectUrl,
      downloadUrl: file.webContentLink || file.webViewLink || '',
      folder: watched?.name || 'Drive Folder',
      size: Number(file.size || 0),
      time: file.createdTime ? new Date(file.createdTime).toLocaleString() : 'Unknown',
      timestamp: file.createdTime ? new Date(file.createdTime).getTime() : Date.now(),
      uploading: false,
    }
  }))
}

async function loadFromDriveDirect(userId) {
  let token = await getDriveAccessTokenDirect(userId)
  if (!token) return false

  let watched = watchedTargetFolders.value
  if (!watched.length) {
    const cachedFolders = localStorage.getItem('ak_watched_folders_cache')
    if (cachedFolders) {
      try {
        watched = JSON.parse(cachedFolders)
      } catch {
        watched = []
      }
    }
  }
  if (!watched.length) return false

  const effective = selectedFolderId.value
    ? watched.filter(f => String(f.id) === String(selectedFolderId.value))
    : watched
  const driveFolderIds = effective.map(f => f.driveFolderId).filter(Boolean)
  // Fallback: if watched-folder ids are unavailable in cache, still show latest drive images.
  const q = driveFolderIds.length
    ? `trashed=false and mimeType contains 'image/' and (${driveFolderIds.map(id => `'${id}' in parents`).join(' or ')})`
    : `trashed=false and mimeType contains 'image/'`
  const params = new URLSearchParams({
    q,
    orderBy: 'createdTime desc',
    pageSize: String(perPage),
    fields: 'files(id,name,mimeType,size,createdTime,thumbnailLink,webViewLink,webContentLink,parents),nextPageToken',
    includeItemsFromAllDrives: 'true',
    supportsAllDrives: 'true',
  })
  if (page.value > 1 && pageTokens.value[page.value - 1]) {
    params.set('pageToken', pageTokens.value[page.value - 1])
  }

  let resp = await fetch(`https://www.googleapis.com/drive/v3/files?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (resp.status === 401) {
    // Cached token expired/invalid: clear and attempt one refresh via backend.
    localStorage.removeItem('ak_drive_access_token')
    const refreshed = await refreshDriveAccessToken(userId)
    if (!refreshed) {
      driveAuthInvalid.value = true
      return false
    }
    token = refreshed
    resp = await fetch(`https://www.googleapis.com/drive/v3/files?${params.toString()}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  }
  if (resp.status === 401) {
    driveAuthInvalid.value = true
    localStorage.removeItem('ak_drive_access_token')
    return false
  }
  if (!resp.ok) return false
  const data = await resp.json()

  const watchedMap = new Map(watched.map(w => [w.driveFolderId, w]))
  const newImages = await mapDriveFilesToImages(data.files || [], watchedMap, token)
  
  if (driveBlobCache.size > 100) {
    const keepIds = new Set(newImages.map(img => img.driveFileId))
    if (selectedImage.value?.driveFileId) {
      keepIds.add(selectedImage.value.driveFileId)
    }
    for (const [id, url] of driveBlobCache.entries()) {
      if (!keepIds.has(id)) {
        URL.revokeObjectURL(url)
        driveBlobCache.delete(id)
      }
    }
  }
  
  images.value = newImages
  nextPageToken.value = data.nextPageToken || null
  if (nextPageToken.value && !pageTokens.value[page.value]) {
    pageTokens.value[page.value] = nextPageToken.value
  }
  return true
}

function connectWebSocket() {
  const userId = JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
  if (!userId) return
  if (!shouldAttemptBackendNow()) return

  try {
    const apiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
    const wsUrl = apiUrl.replace(/^http/, 'ws') + `/ws/live/${userId}`
    ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      isWatching.value = true
      markBackendOnline()
    }
    
    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data)

      if (data.type === 'new_file') {
        const sourceUrl = data.preview_url || ''
        if (sourceUrl) {
          showToast(`New file detected: ${data.file_name} (Uploading to Drive...)`)

          if (data.upload_log_id && data.folder_id) {
            // Push to parallel sync queue
            syncQueue.value.push({
              id: data.upload_log_id,
              uploadLogId: data.upload_log_id,
              folderId: data.folder_id,
              name: data.file_name,
              url: sourceUrl,
              size: data.file_size || 0,
              stage: 'detected',
              progress: 5,
              error: ''
            })
          }
        }
      }

      if (data.type === 'upload_completed') {
        if (selectedFolderId.value && String(selectedFolderId.value) !== String(data.folder_id)) {
          return
        }
        
        // Mark item as completed in our frontend queue if it exists
        const queueItem = syncQueue.value.find(item => item.uploadLogId === data.upload_log_id)
        if (queueItem) {
          queueItem.stage = 'completed'
          queueItem.progress = 100
          
          // Smoothly remove item from the queue after 8 seconds so the user sees the success state
          setTimeout(() => {
            syncQueue.value = syncQueue.value.filter(item => item.uploadLogId !== data.upload_log_id)
          }, 8000)
        }

        const previewUrl = getDriveImageViewUrl(data.drive_file_id)
        const viewUrl = getDriveThumbnailUrl(data.drive_file_id) || previewUrl
        if (viewUrl) {
        const image = {
          id: (data.upload_log_id || Date.now()).toString(),
          uploadLogId: data.upload_log_id,
          driveFileId: data.drive_file_id || '',
          name: data.file_name,
          url: viewUrl,
          previewUrl,
          downloadUrl: data.public_link || previewUrl || '',
          watchedFolderId: data.folder_id || null,
          folder: data.drive_folder_name || data.folder_name || 'Unknown',
          size: data.file_size || 0,
            time: 'Just now',
            timestamp: Date.now(),
            uploading: false,
          }
          const filtered = images.value.filter(i => i.uploadLogId !== data.upload_log_id)
          images.value = [image, ...filtered]
          // Hard refresh from Drive so UI always reflects current Drive truth.
          loadRecentUploads()
        }
      }

      if (data.type === 'delete_file') {
        const deletedName = (data.file_name || data.file_path || '').split('\\').pop().split('/').pop()
        images.value = images.value.filter(i => i.name !== deletedName)
        // Remove from current view if it was the only one
        if (selectedImage.value && selectedImage.value.name === deletedName) {
          closeModal()
        }
        loadRecentUploads()
      }
    }
    
    ws.onclose = () => {
      isWatching.value = false
      if (!backendUnavailable.value) {
        setTimeout(connectWebSocket, 3000)
      }
    }
    ws.onerror = () => {
      markBackendOffline()
      isWatching.value = false
    }
  } catch {
    markBackendOffline()
    isWatching.value = false
  }
}

async function loadRecentUploads() {
  const userId = JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
  if (!userId) return

  try {
    cacheBustSeed.value = Date.now()
    // Always prefer direct Google Drive mode first to avoid backend dependency.
    const directOk = await loadFromDriveDirect(userId)
    if (directOk) return
    if (!shouldAttemptBackendNow()) return
    const fetchDriveFiles = async (withFolderFilter = true) => {
      const token = page.value > 1 ? pageTokens.value[page.value - 1] : ''
      const params = new URLSearchParams({
        user_id: String(userId),
        limit: String(perPage),
      })
      if (token) params.append('page_token', token)
      if (withFolderFilter && selectedFolderId.value) params.append('folder_id', selectedFolderId.value)
      const { data } = await api.get(`/api/uploads/drive-files?${params.toString()}`)
      return data
    }

    let data = await fetchDriveFiles(true)
    markBackendOnline()
    // If a folder filter is active but returns nothing, retry once without filter.
    if (selectedFolderId.value && (!data?.items || data.items.length === 0)) {
      data = await fetchDriveFiles(false)
    }

    images.value = (data.items || []).map((item) => {
      const previewUrl = getDriveImageViewUrl(item.drive_file_id)
      const viewUrl = getDriveThumbnailUrl(item.drive_file_id) || previewUrl
      return {
        id: item.id?.toString() || `${Date.now()}`,
        uploadLogId: item.id,
        watchedFolderId: item.watched_folder_id || null,
        driveFileId: item.drive_file_id || '',
        name: item.name,
        url: viewUrl,
        previewUrl,
        downloadUrl: item.public_link || previewUrl || viewUrl,
        folder: item.drive_folder_name || item.folder_name || 'Unknown',
        size: item.size || 0,
        time: item.created_at ? new Date(item.created_at).toLocaleString() : 'Unknown',
        timestamp: item.created_at ? new Date(item.created_at).getTime() : Date.now(),
        uploading: false,
      }
    }).filter(item => item.url)

    if ((!images.value.length) && driveAuthInvalid.value) {
      showToast('Google Drive session expired. Reconnect Drive in Drive Config.', 'error')
    }

    nextPageToken.value = data.next_page_token || null
    if (nextPageToken.value && !pageTokens.value[page.value]) {
      pageTokens.value[page.value] = nextPageToken.value
    }

  } catch (err) {
    const isNetworkDown = !err?.response
    if (isNetworkDown) {
      markBackendOffline()
    }
    try {
      const ok = await loadFromDriveDirect(userId)
      if (ok) return
    } catch {}
    if (driveAuthInvalid.value) {
      showToast('Google Drive auth invalid. Please reconnect in Drive Config.', 'error')
    }
    if (!isNetworkDown) {
      console.warn('Failed to load recent uploads', err)
    }
  }
}

async function loadWatchingTargetFolders() {
  const userId = JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
  if (!userId) return
  if (!shouldAttemptBackendNow()) {
    const cachedFolders = localStorage.getItem('ak_watched_folders_cache')
    if (cachedFolders) {
      try {
        watchedTargetFolders.value = JSON.parse(cachedFolders)
      } catch {
        watchedTargetFolders.value = []
      }
    }
    return
  }
  try {
    const { data } = await api.get(`/api/folders/?user_id=${userId}`)
    watchedTargetFolders.value = (data || [])
      .filter(f => f.drive_folder_id)
      .map(f => ({
        id: f.id,
        name: f.drive_folder_name || f.folder_name,
        driveFolderId: f.drive_folder_id || null,
      }))
    localStorage.setItem('ak_watched_folders_cache', JSON.stringify(watchedTargetFolders.value))
    if (
      selectedFolderId.value &&
      !watchedTargetFolders.value.some(f => String(f.id) === String(selectedFolderId.value))
    ) {
      selectedFolderId.value = ''
    }
  } catch {
    markBackendOffline()
    const cachedFolders = localStorage.getItem('ak_watched_folders_cache')
    if (cachedFolders) {
      try {
        watchedTargetFolders.value = JSON.parse(cachedFolders)
      } catch {
        watchedTargetFolders.value = []
      }
    } else {
      watchedTargetFolders.value = []
      selectedFolderId.value = ''
    }
  }
}

async function goNextPage() {
  if (!nextPageToken.value) return
  page.value += 1
  await loadRecentUploads()
}

async function goPrevPage() {
  if (page.value <= 1) return
  page.value -= 1
  await loadRecentUploads()
}

onMounted(async () => {
  // Fetch active studio user profile details
  try {
    currentUser.value = JSON.parse(localStorage.getItem('ak_user') || 'null')
  } catch (e) {
    console.error('Failed to parse user details from local storage:', e)
  }

  // Do not keep offline mode sticky forever across backend restarts.
  if (localStorage.getItem('ak_backend_offline') === '1') {
    const since = Number(localStorage.getItem('ak_backend_offline_since') || '0')
    if (!since || (Date.now() - since) >= BACKEND_RETRY_MS) {
      markBackendOnline()
    }
  }
  selectedFolderId.value = ''
  await loadWatchingTargetFolders()
  await loadRecentUploads()
  connectWebSocket()
  startPollingUploads()
  window.addEventListener('focus', loadRecentUploads)
  document.addEventListener('visibilitychange', handleVisibilityRefresh)
})

onUnmounted(() => {
  if (ws) ws.close()
  stopPollingUploads()
  for (const url of driveBlobCache.values()) URL.revokeObjectURL(url)
  driveBlobCache.clear()
  window.removeEventListener('focus', loadRecentUploads)
  document.removeEventListener('visibilitychange', handleVisibilityRefresh)
})

function handleVisibilityRefresh() {
  if (document.visibilityState === 'visible') {
    loadRecentUploads()
  }
}

// Reset pagination when folder changes
watch(selectedFolderId, () => {
  page.value = 1
  pageTokens.value = []
  nextPageToken.value = null
  loadRecentUploads()
})

// ═══════════════════════════════════════════════════════════════════
// ═══════════════ FACE SCAN FEATURE ═══════════════════════════════
// ═══════════════════════════════════════════════════════════════════

// State
const showFaceScanModal = ref(false)
const fsStep = ref('choose')         // choose | camera | preview | results
const fsCapturedImage = ref('')
const fsCapturedBlob = ref(null)
const fsFaceDetected = ref(false)
const fsBboxStyle = ref({})
const fsSearching = ref(false)
const fsResults = ref([])
const fsAllResults = ref([])          // unfiltered (for live threshold)
const fsSearchTime = ref(0)
const fsThreshold = ref(0.45)
const fsProgressPercent = ref(0)
const fsProgressText = ref('')
const fsProgressDetail = ref('')
const fsSelectedResult = ref(null)
const fsLoadedImages = ref(new Set())
let fsStream = null

// Refs
const fsCameraVideo = ref(null)
const fsSelfieInput = ref(null)
const fsDetailQrCanvas = ref(null)

// ── FAB / Modal open/close ────────────────────────────────────
function openFaceScan() {
  showFaceScanModal.value = true
  fsStep.value = 'choose'
  fsResults.value = []
  fsAllResults.value = []
  fsCapturedImage.value = ''
  fsCapturedBlob.value = null
  fsFaceDetected.value = false
  fsSearching.value = false
  fsSelectedResult.value = null
  fsLoadedImages.value = new Set()
  document.body.style.overflow = 'hidden'
}

function closeFaceScan() {
  stopCamera()
  showFaceScanModal.value = false
  fsSelectedResult.value = null
  document.body.style.overflow = ''
}

function closeFaceScanIfNotProcessing() {
  if (!fsSearching.value) closeFaceScan()
}

function resetFaceScan() {
  stopCamera()
  fsStep.value = 'choose'
  fsResults.value = []
  fsAllResults.value = []
  fsCapturedImage.value = ''
  fsCapturedBlob.value = null
  fsFaceDetected.value = false
  fsSearching.value = false
  fsSelectedResult.value = null
  fsLoadedImages.value = new Set()
}

// ── Camera ────────────────────────────────────────────────────
async function startCamera() {
  fsStep.value = 'camera'
  await nextTick()
  try {
    fsStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }
    })
    if (fsCameraVideo.value) {
      fsCameraVideo.value.srcObject = fsStream
    }
  } catch (err) {
    console.error('Camera access denied:', err)
    showToast('Camera access denied. Please allow camera permission.')
    fsStep.value = 'choose'
  }
}

function stopCamera() {
  if (fsStream) {
    fsStream.getTracks().forEach(t => t.stop())
    fsStream = null
  }
}

function capturePhoto() {
  if (!fsCameraVideo.value) return
  const video = fsCameraVideo.value
  const canvas = document.createElement('canvas')
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  // Mirror the image (selfie mode)
  ctx.translate(canvas.width, 0)
  ctx.scale(-1, 1)
  ctx.drawImage(video, 0, 0)
  fsCapturedImage.value = canvas.toDataURL('image/jpeg', 0.9)
  canvas.toBlob((blob) => {
    fsCapturedBlob.value = blob
  }, 'image/jpeg', 0.9)
  stopCamera()
  fsStep.value = 'preview'
  fsFaceDetected.value = false
}

// ── Upload ────────────────────────────────────────────────────
function triggerUpload() {
  if (fsSelfieInput.value) fsSelfieInput.value.click()
}

function onSelfieSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  fsCapturedBlob.value = file
  const reader = new FileReader()
  reader.onload = () => {
    fsCapturedImage.value = reader.result
    fsStep.value = 'preview'
    fsFaceDetected.value = false
  }
  reader.readAsDataURL(file)
  // Reset so same file can be re-selected
  e.target.value = ''
}

function retakePhoto() {
  fsCapturedImage.value = ''
  fsCapturedBlob.value = null
  fsFaceDetected.value = false
  fsStep.value = 'choose'
}

// ── Search ────────────────────────────────────────────────────
async function searchByFace() {
  if (!fsCapturedBlob.value && !fsCapturedImage.value) return
  const userId = JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
  if (!userId) {
    showToast('User session not found')
    return
  }

  fsSearching.value = true
  fsProgressPercent.value = 10
  fsProgressText.value = 'Detecting face'
  fsProgressDetail.value = 'Analyzing your photo...'

  try {
    let response

    // Animate progress
    const progressInterval = setInterval(() => {
      if (fsProgressPercent.value < 85) {
        fsProgressPercent.value += Math.random() * 8
        if (fsProgressPercent.value > 30 && fsProgressPercent.value < 60) {
          fsProgressText.value = 'Generating embedding'
          fsProgressDetail.value = 'Creating face signature...'
        } else if (fsProgressPercent.value >= 60) {
          fsProgressText.value = 'Searching photos'
          fsProgressDetail.value = 'Comparing across all folders...'
        }
      }
    }, 300)

    if (fsCapturedBlob.value instanceof Blob || fsCapturedBlob.value instanceof File) {
      // File upload method
      const formData = new FormData()
      formData.append('file', fsCapturedBlob.value, 'selfie.jpg')
      response = await api.post(
        `/api/face-search/search?user_id=${userId}&threshold=${fsThreshold.value}&limit=100`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 60000 }
      )
    } else {
      // Base64 method (camera capture)
      response = await api.post('/api/face-search/search-base64', {
        image_base64: fsCapturedImage.value,
        user_id: userId,
        threshold: fsThreshold.value,
        limit: 100,
      }, { timeout: 60000 })
    }

    clearInterval(progressInterval)
    fsProgressPercent.value = 100
    fsProgressText.value = 'Complete'
    fsProgressDetail.value = `Found ${response.data.total_matches} photos`

    const data = response.data
    fsSearchTime.value = data.search_time_ms || 0
    fsAllResults.value = data.matches || []
    fsResults.value = [...fsAllResults.value]
    fsFaceDetected.value = data.face_detected

    if (!data.face_detected) {
      showToast('No face detected in the photo. Try again with a clearer photo.')
    }

    await new Promise(r => setTimeout(r, 600))
    fsSearching.value = false
    fsStep.value = 'results'
  } catch (err) {
    console.error('Face search failed:', err)
    fsSearching.value = false
    showToast('Face search failed. Please try again.')
    fsStep.value = 'preview'
  }
}

// ── Threshold live re-filter ──────────────────────────────────
let thresholdDebounce = null
function onThresholdChange(e) {
  const newVal = Number(e.target.value) / 100
  fsThreshold.value = newVal
  if (thresholdDebounce) clearTimeout(thresholdDebounce)
  thresholdDebounce = setTimeout(async () => {
    // Re-filter from the full result set
    fsResults.value = fsAllResults.value.filter(r => r.similarity >= newVal)
  }, 150)
}

// ── Result image helpers (same pattern as gallery — from Drive) ─
function getFsResultThumbnail(res) {
  const data = res?.value || res
  if (!data) return ''
  if (data.drive_file_id) return getDriveThumbnailUrl(data.drive_file_id)
  if (data.thumbnail_url) return data.thumbnail_url
  return ''
}

function getFsResultFullImage(res) {
  const data = res?.value || res
  if (!data) return ''
  if (data.drive_file_id) return getDriveImageViewUrl(data.drive_file_id)
  if (data.public_link) return data.public_link
  return getFsResultThumbnail(data)
}

function isFsImageLoaded(res) {
  const data = res?.value || res
  return fsLoadedImages.value.has(data?.drive_file_id || data?.face_embedding_id)
}

function onFsImageLoad(res) {
  const data = res?.value || res
  if (data) {
    fsLoadedImages.value.add(data.drive_file_id || data.face_embedding_id)
  }
}

function getSimilarityClass(sim) {
  if (sim >= 0.7) return 'sim-high'
  if (sim >= 0.5) return 'sim-medium'
  return 'sim-low'
}

// ── Result detail modal with QR ───────────────────────────────
function openFsResultModal(res) {
  fsSelectedResult.value = res
  // Use a slight timeout (50ms) to ensure nested v-if canvas is fully mounted in the DOM
  setTimeout(() => {
    if (fsDetailQrCanvas.value) {
      const link = res.public_link || (res.drive_file_id ? getDriveImageViewUrl(res.drive_file_id) : '')
      if (link) {
        QRCode.toCanvas(fsDetailQrCanvas.value, link, {
          width: 180, margin: 2,
          color: { dark: '#111827', light: '#ffffff' }
        }, (err) => { if (err) console.error(err) })
      }
    }
  }, 50)
}

// ── Cleanup on unmount ────────────────────────────────────────
onUnmounted(() => {
  stopCamera()
})
</script>


<style scoped>
/* =================================================================== */
/* AK Lumora — Premium Scoped Glassmorphic Dark UI & Pipeline Conveyor */
/* =================================================================== */

.live-page {
  --page-pad: clamp(16px, 2.5vw, 36px);
  --panel-gap: clamp(16px, 2vw, 28px);
  --card-pad: clamp(16px, 1.8vw, 26px);
  --radius-xl: clamp(16px, 1.6vw, 24px);
  padding: var(--page-pad);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: var(--font-primary);
  min-height: 100vh;
  max-width: 1800px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
}

/* ─── Ambient Glow Flares ─── */
.ambient-glows {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.flare {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.18;
}

.flare-1 {
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  top: -10%;
  right: 5%;
  animation: orbFloat 18s ease-in-out infinite;
}

.flare-2 {
  width: 400px;
  height: 400px;
  background: var(--color-secondary);
  bottom: -5%;
  left: 2%;
  animation: orbFloat 24s ease-in-out infinite reverse;
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-40px) scale(1.1); }
}

/* ─── Animations ─── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}
@keyframes pulseRing {
  0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
  70% { transform: scale(1.1); opacity: 0; box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
  100% { transform: scale(0.95); opacity: 0; }
}
@keyframes glowPulse {
  0%, 100% { box-shadow: var(--shadow-glow); border-color: var(--border-glow); }
  50% { box-shadow: 0 0 35px rgba(108, 99, 255, 0.35); border-color: rgba(108, 99, 255, 0.5); }
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ─── Premium Glass Topbar ─── */
.topbar.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px 28px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--panel-gap);
  flex-wrap: wrap;
  gap: 16px;
  z-index: 10;
  position: relative;
  box-shadow: var(--shadow-lg);
}

.topbar-left h2 {
  font-family: var(--font-display);
  font-size: 1.8rem;
  font-weight: 800;
  letter-spacing: var(--tracking-tight);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background-color: var(--color-success);
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 12px var(--color-success);
}

.gradient-text-branding {
  background: linear-gradient(135deg, #FFF 30%, var(--color-primary-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.topbar-left p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 4px 0 0;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  appearance: none;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  padding: 10px 36px 10px 18px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
  outline: none;
}

.select-wrapper select option {
  background-color: #111127;
  color: #f8fafc;
}

.select-wrapper::after {
  content: '▼';
  font-size: 0.7rem;
  color: var(--text-secondary);
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
}

.select-wrapper select:hover, .select-wrapper select:focus {
  border-color: var(--color-primary);
  background: rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow-glow);
}

.watching-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--color-success);
  font-weight: 700;
  background: rgba(16, 185, 129, 0.08);
  padding: 10px 18px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(16, 185, 129, 0.15);
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.05);
}

.watching-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-success);
  position: relative;
}
.watching-dot::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid var(--color-success);
  animation: pulseRing 1.8s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

.count-badge {
  font-size: 0.8rem;
  color: var(--text-primary);
  background: var(--bg-glass-strong);
  border: 1px solid var(--border-subtle);
  padding: 10px 18px;
  border-radius: var(--radius-full);
  font-weight: 700;
}

/* ═══════════ LIVE DRIVE Sync Pipeline Conveyor Card ═══════════ */
.sync-pipeline-card {
  position: relative;
  background: var(--bg-card);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px 24px;
  margin-bottom: var(--panel-gap);
  transition: all var(--transition-slow);
  z-index: 10;
  box-shadow: var(--shadow-md);
}

.sync-pipeline-card.is-active {
  border-color: rgba(108, 99, 255, 0.25);
  background: rgba(255, 255, 255, 0.02);
  box-shadow: var(--shadow-glow);
}

.pipeline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.pipeline-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pulse-ring {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--text-tertiary);
  position: relative;
  transition: background var(--transition-normal);
}
.pulse-ring.pulsing {
  background: var(--color-success);
}
.pulse-ring.pulsing::after {
  content: '';
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 2px solid var(--color-success);
  animation: pulseRing 2s cubic-bezier(0.24, 0, 0.38, 1) infinite;
}

.pipeline-icon {
  width: 20px;
  height: 20px;
  color: var(--color-primary-light);
}

.pipeline-title h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  font-family: var(--font-display);
  letter-spacing: var(--tracking-wide);
  color: var(--text-primary);
}

.status-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border: 1px solid transparent;
}
.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
  border-color: rgba(16, 185, 129, 0.2);
}
.status-badge.idle {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-tertiary);
  border-color: var(--border-subtle);
}

.pipeline-body {
  display: flex;
  align-items: center;
  gap: 20px;
  justify-content: space-between;
}

.node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.node-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-subtle);
  transition: all var(--transition-normal);
}

.drive-brand {
  background: rgba(255, 255, 255, 0.03);
  color: var(--color-accent);
}
.studio-brand {
  background: rgba(108, 99, 255, 0.06);
  color: var(--color-primary-light);
}

.sync-pipeline-card.is-active .node-icon {
  border-color: var(--border-strong);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.svg-drive {
  width: 26px;
  height: 26px;
}

.node-icon svg:not(.svg-drive) {
  width: 24px;
  height: 24px;
}

.node-label {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.pipeline-flow {
  flex: 1;
  height: 36px;
  position: relative;
}

.flow-track {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  height: 6px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-subtle);
  overflow: visible;
}

/* Conveyor dot flow animation */
.flow-particles {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: space-around;
  overflow: hidden;
}

.particle {
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--color-success), 0 0 16px var(--color-success);
  opacity: 0;
}

.flow-particles.animating .particle {
  animation: conveyorFlow 2.8s infinite linear;
}

.particle.p-1 { animation-delay: 0s; }
.particle.p-2 { animation-delay: 0.5s; }
.particle.p-3 { animation-delay: 1s; }
.particle.p-4 { animation-delay: 1.5s; }
.particle.p-5 { animation-delay: 2s; }

@keyframes conveyorFlow {
  0% { transform: translateX(-80px); opacity: 0; }
  15% { opacity: 1; }
  85% { opacity: 1; }
  100% { transform: translateX(380px); opacity: 0; }
}

/* ═══════════ LIVE DRIVE Sync Queue List Styles ═══════════ */
.sync-queue-container {
  width: 100%;
  margin-top: 12px;
  display: flex;
  flex-direction: column;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.queue-item {
  border-radius: var(--radius-md);
  padding: 12px 16px;
  border: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all var(--transition-normal);
  background: rgba(255, 255, 255, 0.01);
  box-shadow: var(--shadow-sm);
}

.queue-item:hover {
  border-color: rgba(108, 99, 255, 0.15);
  background: rgba(255, 255, 255, 0.025);
}

.queue-item.completed {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.015);
}

.queue-item.failed {
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.015);
}

.queue-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-item-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.queue-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
}

.icon-success {
  color: var(--color-success);
  font-weight: 700;
  font-size: 0.95rem;
}

.icon-failed {
  color: #ef4444;
  font-weight: 700;
  font-size: 0.95rem;
}

.spinner-tiny {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.queue-item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.queue-item-name {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--text-primary);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.queue-item-size {
  font-size: 0.65rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.queue-item-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stage-badge {
  font-size: 0.62rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stage-badge.detected {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.stage-badge.analyzing {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.stage-badge.compressing {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.stage-badge.resuming {
  background: rgba(234, 179, 8, 0.1);
  color: #eab308;
}

.stage-badge.uploading {
  background: rgba(6, 182, 212, 0.1);
  color: #06b6d4;
}

.stage-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.stage-badge.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.percentage-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary);
  min-width: 30px;
  text-align: right;
}

.queue-progress-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-full);
  overflow: hidden;
  position: relative;
}

.queue-progress-bar {
  height: 100%;
  width: 0;
  border-radius: var(--radius-full);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: var(--color-primary);
}

.queue-progress-bar.analyzing {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
}

.queue-progress-bar.compressing {
  background: linear-gradient(90deg, #8b5cf6, #a78bfa);
}

.queue-progress-bar.resuming {
  background: linear-gradient(90deg, #eab308, #fde047);
}

.queue-progress-bar.uploading {
  background: linear-gradient(90deg, #06b6d4, #67e8f9);
  animation: progressGlow 1.2s ease-in-out infinite alternate;
}

.queue-progress-bar.completed {
  background: var(--color-success);
}

.queue-progress-bar.failed {
  background: #ef4444;
}

.queue-counter-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  background: rgba(108, 99, 255, 0.08);
  color: var(--color-primary-light);
  border: 1px solid rgba(108, 99, 255, 0.15);
}

/* Transitions */
.queue-list-enter-active,
.queue-list-leave-active {
  transition: all 0.4s cubic-bezier(0.55, 0, 0.1, 1);
}

.queue-list-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.queue-list-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-15px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes progressGlow {
  0% { box-shadow: 0 0 2px rgba(6, 182, 212, 0.2); }
  100% { box-shadow: 0 0 6px rgba(6, 182, 212, 0.5); }
}

/* ─── Dashboard Grid ─── */
.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
  gap: var(--panel-gap);
  align-items: start;
  position: relative;
  z-index: 5;
}

.dashboard-left, .dashboard-right {
  display: flex;
  flex-direction: column;
  gap: var(--panel-gap);
}

.dashboard-right {
  position: sticky;
  top: 24px;
}

/* Glassmorphism Card Style */
.card, .gallery-section-full, .empty-gallery {
  background: var(--bg-card);
  backdrop-filter: blur(var(--glass-blur));
  -webkit-backdrop-filter: blur(var(--glass-blur));
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--card-pad);
  transition: transform var(--transition-normal), border-color var(--transition-normal), box-shadow var(--transition-normal), background var(--transition-normal);
  box-shadow: var(--shadow-md);
}

.card:hover, .gallery-section-full:hover {
  border-color: var(--border-glow);
  box-shadow: var(--shadow-glow);
  background: var(--bg-card-hover);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.card-header h3 {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--color-success);
  background: rgba(16, 185, 129, 0.1);
  padding: 4px 10px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(16, 185, 129, 0.2);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ─── Compact Live Preview Card ─── */
.live-preview-card {
  padding: var(--card-pad);
}

.live-preview-card.is-watching {
  animation: glowPulse 4s infinite ease-in-out;
}

.live-image-wrap {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  aspect-ratio: 16/10;
  max-height: min(34vh, 340px); /* reduced as requested */
  cursor: pointer;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
}

.live-image-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.8s cubic-bezier(0.25, 1, 0.5, 1);
}

.img-hidden {
  opacity: 0;
}

.img-skeleton {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(255,255,255,0.03) 20%, rgba(255,255,255,0.08) 45%, rgba(255,255,255,0.03) 70%);
  background-size: 220% 100%;
  animation: shimmer 1.5s infinite linear;
}

.live-image-wrap:hover img {
  transform: scale(1.05);
}

.live-overlay {
  position: absolute;
  inset: 0;
  background: rgba(10, 10, 26, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity var(--transition-normal) ease;
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.9rem;
  backdrop-filter: blur(4px);
}

.live-image-wrap:hover .live-overlay {
  opacity: 1;
}

.live-meta {
  margin-top: 16px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.meta-name {
  font-weight: 700;
  color: var(--text-primary);
}

.meta-dot {
  opacity: 0.3;
}

/* ─── Recent Photos Grid ─── */
.recent-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.recent-thumb {
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  cursor: pointer;
  position: relative;
  background: var(--bg-secondary);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-subtle);
  transition: transform var(--transition-spring), border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.recent-thumb:hover {
  transform: translateY(-4px) scale(1.03);
  border-color: rgba(108, 99, 255, 0.3);
  box-shadow: var(--shadow-glow);
}

.recent-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}

.recent-thumb:hover img {
  transform: scale(1.08);
}

.empty-recent {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px var(--space-md);
  color: var(--text-tertiary);
  font-size: 0.85rem;
}

/* ─── Gallery Section ─── */
.gallery-section-full {
  margin-top: 4px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.section-header h3 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(clamp(130px, 14vw, 190px), 1fr));
  gap: clamp(12px, 1.5vw, 20px);
}

.gallery-card {
  background: rgba(255, 255, 255, 0.02);
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 1px solid var(--border-subtle);
  animation: fadeInUp 0.5s ease both;
}

.gallery-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: var(--shadow-glow);
  border-color: var(--border-glow);
  background: rgba(255, 255, 255, 0.04);
}

.gallery-img-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.gallery-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s ease;
}

.gallery-card:hover .gallery-img-wrap img {
  transform: scale(1.08);
}

.gallery-info {
  padding: 12px 14px;
}

.gallery-name {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.gallery-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.folder-badge {
  background: rgba(108, 99, 255, 0.12);
  color: var(--color-primary-light);
  border: 1px solid rgba(108, 99, 255, 0.2);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.empty-gallery {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  background: var(--bg-card);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
  filter: drop-shadow(0 0 15px rgba(108, 99, 255, 0.3));
}

/* ─── Pagination Buttons ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  border: 1px solid transparent;
  outline: none;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--color-primary);
  box-shadow: var(--shadow-glow);
}

.btn-secondary:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 0.8rem;
}

.page-info {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
}

/* ─── Light/Dark Modal System ─── */
.modal {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal.active {
  display: flex;
}

.modal-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(3, 3, 10, 0.65);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  animation: fadeInUp 0.3s ease;
}

.modal-content {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  max-width: 960px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 1001;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
  font-size: 1.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
  z-index: 10;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  transform: rotate(90deg);
}

.modal-body {
  display: flex;
  flex-direction: row;
  overflow: auto;
  min-height: 0;
}

.modal-image-section {
  flex: 1.2;
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28px;
  min-height: 320px;
  border-right: 1px solid var(--border-subtle);
}

.modal-image-section img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  object-fit: contain;
}

.modal-info-section {
  flex: 0.8;
  padding: 36px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-width: 300px;
}

.modal-title {
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  word-break: break-word;
}

.modal-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.82rem;
  color: var(--text-secondary);
  align-items: center;
}

.modal-badge {
  background: rgba(108, 99, 255, 0.15);
  color: var(--color-primary-light);
  border: 1px solid rgba(108, 99, 255, 0.25);
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 0.7rem;
  text-transform: uppercase;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

/* Keep QR Code strictly white and high-contrast for phone scans */
.qr-section, .fs-detail-qr {
  background: #FFFFFF !important;
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5), 0 0 25px rgba(108, 99, 255, 0.2);
  min-width: 210px;
  min-height: 210px;
  justify-content: center;
}

.qr-label {
  color: #111827 !important;
  font-weight: 700;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.qr-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(108, 99, 255, 0.15);
  border-top-color: var(--color-primary-light);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.qr-loading span {
  color: #6b7280;
  font-size: 0.875rem;
  text-align: center;
}

.qr-details canvas {
  border-radius: 8px;
  max-width: 100%;
}

/* ─── Toast System ─── */
.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #111127;
  color: white;
  border: 1px solid var(--border-glow);
  padding: 14px 24px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 20px 50px rgba(0,0,0,0.5), 0 0 20px rgba(108, 99, 255, 0.25);
  transform: translateY(120px);
  opacity: 0;
  transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 3000;
  pointer-events: none;
  max-width: 340px;
}

.toast.show {
  transform: translateY(0);
  opacity: 1;
}

/* ─── Responsive Media Adaptations ─── */

/* ─── Wide Displays ─── */
@media (min-width: 1600px) {
  .dashboard-grid {
    grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.75fr);
  }
  .live-image-wrap {
    max-height: min(32vh, 340px);
  }
}

/* ─── Tablet / Small Laptop ─── */
@media (max-width: 1100px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .dashboard-right {
    position: static;
  }
  .dashboard-right .card {
    order: -1;
  }
  .recent-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .live-image-wrap {
    max-height: min(34vh, 320px);
  }
  .modal-body {
    flex-direction: column;
  }
  .modal-image-section {
    min-height: 220px;
    border-right: none;
    border-bottom: 1px solid var(--border-subtle);
  }
  .modal-info-section {
    min-width: auto;
    padding: 24px;
  }
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 14px;
  }
}

/* ─── Phones ─── */
@media (max-width: 640px) {
  .topbar.glass-card {
    flex-direction: column;
    align-items: flex-start;
    padding: 16px 20px;
  }
  .topbar-right {
    width: 100%;
    gap: 12px;
  }
  .select-wrapper, .select-wrapper select {
    width: 100%;
  }
  .watching-indicator, .count-badge {
    font-size: 0.75rem;
    padding: 8px 14px;
  }
  .live-image-wrap {
    aspect-ratio: 4 / 3;
    max-height: 28vh;
  }
  .recent-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .gallery-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .live-meta {
    font-size: 0.78rem;
    gap: 8px;
  }
  .meta-dot:nth-of-type(2),
  .meta-dot:nth-of-type(3) {
    display: none;
  }
  
  .pipeline-body {
    flex-direction: column;
    gap: 14px;
    align-items: stretch;
  }
  .pipeline-flow {
    height: 12px;
  }
  .flow-track {
    top: 50%;
    transform: translateY(-50%);
  }
  .flow-particles.animating .particle {
    animation: conveyorFlowMobile 2.5s infinite linear;
  }
  @keyframes conveyorFlowMobile {
    0% { transform: translateX(-50px); opacity: 0; }
    20% { opacity: 1; }
    80% { opacity: 1; }
    100% { transform: translateX(200px); opacity: 0; }
  }
  .flow-file-bubble {
    padding: 6px 12px;
  }
  .bubble-meta {
    max-width: 100px;
  }
}

/* ─── Portrait Kiosk / Vertical Displays ─── */
@media (orientation: portrait) and (min-width: 700px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  .dashboard-right {
    position: static;
  }
  .recent-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  .live-image-wrap {
    aspect-ratio: 16/9;
    max-height: min(34vh, 320px);
  }
}

/* =================================================================== */
/* ═════════════════════  FACE SCAN STYLES  ═════════════════════════ */
/* =================================================================== */

/* ─── FAB Button ─── */
.face-scan-fab {
  position: fixed;
  bottom: 90px;
  right: 28px;
  z-index: 2500;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 24px;
  border: none;
  border-radius: 50px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  box-shadow:
    0 8px 32px rgba(108, 99, 255, 0.35),
    0 0 0 0 rgba(108, 99, 255, 0.4);
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: fabPulse 3s ease-in-out infinite;
}

.face-scan-fab:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 12px 40px rgba(108, 99, 255, 0.45);
}

.face-scan-fab.fab-hidden {
  transform: translateY(200px);
  opacity: 0;
  pointer-events: none;
}

.fab-icon {
  width: 22px;
  height: 22px;
}

.fab-label {
  white-space: nowrap;
}

.fab-pulse {
  position: absolute;
  inset: -4px;
  border-radius: 50px;
  border: 2px solid rgba(108, 99, 255, 0.5);
  animation: fabRingPulse 2.5s ease-out infinite;
  pointer-events: none;
}

@keyframes fabPulse {
  0%, 100% { box-shadow: 0 8px 32px rgba(108, 99, 255, 0.3), 0 0 0 0 rgba(108, 99, 255, 0.25); }
  50% { box-shadow: 0 8px 32px rgba(108, 99, 255, 0.3), 0 0 0 12px rgba(108, 99, 255, 0); }
}

@keyframes fabRingPulse {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(1.15); opacity: 0; }
}

/* ─── Modal Shell & Backdrops ─── */
.fs-overlay {
  position: fixed;
  inset: 0;
  z-index: 5000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(3, 3, 10, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  animation: fadeInUp 0.25s ease;
  padding: 16px;
}

.fs-modal {
  position: relative;
  width: 100%;
  max-width: 520px;
  max-height: 92vh;
  overflow-y: auto;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.5);
  animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fs-close {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  transition: all var(--transition-normal);
}

.fs-close svg {
  width: 18px;
  height: 18px;
  color: var(--text-secondary);
}
.fs-close:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: rotate(90deg);
}

.fs-close svg line {
  stroke: var(--text-primary);
}

.fs-hidden-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* ─── Step 1: Choose Method ─── */
.fs-step {
  padding: 36px 32px;
}

.fs-header {
  text-align: center;
  margin-bottom: 32px;
}

.fs-header-icon {
  width: 76px;
  height: 76px;
  margin: 0 auto 16px;
}

.fs-header-icon svg {
  width: 100%;
  height: 100%;
}

.fs-header h2 {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 8px;
}

.fs-header p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin: 0;
}

.fs-options {
  display: flex;
  gap: 16px;
}

.fs-option-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 28px 18px;
  border: 1.5px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.02);
  cursor: pointer;
  transition: all var(--transition-spring);
}

.fs-option-btn:hover {
  border-color: var(--color-primary);
  background: rgba(108, 99, 255, 0.08);
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

.fs-option-icon {
  width: 46px;
  height: 46px;
  color: var(--color-primary-light);
}

.fs-option-icon svg {
  width: 100%;
  height: 100%;
}

.fs-option-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}

.fs-option-desc {
  font-size: 0.76rem;
  color: var(--text-tertiary);
  text-align: center;
  line-height: 1.4;
}

/* ─── Step 2: Live Camera ─── */
.fs-step-camera {
  padding: 0;
}

.fs-camera-container {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  max-height: 70vh;
  background: #000;
  border-radius: 24px;
  overflow: hidden;
}

.fs-camera-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1);
}

.fs-camera-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.fs-face-guide {
  width: 58%;
  aspect-ratio: 3/4;
  border: 3px dashed rgba(255, 255, 255, 0.25);
  border-radius: 50%;
  animation: faceGuidePulse 2.2s ease-in-out infinite;
}

@keyframes faceGuidePulse {
  0%, 100% { border-color: rgba(255, 255, 255, 0.2); transform: scale(1); }
  50% { border-color: var(--color-primary-light); transform: scale(1.03); }
}

.fs-camera-controls {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
}

.fs-cam-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all var(--transition-normal);
}

.fs-cam-btn svg {
  width: 24px;
  height: 24px;
}
.fs-cam-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.fs-cam-capture {
  width: 76px;
  height: 76px;
  background: rgba(255, 255, 255, 0.2);
  border: 4px solid white;
}

.fs-shutter-ring {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: white;
  transition: transform 0.15s ease;
}

.fs-cam-capture:hover .fs-shutter-ring { transform: scale(0.9); }
.fs-cam-capture:active .fs-shutter-ring { transform: scale(0.85); }

/* ─── Step 3: Selfie Preview ─── */
.fs-step-preview {
  text-align: center;
}

.fs-preview-wrap {
  position: relative;
  display: inline-block;
  max-width: 100%;
  margin-bottom: 24px;
}

.fs-preview-img {
  max-width: 100%;
  max-height: 45vh;
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  border: 1px solid var(--border-subtle);
}

.fs-face-bbox {
  position: absolute;
  border: 2px solid var(--color-success);
  border-radius: 8px;
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
  animation: bboxPulse 1.5s ease-in-out infinite;
}

@keyframes bboxPulse {
  0%, 100% { box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
  50% { box-shadow: 0 0 24px rgba(16, 185, 129, 0.8); }
}

.fs-preview-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.fs-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: none;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.fs-action-btn svg {
  width: 18px;
  height: 18px;
}

.fs-retake {
  background: var(--bg-glass-strong);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
}

.fs-retake:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: var(--border-strong);
}

.fs-search {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  box-shadow: 0 6px 20px rgba(108, 99, 255, 0.35);
}

.fs-search:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(108, 99, 255, 0.45);
}

/* ─── Search Progress Card ─── */
.fs-progress-overlay {
  position: absolute;
  inset: 0;
  z-index: 5010;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(10, 10, 26, 0.85);
  backdrop-filter: blur(10px);
  border-radius: 24px;
}

.fs-progress-card {
  text-align: center;
  padding: 36px;
  animation: scaleIn 0.3s ease;
}

.fs-progress-icon {
  width: 68px;
  height: 68px;
  margin: 0 auto 20px;
}

.fs-scan-anim {
  width: 100%;
  height: 100%;
}

.fs-progress-text {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
  letter-spacing: var(--tracking-wide);
}

.fs-progress-bar-wrap {
  width: 250px;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.08);
  margin: 0 auto 16px;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}

.fs-progress-bar {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-success));
  transition: width 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.fs-progress-detail {
  font-size: 0.82rem;
  color: var(--text-secondary);
}

/* ─── Step 4: Search Results ─── */
.fs-step-results {
  padding: 26px 26px 20px;
}

.fs-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.fs-results-header h3 {
  font-family: var(--font-display);
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
}

.fs-search-time {
  font-size: 0.78rem;
  color: var(--text-secondary);
  background: var(--bg-glass-strong);
  border: 1px solid var(--border-subtle);
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 700;
}

/* Threshold slider component */
.fs-threshold-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
}

.fs-threshold-label {
  font-size: 0.82rem;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 115px;
}

.fs-threshold-slider {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(90deg, var(--color-error), var(--color-warning), var(--color-success));
  outline: none;
  cursor: pointer;
}

.fs-threshold-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  border: 3.5px solid var(--color-primary);
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.fs-threshold-slider::-webkit-slider-thumb:hover {
  transform: scale(1.25);
}

/* Results photo grid */
.fs-results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 14px;
  max-height: 48vh;
  overflow-y: auto;
  padding-right: 6px;
}

.fs-result-card {
  border-radius: var(--radius-md);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all var(--transition-normal);
  animation: fadeInUp 0.4s ease both;
}

.fs-result-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-glow);
  border-color: rgba(108, 99, 255, 0.25);
  background: rgba(255, 255, 255, 0.04);
}

.fs-result-img-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-subtle);
}

.fs-result-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.fs-result-card:hover .fs-result-img-wrap img { transform: scale(1.08); }

.fs-similarity-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.68rem;
  font-weight: 800;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  letter-spacing: 0.3px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
}

.sim-high { background: rgba(16, 185, 129, 0.88); color: white; }
.sim-medium { background: rgba(245, 158, 11, 0.88); color: #000; }
.sim-low { background: rgba(239, 68, 68, 0.8); color: white; }

.fs-result-info {
  padding: 10px;
}

.fs-result-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.fs-result-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.fs-no-results {
  text-align: center;
  padding: 50px 20px;
  color: var(--text-secondary);
}

.fs-no-results p {
  margin-top: 14px;
  font-size: 0.85rem;
}

.fs-results-actions {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}

/* ─── Nested Result Detail Overlay ─── */
.fs-detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 5020;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(3, 3, 10, 0.7);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 20px;
}

.fs-detail-card {
  position: relative;
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: 20px;
  max-width: 700px;
  width: 100%;
  max-height: 85vh;
  overflow: auto;
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.6);
  animation: scaleIn 0.25s ease;
  display: flex;
  flex-direction: column;
}

.fs-detail-close {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
}

.fs-detail-img {
  background: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.fs-detail-img img {
  max-width: 100%;
  max-height: 50vh;
  border-radius: 12px;
  object-fit: contain;
  box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}

.fs-detail-info {
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.fs-detail-name {
  font-family: var(--font-display);
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  word-break: break-word;
  text-align: center;
}

.fs-detail-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* ─── Adaptive Responsive Rules ─── */
@media (max-width: 640px) {
  .face-scan-fab {
    bottom: 76px;
    right: 16px;
    padding: 12px 20px;
    font-size: 0.82rem;
  }
  .fs-modal { max-width: 100%; border-radius: 18px; }
  .fs-options { flex-direction: column; }
  .fs-step { padding: 28px 20px; }
  .fs-results-grid { grid-template-columns: repeat(2, 1fr); }
  .fs-camera-container { aspect-ratio: 3/4; max-height: 80vh; border-radius: 18px; }
  .fs-detail-card { max-width: 100%; border-radius: 16px; }
}

/* ─── Studio Profile Trigger & Modal ─── */
.studio-trigger-title {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}
.studio-trigger-title:hover {
  opacity: 0.95;
  transform: translateY(-1px);
}

.studio-glow-text {
  animation: studioTitleGlow 3.5s ease-in-out infinite;
}

@keyframes studioTitleGlow {
  0%, 100% {
    text-shadow: 0 0 10px rgba(108, 99, 255, 0.1), 0 0 20px rgba(0, 210, 255, 0.05);
  }
  50% {
    text-shadow: 0 0 15px rgba(108, 99, 255, 0.4), 0 0 30px rgba(0, 210, 255, 0.25), 0 0 45px rgba(108, 99, 255, 0.15);
  }
}

/* ─── Studio Details Overlay ─── */
.studio-details-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(3, 3, 10, 0.7);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  padding: 20px;
}

.studio-details-card {
  width: 100%;
  max-width: 520px;
  background: rgba(10, 10, 26, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  position: relative;
  animation: scaleIn 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  overflow: hidden;
  box-shadow:
    0 25px 60px rgba(0, 0, 0, 0.55),
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 0 40px rgba(108, 99, 255, 0.06);
}

.studio-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.studio-close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.15);
}

.studio-details-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 32px 28px 16px;
  scrollbar-width: thin;
  scrollbar-color: rgba(108, 99, 255, 0.2) transparent;
}

.studio-details-scroll::-webkit-scrollbar {
  width: 5px;
}

.studio-details-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.studio-details-scroll::-webkit-scrollbar-thumb {
  background: rgba(108, 99, 255, 0.2);
  border-radius: 10px;
}

/* ─── Profile Header ─── */
.studio-profile-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 22px;
  margin-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.studio-avatar-ring {
  padding: 3px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.5), rgba(0, 210, 255, 0.4));
  margin-bottom: 14px;
}

.studio-avatar-large {
  width: 82px;
  height: 82px;
  border-radius: 50%;
  overflow: hidden;
  background: rgba(10, 10, 26, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.studio-avatar-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.studio-initial-large {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 800;
  color: var(--color-primary-light);
  text-shadow: 0 0 10px rgba(108, 99, 255, 0.3);
}

.studio-brand-title {
  font-size: 1.4rem;
  font-weight: 800;
  margin-bottom: 4px;
  letter-spacing: -0.02em;
}

.studio-brand-subtitle {
  font-size: 10px;
  color: var(--text-tertiary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.7;
}

/* ─── Sections ─── */
.studio-section {
  padding: 18px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.studio-section:last-child {
  border-bottom: none;
  padding-bottom: 8px;
}

.studio-section-title {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-tertiary);
  margin-bottom: 14px;
  opacity: 0.75;
}

/* ─── Contact Info Grid (2-col) ─── */
.studio-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.studio-info-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  transition: background var(--transition-fast);
}

.studio-info-item:hover {
  background: rgba(255, 255, 255, 0.03);
}

.studio-info-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(108, 99, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
  margin-top: 1px;
}

.studio-info-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.studio-info-label {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
  opacity: 0.65;
}

.studio-info-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  word-break: break-word;
}

.studio-info-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ─── Website Row ─── */
.studio-website-row {
  margin-bottom: 12px;
}

.studio-website-btn {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(108, 99, 255, 0.06);
  border: 1px solid rgba(108, 99, 255, 0.2);
  border-radius: 12px;
  color: var(--color-primary-light);
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s ease;
}

.studio-website-btn:hover {
  background: rgba(108, 99, 255, 0.14);
  border-color: rgba(108, 99, 255, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(108, 99, 255, 0.12);
}

.studio-website-btn-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.studio-website-btn-left span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.studio-website-btn svg:last-child {
  flex-shrink: 0;
  opacity: 0.6;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.studio-website-btn:hover svg:last-child {
  opacity: 1;
  transform: translate(1px, -1px);
}

/* ─── Address Row ─── */
.studio-address-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.015);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: 12px;
}

/* ─── Social QR Grid ─── */
.studio-social-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.studio-social-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.25s ease;
}

.studio-social-card:hover {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.studio-social-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
}

.studio-social-badge span {
  color: var(--text-secondary);
}

.studio-qr-box {
  width: 110px;
  height: 110px;
  padding: 8px;
  background: white;
  border-radius: 14px;
  box-shadow:
    0 4px 16px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.studio-qr-box img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  image-rendering: pixelated;
}

.studio-social-handle {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-decoration: none;
  transition: color 0.2s ease;
  text-align: center;
  max-width: 100%;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 0 4px;
}

.studio-social-handle:hover {
  color: var(--color-primary-light);
}

/* ─── Footer ─── */
.studio-profile-footer {
  padding: 16px 28px 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.04);
  flex-shrink: 0;
}

.btn-full {
  width: 100%;
}

/* ─── Mobile Responsive ─── */
@media (max-width: 520px) {
  .studio-details-card {
    max-width: 100%;
    border-radius: 20px;
  }
  
  .studio-details-scroll {
    padding: 24px 20px 12px;
  }

  .studio-info-grid {
    grid-template-columns: 1fr;
  }

  .studio-social-grid {
    grid-template-columns: 1fr 1fr;
  }

  .studio-profile-footer {
    padding: 14px 20px 20px;
  }
}

@media (max-width: 360px) {
  .studio-social-grid {
    grid-template-columns: 1fr;
  }
}
</style>

