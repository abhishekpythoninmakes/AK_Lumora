<template>
  <div class="oauth-callback-page">
    <div class="glass-card callback-card">
      <div v-if="loading" class="status-content">
        <svg class="spin" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="2">
          <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
        </svg>
        <h3>Authenticating with Google...</h3>
        <p>Please wait while we securely connect your Drive.</p>
      </div>

      <div v-else-if="success" class="status-content">
        <div class="success-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="1.5">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <h3>Google Drive Connected! 🎉</h3>
        <p>Your authorization was successful.</p>
        <button class="btn btn-primary btn-lg" @click="$router.push('/dashboard/drive')" style="margin-top: var(--space-xl)">
          Go to Dashboard
        </button>
      </div>

      <div v-else class="status-content">
        <div class="error-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--color-error)" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="15" y1="9" x2="9" y2="15"/>
            <line x1="9" y1="9" x2="15" y2="15"/>
          </svg>
        </div>
        <h3>Authentication Failed</h3>
        <p class="error-msg">{{ errorMessage }}</p>
        <div class="actions" style="margin-top: var(--space-xl); display: flex; gap: var(--space-md); justify-content: center">
          <button class="btn btn-secondary" @click="$router.push('/dashboard/drive')">Try Again</button>
          <button class="btn btn-primary" @click="$router.push('/dashboard/drive')">Dashboard</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../utils/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const showToast = inject('showToast')

const loading = ref(true)
const success = ref(false)
const errorMessage = ref('')

onMounted(async () => {
  const code = route.query.code
  const error = route.query.error

  if (error) {
    loading.value = false
    errorMessage.value = `Google returned an error: ${error}`
    return
  }

  if (!code) {
    loading.value = false
    errorMessage.value = "No authorization code found in the URL."
    return
  }

  try {
    const formData = new FormData()
    formData.append('user_id', authStore.user.id)
    formData.append('code', code)
    formData.append('redirect_uri', window.location.origin + '/oauth-callback')
    
    const codeVerifier = sessionStorage.getItem('oauth_code_verifier')
    if (codeVerifier) {
      formData.append('code_verifier', codeVerifier)
    }

    await api.post('/api/drive/callback', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    success.value = true
    showToast('Google Drive authenticated successfully! ✅', 'success')
    
    // Automatically redirect after 2 seconds
    setTimeout(() => {
      if (router.currentRoute.value.path === '/oauth-callback') {
        router.push('/dashboard/drive')
      }
    }, 2000)
    
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Failed to exchange authorization code.'
    showToast('Authentication failed', 'error')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.oauth-callback-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: var(--space-xl); }
.callback-card { width: 100%; max-width: 480px; padding: var(--space-2xl); text-align: center; }
.status-content { display: flex; flex-direction: column; align-items: center; gap: var(--space-md); }
.success-icon { animation: bounce 0.6s ease; margin-bottom: var(--space-md); }
.error-icon { margin-bottom: var(--space-md); }
.error-msg { color: var(--color-error); font-size: var(--text-sm); margin-top: var(--space-sm); }
p { color: var(--text-secondary); }
</style>
