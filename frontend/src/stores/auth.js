import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('ak_token') || null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value)
  const isProfileComplete = computed(() => user.value?.profile_completed ?? false)
  const isDriveConfigured = computed(() => user.value?.drive_configured ?? false)
  const showTutorial = computed(() => user.value && !user.value.first_login_tutorial)

  function isBackendOffline() {
    return localStorage.getItem('ak_backend_offline') === '1'
  }

  async function firebaseLogin(idToken) {
    loading.value = true
    try {
      const { data } = await api.post('/api/auth/firebase-login', { id_token: idToken })
      token.value = data.access_token
      user.value = data.user
      localStorage.setItem('ak_token', data.access_token)
      localStorage.setItem('ak_user', JSON.stringify(data.user))
      return data.user
    } finally {
      loading.value = false
    }
  }

  async function completeProfile(formData) {
    loading.value = true
    try {
      const { data } = await api.post('/api/auth/complete-profile', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      user.value = data
      localStorage.setItem('ak_user', JSON.stringify(data))
      return data
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(formData) {
    loading.value = true
    try {
      const { data } = await api.put('/api/auth/update-profile', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      user.value = data
      localStorage.setItem('ak_user', JSON.stringify(data))
      return data
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    if (!user.value?.id) {
      const stored = localStorage.getItem('ak_user')
      if (stored) user.value = JSON.parse(stored)
      return
    }
    if (isBackendOffline()) return
    try {
      const { data } = await api.get(`/api/auth/me?user_id=${user.value.id}`)
      user.value = data
      localStorage.setItem('ak_user', JSON.stringify(data))
    } catch (err) {
      if (!err?.response) localStorage.setItem('ak_backend_offline', '1')
    }
  }

  async function markTutorialComplete() {
    if (!user.value?.id) return
    await api.put(`/api/auth/tutorial-complete?user_id=${user.value.id}`)
    user.value.first_login_tutorial = true
    localStorage.setItem('ak_user', JSON.stringify(user.value))
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('ak_token')
    localStorage.removeItem('ak_user')
  }

  // Restore on init
  const storedUser = localStorage.getItem('ak_user')
  if (storedUser) user.value = JSON.parse(storedUser)

  return {
    user, token, loading,
    isAuthenticated, isProfileComplete, isDriveConfigured, showTutorial,
    firebaseLogin, completeProfile, updateProfile, fetchUser, markTutorialComplete, logout,
  }
})
