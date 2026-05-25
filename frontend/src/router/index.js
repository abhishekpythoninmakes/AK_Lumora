import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue'),
  },
  {
    path: '/setup',
    name: 'StudioSetup',
    component: () => import('../views/StudioSetup.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/drive-config',
    redirect: '/dashboard/drive',
  },
  {
    path: '/dashboard/:section?',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/live',
    name: 'LivePresentation',
    component: () => import('../views/LivePresentation.vue'),
  },
  {
    path: '/oauth-callback',
    name: 'OAuthCallback',
    component: () => import('../views/OAuthCallback.vue'),
    // meta: { requiresAuth: true },
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/PrivacyView.vue'),
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('../views/TermsView.vue'),
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/ContactView.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0, behavior: 'smooth' }
  },
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('ak_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
