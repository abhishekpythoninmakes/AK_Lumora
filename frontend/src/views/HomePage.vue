<template>
  <div class="home-page">
    <!-- Navigation -->
    <nav class="nav glass" :class="{ 'nav-scrolled': scrolled }">
      <div class="container flex-between">
        <div class="nav-brand" @click="$router.push('/')">
          <img src="/logo.png" alt="AK Lumora Logo" style="width: 40px; height: 40px; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(108, 99, 255, 0.25));">
          <span class="brand-text">AK <span class="gradient-text">Lumora</span></span>
        </div>
        <div class="nav-links" :class="{ open: mobileMenu }">
          <a href="#features" @click="mobileMenu = false">Features</a>
          <a href="#how-it-works" @click="mobileMenu = false">How It Works</a>
          <a href="#pricing" @click="scrollToPricing">Pricing</a>
          <button class="btn btn-primary btn-sm" @click="$router.push('/login')">Get Started</button>
        </div>
        <button class="mobile-menu-btn btn-icon btn-ghost" @click="mobileMenu = !mobileMenu">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path v-if="!mobileMenu" d="M3 12h18M3 6h18M3 18h18"/>
            <path v-else d="M6 6l12 12M6 18L18 6"/>
          </svg>
        </button>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-grid"></div>
        <div class="hero-glow"></div>
        <div class="ambient-blob ambient-blob-1"></div>
        <div class="ambient-blob ambient-blob-2"></div>
      </div>
      <div class="container hero-content">
        <div class="hero-badge glass" ref="heroBadge">
          <span class="badge-dot"></span>
          <span>Built for Professional Studios</span>
        </div>
        <h1 class="hero-title" ref="heroTitle">
          Elevate Your<br>
          <span class="gradient-text">Photography Studio</span><br>
          Experience
        </h1>
        <p class="hero-subtitle" ref="heroSubtitle">
          Seamlessly manage, share, and present your photos in real-time.
          Powered by Google Drive integration and live studio presentations.
        </p>
        <div class="hero-actions" ref="heroActions">
          <button class="btn btn-primary btn-lg ripple" @click="$router.push('/login')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            Get Started Free
          </button>
          <button class="btn btn-secondary btn-lg" @click="scrollToFeatures">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            Watch Demo
          </button>
        </div>
        <div class="hero-stats" ref="heroStats">
          <div class="stat-item glass-card">
            <span class="stat-number gradient-text">500+</span>
            <span class="stat-label">Studios</span>
          </div>
          <div class="stat-item glass-card">
            <span class="stat-number gradient-text">1M+</span>
            <span class="stat-label">Photos Shared</span>
          </div>
          <div class="stat-item glass-card">
            <span class="stat-number gradient-text">99.9%</span>
            <span class="stat-label">Uptime</span>
          </div>
        </div>

        <!-- Glassmorphic Mockup Showcase -->
        <div class="hero-mockup glass-strong" ref="heroMockup">
          <div class="mockup-header">
            <div class="window-dots">
              <span class="dot dot-red"></span>
              <span class="dot dot-yellow"></span>
              <span class="dot dot-green"></span>
            </div>
            <div class="mockup-tab active">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; vertical-align: middle;"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <span>wedding_shoot_2026</span>
            </div>
            <div class="mockup-status">
              <span class="pulse-green"></span>
              <span style="font-size: 11px; font-weight: 600; letter-spacing: 0.05em; color: var(--color-success)">LIVE WATCHING</span>
            </div>
          </div>
          <div class="mockup-body">
            <aside class="mockup-sidebar">
              <div class="mockup-nav-item active">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
                <span>Dashboard</span>
              </div>
              <div class="mockup-nav-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
                <span>Monitored (2/20)</span>
              </div>
              <div class="mockup-nav-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                <span>Google Drive</span>
              </div>
            </aside>
            <div class="mockup-content">
              <div class="mockup-grid">
                <div class="mockup-card glass-card">
                  <div class="mockup-card-img img-1">
                    <span class="badge-raw">RAW</span>
                  </div>
                  <div class="mockup-card-info">
                    <span class="img-name">DSC_9821.NEF</span>
                    <div class="img-meta">
                      <span class="img-size">48.2 MB</span>
                      <span class="img-status synced">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                        Synced
                      </span>
                    </div>
                  </div>
                </div>
                <div class="mockup-card glass-card">
                  <div class="mockup-card-img img-2">
                    <span class="badge-raw">RAW</span>
                  </div>
                  <div class="mockup-card-info">
                    <span class="img-name">DSC_9822.NEF</span>
                    <div class="img-meta">
                      <span class="img-size">51.4 MB</span>
                      <span class="img-status synced">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                        Synced
                      </span>
                    </div>
                  </div>
                </div>
                <div class="mockup-card glass-card">
                  <div class="mockup-card-img img-3">
                    <span class="badge-raw">RAW</span>
                  </div>
                  <div class="mockup-card-info">
                    <span class="img-name">DSC_9823.NEF</span>
                    <div class="img-meta">
                      <span class="img-size">47.8 MB</span>
                      <span class="img-status syncing">
                        <svg class="spin" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                        Syncing
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Camera Elements -->
      <div class="floating-elements" aria-hidden="true">
        <div class="float-el float-el-1 float">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5" opacity="0.3">
            <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
        </div>
        <div class="float-el float-el-2 float" style="animation-delay:-1.5s">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="var(--color-secondary)" stroke-width="1.5" opacity="0.25">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <div class="float-el float-el-3 float" style="animation-delay:-3s">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="1.5" opacity="0.2">
            <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
            <circle cx="12" cy="13" r="3"/>
          </svg>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag gradient-text">FEATURES</span>
          <h2>Everything Your Studio Needs</h2>
          <p class="section-desc">From real-time monitoring to instant QR sharing, we've got you covered.</p>
        </div>
        <div class="features-grid">
          <div v-for="(feature, i) in features" :key="i"
               class="feature-card glass-card"
               :style="{ animationDelay: `${i * 0.1}s` }">
            <div class="feature-icon" :style="{ background: feature.gradient }">
              <span v-html="feature.icon"></span>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="how-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag gradient-text">HOW IT WORKS</span>
          <h2>Simple. Powerful. Beautiful.</h2>
        </div>
        <div class="steps-container">
          <div v-for="(step, i) in steps" :key="i" class="step-item">
            <div class="step-number gradient-border">
              <span class="gradient-text">{{ String(i + 1).padStart(2, '0') }}</span>
            </div>
            <div class="step-content glass-card">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
            <div v-if="i < steps.length - 1" class="step-connector"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- Reviews Section -->
    <section class="reviews-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag gradient-text">TESTIMONIALS</span>
          <h2>Loved by Photographers</h2>
          <p class="section-desc">See how studios and event creators are streamlining their live delivery pipelines with AK Lumora.</p>
        </div>
      </div>
      
      <!-- Infinite Horizontally Scrolling Marquee -->
      <div class="reviews-marquee">
        <div class="marquee-track">
          <!-- Slide List (Double the list in markup for seamless infinite looping!) -->
          <div v-for="n in 2" :key="n" class="marquee-slide">
            <div v-for="(review, idx) in reviews" :key="idx" class="review-card glass-card">
              <div class="stars">
                <svg v-for="star in 5" :key="star" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <p class="review-comment">"{{ review.comment }}"</p>
              <div class="review-user">
                <div class="avatar" :style="{ background: review.bg }">{{ review.initials }}</div>
                <div class="user-meta">
                  <span class="user-name">{{ review.name }}</span>
                  <span class="user-role">{{ review.role }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Section -->
    <section id="pricing" class="pricing-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag gradient-text">PRICING</span>
          <h2>Simple, Credit-Based Plans</h2>
          <p class="section-desc">No expensive flat rates. Pay for the photos you actually watch, compress, and sync. Rollover unused credits.</p>
          
          <!-- Billing Cycle Switcher -->
          <div class="pricing-toggle-wrapper">
            <span class="toggle-label" :class="{ active: !isAnnual }">Monthly</span>
            <button class="pricing-toggle-btn" @click="isAnnual = !isAnnual" aria-label="Toggle billing cycle">
              <span class="toggle-slider" :class="{ annual: isAnnual }"></span>
            </button>
            <span class="toggle-label" :class="{ active: isAnnual }">
              Yearly
              <span class="discount-pill">Save 20%</span>
            </span>
          </div>
        </div>

        <div class="pricing-grid">
          <div v-for="plan in plans" :key="plan.id" class="pricing-card glass-card" :class="{ 'popular-glow': plan.popular }">
            <div v-if="plan.popular" class="popular-badge">MOST POPULAR</div>
            
            <div class="plan-header">
              <div class="plan-icon" :style="{ background: plan.gradient, color: plan.color }">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path v-if="plan.id === 'lite'" d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
                  <path v-else-if="plan.id === 'pro'" d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  <path v-else d="M12 22s8-4 8-10V5l-8-3-8 3v7s0 6 8 10z"/>
                </svg>
              </div>
              <h3 class="plan-name">{{ plan.name }}</h3>
              <p class="plan-desc">{{ plan.desc }}</p>
            </div>

            <div class="plan-price-block">
              <div class="plan-price">
                <span class="currency">$</span>
                <span class="price-value">{{ isAnnual ? plan.annualPrice : plan.monthlyPrice }}</span>
                <span class="period">/mo</span>
              </div>
              <span class="billed-annually-detail" v-if="isAnnual">Billed ${{ plan.annualPrice * 12 }}/year</span>
              <span class="billed-annually-detail" v-else>Billed monthly</span>
            </div>

            <div class="plan-credits-showcase glass">
              <div class="credits-count gradient-text">{{ plan.credits }}</div>
              <div class="credits-label">Sync Credits / mo</div>
              <div class="credits-cost">Avg. {{ plan.avgCost }} per photo sync</div>
            </div>

            <ul class="plan-features">
              <li v-for="(feat, idx) in plan.features" :key="idx">
                <svg class="feat-check" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="3">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                <span>{{ feat }}</span>
              </li>
            </ul>

            <button class="btn btn-block" :class="plan.popular ? 'btn-primary ripple' : 'btn-secondary'" @click="$router.push('/login')">
              {{ plan.btnText }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="container">
        <div class="cta-card glass-strong gradient-border">
          <h2>Ready to Transform Your Studio?</h2>
          <p>Join hundreds of professional photographers who trust AK Lumora.</p>
          <button class="btn btn-primary btn-lg ripple" @click="$router.push('/login')">
            Start Your Free Trial
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="container flex-between">
        <div class="footer-brand">
          <span class="brand-text">AK <span class="gradient-text">Lumora</span></span>
          <p>© 2026 AK Lumora. Crafted with ❤️ for photographers.</p>
        </div>
        <div class="footer-links">
          <a href="#" @click.prevent="$router.push('/privacy')">Privacy Policy</a>
          <a href="#" @click.prevent="$router.push('/terms')">Terms of Service</a>
          <a href="#" @click.prevent="$router.push('/contact')">Contact Us</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'

const scrolled = ref(false)
const mobileMenu = ref(false)
const heroTitle = ref(null)
const heroSubtitle = ref(null)
const heroActions = ref(null)
const heroStats = ref(null)
const heroBadge = ref(null)
const heroMockup = ref(null)

const isAnnual = ref(false)

const plans = ref([
  {
    id: 'lite',
    name: 'Studio Lite',
    desc: 'Perfect for single shooters, local portraits, or studio trials.',
    credits: '300',
    avgCost: '$0.05',
    monthlyPrice: 15,
    annualPrice: 12,
    features: [
      '300 Sync Credits / month',
      '2 Watched Folders active',
      'Zero-load client-side compression',
      'Google Drive secure sync pipeline',
      'Live Presentation Gallery (Basic)',
      'Standard download lanes'
    ],
    popular: false,
    btnText: 'Start Free Trial',
    gradient: 'linear-gradient(135deg, rgba(0, 210, 255, 0.2), rgba(0, 210, 255, 0.05))',
    color: 'var(--color-primary-light)'
  },
  {
    id: 'pro',
    name: 'Pro Studio',
    desc: 'Ideal for busy wedding, portrait, and event photographers.',
    credits: '1,500',
    avgCost: '$0.026',
    monthlyPrice: 39,
    annualPrice: 31,
    features: [
      '1,500 Sync Credits / month',
      '10 Watched Folders active',
      'Advanced fast JPEG parser',
      'Rollover unused credits (up to 3k)',
      'Branded Live Presentations (White-label)',
      'Priority Upload (3 concurrent tasks)',
      'High-speed RAW formats (CR3, ARW, NEF)',
      'Custom client QR code downloads'
    ],
    popular: true,
    btnText: 'Upgrade to Pro',
    gradient: 'linear-gradient(135deg, rgba(255, 107, 157, 0.25), rgba(255, 107, 157, 0.05))',
    color: 'var(--color-accent)'
  },
  {
    id: 'enterprise',
    name: 'Elite Agency',
    desc: 'For high-volume studios, agencies, and massive commercial shoots.',
    credits: '5,000',
    avgCost: '$0.015',
    monthlyPrice: 79,
    annualPrice: 63,
    features: [
      '5,000 Sync Credits / month',
      '30 Watched Folders active',
      'Dedicated high-speed sync lanes',
      'Face Recognition & Auto-grouping',
      'Unlimited Live Slideshow screens',
      'Extra credits just $0.01 / each',
      'Custom domain presentation galleries',
      '24/7 dedicated support priority'
    ],
    popular: false,
    btnText: 'Go Elite',
    gradient: 'linear-gradient(135deg, rgba(255, 179, 71, 0.2), rgba(255, 179, 71, 0.05))',
    color: 'rgba(255, 179, 71, 1)'
  }
])

function scrollToPricing(e) {
  if (e) e.preventDefault()
  mobileMenu.value = false
  document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })
}

const features = [
  { title: 'Live File Monitoring', description: 'Auto-detect new photos from up to 20 folders simultaneously with instant notifications.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>', gradient: 'linear-gradient(135deg, rgba(108,99,255,0.2), rgba(108,99,255,0.05))' },
  { title: 'Google Drive Sync', description: 'Automatic resumable uploads to Google Drive with zero backend load.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>', gradient: 'linear-gradient(135deg, rgba(0,210,255,0.2), rgba(0,210,255,0.05))' },
  { title: 'QR Code Sharing', description: 'Instant QR codes for every photo — guests download directly from Drive.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="4" height="4"/></svg>', gradient: 'linear-gradient(135deg, rgba(255,107,157,0.2), rgba(255,107,157,0.05))' },
  { title: 'Live Presentation', description: 'Real-time photo slideshow on a second monitor for guests at events.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>', gradient: 'linear-gradient(135deg, rgba(255,179,71,0.2), rgba(255,179,71,0.05))' },
  { title: 'RAW Format Support', description: 'Full support for CR2, NEF, ARW, DNG and all professional camera RAW formats.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>', gradient: 'linear-gradient(135deg, rgba(16,185,129,0.2), rgba(16,185,129,0.05))' },
  { title: 'Real-time Analytics', description: 'Live charts showing upload rates, download counts, and studio performance.', icon: '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>', gradient: 'linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05))' },
]

const steps = [
  { title: 'Create Your Studio', description: 'Sign up with Google and set up your studio profile in seconds.' },
  { title: 'Connect Google Drive', description: 'Configure your Drive credentials for direct cloud uploads.' },
  { title: 'Add Your Folders', description: 'Select up to 20 local folders to monitor for new photos.' },
  { title: 'Go Live!', description: 'Start the live presentation and let guests scan QR codes to download.' },
]

const reviews = [
  { name: 'Arjun K.', role: 'Wedding Studio Lead', comment: 'AK Lumora completely revolutionized our wedding workflows. Monitored folders instantly compress RAWs on the spot and upload to Drive in seconds. Clients scan the QR code and download their portraits immediately!', initials: 'AK', bg: 'rgba(108, 99, 255, 0.2)' },
  { name: 'Sarah M.', role: 'Event Photographer', comment: 'The client-side raw compression is absolute magic. We sync hundreds of ARW files over local event Wi-Fi without crushing our upload bandwidth. Saving on server flat rates with credit usage is a huge plus!', initials: 'SM', bg: 'rgba(0, 210, 255, 0.2)' },
  { name: 'Carlos R.', role: 'Commercial Director', comment: 'Our live gallery presentation is a massive hit at corporate events. Guests love watching the slideshow update live on a secondary screen as we capture. Very elegant, smooth, and professional!', initials: 'CR', bg: 'rgba(255, 107, 157, 0.2)' },
  { name: 'Priya S.', role: 'Studio Director', comment: 'No complex backend server overhead or RAW file safety concerns. Everything syncs straight to our own secure Google Drive. Credits are highly reasonable, cost-effective, and fully transparent.', initials: 'PS', bg: 'rgba(255, 179, 71, 0.2)' },
  { name: 'Marcus V.', role: 'Portrait Photographer', comment: 'We watch up to 10 folders simultaneously. The fast JPEG segment parser is unbelievably fast. We\'ve synced over 10,000 files in parallel without a single crash. Highly recommended!', initials: 'MV', bg: 'rgba(16, 185, 129, 0.2)' },
  { name: 'Jessica L.', role: 'Fashion Studio Owner', comment: 'Direct drive sync and client-side extraction saved us hours of post-production uploads. The custom guest presentation page adds a high-end premium signature to our photography packages.', initials: 'JL', bg: 'rgba(139, 92, 246, 0.2)' }
]

function handleScroll() {
  scrolled.value = window.scrollY > 50
}

function scrollToFeatures() {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)

  // GSAP hero animations
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.from(heroBadge.value, { y: -20, opacity: 0, duration: 0.6 })
    .from(heroTitle.value, { y: 40, opacity: 0, duration: 0.8 }, '-=0.3')
    .from(heroSubtitle.value, { y: 30, opacity: 0, duration: 0.6 }, '-=0.4')
    .from(heroActions.value, { y: 20, opacity: 0, duration: 0.5 }, '-=0.3')
    .from(heroStats.value?.children || [], { y: 30, opacity: 0, duration: 0.5, stagger: 0.1 }, '-=0.2')
    .from(heroMockup.value, { y: 60, opacity: 0, duration: 1, scale: 0.96 }, '-=0.4')

  // GSAP pricing card scroll trigger observer for smooth modern entrance animation
  const pricingSection = document.getElementById('pricing')
  if (pricingSection) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          gsap.from('.pricing-card', {
            y: 50,
            opacity: 0,
            duration: 0.8,
            stagger: 0.15,
            ease: 'power3.out'
          })
          observer.disconnect() // Run once
        }
      })
    }, { threshold: 0.1 })
    observer.observe(pricingSection)
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.home-page { position: relative; z-index: 1; }

/* Nav */
.nav { position: fixed; top: 0; left: 0; right: 0; z-index: var(--z-sticky); padding: var(--space-md) 0; transition: all var(--transition-normal); background: transparent; border: none; border-radius: 0; backdrop-filter: none; }
.nav-scrolled { background: rgba(10,10,26,0.8); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border-subtle); }
.nav-brand { display: flex; align-items: center; gap: var(--space-sm); cursor: pointer; }
.brand-icon { display: flex; }
.brand-text { font-family: var(--font-display); font-size: var(--text-xl); font-weight: 700; color: var(--text-primary); }
.nav-links { display: flex; align-items: center; gap: var(--space-xl); }
.nav-links a { color: var(--text-secondary); font-size: var(--text-sm); font-weight: 500; transition: color var(--transition-fast); }
.nav-links a:hover { color: var(--text-primary); }
.mobile-menu-btn { display: none; }

/* Hero */
.hero { position: relative; min-height: 100vh; display: flex; align-items: center; padding: 120px 0 80px; overflow: hidden; }
.hero-bg { position: absolute; inset: 0; pointer-events: none; }
.hero-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px); background-size: 60px 60px; mask-image: radial-gradient(ellipse at center, black 30%, transparent 70%); }
.hero-glow { position: absolute; top: 20%; left: 50%; transform: translateX(-50%); width: 800px; height: 400px; background: radial-gradient(ellipse, rgba(108,99,255,0.15) 0%, transparent 70%); filter: blur(60px); }

/* Ambient Blobs styling */
.ambient-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  pointer-events: none;
  opacity: 0.12;
}
.ambient-blob-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--color-primary) 0%, transparent 80%);
  top: 10%;
  left: 5%;
  animation: blobFloat 25s infinite ease-in-out alternate;
}
.ambient-blob-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 80%);
  bottom: 15%;
  right: 5%;
  animation: blobFloat 30s infinite ease-in-out alternate-reverse;
}

@keyframes blobFloat {
  0% {
    transform: translate(0, 0) scale(1) rotate(0deg);
  }
  50% {
    transform: translate(60px, -50px) scale(1.15) rotate(180deg);
  }
  100% {
    transform: translate(-40px, 40px) scale(0.9) rotate(360deg);
  }
}

/* Hero Mockup Showcase styling */
.hero-mockup {
  margin: var(--space-4xl) auto 0;
  max-width: 900px;
  width: 100%;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: var(--shadow-2xl), 0 20px 50px rgba(0, 0, 0, 0.5), var(--shadow-glow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: rgba(10, 10, 26, 0.6);
  backdrop-filter: blur(25px);
  text-align: left;
}

.mockup-header {
  display: flex;
  align-items: center;
  padding: var(--space-md) var(--space-xl);
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.window-dots {
  display: flex;
  gap: 6px;
  margin-right: var(--space-xl);
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.dot-red { background: #ff5f56; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #27c93f; }

.mockup-tab {
  display: flex;
  align-items: center;
  padding: 6px var(--space-lg);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  font-size: 12px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
}
.mockup-tab.active {
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-bottom: none;
}

.mockup-status {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 6px;
}
.pulse-green {
  width: 6px;
  height: 6px;
  background: var(--color-success);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--color-success);
  animation: pulse 1.5s infinite;
}

.mockup-body {
  display: flex;
  flex: 1;
  min-height: 330px;
}

.mockup-sidebar {
  width: 180px;
  background: rgba(0, 0, 0, 0.15);
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mockup-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px var(--space-md);
  border-radius: var(--radius-md);
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 500;
  transition: all var(--transition-fast);
}
.mockup-nav-item.active {
  background: rgba(108, 99, 255, 0.1);
  color: var(--color-primary-light);
}

.mockup-content {
  flex: 1;
  padding: var(--space-xl);
  background: rgba(0, 0, 0, 0.05);
}

.mockup-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
}

.mockup-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform var(--transition-fast);
}
.mockup-card:hover {
  transform: translateY(-4px);
}

.mockup-card-img {
  height: 120px;
  position: relative;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: flex-end;
  padding: var(--space-sm);
}

/* Beautiful mock background visuals using gradient combinations */
.img-1 {
  background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
  position: relative;
}
.img-1::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 70% 30%, rgba(255,107,157,0.3) 0%, transparent 60%);
}
.img-2 {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
}
.img-2::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 70%, rgba(0,210,255,0.2) 0%, transparent 60%);
}
.img-3 {
  background: linear-gradient(135deg, #020617 0%, #0f172a 100%);
}
.img-3::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(108,99,255,0.25) 0%, transparent 70%);
}

.badge-raw {
  background: rgba(10, 10, 26, 0.72);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-sm);
  padding: 2px 6px;
  font-size: 9px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--color-accent);
}

.mockup-card-info {
  padding: var(--space-md);
}

.img-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.img-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.img-size {
  font-size: 10px;
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}

.img-status {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 10px;
  font-weight: 600;
}
.img-status.synced {
  color: var(--color-success);
}
.img-status.syncing {
  color: var(--color-accent);
}

/* Shimmer/pulse keyframe enhancements */
@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Responsive mockup rules */
@media (max-width: 768px) {
  .hero-mockup {
    display: none; /* Hide on mobile to keep focus on simple CTA cards */
  }
}

.hero-content { text-align: center; position: relative; z-index: 1; }
.hero-badge { display: inline-flex; align-items: center; gap: var(--space-sm); padding: var(--space-sm) var(--space-lg); border-radius: var(--radius-full); font-size: var(--text-sm); color: var(--text-secondary); margin-bottom: var(--space-xl); }
.badge-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--color-success); animation: pulse 2s infinite; }
.hero-title { font-size: clamp(2.5rem, 6vw, 4.5rem); margin-bottom: var(--space-xl); line-height: 1.1; }
.hero-subtitle { font-size: var(--text-lg); color: var(--text-secondary); max-width: 600px; margin: 0 auto var(--space-2xl); line-height: var(--leading-relaxed); }
.hero-actions { display: flex; align-items: center; justify-content: center; gap: var(--space-lg); margin-bottom: var(--space-3xl); flex-wrap: wrap; }
.hero-stats { display: flex; justify-content: center; gap: var(--space-xl); flex-wrap: wrap; }
.stat-item { padding: var(--space-lg) var(--space-2xl); text-align: center; min-width: 140px; }
.stat-number { font-family: var(--font-display); font-size: var(--text-3xl); font-weight: 800; display: block; }
.stat-label { font-size: var(--text-sm); color: var(--text-tertiary); margin-top: var(--space-xs); display: block; }

/* Floating Elements */
.floating-elements { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
.float-el { position: absolute; }
.float-el-1 { top: 25%; left: 8%; }
.float-el-2 { top: 60%; right: 10%; }
.float-el-3 { bottom: 20%; left: 15%; }

/* Sections */
.features-section, .how-section { padding: var(--space-4xl) 0; position: relative; z-index: 1; }
.section-header { text-align: center; margin-bottom: var(--space-3xl); }
.section-tag { font-size: var(--text-sm); font-weight: 700; letter-spacing: 0.1em; display: block; margin-bottom: var(--space-md); }
.section-desc { color: var(--text-secondary); max-width: 500px; margin: var(--space-md) auto 0; }

/* Features Grid */
.features-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-xl); }
.feature-card { padding: var(--space-2xl); }
.feature-icon { width: 56px; height: 56px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-lg); }
.feature-card h3 { font-size: var(--text-lg); margin-bottom: var(--space-sm); }
.feature-card p { font-size: var(--text-sm); color: var(--text-secondary); line-height: var(--leading-relaxed); }

/* Steps */
.steps-container { max-width: 600px; margin: 0 auto; }
.step-item { display: flex; align-items: flex-start; gap: var(--space-xl); position: relative; margin-bottom: var(--space-2xl); }
.step-number { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-weight: 800; font-size: var(--text-lg); flex-shrink: 0; background: var(--bg-secondary); }
.step-content { flex: 1; padding: var(--space-lg) var(--space-xl); }
.step-content h3 { font-size: var(--text-base); margin-bottom: var(--space-xs); }
.step-content p { font-size: var(--text-sm); color: var(--text-secondary); }
.step-connector { position: absolute; left: 23px; top: 56px; width: 2px; height: calc(100% - 24px); background: linear-gradient(to bottom, var(--color-primary), transparent); }

/* CTA */
.cta-section { padding: var(--space-4xl) 0; }
.cta-card { text-align: center; padding: var(--space-4xl) var(--space-2xl); }
.cta-card h2 { margin-bottom: var(--space-md); }
.cta-card p { color: var(--text-secondary); margin-bottom: var(--space-2xl); }

/* Footer */
.footer { padding: var(--space-2xl) 0; border-top: 1px solid var(--border-subtle); }
.footer-brand p { font-size: var(--text-sm); color: var(--text-tertiary); margin-top: var(--space-sm); }
.footer-links { display: flex; gap: var(--space-xl); }
.footer-links a { color: var(--text-tertiary); font-size: var(--text-sm); }
.footer-links a:hover { color: var(--text-primary); }

/* Mobile */
@media (max-width: 768px) {
  .mobile-menu-btn { display: flex; }
  .nav-links { position: fixed; top: 0; right: -100%; width: 280px; height: 100vh; flex-direction: column; background: var(--bg-secondary); padding: 80px var(--space-xl) var(--space-xl); transition: right var(--transition-slow); border-left: 1px solid var(--border-subtle); z-index: 999; }
  .nav-links.open { right: 0; }
  .features-grid { grid-template-columns: 1fr; }
  .hero-stats { flex-direction: column; align-items: center; }
  .hero-actions { flex-direction: column; }
  .footer .flex-between { flex-direction: column; gap: var(--space-lg); text-align: center; }
  .footer-links { justify-content: center; }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .features-grid { grid-template-columns: repeat(2, 1fr); }
}

/* Pricing Section */
.pricing-section {
  padding: var(--space-4xl) 0;
  position: relative;
  z-index: 1;
}

.pricing-toggle-wrapper {
  display: inline-flex;
  align-items: center;
  gap: var(--space-md);
  margin-top: var(--space-xl);
  background: rgba(255, 255, 255, 0.03);
  padding: 6px 16px;
  border-radius: var(--radius-full);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.toggle-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-tertiary);
  transition: color var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 6px;
}

.toggle-label.active {
  color: var(--text-primary);
}

.discount-pill {
  font-size: 10px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-accent), var(--color-primary));
  color: #fff;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
}

.pricing-toggle-btn {
  width: 44px;
  height: 24px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  position: relative;
  cursor: pointer;
  padding: 0;
  transition: background var(--transition-normal);
}

.pricing-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 18px;
  height: 18px;
  background: var(--color-primary-light);
  border-radius: 50%;
  transition: transform var(--transition-normal), background var(--transition-normal);
  box-shadow: 0 2px 6px rgba(108, 99, 255, 0.4);
}

.toggle-slider.annual {
  transform: translateX(20px);
  background: var(--color-accent);
  box-shadow: 0 2px 6px rgba(255, 107, 157, 0.4);
}

/* Pricing Grid */
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-xl);
  align-items: stretch;
  margin-top: var(--space-3xl);
}

.pricing-card {
  padding: var(--space-3xl);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.pricing-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-2xl), 0 20px 40px rgba(0, 0, 0, 0.4);
}

.popular-glow {
  border: 1px solid rgba(255, 107, 157, 0.25) !important;
  box-shadow: 0 10px 30px rgba(255, 107, 157, 0.08), var(--shadow-glow);
}

.popular-glow:hover {
  box-shadow: 0 15px 40px rgba(255, 107, 157, 0.15), var(--shadow-glow), 0 20px 45px rgba(0, 0, 0, 0.5);
}

.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, var(--color-accent), var(--color-primary));
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  padding: 4px 16px;
  border-radius: var(--radius-full);
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.3);
}

.plan-header {
  margin-bottom: var(--space-xl);
  text-align: left;
}

.plan-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-lg);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.plan-name {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.plan-desc {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  line-height: 1.4;
}

.plan-price-block {
  margin-bottom: var(--space-xl);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: var(--space-xl);
  text-align: left;
}

.plan-price {
  display: flex;
  align-items: baseline;
}

.currency {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--text-primary);
}

.price-value {
  font-size: var(--text-4xl);
  font-weight: 800;
  font-family: var(--font-display);
  color: var(--text-primary);
  line-height: 1;
}

.period {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.billed-annually-detail {
  display: block;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.plan-credits-showcase {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  text-align: center;
  margin-bottom: var(--space-xl);
}

.credits-count {
  font-size: var(--text-3xl);
  font-weight: 800;
  font-family: var(--font-display);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.credits-label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.credits-cost {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 6px;
}

.plan-features {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--space-2xl);
  display: flex;
  flex-direction: column;
  gap: 12px;
  flex: 1;
  text-align: left;
}

.plan-features li {
  display: flex;
  align-items: flex-start;
  gap: var(--space-md);
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}

.feat-check {
  margin-top: 2px;
  flex-shrink: 0;
}

.pricing-section .btn-block {
  width: 100%;
}

@media (max-width: 1024px) {
  .pricing-grid {
    grid-template-columns: 1fr;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
  }
}

/* Reviews Section */
.reviews-section {
  padding: var(--space-4xl) 0;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.reviews-marquee {
  width: 100%;
  position: relative;
  overflow: hidden;
  padding: var(--space-md) 0;
  mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);
}

.marquee-track {
  display: flex;
  width: max-content;
  animation: scrollMarquee 40s linear infinite;
}

.marquee-track:hover {
  animation-play-state: paused;
}

.marquee-slide {
  display: flex;
  gap: var(--space-xl);
  padding-right: var(--space-xl);
}

.review-card {
  width: 380px;
  padding: var(--space-xl);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.01);
  transition: transform var(--transition-normal), border-color var(--transition-fast);
}

.review-card:hover {
  transform: translateY(-4px);
  border-color: rgba(108, 99, 255, 0.2);
}

.stars {
  display: flex;
  gap: 4px;
  margin-bottom: var(--space-md);
}

.star-icon {
  color: #f59e0b; /* Golden Yellow */
  filter: drop-shadow(0 0 4px rgba(245, 158, 11, 0.4));
}

.review-comment {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
  margin-bottom: var(--space-lg);
  flex: 1;
  text-align: left;
}

.review-user {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: var(--space-md);
  text-align: left;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--text-sm);
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.user-role {
  font-size: 11px;
  color: var(--text-tertiary);
}

@keyframes scrollMarquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}
</style>
