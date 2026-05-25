<template>
  <div class="dashboard">
    <!-- Sidebar -->
    <aside class="sidebar glass" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="brand" @click="sidebarCollapsed = !sidebarCollapsed">
          <img src="/logo.png" alt="AK Lumora Logo" style="width: 36px; height: 36px; object-fit: contain; filter: drop-shadow(0 4px 10px rgba(108, 99, 255, 0.2));">
          <span v-if="!sidebarCollapsed" class="brand-text">AK <span class="gradient-text">Lumora</span></span>
        </div>
      </div>
      <nav class="sidebar-nav">
        <button v-for="item in menuItems" :key="item.id" :class="['nav-item', { active: activeMenu === item.id }]" @click="setActiveMenu(item.id)">
          <span class="nav-icon" v-html="item.icon"></span>
          <span v-if="!sidebarCollapsed" class="nav-label">{{ item.label }}</span>
        </button>
      </nav>
      <div class="sidebar-footer">
        <button class="nav-item" @click="handleLogout">
          <span class="nav-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg></span>
          <span v-if="!sidebarCollapsed" class="nav-label">Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar -->
      <header class="topbar glass">
        <div class="topbar-left">
          <h1 class="page-title">{{ currentTitle }}</h1>
          <p class="studio-name">{{ authStore.user?.studio_name || 'Studio' }}</p>
        </div>
        <div class="topbar-right">
          <button class="btn btn-accent btn-sm ripple" @click="openLivePresentation" v-if="folders.length > 0">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            Live Studio
          </button>
          <div class="user-avatar">
            <img 
              v-if="authStore.user?.profile_image && !imageLoadError" 
              :src="resolveLogoUrl(authStore.user.profile_image)" 
              alt="avatar"
              @error="imageLoadError = true"
            />
            <span v-else class="avatar-initial">{{ (authStore.user?.email || 'U')[0].toUpperCase() }}</span>
          </div>
        </div>
      </header>

      <!-- Dashboard Content -->
      <div class="content-area">
        <!-- Stats Cards -->
        <div class="stats-grid" v-if="activeMenu === 'dashboard'">
          <div v-for="stat in statsCards" :key="stat.label" class="stat-card glass-card">
            <div class="stat-icon" :style="{ background: stat.bg }"><span v-html="stat.icon"></span></div>
            <div class="stat-info">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>

        <!-- Charts -->
        <div class="charts-row" v-if="activeMenu === 'dashboard'">
          <div class="chart-card glass-card">
            <h3>Upload Activity</h3>
            <div class="chart-placeholder"><canvas ref="uploadChart"></canvas></div>
          </div>
          <div class="chart-card glass-card">
            <h3>Status Overview</h3>
            <div class="chart-placeholder"><canvas ref="statusChart"></canvas></div>
          </div>
        </div>

        <!-- Date Filter -->
        <div class="filter-bar glass" v-if="activeMenu === 'dashboard'">
          <div class="filter-group">
            <label>From</label>
            <input type="datetime-local" v-model="filterFrom" class="input input-neu" />
          </div>
          <div class="filter-group">
            <label>To</label>
            <input type="datetime-local" v-model="filterTo" class="input input-neu" />
          </div>
          <button class="btn btn-primary btn-sm" @click="refreshStats">Apply Filter</button>
        </div>

        <!-- Folders Section -->
        <div v-if="activeMenu === 'folders'" class="folders-section">
          <div class="section-bar flex-between">
            <h3>Monitored Folders ({{ folders.length }}/20)</h3>
            <button class="btn btn-primary btn-sm" @click="addFolder" :disabled="folders.length >= 20">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              Add Folder
            </button>
          </div>

          <!-- Browser support warning -->
          <div v-if="!isFSASupported" class="alert alert-warning glass-card" style="margin-bottom: var(--space-lg); padding: var(--space-md) var(--space-lg); border-left: 3px solid var(--color-warning);">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <span style="font-size: var(--text-sm); color: var(--text-secondary);">
              Folder picker requires <strong>Chrome or Edge</strong> browser. Firefox and Safari are not supported for local folder access.
            </span>
          </div>
          <div class="folders-list">
            <div v-for="folder in folders" :key="folder.id" :class="['folder-card glass-card', { 'is-watching gradient-border': folder.is_watching }]">
              <div class="folder-header flex-between">
                <div class="folder-info">
                  <div class="folder-icon-wrapper" :class="{ 'active-watching': folder.is_watching }">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2" class="folder-svg-icon"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                    <!-- Sonar pings when watching -->
                    <span v-if="folder.is_watching" class="sonar-wave wave-1"></span>
                    <span v-if="folder.is_watching" class="sonar-wave wave-2"></span>
                  </div>
                  <div>
                    <span class="folder-name">{{ folder.folder_name }}</span>
                    <span class="folder-path">{{ folder.local_path }}</span>
                  </div>
                </div>
                <div class="folder-actions">
                  <button :class="['btn btn-icon', folder.is_watching ? 'btn-stop' : 'btn-play']" @click="toggleWatch(folder)">
                    <svg v-if="!folder.is_watching" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                  </button>
                  <button class="btn btn-icon btn-ghost" @click="removeFolder(folder.id)">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                  </button>
                </div>
              </div>
              <div class="folder-drive" v-if="folder.drive_folder_name">
                <label>Drive Target Folder</label>
                <div class="detail-value" style="font-size: var(--text-sm); color: var(--text-secondary);">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 4px; vertical-align: middle;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                  {{ folder.drive_folder_name }}
                </div>
              </div>
              <!-- Sync Queue List for this folder -->
              <div class="sync-queue-container" v-if="syncQueue.some(item => item.folderId === folder.id)">
                <div class="queue-header-mini">
                  <span class="queue-counter-badge">
                    {{ getActiveSyncCountForFolder(folder.id) }} syncing • {{ getQueuedSyncCountForFolder(folder.id) }} queued
                  </span>
                </div>
                <TransitionGroup name="queue-list" tag="div" class="queue-list">
                  <div class="queue-item glass-card" v-for="item in syncQueue.filter(item => item.folderId === folder.id)" :key="item.id" :class="item.stage">
                    <div class="queue-item-header">
                      <div class="queue-item-info">
                        <span class="queue-item-icon">
                          <span v-if="item.stage === 'completed'" class="icon-success">✓</span>
                          <span v-else-if="item.stage === 'failed'" class="icon-failed">✕</span>
                          <span v-else class="spinner-tiny"></span>
                        </span>
                        <div class="queue-item-meta">
                          <div class="queue-item-name" :title="item.name">{{ item.name }}</div>
                          <div class="queue-item-size">{{ formatBytes(item.size) }}</div>
                        </div>
                      </div>
                      <div class="queue-item-status">
                        <span class="stage-badge" :class="item.stage">{{ getStageLabel(item.stage) }}</span>
                        <span class="percentage-label" v-if="item.stage !== 'completed' && item.stage !== 'failed'">{{ item.progress }}%</span>
                      </div>
                    </div>
                    
                    <!-- Dynamic Progress Bar -->
                    <div class="queue-progress-track">
                      <div class="queue-progress-bar" :style="{ width: `${item.progress}%` }" :class="item.stage"></div>
                    </div>
                  </div>
                </TransitionGroup>
              </div>

              <!-- Conveyor / Pipeline Animation (Fallback when folder has no active uploads) -->
              <div v-else-if="folder.is_watching" class="fetching-animation-panel glass-strong">
                <div class="sync-graphic">
                  <!-- Local computer icon -->
                  <div class="sync-node local-node">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                    <span class="node-label">Local</span>
                  </div>
                  
                  <!-- Conveyor belt with floating/syncing files -->
                  <div class="sync-flow">
                    <div class="flow-line"></div>
                    <div class="floating-files">
                      <div class="floating-file file-1">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                      </div>
                      <div class="floating-file file-2">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary-light)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                      </div>
                      <div class="floating-file file-3">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-secondary)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Cloud icon -->
                  <div class="sync-node cloud-node">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>
                    <span class="node-label">Drive</span>
                  </div>
                </div>
                <div class="sync-info flex-between">
                  <div class="sync-status">
                    <span class="status-pulse-dot"></span>
                    <span class="status-text">Actively scanning & syncing files...</span>
                  </div>
                  <div class="fetching-progress-line">
                    <div class="progress-bar-shimmer"></div>
                  </div>
                </div>
              </div>
              <div class="folder-status">
                <span :class="['badge', folder.is_watching ? 'badge-success' : 'badge-warning']">
                  {{ folder.is_watching ? '● Watching' : '○ Stopped' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Drive Config View -->
        <div v-if="activeMenu === 'drive'" class="drive-section">
          <div class="drive-container">
            <!-- Left Column: Connected Accounts List -->
            <div class="drive-accounts-card glass-card">
              <div class="section-header">
                <h3>Google Drive Accounts</h3>
                <p>Manage multiple connected Drive accounts & storage environments.</p>
              </div>

              <div class="accounts-list">
                <div v-if="connectedAccounts.length === 0" class="empty-state">
                  <div class="empty-icon">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  </div>
                  <h3>No Drive accounts connected</h3>
                  <p>Connect your first Google Drive account to begin streaming photos live.</p>
                </div>

                <div v-else class="accounts-grid-items">
                  <div 
                    v-for="account in connectedAccounts" 
                    :key="account.id" 
                    :class="['account-item-card glass-card', account.id === selectedDriveConfigId ? 'active-account' : '']" 
                    @click="selectedDriveConfigId = account.id"
                  >
                    <div class="account-item-icon">
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" :stroke="account.connected ? 'var(--color-success)' : 'var(--color-warning)'" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                        <polyline points="22 4 12 14.01 9 11.01"/>
                      </svg>
                    </div>
                    <div class="account-item-info">
                      <span class="account-item-email">{{ account.email || 'Connected Account' }}</span>
                      <span class="account-item-status" :style="{ color: account.connected ? 'var(--color-success)' : 'var(--color-warning)' }">
                        {{ account.connected ? 'Connected' : 'Sign-in required' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="action-btn-row">
                <button class="btn btn-primary btn-lg full-width ripple" @click="authorizeGoogle" :disabled="authorizingGoogle">
                  <svg v-if="authorizingGoogle" class="spin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                  <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  <span>{{ authorizingGoogle ? 'Connecting to Google...' : 'Connect Another Drive Account' }}</span>
                </button>
              </div>
            </div>

            <!-- Right Column: Storage Stats & Directory Folders -->
            <div class="drive-details-card glass-card">
              <div v-if="fetchingDriveFolders" class="drive-details-loading">
                <svg class="spin" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                <span>Fetching account workspace...</span>
              </div>

              <div v-else-if="!selectedDriveConfigId" class="drive-details-empty">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="3" x2="9" y2="21"/></svg>
                <p>Select a Google account from the left to view its storage quotas and folders.</p>
              </div>

              <div v-else class="drive-details-content">
                <div class="details-section-header">
                  <h3>Workspace Status</h3>
                  <span class="badge" :class="driveStatus?.connected ? 'badge-success' : 'badge-warning'">
                    {{ driveStatus?.connected ? 'Online' : 'Disconnected' }}
                  </span>
                </div>

                <!-- Storage Info Grid -->
                <div class="drive-storage-grid">
                  <div class="storage-stats-card glass-card">
                    <span class="stat-meta">Used</span>
                    <strong class="stat-value-text">{{ formatBytes(driveStatus?.storage?.used_bytes || 0) }}</strong>
                  </div>
                  <div class="storage-stats-card glass-card">
                    <span class="stat-meta">Total</span>
                    <strong class="stat-value-text">{{ formatBytes(driveStatus?.storage?.total_bytes || 0) }}</strong>
                  </div>
                  <div class="storage-stats-card glass-card">
                    <span class="stat-meta">Available</span>
                    <strong class="stat-value-text">{{ formatBytes(driveStatus?.storage?.free_bytes || 0) }}</strong>
                  </div>
                </div>

                <!-- Folders List section -->
                <div class="drive-folders-list-section glass-card">
                  <div class="folders-header-row">
                    <h4>Available Drive Folders ({{ currentDriveFolders.length }})</h4>
                  </div>

                  <div v-if="driveFoldersError" class="folders-error-state">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    <span>{{ driveFoldersError }}</span>
                  </div>

                  <div v-else-if="currentDriveFolders.length === 0" class="folders-empty-state">
                    <p>No directories found in this Google Drive account. Add one inside the Folders tab.</p>
                  </div>

                  <ul v-else class="cloud-folders-ul">
                    <li v-for="folder in currentDriveFolders" :key="folder.id" class="cloud-folder-item">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary-light)" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                      <span class="cloud-folder-name">{{ folder.name }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Studio Profile Section -->
        <div v-if="activeMenu === 'profile'" class="profile-section">
          <div class="profile-container">
            <!-- Left Side: Profile Form -->
            <div class="glass-card profile-card" style="padding: var(--space-2xl); width: 100%;">
              <div class="profile-header">
                <span class="gradient-text-branding">Creative Studio Profile</span>
                <h3>Edit Studio Details</h3>
                <p>Keep your branding and display information up to date</p>
              </div>

              <form @submit.prevent="saveProfile" class="profile-form">
                <!-- Studio Name -->
                <div class="input-group">
                  <label for="profStudioName">Studio Name *</label>
                  <input id="profStudioName" v-model="studioName" type="text" class="input input-neu" placeholder="e.g., Golden Frame Studios" required />
                </div>

                <!-- Owner Name / Display Name -->
                <div class="input-group">
                  <label for="profDisplayName">Owner / Photographer Name *</label>
                  <input id="profDisplayName" v-model="displayName" type="text" class="input input-neu" placeholder="e.g., Abhishek Gupta" required />
                </div>

                <!-- Profile Image (Studio Logo) Drag and Drop Uploader -->
                <div class="input-group">
                  <label>Studio Logo / Avatar</label>
                  <div 
                    class="profile-upload-zone neu-inset" 
                    :class="{ 'drag-over': isDraggingImage }"
                    @click="$refs.profileImageInput.click()" 
                    @dragover.prevent="isDraggingImage = true" 
                    @dragleave.prevent="isDraggingImage = false" 
                    @drop.prevent="handleProfileImageDrop"
                  >
                    <input ref="profileImageInput" type="file" accept="image/*" @change="handleProfileImageFileChange" hidden />
                    
                    <!-- If previewUrl is set (either from current image or new selected image) -->
                    <div v-if="previewUrl" class="profile-upload-preview">
                      <img :src="resolveLogoUrl(previewUrl)" alt="Studio logo preview" />
                      <div class="preview-overlay">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                        <span>Drag & drop or click to replace</span>
                      </div>
                      <button type="button" class="profile-remove-btn" @click.stop="resetProfileImage" title="Restore default logo">✕</button>
                    </div>
                    
                    <!-- Fallback: Initials if no image is uploaded/configured -->
                    <div v-else-if="authStore.user?.email" class="profile-initial-preview">
                      <div class="avatar-initial-large">{{ (authStore.user?.email || 'U')[0].toUpperCase() }}</div>
                      <div class="upload-hint">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                        <span>Drag & drop or click to upload logo</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Phone -->
                <div class="input-group">
                  <label for="profPhone">Phone Number *</label>
                  <div class="phone-row">
                    <select v-model="countryCode" class="input input-neu country-select">
                      <option v-for="c in countryCodes" :key="c.code" :value="c.code">{{ c.flag }} {{ c.code }}</option>
                    </select>
                    <input id="profPhone" v-model="phoneNumber" type="tel" class="input input-neu" placeholder="9876543210" required />
                  </div>
                </div>

                <!-- Alternative Phone Numbers -->
                <div class="input-group">
                  <label for="profAltPhone">Alternate Contacts (comma-separated, optional)</label>
                  <input id="profAltPhone" v-model="contactNumbers" type="text" class="input input-neu" placeholder="e.g., +91 9999988888, 022-2234567" />
                </div>

                <!-- Website Link -->
                <div class="input-group">
                  <label for="profWebsite">Website Link (optional)</label>
                  <input id="profWebsite" v-model="websiteLink" type="url" class="input input-neu" placeholder="e.g., https://yourstudioname.com" />
                </div>

                <!-- Instagram Link -->
                <div class="input-group">
                  <label for="profInstagram">Instagram ID or Link (optional)</label>
                  <input id="profInstagram" v-model="instagramLink" type="text" class="input input-neu" placeholder="e.g., my_studio_instagram" />
                </div>

                <!-- Facebook Link -->
                <div class="input-group">
                  <label for="profFacebook">Facebook ID or Link (optional)</label>
                  <input id="profFacebook" v-model="facebookLink" type="text" class="input input-neu" placeholder="e.g., my_studio_facebook" />
                </div>

                <!-- WhatsApp Number -->
                <div class="input-group">
                  <label for="profWhatsApp">WhatsApp Number (optional)</label>
                  <input id="profWhatsApp" v-model="whatsappNumber" type="tel" class="input input-neu" placeholder="e.g., +91 9876543210" />
                </div>

                <!-- Address -->
                <div class="input-group">
                  <label for="profAddress">Studio Address (optional)</label>
                  <textarea id="profAddress" v-model="address" class="input input-neu" placeholder="e.g., 123 Creative Space, Gallery Lane" rows="3" style="resize: vertical; min-height: 80px; padding: 12px;"></textarea>
                </div>

                <!-- Bio -->
                <div class="input-group">
                  <label for="profBio">Short Bio (optional)</label>
                  <textarea id="profBio" v-model="bio" class="input input-neu" placeholder="e.g., Wedding & portrait photographer with 10+ years of experience" rows="3" style="resize: vertical; min-height: 80px; padding: 12px;" maxlength="500"></textarea>
                  <span v-if="bio" style="font-size: 11px; color: var(--text-tertiary); text-align: right; display: block; margin-top: 4px;">{{ bio.length }}/500</span>
                </div>

                <!-- Save Button -->
                <button type="submit" class="btn btn-primary btn-lg" style="width: 100%; margin-top: var(--space-md);" :disabled="isSavingProfile">
                  <span v-if="isSavingProfile">Saving Changes...</span>
                  <span v-else>Save Studio Details</span>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                </button>
              </form>
            </div>

            <!-- Right Side: Completeness gauge & Checklist -->
            <div class="glass-card profile-completion-card">
              <h4>Profile Completion</h4>
              
              <div class="completion-gauge-container">
                <svg class="completion-gauge" viewBox="0 0 100 100">
                  <defs>
                    <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="var(--color-primary)" />
                      <stop offset="100%" stop-color="var(--color-accent)" />
                    </linearGradient>
                  </defs>
                  <circle class="gauge-bg" cx="50" cy="50" r="40" />
                  <circle 
                    class="gauge-fill" 
                    cx="50" 
                    cy="50" 
                    r="40" 
                    stroke="url(#gaugeGradient)"
                    :stroke-dasharray="2 * Math.PI * 40"
                    :stroke-dashoffset="2 * Math.PI * 40 * (1 - profileCompletion / 100)"
                  />
                </svg>
                <div class="gauge-text">
                  <span class="percentage">{{ profileCompletion }}%</span>
                  <span class="label">Complete</span>
                </div>
              </div>

              <ul class="completion-checklist">
                <li :class="{ complete: !!studioName?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Studio Name <span class="weight">(15%)</span></span>
                </li>
                <li :class="{ complete: !!displayName?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Owner Name <span class="weight">(15%)</span></span>
                </li>
                <li :class="{ complete: !!phoneNumber?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Primary Phone <span class="weight">(15%)</span></span>
                </li>
                <li :class="{ complete: !!countryCode?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Country Code <span class="weight">(5%)</span></span>
                </li>
                <li :class="{ complete: !!previewUrl || !!profileImageFile }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Studio Logo <span class="weight">(10%)</span></span>
                </li>
                <li :class="{ complete: !!websiteLink?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Website Link <span class="weight">(5%)</span></span>
                </li>
                <li :class="{ complete: !!address?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Physical Address <span class="weight">(10%)</span></span>
                </li>
                <li :class="{ complete: !!contactNumbers?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Alternative Phone <span class="weight">(10%)</span></span>
                </li>
                <li :class="{ complete: !!instagramLink?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Instagram Link <span class="weight">(5%)</span></span>
                </li>
                <li :class="{ complete: !!facebookLink?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Facebook Link <span class="weight">(5%)</span></span>
                </li>
                <li :class="{ complete: !!whatsappNumber?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">WhatsApp <span class="weight">(3%)</span></span>
                </li>
                <li :class="{ complete: !!bio?.trim() }">
                  <span class="check-icon">✓</span>
                  <span class="checklist-label">Bio <span class="weight">(2%)</span></span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- ✅ NEW: Browser Folder Picker Modal (uses File System Access API) -->
    <Transition name="fade">
      <div v-if="showFolderPicker" class="tutorial-overlay" @click="closeFolderPicker">
        <div class="tutorial-tooltip glass-strong" style="max-width: 600px; width: 90vw; position: relative;" @click.stop>

          <div v-if="isSavingFolder" class="modal-blocker">
            <div class="modal-blocker-content">
              <svg class="spin" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              <span>Creating folder in Drive and starting watcher...</span>
            </div>
          </div>

          <div class="flex-between" style="margin-bottom: var(--space-lg)">
            <h3>Select Folder</h3>
            <button class="btn btn-icon btn-ghost" @click="closeFolderPicker">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <!-- Step 1: Pick folder from browser -->
          <div v-if="!selectedFolderPath" class="folder-browser">

            <div class="fsa-pick-area glass-card" style="padding: var(--space-2xl); text-align: center; margin-bottom: var(--space-lg);">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" style="margin: 0 auto var(--space-md);">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
              <p style="color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-lg);">
                Click the button below to open a folder picker.<br/>
                Choose the folder you want to monitor on your computer.
              </p>
              <button
                class="btn btn-primary"
                @click="pickFolderFromBrowser"
                :disabled="!isFSASupported || pickerLoading"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                {{ pickerLoading ? 'Opening...' : 'Browse & Select Folder' }}
              </button>
              <p v-if="!isFSASupported" style="color: var(--color-warning); font-size: var(--text-xs); margin-top: var(--space-md);">
                ⚠ Your browser doesn't support folder picking. Please use Chrome or Edge.
              </p>
            </div>

          </div>

          <!-- Step 2: Folder selected — configure Drive target -->
          <div v-else class="folder-details-form">
            <div class="selected-folder-banner glass-card" style="padding: var(--space-md) var(--space-lg); margin-bottom: var(--space-xl); display: flex; align-items: center; gap: var(--space-md);">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              <div>
                <span style="font-size: var(--text-xs); color: var(--text-tertiary); display: block;">Selected Folder</span>
                <span style="color: var(--color-primary); font-weight: 600; font-size: var(--text-sm);">{{ selectedFolderPath }}</span>
              </div>
              <button class="btn btn-icon btn-ghost" style="margin-left: auto;" @click="selectedFolderPath = ''" title="Change folder">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
              </button>
            </div>

            <div class="input-group" style="margin-bottom: var(--space-md);">
              <label>Target Google Drive Account</label>
              <input class="input input-neu" :value="selectedDriveAccountEmail || 'No account selected (choose in Drive page)'" disabled />
            </div>

            <div class="input-group" style="margin-bottom: var(--space-md);" v-if="selectedDriveConfigId">
              <label>Target Folder (Existing)</label>
              <div v-if="fetchingDriveFolders" style="font-size: 12px; color: var(--text-tertiary); margin-bottom: 4px;">Loading existing folders...</div>
              <div v-else-if="driveFoldersError" style="font-size: 12px; color: #ef4444; margin-bottom: 6px;">{{ driveFoldersError }}</div>
              <div v-else-if="currentDriveFolders.length === 0" style="font-size: 12px; color: var(--text-tertiary); margin-bottom: 6px;">
                No existing folders found in this Drive account.
              </div>
              <select v-model="selectedExistingDriveFolderId" class="input input-neu">
                <option value="">Select existing folder</option>
                <option v-for="df in currentDriveFolders" :key="df.id" :value="df.id">{{ df.name }}</option>
              </select>
            </div>

            <div class="input-group" style="margin-bottom: var(--space-xl);" v-if="selectedDriveConfigId">
              <div class="flex-between" style="margin-bottom: 6px;">
                <label>Create New Folder</label>
                <button class="btn btn-secondary btn-sm" @click="showCreateDriveFolder = !showCreateDriveFolder">
                  {{ showCreateDriveFolder ? 'Use Existing' : 'Create New Folder' }}
                </button>
              </div>
              <input
                v-if="showCreateDriveFolder"
                v-model="newDriveFolderName"
                class="input input-neu"
                placeholder="Enter new folder name"
              />
            </div>

            <div class="flex-between">
              <button class="btn btn-secondary" @click="selectedFolderPath = ''" :disabled="isSavingFolder">Back</button>
              <button
                class="btn btn-primary"
                @click="saveNewFolder"
                :class="{ 'btn-loading': isSavingFolder }"
                :disabled="!selectedDriveConfigId || !selectedFolderPath || (showCreateDriveFolder ? !newDriveFolderName : !selectedExistingDriveFolderId)"
              >
                <span v-if="isSavingFolder">Creating...</span>
                <span v-else>Start Watching</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Tutorial Tooltip -->
    <Transition name="fade">
      <div v-if="showTutorial" class="tutorial-overlay" @click="closeTutorial">
        <div class="tutorial-tooltip glass-strong" @click.stop>
          <h3>Welcome to your Dashboard! 🎉</h3>
          <p>Here's a quick overview:</p>
          <ul>
            <li>📁 <strong>Folders</strong> — Add up to 20 folders to monitor</li>
            <li>▶️ <strong>Play/Stop</strong> — Control live file watching</li>
            <li>📊 <strong>Analytics</strong> — Real-time upload statistics</li>
            <li>🖥️ <strong>Live Studio</strong> — Present photos on a second screen</li>
          </ul>
          <button class="btn btn-primary btn-sm" @click="closeTutorial">Got it!</button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, inject, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'
import { Chart, registerables } from 'chart.js'
import { folderWatcher, saveDirHandle, getDirHandle, removeDirHandle } from '../services/folderWatcher'
import imageCompression from 'browser-image-compression'
import exifr from 'exifr'
import axios from 'axios'

Chart.register(...registerables)

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const showToast = inject('showToast')

const imageLoadError = ref(false)

const sidebarCollapsed = ref(false)
const activeMenu = ref('dashboard')
const showTutorial = ref(false)
const folders = ref([])
const driveFolders = ref([])
const driveConfig = ref(null)
const filterFrom = ref('')
const filterTo = ref('')
const uploadChart = ref(null)
const statusChart = ref(null)

const syncQueue = ref([])
const activeSyncCount = computed(() => syncQueue.value.filter(item => ['analyzing', 'compressing', 'resuming', 'uploading'].includes(item.stage)).length)
const queuedSyncCount = computed(() => syncQueue.value.filter(item => item.stage === 'detected').length)

function getActiveSyncCountForFolder(folderId) {
  return syncQueue.value.filter(item => item.folderId === folderId && ['analyzing', 'compressing', 'resuming', 'uploading'].includes(item.stage)).length
}

function getQueuedSyncCountForFolder(folderId) {
  return syncQueue.value.filter(item => item.folderId === folderId && item.stage === 'detected').length
}

// Studio Profile Edit Form state
const studioName = ref('')
const displayName = ref('')
const phoneNumber = ref('')
const countryCode = ref('+91')
const instagramLink = ref('')
const facebookLink = ref('')
const address = ref('')
const contactNumbers = ref('')
const websiteLink = ref('')
const whatsappNumber = ref('')
const bio = ref('')
const profileImageFile = ref(null)
const previewUrl = ref(null)
const isDraggingImage = ref(false)
const isSavingProfile = ref(false)

const countryCodes = [
  { code: '+91', flag: '🇮🇳' }, { code: '+1', flag: '🇺🇸' }, { code: '+44', flag: '🇬🇧' },
  { code: '+61', flag: '🇦🇺' }, { code: '+81', flag: '🇯🇵' }, { code: '+49', flag: '🇩🇪' },
  { code: '+33', flag: '🇫🇷' }, { code: '+86', flag: '🇨🇳' }, { code: '+971', flag: '🇦🇪' },
  { code: '+65', flag: '🇸🇬' }, { code: '+60', flag: '🇲🇾' }, { code: '+966', flag: '🇸🇦' },
]

const profileCompletion = computed(() => {
  let score = 0
  if (studioName.value && studioName.value.trim() !== '') score += 15
  if (displayName.value && displayName.value.trim() !== '') score += 15
  if (phoneNumber.value && phoneNumber.value.trim() !== '') score += 15
  if (countryCode.value && countryCode.value.trim() !== '') score += 5
  if (previewUrl.value || profileImageFile.value) score += 10
  if (address.value && address.value.trim() !== '') score += 10
  if (contactNumbers.value && contactNumbers.value.trim() !== '') score += 10
  if (websiteLink.value && websiteLink.value.trim() !== '') score += 5
  if (instagramLink.value && instagramLink.value.trim() !== '') score += 5
  if (facebookLink.value && facebookLink.value.trim() !== '') score += 5
  if (whatsappNumber.value && whatsappNumber.value.trim() !== '') score += 3
  if (bio.value && bio.value.trim() !== '') score += 2
  return score
})

function initializeProfileForm() {
  if (authStore.user) {
    studioName.value = authStore.user.studio_name || ''
    displayName.value = authStore.user.display_name || authStore.user.name || ''
    phoneNumber.value = authStore.user.phone_number || authStore.user.phone || ''
    countryCode.value = authStore.user.country_code || '+91'
    instagramLink.value = authStore.user.instagram_link || ''
    facebookLink.value = authStore.user.facebook_link || ''
    address.value = authStore.user.address || ''
    contactNumbers.value = authStore.user.contact_numbers || ''
    websiteLink.value = authStore.user.website_link || ''
    whatsappNumber.value = authStore.user.whatsapp_number || ''
    bio.value = authStore.user.bio || ''
    previewUrl.value = authStore.user.profile_image || null
    profileImageFile.value = null
  }
}

watch(() => authStore.user, (newUser) => {
  if (newUser) {
    initializeProfileForm()
  }
}, { immediate: true })

function handleProfileImageFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    profileImageFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function handleProfileImageDrop(e) {
  isDraggingImage.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    profileImageFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function resetProfileImage() {
  profileImageFile.value = null
  previewUrl.value = authStore.user?.profile_image || null
  imageLoadError.value = false
}

async function saveProfile() {
  if (isSavingProfile.value) return
  isSavingProfile.value = true
  try {
    const formData = new FormData()
    formData.append('user_id', String(authStore.user.id))
    formData.append('studio_name', studioName.value)
    formData.append('display_name', displayName.value)
    formData.append('phone_number', phoneNumber.value)
    formData.append('country_code', countryCode.value)
    formData.append('instagram_link', instagramLink.value)
    formData.append('facebook_link', facebookLink.value)
    formData.append('address', address.value)
    formData.append('contact_numbers', contactNumbers.value)
    formData.append('website_link', websiteLink.value)
    formData.append('whatsapp_number', whatsappNumber.value)
    formData.append('bio', bio.value)
    if (profileImageFile.value) {
      formData.append('profile_image', profileImageFile.value)
    }

    await authStore.updateProfile(formData)
    imageLoadError.value = false // reset avatar broken error if they uploaded new one
    showToast('Studio profile details updated! 🎉', 'success')
  } catch (err) {
    showToast(err.message || 'Failed to update profile', 'error')
  } finally {
    isSavingProfile.value = false
  }
}


// ✅ Check if File System Access API is supported (Chrome/Edge only)
const isFSASupported = typeof window !== 'undefined' && 'showDirectoryPicker' in window

// Folder Picker State
const showFolderPicker = ref(false)
const pickerLoading = ref(false)
const selectedFolderPath = ref('')
const newDriveFolderName = ref('')
const selectedExistingDriveFolderId = ref('')
const showCreateDriveFolder = ref(false)

const connectedAccounts = ref([])
const selectedDriveConfigId = ref(null)
const selectedDriveAccountEmail = ref('')

const currentDriveFolders = ref([])
const fetchingDriveFolders = ref(false)
const driveStatus = ref(null)
const driveFoldersError = ref('')
const dashboardStats = ref(null)
const isSavingFolder = ref(false)
let uploadChartInstance = null
let statusChartInstance = null
let statsPollTimer = null

function getCurrentUserId() {
  try {
    return authStore.user?.id || JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
  } catch (e) {
    return null
  }
}

watch(selectedDriveConfigId, async (newVal) => {
  if (newVal) {
    fetchingDriveFolders.value = true
    driveFoldersError.value = ''
    try {
      const userId = getCurrentUserId()
      if (!userId) {
        currentDriveFolders.value = []
        driveStatus.value = null
        driveFoldersError.value = 'Unable to identify current user session.'
        return
      }
      const [{ data: folders }, { data: status }] = await Promise.all([
        api.get(`/api/folders/drive-folders?user_id=${userId}&drive_config_id=${newVal}`),
        api.get(`/api/drive/status?user_id=${userId}&drive_config_id=${newVal}`),
      ])
      currentDriveFolders.value = folders
      driveStatus.value = status
      const matched = connectedAccounts.value.find(a => a.id === newVal)
      selectedDriveAccountEmail.value = matched?.email || status?.email || ''
      localStorage.setItem('ak_selected_drive_config_id', String(newVal))
    } catch(e) {
      currentDriveFolders.value = []
      driveStatus.value = null
      driveFoldersError.value = e?.response?.data?.detail?.drive_error?.error?.message
        || e?.response?.data?.detail
        || 'Failed to fetch Drive folders for selected account.'
    } finally {
      fetchingDriveFolders.value = false
    }
  } else {
    currentDriveFolders.value = []
    driveStatus.value = null
    driveFoldersError.value = ''
  }
}, { immediate: true })

const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>' },
  { id: 'folders', label: 'Folders', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>' },
  { id: 'drive', label: 'Drive', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>' },
  { id: 'profile', label: 'Studio Profile', icon: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
]
const validSections = new Set(menuItems.map(m => m.id))

const statsCards = computed(() => [
  { label: 'Total Uploads', value: String(dashboardStats.value?.stats?.total_uploads || 0), icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>', bg: 'rgba(108,99,255,0.15)' },
  { label: 'Successful', value: String(dashboardStats.value?.stats?.successful_uploads || 0), icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', bg: 'rgba(16,185,129,0.15)' },
  { label: 'Failed', value: String(dashboardStats.value?.stats?.failed_uploads || 0), icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>', bg: 'rgba(239,68,68,0.15)' },
  { label: 'Active Folders', value: folders.value.filter(f => f.is_watching).length.toString(), icon: '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>', bg: 'rgba(255,179,71,0.15)' },
])

const currentTitle = computed(() => menuItems.find(m => m.id === activeMenu.value)?.label || 'Dashboard')

function normalizeSection(section) {
  if (!section) return 'dashboard'
  return validSections.has(section) ? section : 'dashboard'
}

function setActiveMenu(section) {
  const next = normalizeSection(section)
  activeMenu.value = next
  if (route.params.section !== next) {
    router.replace({ name: 'Dashboard', params: { section: next } })
  }
}

function openLivePresentation() {
  window.open('/live', '_blank')
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

// ✅ NEW: Use File System Access API to pick folder from browser
async function pickFolderFromBrowser() {
  if (!isFSASupported) {
    showToast('Your browser does not support folder picking. Please use Chrome or Edge.', 'error')
    return
  }
  pickerLoading.value = true
  try {
    const dirHandle = await window.showDirectoryPicker({ mode: 'read' })
    // Use the folder name as path identifier (browser sandboxed path)
    selectedFolderPath.value = dirHandle.name
    // Store the handle for later file reading if needed
    window._selectedDirHandle = dirHandle
    // Pre-fill drive folder name from local folder name
    newDriveFolderName.value = dirHandle.name
    selectedExistingDriveFolderId.value = ''
    showCreateDriveFolder.value = false
  } catch (err) {
    if (err.name !== 'AbortError') {
      // AbortError means user cancelled — don't show error
      showToast('Failed to open folder picker: ' + err.message, 'error')
    }
  } finally {
    pickerLoading.value = false
  }
}

async function addFolder() {
  showFolderPicker.value = true
  selectedFolderPath.value = ''
  newDriveFolderName.value = ''
  selectedExistingDriveFolderId.value = ''
  showCreateDriveFolder.value = false

  if (selectedDriveConfigId.value) {
    fetchingDriveFolders.value = true
    driveFoldersError.value = ''
    try {
      const userId = getCurrentUserId()
      if (userId) {
        const [{ data: dFolders }, { data: status }] = await Promise.all([
          api.get(`/api/folders/drive-folders?user_id=${userId}&drive_config_id=${selectedDriveConfigId.value}`),
          api.get(`/api/drive/status?user_id=${userId}&drive_config_id=${selectedDriveConfigId.value}`),
        ])
        currentDriveFolders.value = dFolders || []
        driveStatus.value = status || null
      }
    } catch (e) {
      currentDriveFolders.value = []
      driveFoldersError.value = e?.response?.data?.detail?.drive_error?.error?.message
        || e?.response?.data?.detail
        || 'Failed to refresh Drive folders.'
    } finally {
      fetchingDriveFolders.value = false
    }
  }
}

function closeFolderPicker() {
  showFolderPicker.value = false
}

async function saveNewFolder() {
  if (isSavingFolder.value) return
  isSavingFolder.value = true
  try {
    const existingFolder = currentDriveFolders.value.find(df => String(df.id) === String(selectedExistingDriveFolderId.value))
    const folderName = showCreateDriveFolder.value
      ? newDriveFolderName.value
      : (existingFolder?.name || '')

    const folderData = {
      local_path: selectedFolderPath.value,
      folder_name: folderName || selectedFolderPath.value,
      drive_config_id: selectedDriveConfigId.value || null,
      drive_folder_name: folderName,
    }

    if (existingFolder) {
      folderData.drive_folder_id = existingFolder.id
    }

    const { data } = await api.post(`/api/folders/?user_id=${getCurrentUserId()}`, folderData)
    data.is_watching = data.is_watching ?? true
    folders.value.unshift(data)

    // ✅ Save the directory handle and start frontend file watcher
    const dirHandle = window._selectedDirHandle
    if (dirHandle && data.id) {
      await saveDirHandle(data.id, dirHandle)
      const started = await folderWatcher.startWatching(data.id, dirHandle)
      if (started) {
        console.log(`[Dashboard] Frontend watcher started for folder ${data.id}`)
      }
    }

    showToast(`Folder "${folderData.folder_name}" added! 📁`, 'success')
    closeFolderPicker()
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to add folder', 'error')
  } finally {
    isSavingFolder.value = false
  }
}

async function toggleWatch(folder) {
  const action = folder.is_watching ? 'stop' : 'start'
  try {
    await api.post(`/api/folders/${folder.id}/${action}?user_id=${authStore.user.id}`)
    folder.is_watching = !folder.is_watching

    // ✅ Start or stop the frontend file watcher
    if (folder.is_watching) {
      const started = await folderWatcher.startWatching(folder.id)
      if (started) {
        showToast(`Watching "${folder.folder_name}" 👁️`, 'info')
      } else {
        showToast(`Watching "${folder.folder_name}" (re-select folder to enable local file detection)`, 'info')
      }
    } else {
      folderWatcher.stopWatching(folder.id)
      showToast(`Stopped "${folder.folder_name}"`, 'info')
    }
  } catch (err) {
    showToast(err.response?.data?.detail || `Failed to ${action}`, 'error')
  }
}

async function removeFolder(id) {
  if (!confirm('Remove this folder?')) return
  try {
    folderWatcher.stopWatching(id)
    await removeDirHandle(id)
    await api.delete(`/api/folders/${id}?user_id=${authStore.user.id}`)
    folders.value = folders.value.filter(f => f.id !== id)
    showToast('Folder removed', 'info')
  } catch { showToast('Failed to remove', 'error') }
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
    const userId = getCurrentUserId()
    if (!userId) throw new Error('User session not found')

    // 1. Log the upload on the backend
    queueItem.stage = 'analyzing'
    queueItem.progress = 15

    const ext = queueItem.name.split('.').pop()?.toLowerCase() || ''
    const sizeMb = Math.round((queueItem.file.size / 1024 / 1024) * 100) / 100
    const logParams = new URLSearchParams({
      user_id: String(userId),
      folder_id: String(queueItem.folderId),
      file_name: queueItem.name,
      file_path: `browser://${queueItem.name}`,
      file_format: `.${ext}`,
      file_size_mb: String(sizeMb),
      status_val: 'pending',
    })
    const { data: uploadLog } = await api.post(`/api/uploads/log?${logParams.toString()}`)
    
    queueItem.progress = 25
    await new Promise(resolve => setTimeout(resolve, 150))

    // 2. Compressing stage
    let finalFileName = queueItem.name
    let mimeType = queueItem.file.type || 'image/' + (ext === 'jpg' ? 'jpeg' : ext)
    let compressibleBlob = queueItem.file;

    const isRaw = /\.(arw|cr2|nef|dng|raw|orf|raf)$/i.test(finalFileName);

    if (isRaw) {
      queueItem.stage = 'compressing'
      queueItem.progress = 30
      
      let extractedBlob = null;
      try {
        extractedBlob = await extractLargestJpegFromRaw(queueItem.file);
      } catch (e) {
        console.warn("Binary raw JPEG extraction failed:", e);
      }

      if (extractedBlob) {
        compressibleBlob = extractedBlob;
        finalFileName = finalFileName.replace(/\.[^/.]+$/, "") + ".jpg";
        mimeType = 'image/jpeg';
      } else {
        try {
          const thumbData = await exifr.thumbnail(queueItem.file);
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
      compressibleBlob = compressedBlob;
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
      file_size: compressibleBlob.size,
      mime_type: mimeType,
      folder_id: queueItem.folderId,
    })

    // 4. Uploading directly from browser to Google Drive with dynamic progress
    queueItem.stage = 'uploading'
    queueItem.progress = 65

    const driveResp = await axios.put(resumable.upload_url, compressibleBlob, {
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
      upload_log_id: uploadLog.id,
      drive_file_id: fileId,
      upload_time_sec: uploadTime,
    })

    queueItem.stage = 'completed'
    queueItem.progress = 100
    showToast(`✅ ${queueItem.name} uploaded to Drive!`, 'success')
    
    // Smoothly remove item from the queue after 8 seconds so the user sees the success state
    setTimeout(() => {
      syncQueue.value = syncQueue.value.filter(item => item.id !== queueItem.id)
    }, 8000)
  } catch (err) {
    console.error('Queue upload failed:', err)
    queueItem.stage = 'failed'
    queueItem.error = err.message || 'Upload failed'
    showToast(`❌ Failed to upload ${queueItem.name}: ${err.message}`, 'error')
  }
}

// ✅ Frontend file detection callback — pushes to parallel sync queue
async function onNewFileDetected(folderId, file, fileName) {
  const userId = getCurrentUserId()
  if (!userId) return

  const folder = folders.value.find(f => f.id === folderId)
  if (!folder) return

  showToast(`📷 New image detected: ${fileName}`, 'info')

  const itemId = `${folderId}-${fileName}-${Date.now()}`
  syncQueue.value.push({
    id: itemId,
    folderId,
    name: fileName,
    file,
    size: file.size,
    stage: 'detected',
    progress: 5,
    error: ''
  })
}

const authorizingGoogle = ref(false)

async function authorizeGoogle() {
  authorizingGoogle.value = true
  try {
    const redirectUri = window.location.origin + '/oauth-callback'
    const { data } = await api.get(`/api/drive/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`)
    if (data.code_verifier) {
      sessionStorage.setItem('oauth_code_verifier', data.code_verifier)
    }
    window.location.href = data.auth_url
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to generate auth URL', 'error')
    authorizingGoogle.value = false
  }
}

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
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let value = bytes
  let index = 0
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024
    index += 1
  }
  return `${value.toFixed(1)} ${units[index]}`
}

async function loadDashboardStats() {
  const userId = getCurrentUserId()
  if (!userId) return
  const params = new URLSearchParams({ user_id: String(userId) })
  if (filterFrom.value) params.append('date_from', new Date(filterFrom.value).toISOString())
  if (filterTo.value) params.append('date_to', new Date(filterTo.value).toISOString())
  const { data } = await api.get(`/api/uploads/stats?${params.toString()}`)
  dashboardStats.value = data
}

async function refreshStats() {
  try {
    await loadDashboardStats()
    initCharts()
  } catch {
    showToast('Failed to refresh dashboard stats', 'error')
  }
}

function stopStatsPolling() {
  if (statsPollTimer) {
    clearInterval(statsPollTimer)
    statsPollTimer = null
  }
}

function startStatsPolling() {
  stopStatsPolling()
  if (activeMenu.value !== 'dashboard') return
  statsPollTimer = setInterval(async () => {
    try {
      await loadDashboardStats()
      initCharts()
    } catch {
      // keep silent during background polling
    }
  }, 10000)
}

function closeTutorial() {
  showTutorial.value = false
  authStore.markTutorialComplete()
}

function initCharts() {
  if (!dashboardStats.value) return
  if (uploadChartInstance) uploadChartInstance.destroy()
  if (statusChartInstance) statusChartInstance.destroy()

  const labels = (dashboardStats.value.upload_rate || []).map(p => {
    const d = new Date(p.timestamp)
    return `${String(d.getHours()).padStart(2, '0')}:00`
  })
  const counts = (dashboardStats.value.upload_rate || []).map(p => p.count || 0)

  if (uploadChart.value) {
    uploadChartInstance = new Chart(uploadChart.value, {
      type: 'line',
      data: {
        labels: labels.length ? labels : ['00:00'],
        datasets: [{ label: 'Uploads', data: counts.length ? counts : [0], borderColor: '#6C63FF', backgroundColor: 'rgba(108,99,255,0.1)', fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#6C63FF' }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748B' } }, y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#64748B' } } } }
    })
  }
  if (statusChart.value) {
    statusChartInstance = new Chart(statusChart.value, {
      type: 'doughnut',
      data: {
        labels: ['Completed', 'Failed', 'Other'],
        datasets: [{
          data: [
            dashboardStats.value.stats?.successful_uploads || 0,
            dashboardStats.value.stats?.failed_uploads || 0,
            Math.max(0, (dashboardStats.value.stats?.total_uploads || 0) - (dashboardStats.value.stats?.successful_uploads || 0) - (dashboardStats.value.stats?.failed_uploads || 0)),
          ],
          backgroundColor: ['#10B981', '#EF4444', '#F59E0B'],
          borderWidth: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 16 } } }, cutout: '70%' }
    })
  }
}

onMounted(async () => {
  setActiveMenu(route.params.section)
  if (authStore.showTutorial) showTutorial.value = true

  // ✅ Set the frontend file watcher callback
  folderWatcher.setCallback(onNewFileDetected)

  const userId = getCurrentUserId()
  if (userId) {
    try {
      const { data } = await api.get(`/api/folders/?user_id=${userId}`)
      folders.value = data
    } catch { /* ignore */ }

    try {
      const { data } = await api.get(`/api/drive/accounts?user_id=${userId}`)
      connectedAccounts.value = data
      if (data.length > 0) {
        const storedId = Number(localStorage.getItem('ak_selected_drive_config_id') || 0)
        const preferred = data.find(a => a.id === storedId) || data.find(a => a.connected) || data[0]
        selectedDriveConfigId.value = preferred.id
        selectedDriveAccountEmail.value = preferred.email || ''
      }
    } catch (e) { /* ignore */ }

    // ✅ Auto-resume frontend file watchers for folders marked as watching
    for (const folder of folders.value) {
      if (folder.is_watching) {
        const handle = await getDirHandle(folder.id)
        if (handle) {
          try {
            const started = await folderWatcher.startWatching(folder.id, handle)
            if (started) {
              console.log(`[Dashboard] Auto-resumed watcher for folder ${folder.id}: ${folder.folder_name}`)
            }
          } catch (e) {
            console.warn(`[Dashboard] Could not auto-resume watcher for folder ${folder.id}:`, e)
          }
        }
      }
    }
  }

  try {
    await loadDashboardStats()
  } catch { /* ignore */ }

  await nextTick()
  initCharts()
  startStatsPolling()
})

watch(activeMenu, () => {
  startStatsPolling()
})

watch(
  () => route.params.section,
  (section) => {
    const normalized = normalizeSection(section)
    if (activeMenu.value !== normalized) {
      activeMenu.value = normalized
    }
  }
)

watch([filterFrom, filterTo], async () => {
  if (activeMenu.value !== 'dashboard') return
  try {
    await loadDashboardStats()
    initCharts()
  } catch { /* ignore */ }
})

onUnmounted(() => {
  stopStatsPolling()
  folderWatcher.stopAll()
  if (uploadChartInstance) uploadChartInstance.destroy()
  if (statusChartInstance) statusChartInstance.destroy()
})
</script>

<style scoped>
.dashboard { display: flex; min-height: 100vh; position: relative; z-index: 1; }

/* Sidebar */
.sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: var(--sidebar-width); display: flex; flex-direction: column; padding: var(--space-lg); border-radius: 0; border: none; border-right: 1px solid var(--border-subtle); z-index: var(--z-sticky); transition: width var(--transition-normal); }
.sidebar.collapsed { width: var(--sidebar-collapsed); }
.sidebar-header { margin-bottom: var(--space-2xl); }
.brand { display: flex; align-items: center; gap: var(--space-sm); cursor: pointer; }
.brand-text { font-family: var(--font-display); font-weight: 700; font-size: var(--text-lg); white-space: nowrap; }
.sidebar-nav { flex: 1; display: flex; flex-direction: column; gap: var(--space-xs); }
.nav-item { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-md); border-radius: var(--radius-md); background: none; border: none; color: var(--text-secondary); font-family: var(--font-primary); font-size: var(--text-sm); cursor: pointer; transition: all var(--transition-fast); white-space: nowrap; width: 100%; text-align: left; }
.nav-item:hover { background: var(--bg-glass); color: var(--text-primary); }
.nav-item.active { background: rgba(108,99,255,0.1); color: var(--color-primary); }
.nav-icon { display: flex; flex-shrink: 0; }

/* Main */
.main-content { flex: 1; margin-left: var(--sidebar-width); transition: margin-left var(--transition-normal); }
.sidebar.collapsed ~ .main-content { margin-left: var(--sidebar-collapsed); }

/* Topbar */
.topbar { position: sticky; top: 0; display: flex; align-items: center; justify-content: space-between; padding: var(--space-md) var(--space-xl); border-radius: 0; border: none; border-bottom: 1px solid var(--border-subtle); z-index: var(--z-sticky); }
.topbar-left { display: flex; flex-direction: column; gap: 2px; }
.page-title { font-size: var(--text-xl); }
.studio-name {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent), var(--color-primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: var(--tracking-wide);
  text-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
}
.topbar-right { display: flex; align-items: center; gap: var(--space-md); }
.user-avatar { width: 36px; height: 36px; border-radius: 50%; overflow: hidden; background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; }
.user-avatar img { width: 100%; height: 100%; object-fit: cover; }
.avatar-initial { font-weight: 700; color: var(--color-primary); font-size: var(--text-sm); }

/* Content */
.content-area { padding: var(--space-xl); }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-lg); margin-bottom: var(--space-xl); }
.stat-card { display: flex; align-items: center; gap: var(--space-lg); padding: var(--space-xl); }
.stat-icon { width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-value { font-family: var(--font-display); font-size: var(--text-2xl); font-weight: 800; display: block; }
.stat-label { font-size: var(--text-xs); color: var(--text-tertiary); }

/* Charts */
.charts-row { display: grid; grid-template-columns: 2fr 1fr; gap: var(--space-lg); margin-bottom: var(--space-xl); }
.chart-card { padding: var(--space-xl); }
.chart-card h3 { font-size: var(--text-base); margin-bottom: var(--space-lg); }
.chart-placeholder { height: 250px; position: relative; }

/* Filter */
.filter-bar { display: flex; align-items: flex-end; gap: var(--space-lg); padding: var(--space-lg); border-radius: var(--radius-lg); margin-bottom: var(--space-xl); }
.filter-group { display: flex; flex-direction: column; gap: var(--space-xs); }
.filter-group label { font-size: var(--text-xs); color: var(--text-tertiary); }
.filter-group .input { font-size: var(--text-sm); padding: var(--space-sm) var(--space-md); }

/* Folders */
.section-bar { margin-bottom: var(--space-xl); }
.folders-list { display: flex; flex-direction: column; gap: var(--space-lg); }
.folder-card { padding: var(--space-xl); }
.folder-header { margin-bottom: var(--space-lg); }
.folder-info { display: flex; align-items: center; gap: var(--space-md); }
.folder-name { font-weight: 600; display: block; }
.folder-path { font-size: var(--text-xs); color: var(--text-tertiary); display: block; }
.folder-actions { display: flex; gap: var(--space-sm); }
.btn-play { color: var(--color-success); background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); }
.btn-stop { color: var(--color-error); background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); }
.folder-drive { margin-bottom: var(--space-md); }
.folder-drive label { font-size: var(--text-xs); color: var(--text-tertiary); display: block; margin-bottom: var(--space-sm); }

/* Drive */
.drive-details { display: flex; flex-direction: column; gap: var(--space-md); margin-top: var(--space-lg); }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: var(--space-sm) 0; border-bottom: 1px solid var(--border-subtle); }
.detail-label { font-size: var(--text-sm); color: var(--text-secondary); }
.detail-value { font-size: var(--text-sm); font-family: var(--font-mono); color: var(--text-tertiary); max-width: 200px; overflow: hidden; text-overflow: ellipsis; }

/* FSA Pick Area */
.fsa-pick-area { border: 2px dashed var(--border-subtle); transition: border-color var(--transition-fast); }
.fsa-pick-area:hover { border-color: var(--color-primary); }
.selected-folder-banner { border: 1px solid rgba(16,185,129,0.25); }
.alert { display: flex; align-items: center; gap: var(--space-sm); }

/* Tutorial */
.tutorial-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: var(--z-modal); backdrop-filter: blur(4px); }
.tutorial-tooltip { max-width: 420px; padding: var(--space-2xl); border-radius: var(--radius-xl); }
.tutorial-tooltip h3 { margin-bottom: var(--space-md); }
.tutorial-tooltip p { color: var(--text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-lg); }
.tutorial-tooltip ul { list-style: none; display: flex; flex-direction: column; gap: var(--space-md); margin-bottom: var(--space-xl); }
.tutorial-tooltip li { font-size: var(--text-sm); color: var(--text-secondary); }
.modal-blocker { position: absolute; inset: 0; background: rgba(8,10,25,0.72); backdrop-filter: blur(3px); border-radius: var(--radius-xl); z-index: 20; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-blocker-content { display: flex; align-items: center; gap: 10px; color: #e5e7eb; font-size: 14px; font-weight: 600; text-align: center; }
.btn-loading { opacity: 0.9; pointer-events: none; }
.input-group { display: flex; flex-direction: column; gap: var(--space-xs); }
.input-group label { font-size: var(--text-sm); color: var(--text-secondary); font-weight: 500; }

/* Custom folder card enhancements when watching */
.folder-card.is-watching {
  box-shadow: var(--shadow-lg), var(--shadow-glow-strong);
  background: linear-gradient(
    135deg,
    rgba(108, 99, 255, 0.08) 0%,
    rgba(0, 210, 255, 0.03) 100%
  );
  border-color: transparent !important;
  transform: translateY(-2px);
}

/* Folder Icon Wrapper with Pulsing Radar Rings */
.folder-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  transition: all var(--transition-normal);
}

.folder-icon-wrapper.active-watching {
  background: rgba(108, 99, 255, 0.15);
  box-shadow: 0 0 15px rgba(108, 99, 255, 0.2);
}

.folder-icon-wrapper.active-watching .folder-svg-icon {
  stroke: var(--color-accent);
  filter: drop-shadow(0 0 6px var(--color-accent));
  animation: activeFolderPulse 2s ease-in-out infinite;
}

@keyframes activeFolderPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); filter: drop-shadow(0 0 10px var(--color-accent)); }
}

.sonar-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-accent);
  opacity: 0;
  pointer-events: none;
}

.wave-1 {
  animation: sonarPing 2.4s cubic-bezier(0.25, 0, 0, 1) infinite;
}

.wave-2 {
  animation: sonarPing 2.4s cubic-bezier(0.25, 0, 0, 1) infinite;
  animation-delay: 1.2s;
}

@keyframes sonarPing {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(2.2);
    opacity: 0;
  }
}

/* Syncing/Fetching Animation Panel */
.fetching-animation-panel {
  margin: var(--space-md) 0 var(--space-lg) 0;
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  overflow: hidden;
}

.sync-graphic {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  padding: 10px 0;
}

.sync-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--text-secondary);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  z-index: 2;
  transition: all var(--transition-normal);
}

.local-node {
  color: var(--color-accent);
}

.local-node svg {
  filter: drop-shadow(0 0 6px rgba(0, 210, 255, 0.4));
}

.cloud-node {
  color: var(--color-primary);
  animation: cloudPulse 3s ease-in-out infinite;
}

.cloud-node svg {
  filter: drop-shadow(0 0 6px rgba(108, 99, 255, 0.4));
}

@keyframes cloudPulse {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

.sync-flow {
  flex: 1;
  height: 24px;
  margin: 0 var(--space-md);
  position: relative;
  overflow: hidden;
}

.flow-line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 2px;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 4px,
    rgba(255, 255, 255, 0.15) 4px,
    rgba(255, 255, 255, 0.15) 12px
  );
  transform: translateY(-50%);
}

.floating-files {
  position: absolute;
  inset: 0;
}

.floating-file {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(10, 10, 26, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 4px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3), var(--shadow-glow);
  opacity: 0;
}

.file-1 {
  animation: fileFlow 3.6s linear infinite;
}

.file-2 {
  animation: fileFlow 3.6s linear infinite;
  animation-delay: 1.2s;
}

.file-3 {
  animation: fileFlow 3.6s linear infinite;
  animation-delay: 2.4s;
}

@keyframes fileFlow {
  0% {
    left: 0%;
    opacity: 0;
    transform: translateY(-50%) scale(0.6) rotate(0deg);
  }
  10% {
    opacity: 1;
    transform: translateY(-50%) scale(1) rotate(5deg);
  }
  50% {
    transform: translateY(-70%) scale(1.1) rotate(15deg);
  }
  90% {
    opacity: 1;
    transform: translateY(-50%) scale(1) rotate(-5deg);
  }
  100% {
    left: 100%;
    opacity: 0;
    transform: translateY(-50%) scale(0.6) rotate(0deg);
  }
}

.sync-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-top: 2px;
}

.sync-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-pulse-dot {
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--color-success);
  animation: statusPulse 1.5s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.status-text {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.fetching-progress-line {
  flex: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-full);
  overflow: hidden;
  position: relative;
}

.progress-bar-shimmer {
  position: absolute;
  top: 0;
  left: 0;
  width: 40%;
  height: 100%;
  background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
  animation: progressShimmer 1.8s ease-in-out infinite;
}

@keyframes progressShimmer {
  0% { left: -40%; }
  100% { left: 100%; }
}

/* Studio Profile Section Styles */
.profile-section {
  animation: fadeInUp var(--transition-normal) ease both;
}

.profile-container {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: var(--space-xl);
  max-width: 1000px;
  margin: 0 auto;
  align-items: start;
}

@media (max-width: 900px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
}

.profile-completion-card {
  padding: var(--space-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-xl);
  position: sticky;
  top: 100px;
}

.profile-completion-card h4 {
  font-family: var(--font-display);
  font-size: var(--text-md);
  font-weight: 800;
  margin-bottom: var(--space-md);
  color: var(--text-primary);
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.completion-gauge-container {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto var(--space-md) auto;
}

.completion-gauge {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.gauge-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.05);
  stroke-width: 8;
}

.gauge-fill {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.gauge-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.gauge-text .percentage {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 800;
  color: var(--text-primary);
  text-shadow: 0 0 10px rgba(108, 99, 255, 0.35);
}

.gauge-text .label {
  font-size: 8px;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-top: -2px;
}

.completion-checklist {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.completion-checklist li {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  background: rgba(255, 255, 255, 0.01);
  border: 1px solid rgba(255, 255, 255, 0.02);
}

.completion-checklist li.complete {
  color: var(--text-secondary);
  background: rgba(16, 185, 129, 0.03);
  border-color: rgba(16, 185, 129, 0.08);
}

.completion-checklist li .check-icon {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 1.5px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8px;
  color: transparent;
  transition: all var(--transition-fast);
}

.completion-checklist li.complete .check-icon {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.3);
}

.completion-checklist li .checklist-label {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.completion-checklist li .checklist-label .weight {
  font-size: 8px;
  color: var(--text-tertiary);
  opacity: 0.6;
}

.profile-card {
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-xl);
}

.profile-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.profile-header h3 {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: 800;
  margin-top: 4px;
}

.profile-header p {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin-top: 4px;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

/* Upload Zone with Drag & Drop styling */
.profile-upload-zone {
  min-height: 150px;
  border: 2px dashed var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all var(--transition-normal);
  background: rgba(0, 0, 0, 0.15);
}

.profile-upload-zone:hover,
.profile-upload-zone.drag-over {
  border-color: var(--color-primary);
  background: rgba(108, 99, 255, 0.04);
  box-shadow: var(--shadow-glow);
}

.profile-initial-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-md);
  text-align: center;
}

.avatar-initial-large {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(108, 99, 255, 0.15);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-2xl);
  font-weight: 800;
  box-shadow: 0 0 15px rgba(108, 99, 255, 0.2);
}

.upload-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  color: var(--text-tertiary);
  font-size: var(--text-xs);
}

/* Upload Preview */
.profile-upload-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.profile-upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.profile-upload-preview:hover img {
  transform: scale(1.08);
}

.preview-overlay {
  position: absolute;
  inset: 0;
  background: rgba(8, 10, 25, 0.75);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-fast);
  color: #fff;
  font-size: 10px;
  text-align: center;
  padding: var(--space-xs);
}

.profile-upload-preview:hover .preview-overlay {
  opacity: 1;
}

.profile-remove-btn {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-error);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  transition: transform var(--transition-fast);
}

.profile-remove-btn:hover {
  transform: scale(1.15);
}

/* Phone Field */
.phone-row {
  display: flex;
  gap: var(--space-md);
}

.country-select {
  width: 110px;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar { width: var(--sidebar-collapsed); }
  .sidebar .nav-label, .sidebar .brand-text { display: none; }
  .main-content { margin-left: var(--sidebar-collapsed); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .charts-row { grid-template-columns: 1fr; }
  .filter-bar { flex-direction: column; align-items: stretch; }
}
@media (max-width: 480px) {
  .stats-grid { grid-template-columns: 1fr; }
}

/* Google Drive Configuration Embedded Section */
.drive-section {
  animation: fadeInUp var(--transition-normal) ease both;
}

.drive-container {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: var(--space-xl);
  align-items: start;
}

@media (max-width: 992px) {
  .drive-container {
    grid-template-columns: 1fr;
  }
}

.drive-accounts-card,
.drive-details-card {
  padding: var(--space-xl);
  min-height: 480px;
  display: flex;
  flex-direction: column;
}

.section-header,
.details-section-header {
  margin-bottom: var(--space-lg);
}

.section-header h3,
.details-section-header h3 {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 700;
  margin-bottom: 4px;
}

.section-header p {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  margin: 0;
}

.accounts-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: var(--space-lg);
}

.accounts-grid-items {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.account-item-card {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.account-item-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
}

.account-item-card.active-account {
  border: 1.5px solid rgba(108, 99, 255, 0.45) !important;
  background: rgba(99, 102, 241, 0.08) !important;
  box-shadow: var(--shadow-glow);
}

.account-item-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.account-item-info {
  display: flex;
  flex-direction: column;
}

.account-item-email {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
  word-break: break-all;
}

.account-item-status {
  font-size: var(--text-xs);
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-2xl) var(--space-lg);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.01);
  border: 1px dashed var(--border-subtle);
  border-radius: var(--radius-lg);
  flex: 1;
}

.empty-icon {
  margin-bottom: var(--space-md);
  color: var(--text-tertiary);
}

.empty-state h3 {
  font-size: var(--text-base);
  margin-bottom: var(--space-xs);
  color: var(--text-primary);
}

.empty-state p {
  font-size: var(--text-xs);
  max-width: 280px;
  margin: 0;
}

.action-btn-row {
  margin-top: auto;
}

.full-width {
  width: 100%;
}

/* Drive Details Card Column */
.drive-details-loading,
.drive-details-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-secondary);
  flex: 1;
  gap: var(--space-md);
}

.drive-details-empty p {
  font-size: var(--text-sm);
  max-width: 260px;
}

.drive-details-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  flex: 1;
}

.details-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: var(--space-sm);
}

.drive-storage-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

@media (max-width: 480px) {
  .drive-storage-grid {
    grid-template-columns: 1fr;
  }
}

.storage-stats-card {
  padding: var(--space-md);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  text-align: center;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
}

.stat-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.stat-value-text {
  font-size: var(--text-md);
  font-family: var(--font-mono);
  color: var(--text-primary);
  font-weight: 700;
}

/* Drive Folders List Embedded Section */
.drive-folders-list-section {
  padding: var(--space-lg);
  background: rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.04);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.folders-header-row h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  margin-bottom: var(--space-md);
  color: var(--text-secondary);
}

.folders-error-state {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-md);
  background: rgba(239, 68, 68, 0.08);
  border: 1.5px solid rgba(239, 68, 68, 0.25);
  border-radius: var(--radius-md);
  color: #fca5a5;
  font-size: var(--text-xs);
}

.folders-empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: var(--text-tertiary);
  font-size: var(--text-xs);
  flex: 1;
  padding: var(--space-xl);
}

.cloud-folders-ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2xs);
  max-height: 180px;
  overflow-y: auto;
}

.cloud-folder-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.cloud-folder-name {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ═══════════ LIVE DRIVE Sync Queue List Styles ═══════════ */
.sync-queue-container {
  width: 100%;
  margin-top: 14px;
  display: flex;
  flex-direction: column;
}

.queue-header-mini {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 8px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.queue-item {
  border-radius: var(--radius-md);
  padding: 10px 14px;
  border: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  gap: 8px;
}

.queue-item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
}

.icon-success {
  color: var(--color-success);
  font-weight: 700;
  font-size: 0.9rem;
}

.icon-failed {
  color: #ef4444;
  font-weight: 700;
  font-size: 0.9rem;
}

.spinner-tiny {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--color-primary-light);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.queue-item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.queue-item-name {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-primary);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin: 0;
  text-align: left;
}

.queue-item-size {
  font-size: 0.6rem;
  color: var(--text-tertiary);
  font-weight: 500;
}

.queue-item-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stage-badge {
  font-size: 0.58rem;
  font-weight: 700;
  padding: 2px 6px;
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
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-secondary);
  min-width: 26px;
  text-align: right;
}

.queue-progress-track {
  width: 100%;
  height: 3px;
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
  font-size: 0.65rem;
  font-weight: 700;
  padding: 3px 8px;
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
  transform: translateY(10px);
}

.queue-list-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes progressGlow {
  0% { box-shadow: 0 0 2px rgba(6, 182, 212, 0.2); }
  100% { box-shadow: 0 0 6px rgba(6, 182, 212, 0.5); }
}
</style>