<template>
  <div class="drive-config-page">
    <div class="setup-container">
      <div class="setup-card glass-strong gradient-border">
        <div class="setup-header">
          <h2>Google Drive Configuration</h2>
          <p>Manage connected Drive accounts, available folders, and storage status.</p>
        </div>

        <div class="accounts-list">
          <div v-if="loadingAccounts" class="test-item">
            <svg class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            <span class="test-name">Loading Drive accounts...</span>
          </div>

          <div v-else-if="accounts.length === 0" class="empty-state">
            <h3>No connected Drive accounts</h3>
            <p>Connect a Google Drive account to begin uploading and sharing images live.</p>
          </div>

          <div v-else>
            <div v-for="account in accounts" :key="account.id" :class="['test-item', account.id === selectedAccountId ? 'active-account' : '']" @click="selectAccount(account.id)">
              <div class="test-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              </div>
              <div class="test-info">
                <span class="test-name">{{ account.email || 'Connected Account' }}</span>
                <span class="test-error" :style="{ color: account.connected ? 'var(--color-success)' : 'var(--color-warning)' }">
                  {{ account.connected ? 'Connected' : 'Sign-in required' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="selectedAccount" class="account-details">
          <div class="status-row">
            <div>
              <span class="detail-label">Account</span>
              <span class="detail-value">{{ selectedAccount.email }}</span>
            </div>
            <div>
              <span class="detail-label">Status</span>
              <span class="badge" :class="selectedAccount.connected ? 'badge-success' : 'badge-warning'">
                {{ selectedAccount.connected ? 'Connected' : 'Reconnect needed' }}
              </span>
            </div>
          </div>

          <div class="storage-grid">
            <div class="storage-card glass-card">
              <span>Used</span>
              <strong>{{ formatBytes(selectedAccount.storage?.used_bytes || 0) }}</strong>
            </div>
            <div class="storage-card glass-card">
              <span>Total</span>
              <strong>{{ formatBytes(selectedAccount.storage?.total_bytes || 0) }}</strong>
            </div>
            <div class="storage-card glass-card">
              <span>Available</span>
              <strong>{{ formatBytes(selectedAccount.storage?.free_bytes || 0) }}</strong>
            </div>
          </div>

          <div class="folder-list">
            <h3>Available Drive folders</h3>
            <div v-if="loadingFolders" class="folder-loading">Loading folders...</div>
            <div v-else-if="driveFolders.length === 0" class="folder-empty">No Drive folders found for this account.</div>
            <ul v-else>
              <li v-for="folder in driveFolders" :key="folder.id">{{ folder.name }}</li>
            </ul>
          </div>
        </div>

        <div class="action-row">
          <button class="btn btn-primary btn-lg" @click="authorizeGoogle" :disabled="loading">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            {{ loading ? 'Redirecting...' : 'Connect another Drive account' }}
          </button>
          <button class="btn btn-secondary btn-lg" @click="$router.push('/dashboard')">
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'

const authStore = useAuthStore()
const showToast = inject('showToast')

const loading = ref(false)
const loadingAccounts = ref(true)
const loadingFolders = ref(false)
const accounts = ref([])
const selectedAccountId = ref(null)
const driveFolders = ref([])

const selectedAccount = ref(null)

onMounted(async () => {
  await fetchAccounts()
})

watch(selectedAccountId, async (newId) => {
  if (newId) {
    await fetchDriveFolders(newId)
  }
}, { immediate: true })

function getCurrentUserId() {
  return authStore.user?.id || JSON.parse(localStorage.getItem('ak_user') || '{}')?.id
}

async function fetchAccounts() {
  loadingAccounts.value = true
  const userId = getCurrentUserId()
  if (!userId) {
    showToast('Unable to determine current user', 'error')
    loadingAccounts.value = false
    return
  }

  try {
    const { data } = await api.get(`/api/drive/accounts?user_id=${userId}`)
    accounts.value = data
    if (data.length > 0) {
      selectedAccountId.value = data[0].id
    }
  } catch (err) {
    showToast('Failed to load connected accounts', 'error')
  } finally {
    loadingAccounts.value = false
  }
}

async function fetchDriveFolders(accountId) {
  loadingFolders.value = true
  const userId = getCurrentUserId()
  if (!userId) {
    selectedAccount.value = null
    driveFolders.value = []
    showToast('Unable to determine current user', 'error')
    loadingFolders.value = false
    return
  }

  try {
    const { data } = await api.get(`/api/drive/status?user_id=${userId}&drive_config_id=${accountId}`)
    selectedAccount.value = data
    driveFolders.value = data.folders || []
  } catch (err) {
    selectedAccount.value = null
    driveFolders.value = []
    showToast('Failed to load Drive folders', 'error')
  } finally {
    loadingFolders.value = false
  }
}

function selectAccount(accountId) {
  selectedAccountId.value = accountId
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

async function authorizeGoogle() {
  loading.value = true
  try {
    const redirectUri = window.location.origin + '/oauth-callback'
    const { data } = await api.get(`/api/drive/auth-url?redirect_uri=${encodeURIComponent(redirectUri)}`)
    if (data.code_verifier) {
      sessionStorage.setItem('oauth_code_verifier', data.code_verifier)
    }
    window.location.href = data.auth_url
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to generate auth URL', 'error')
    loading.value = false
  }
}
</script>

<style scoped>
.drive-config-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: var(--space-xl); position: relative; z-index: 1; }
.setup-container { width: 100%; max-width: 720px; }
.setup-card { padding: var(--space-2xl); position: relative; overflow: hidden; }
.setup-header { text-align: center; margin-bottom: var(--space-2xl); }
.setup-header p { color: var(--text-secondary); font-size: var(--text-sm); }
.accounts-list { display: flex; flex-direction: column; gap: var(--space-md); }
.test-item { display: flex; align-items: center; gap: var(--space-md); padding: var(--space-md); border-radius: var(--radius-md); background: var(--bg-glass); cursor: pointer; transition: transform var(--transition-normal); }
.test-item:hover { transform: translateY(-1px); }
.active-account { border: 1px solid rgba(108,99,255,0.35); background: rgba(99,102,241,0.08); }
.test-name { font-size: var(--text-sm); }
.test-error { font-size: var(--text-xs); display: block; }
.test-icon { flex-shrink: 0; }
.empty-state { text-align: center; color: var(--text-tertiary); padding: var(--space-xl); background: var(--bg-glass); border-radius: var(--radius-md); }
.account-details { margin-top: var(--space-2xl); }
.status-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-lg); margin-bottom: var(--space-xl); }
.detail-label { display: block; color: var(--text-secondary); font-size: var(--text-xs); margin-bottom: var(--space-2xs); }
.detail-value { font-family: var(--font-mono); font-size: var(--text-sm); }
.storage-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-md); margin-bottom: var(--space-xl); }
.storage-card { padding: var(--space-lg); border-radius: var(--radius-lg); background: rgba(255,255,255,0.04); text-align: center; }
.storage-card span { display: block; color: var(--text-secondary); font-size: var(--text-xs); margin-bottom: var(--space-2xs); }
.storage-card strong { font-size: var(--text-lg); }
.folder-list { padding: var(--space-lg); border-radius: var(--radius-lg); background: rgba(255,255,255,0.04); }
.folder-list h3 { margin-bottom: var(--space-sm); }
.folder-loading,
.folder-empty { color: var(--text-secondary); }
.folder-list ul { display: grid; gap: var(--space-2xs); list-style: none; padding: 0; margin: 0; }
.folder-list li { padding: var(--space-2xs) var(--space-sm); border-radius: var(--radius-md); background: rgba(255,255,255,0.03); }
.action-row { display: flex; flex-wrap: wrap; gap: var(--space-md); margin-top: var(--space-2xl); justify-content: center; }
@media (max-width: 768px) {
  .status-row,
  .storage-grid { grid-template-columns: 1fr; }
}
</style>
