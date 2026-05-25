<template>
  <div class="login-page">
    <!-- Animated Background -->
    <div class="login-bg" aria-hidden="true">
      <div class="lens-flare lens-1"></div>
      <div class="lens-flare lens-2"></div>
      <div class="aperture-ring"></div>
      <div class="film-strip"></div>
    </div>

    <div class="login-container">
      <!-- Left Panel — Branding -->
      <div class="login-panel-left">
        <div class="panel-content">
          <div class="camera-icon float">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="url(#camGrad)" stroke-width="1">
              <defs><linearGradient id="camGrad" x1="0" y1="0" x2="24" y2="24"><stop offset="0%" stop-color="#6C63FF"/><stop offset="100%" stop-color="#FF6B9D"/></linearGradient></defs>
              <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
          </div>
          <h1>AK <span class="gradient-text">Lumora</span></h1>
          <p class="tagline">Where Every Frame Tells a Story</p>
          <div class="feature-pills">
            <span class="pill glass">📸 Live Sharing</span>
            <span class="pill glass">☁️ Cloud Sync</span>
            <span class="pill glass">📱 QR Downloads</span>
          </div>
        </div>
      </div>

      <!-- Right Panel — Google Login Only -->
      <div class="login-panel-right">
        <div class="login-form-wrapper glass-strong">
          <!-- Elegant Glass Back to Home Page Button -->
          <button class="back-btn" @click="router.push('/')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            <span>Back to Home Page</span>
          </button>

          <div class="form-header">
            <h2>Welcome to AK Lumora</h2>
            <p class="animated-message">
              Sign in using your <span class="google-highlight">Google</span> account to access your creative studio and dashboard.
            </p>
          </div>

          <!-- Google Auth Button with Pulsing Glow Ring & Metallic Shimmer -->
          <div class="google-btn-wrapper">
            <div class="glow-ring"></div>
            <button class="google-btn premium-btn shimmer-btn" @click="handleGoogleLogin" :disabled="loading">
              <div class="shimmer-layer"></div>
              <svg class="google-icon" width="22" height="22" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              <span class="btn-text">{{ loading ? 'Connecting...' : 'Continue with Google' }}</span>
            </button>
          </div>

          <p v-if="error" class="error-msg">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { signInWithGoogle } from '../composables/useFirebase'

const router = useRouter()
const authStore = useAuthStore()
const showToast = inject('showToast')

const loading = ref(false)
const error = ref('')

async function handleGoogleLogin() {
  loading.value = true
  error.value = ''
  try {
    const { idToken } = await signInWithGoogle()
    const user = await authStore.firebaseLogin(idToken)
    showToast('Welcome to AK Lumora! 🎉', 'success')
    navigateAfterLogin(user)
  } catch (err) {
    error.value = err.message || 'Google sign-in failed'
    showToast('Sign-in failed. Please try again.', 'error')
  } finally {
    loading.value = false
  }
}

function navigateAfterLogin(user) {
  if (!user.profile_completed) {
    router.push('/setup')
  } else if (!user.drive_configured) {
    router.push('/drive-config')
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1; padding: var(--space-lg); }

/* Background */
.login-bg { position: fixed; inset: 0; pointer-events: none; overflow: hidden; }
.lens-flare { position: absolute; border-radius: 50%; filter: blur(80px); }
.lens-1 { width: 500px; height: 500px; background: rgba(108,99,255,0.1); top: -10%; right: -10%; animation: orbFloat 15s ease-in-out infinite; }
.lens-2 { width: 400px; height: 400px; background: rgba(255,107,157,0.08); bottom: -15%; left: -5%; animation: orbFloat 20s ease-in-out infinite reverse; }
.aperture-ring { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); width: 600px; height: 600px; border: 1px solid rgba(108,99,255,0.05); border-radius: 50%; animation: spin 60s linear infinite; }
.film-strip { position: absolute; bottom: 0; left: 0; right: 0; height: 4px; background: repeating-linear-gradient(90deg, rgba(108,99,255,0.1) 0 20px, transparent 20px 40px); }

/* Container */
.login-container { display: grid; grid-template-columns: 1fr 1fr; max-width: 1000px; width: 100%; min-height: 520px; border-radius: var(--radius-2xl); overflow: hidden; position: relative; z-index: 1; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4); }

/* Left Panel */
.login-panel-left { background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%); display: flex; align-items: center; justify-content: center; padding: var(--space-3xl); position: relative; overflow: hidden; }
.login-panel-left::before { content: ''; position: absolute; inset: 0; background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236C63FF' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"); }
.panel-content { text-align: center; position: relative; z-index: 1; }
.camera-icon { margin-bottom: var(--space-xl); }
.panel-content h1 { font-size: var(--text-4xl); margin-bottom: var(--space-md); }
.tagline { color: var(--text-secondary); font-size: var(--text-lg); margin-bottom: var(--space-2xl); font-style: italic; }
.feature-pills { display: flex; flex-wrap: wrap; gap: var(--space-sm); justify-content: center; }
.pill { padding: var(--space-sm) var(--space-md); border-radius: var(--radius-full); font-size: var(--text-xs); color: var(--text-secondary); }

/* Right Panel */
.login-panel-right { display: flex; align-items: center; justify-content: center; padding: var(--space-2xl); background: var(--bg-primary); }
.login-form-wrapper { width: 100%; max-width: 400px; padding: var(--space-2xl); border-radius: var(--radius-xl); display: flex; flex-direction: column; }
.form-header { text-align: center; margin-bottom: var(--space-xl); }
.form-header h2 { font-size: var(--text-2xl); margin-bottom: var(--space-md); font-weight: 700; color: var(--text-primary); }

/* Animated Message & Google Highlight */
.animated-message {
  font-size: var(--text-md);
  line-height: 1.6;
  color: var(--text-secondary);
  animation: fadeIn 1.2s ease-out;
}
.google-highlight {
  font-weight: 700;
  background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC05, #34A853);
  background-size: 300% 300%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientShift 6s ease infinite;
}

/* Premium Google Button with Glowing Neon Pulse & Sliding Shimmer */
.google-btn-wrapper {
  position: relative;
  width: 100%;
  margin: var(--space-md) 0 var(--space-lg) 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
.glow-ring {
  position: absolute;
  inset: -3px;
  background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC05, #34A853);
  background-size: 200% 200%;
  border-radius: var(--radius-xl);
  filter: blur(12px);
  opacity: 0.7;
  animation: pulseGlow 2.5s ease-in-out infinite, gradientShift 6s ease infinite;
  z-index: 0;
  pointer-events: none;
}
.premium-btn {
  position: relative;
  width: 100%;
  z-index: 1;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: var(--radius-xl);
  padding: var(--space-md) var(--space-xl);
  font-size: var(--text-md);
  font-weight: 600;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-md);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.premium-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.28);
  transform: translateY(-2px);
}
.premium-btn:active {
  transform: translateY(1px);
}
.premium-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
.google-icon {
  z-index: 2;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.15));
}
.btn-text {
  z-index: 2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Shimmer Layer */
.shimmer-btn .shimmer-layer {
  position: absolute;
  top: 0;
  left: -150%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.12) 30%,
    rgba(255, 255, 255, 0.32) 50%,
    rgba(255, 255, 255, 0.12) 70%,
    transparent
  );
  transform: skewX(-25deg);
  animation: shine 3.5s ease-in-out infinite;
}

/* Back Button */
.back-btn {
  align-self: flex-start;
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  padding: var(--space-xs) var(--space-md);
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: 500;
  cursor: pointer;
  margin-bottom: var(--space-xl);
  transition: all 0.2s ease;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.back-btn:hover {
  background: rgba(255, 255, 255, 0.09);
  color: var(--text-primary);
  border-color: rgba(255, 255, 255, 0.16);
  transform: translateX(-3px);
}
.back-btn svg {
  transition: transform 0.2s ease;
}
.back-btn:hover svg {
  transform: translateX(-2px);
}

/* Error */
.error-msg { text-align: center; color: var(--color-error); font-size: var(--text-sm); margin-top: var(--space-md); padding: var(--space-sm) var(--space-md); background: rgba(239,68,68,0.1); border-radius: var(--radius-sm); z-index: 2; }

/* Animations */
@keyframes shine {
  0% { left: -150%; }
  35% { left: 150%; }
  100% { left: 150%; }
}
@keyframes pulseGlow {
  0%, 100% { transform: scale(1.00); filter: blur(10px); opacity: 0.6; }
  50% { transform: scale(1.03); filter: blur(14px); opacity: 0.8; }
}
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Mobile */
@media (max-width: 768px) {
  .login-container { grid-template-columns: 1fr; min-height: auto; }
  .login-panel-left { display: none; }
  .login-form-wrapper { padding: var(--space-xl); }
}
</style>
