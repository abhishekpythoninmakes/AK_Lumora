<template>
  <div id="ak-lumora-app">
    <!-- Background Orbs -->
    <div class="bg-orbs" aria-hidden="true">
      <div class="bg-orb bg-orb-primary" style="top:-10%;left:-5%"></div>
      <div class="bg-orb bg-orb-secondary" style="top:40%;right:-10%"></div>
      <div class="bg-orb bg-orb-accent" style="bottom:-5%;left:30%"></div>
    </div>

    <!-- Toast Container -->
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div v-for="toast in toasts" :key="toast.id" :class="['toast', `toast-${toast.type}`]">
        <span class="toast-icon">{{ toast.type === 'success' ? '✓' : toast.type === 'error' ? '✕' : 'ℹ' }}</span>
        <span>{{ toast.message }}</span>
      </div>
    </TransitionGroup>

    <!-- Router View with Page Transition -->
    <router-view v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="route.path" />
      </Transition>
    </router-view>
  </div>
</template>

<script setup>
import { ref, provide, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

// Toast system
const toasts = ref([])
let toastId = 0

function showToast(message, type = 'info', duration = 4000) {
  const id = ++toastId
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

provide('showToast', showToast)

onMounted(() => {
  authStore.fetchUser()
})
</script>

<style>
#ak-lumora-app {
  position: relative;
  min-height: 100vh;
  overflow-x: hidden;
}

.bg-orbs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.toast-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.toast-success .toast-icon { background: rgba(16,185,129,0.2); color: var(--color-success); }
.toast-error .toast-icon { background: rgba(239,68,68,0.2); color: var(--color-error); }
.toast-info .toast-icon { background: rgba(59,130,246,0.2); color: var(--color-info); }
</style>
