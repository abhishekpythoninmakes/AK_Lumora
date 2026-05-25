<template>
  <div class="setup-page">
    <div class="setup-container">
      <div class="setup-card glass-strong gradient-border">
        <!-- Progress -->
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: '50%' }"></div>
        </div>
        <div class="setup-header">
          <div class="step-badge glass">
            <span class="gradient-text">Step 1 of 2</span>
          </div>
          <h2>Set Up Your Studio</h2>
          <p>Tell us about your photography studio</p>
        </div>

        <form @submit.prevent="handleSubmit" class="setup-form">
          <div class="input-group">
            <label for="studioName">Studio Name *</label>
            <input id="studioName" v-model="studioName" type="text" class="input input-neu" placeholder="e.g., Golden Frame Studios" required />
          </div>

          <!-- Profile Image -->
          <div class="input-group">
            <label>Studio Logo (Optional)</label>
            <div class="upload-zone neu-inset" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="handleDrop">
              <input ref="fileInput" type="file" accept="image/*" @change="handleFileChange" hidden />
              <div v-if="!previewUrl" class="upload-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-tertiary)" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>Click or drag to upload</span>
              </div>
              <div v-else class="upload-preview">
                <img :src="previewUrl" alt="Studio logo" />
                <button type="button" class="remove-btn" @click.stop="removeImage">✕</button>
              </div>
            </div>
          </div>

          <!-- Phone -->
          <div class="input-group">
            <label for="phone">Phone Number *</label>
            <div class="phone-row">
              <select v-model="countryCode" class="input input-neu country-select">
                <option v-for="c in countryCodes" :key="c.code" :value="c.code">{{ c.flag }} {{ c.code }}</option>
              </select>
              <input id="phone" v-model="phoneNumber" type="tel" class="input input-neu" placeholder="9876543210" required />
            </div>
          </div>

          <button type="submit" class="btn btn-primary btn-lg" style="width:100%" :disabled="loading">
            {{ loading ? 'Saving...' : 'Continue to Drive Setup' }}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showToast = inject('showToast')

const studioName = ref('')
const phoneNumber = ref('')
const countryCode = ref('+91')
const profileImage = ref(null)
const previewUrl = ref(null)
const loading = ref(false)

const countryCodes = [
  { code: '+91', flag: '🇮🇳' }, { code: '+1', flag: '🇺🇸' }, { code: '+44', flag: '🇬🇧' },
  { code: '+61', flag: '🇦🇺' }, { code: '+81', flag: '🇯🇵' }, { code: '+49', flag: '🇩🇪' },
  { code: '+33', flag: '🇫🇷' }, { code: '+86', flag: '🇨🇳' }, { code: '+971', flag: '🇦🇪' },
  { code: '+65', flag: '🇸🇬' }, { code: '+60', flag: '🇲🇾' }, { code: '+966', flag: '🇸🇦' },
]

function handleFileChange(e) {
  const file = e.target.files[0]
  if (file) {
    profileImage.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function handleDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    profileImage.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function removeImage() {
  profileImage.value = null
  previewUrl.value = null
}

async function handleSubmit() {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('user_id', authStore.user.id)
    formData.append('studio_name', studioName.value)
    formData.append('phone_number', phoneNumber.value)
    formData.append('country_code', countryCode.value)
    if (profileImage.value) formData.append('profile_image', profileImage.value)

    await authStore.completeProfile(formData)
    showToast('Studio profile saved! 🎉', 'success')
    router.push('/drive-config')
  } catch (err) {
    showToast(err.message || 'Failed to save profile', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.setup-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: var(--space-xl); position: relative; z-index: 1; }
.setup-container { width: 100%; max-width: 520px; }
.setup-card { padding: var(--space-2xl); position: relative; overflow: hidden; }
.progress-bar { height: 4px; background: var(--bg-glass); border-radius: 2px; margin-bottom: var(--space-2xl); overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-secondary)); border-radius: 2px; transition: width 0.5s ease; }
.setup-header { text-align: center; margin-bottom: var(--space-2xl); }
.step-badge { display: inline-block; padding: var(--space-xs) var(--space-md); border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: 600; margin-bottom: var(--space-md); }
.setup-header h2 { margin-bottom: var(--space-sm); }
.setup-header p { color: var(--text-secondary); font-size: var(--text-sm); }
.setup-form { display: flex; flex-direction: column; gap: var(--space-xl); }

.upload-zone { padding: var(--space-2xl); text-align: center; cursor: pointer; transition: all var(--transition-normal); min-height: 140px; display: flex; align-items: center; justify-content: center; }
.upload-zone:hover { box-shadow: var(--shadow-glow); }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: var(--space-md); }
.upload-placeholder span { color: var(--text-tertiary); font-size: var(--text-sm); }
.upload-preview { position: relative; }
.upload-preview img { width: 100px; height: 100px; border-radius: var(--radius-lg); object-fit: cover; }
.remove-btn { position: absolute; top: -8px; right: -8px; width: 24px; height: 24px; border-radius: 50%; background: var(--color-error); color: white; border: none; cursor: pointer; font-size: 12px; display: flex; align-items: center; justify-content: center; }

.phone-row { display: flex; gap: var(--space-md); }
.country-select { width: 120px; flex-shrink: 0; }
</style>
