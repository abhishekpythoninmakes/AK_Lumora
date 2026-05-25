<template>
  <div class="legal-page">
    <!-- Ambient Blobs -->
    <div class="legal-bg">
      <div class="legal-grid"></div>
      <div class="ambient-blob blob-1"></div>
      <div class="ambient-blob blob-2"></div>
    </div>

    <!-- Navigation Header -->
    <nav class="nav glass">
      <div class="container flex-between">
        <div class="nav-brand" @click="$router.push('/')">
          <img src="/logo.png" alt="AK Lumora Logo" style="width: 40px; height: 40px; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(108, 99, 255, 0.25));">
          <span class="brand-text">AK <span class="gradient-text">Lumora</span></span>
        </div>
        <button class="btn btn-secondary btn-sm" @click="$router.push('/')">Back to Home</button>
      </div>
    </nav>

    <!-- Main Content Container -->
    <main class="legal-container container">
      <div class="legal-layout">
        <!-- Sticky Sidebar Index -->
        <aside class="legal-sidebar glass">
          <h4 class="sidebar-title">Terms Index</h4>
          <ul class="index-list">
            <li v-for="item in indexItems" :key="item.id">
              <a :href="`#${item.id}`" @click.prevent="scrollToSection(item.id)" :class="{ active: activeSection === item.id }">
                <span class="index-num">{{ item.num }}</span>
                {{ item.title }}
              </a>
            </li>
          </ul>
        </aside>

        <!-- Document Section -->
        <article class="legal-content glass-strong">
          <div class="doc-header">
            <span class="section-tag gradient-text">USER AGREEMENT</span>
            <h1>Terms of Service</h1>
            <p class="last-updated">Last Updated: May 25, 2026</p>
          </div>

          <section id="agreement" class="doc-section">
            <h2>Agreement to Terms</h2>
            <p>By creating a studio profile or using the synchronization pipelines, watch folders, and slideshow portals provided by AK Lumora, you agree to enter a legally binding contract under these Terms of Service.</p>
            <p>If you do not agree to all of these terms, you are prohibited from accessing or using our services.</p>
          </section>

          <section id="services" class="doc-section">
            <h2>1. Service Scope & watch-folders</h2>
            <p>AK Lumora provides a real-time bridge between your local file storage and your Google Drive folders. The scope of service includes:</p>
            <ul>
              <li><strong>Local Folder Watching:</strong> Automatic filesystem scanning for newly captured camera photos inside folders configured by the user.</li>
              <li><strong>Frontend RAW Parser:</strong> Automated browser-based extraction of JPEG data from RAW binaries (CR2, CR3, ARW, NEF, etc.) and size compression.</li>
              <li><strong>Resumable Sync:</strong> Concurrency-limited upload lanes directly linked to your target Google Drive folders.</li>
              <li><strong>Live Galleries:</strong> Generating web slideshow presentation links and dynamic guest QR download screens.</li>
            </ul>
          </section>

          <section id="credits" class="doc-section">
            <h2>2. Sync Credits & Plan Limits</h2>
            <p>We utilize a credit-based billing system to offset bandwidth management, dashboard processing, and face-recognition vector indexing costs:</p>
            <ul>
              <li><strong>Credit Consumption:</strong> One (1) Sync Credit is deducted each time a RAW photo is successfully processed, compressed, and synchronized to Google Drive.</li>
              <li><strong>Rollover Rules:</strong> Unused sync credits rollover monthly only if you maintain an active **Pro Studio** or **Elite Agency** subscription, capped at two times your monthly allocation.</li>
              <li><strong>Storage Limitations:</strong> AK Lumora does not sell cloud storage. You are entirely responsible for maintaining sufficient storage limits and API quotas on your linked Google Drive account.</li>
            </ul>
          </section>

          <section id="ownership" class="doc-section">
            <h2>3. Media Ownership & Copyrights</h2>
            <p>You retain 100% ownership and legal copyright over every photo synced through our pipelines:</p>
            <ul>
              <li>We make no claim of ownership or licensing rights over your creative media assets.</li>
              <li>You warrant that you own or have obtained all necessary copyrights, release forms, and model permissions for the images you synchronize and display through our live presentation galleries.</li>
            </ul>
          </section>

          <section id="conduct" class="doc-section">
            <h2>4. User Conduct & Safe Watch Folders</h2>
            <p>You agree to use AK Lumora strictly for professional and legal creative photography purposes. Prohibited activities include:</p>
            <ul>
              <li>Configuring watch folders containing malicious scripts, executable binaries, or non-media code formats.</li>
              <li>Attempting to bypass credit limits, upload restrictions, or concurrency bottlenecks through automated hacking scripts.</li>
              <li>Hosting or sharing illegal content, severe graphic violence, or unauthorized intimate media through our live guest presentation URLs.</li>
            </ul>
          </section>

          <section id="liability" class="doc-section">
            <h2>5. Disclaimer of Liability</h2>
            <p>AK Lumora operates as a local sync bridge. We are not liable for filesystems, third-party storage APIs, or event network outages:</p>
            <ul>
              <li><strong>Third-Party Outages:</strong> We are not responsible for Google Drive service downtime, rate limit throttling, API changes, or server data loss.</li>
              <li><strong>Local Filesystem Failures:</strong> We are not liable for data corrupted locally on your machines, network disconnects during a shoot, or lost sync tasks due to system sleep modes.</li>
              <li><strong>"As Is" Warranty:</strong> All features are provided "as is" and "as available" without warranties of any kind.</li>
            </ul>
          </section>

          <section id="termination" class="doc-section">
            <h2>6. Account Suspension & Termination</h2>
            <p>We reserve the right to suspend or terminate your studio's dashboard access if:</p>
            <ul>
              <li>You engage in systematic billing abuse or coordinate chargeback fraud.</li>
              <li>You violate the code of conduct or breach our watch folder security scopes.</li>
              <li>Your studio's usage patterns cause server degradation or interrupt performance for other professional photographer nodes.</li>
            </ul>
          </section>
        </article>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <div class="container flex-between">
        <div class="footer-brand">
          <span class="brand-text">AK <span class="gradient-text">Lumora</span></span>
          <p>© 2026 AK Lumora. Crafted for photographers.</p>
        </div>
        <div class="footer-links">
          <a href="#" @click.prevent="$router.push('/')">Home</a>
          <a href="#" @click.prevent="$router.push('/privacy')">Privacy Policy</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'

const activeSection = ref('agreement')

const indexItems = [
  { id: 'agreement', num: '00', title: 'Agreement to Terms' },
  { id: 'services', num: '01', title: 'Service & Watchers' },
  { id: 'credits', num: '02', title: 'Sync Credits & Limits' },
  { id: 'ownership', num: '03', title: 'Media Copyrights' },
  { id: 'conduct', num: '04', title: 'User Conduct' },
  { id: 'liability', num: '05', title: 'Limit of Liability' },
  { id: 'termination', num: '06', title: 'Account Suspension' },
]

function scrollToSection(id) {
  activeSection.value = id
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// Track scrolling to update active sidebar section
function handleScroll() {
  const sections = indexItems.map(item => document.getElementById(item.id))
  const scrollPos = window.scrollY + 120

  for (let i = sections.length - 1; i >= 0; i--) {
    const section = sections[i]
    if (section && section.offsetTop <= scrollPos) {
      activeSection.value = indexItems[i].id
      break
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  
  // GSAP Fade-In Animations for a premium look
  gsap.from('.legal-sidebar', {
    x: -30,
    opacity: 0,
    duration: 0.8,
    ease: 'power3.out'
  })
  
  gsap.from('.legal-content', {
    y: 30,
    opacity: 0,
    duration: 0.8,
    delay: 0.1,
    ease: 'power3.out'
  })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.legal-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0A0A1A;
  color: var(--text-secondary);
}

/* Background layout similar to landing page */
.legal-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.legal-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.01) 1px, transparent 1px);
  background-size: 80px 80px;
  mask-image: radial-gradient(ellipse at center, black 40%, transparent 80%);
}

.ambient-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.08;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--color-primary) 0%, transparent 80%);
  top: 10%;
  left: -5%;
}

.blob-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 80%);
  bottom: 20%;
  right: -5%;
}

/* Navigation */
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: var(--z-sticky);
  padding: var(--space-md) 0;
  background: rgba(10, 10, 26, 0.7);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
}

.brand-text {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--text-primary);
}

/* Container */
.legal-container {
  margin-top: 120px;
  flex: 1;
  position: relative;
  z-index: 1;
  padding-bottom: var(--space-4xl);
}

.legal-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--space-2xl);
  align-items: start;
}

/* Sidebar Index */
.legal-sidebar {
  position: sticky;
  top: 120px;
  padding: var(--space-xl);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.sidebar-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  margin-bottom: var(--space-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: var(--space-sm);
}

.index-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.index-list a {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
  font-weight: 500;
  padding: 8px var(--space-sm);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.index-num {
  font-size: 10px;
  font-family: var(--font-mono);
  background: rgba(255, 255, 255, 0.03);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--text-tertiary);
}

.index-list a:hover,
.index-list a.active {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.03);
}

.index-list a.active .index-num {
  background: var(--color-primary-light);
  color: #fff;
}

/* Document Content */
.legal-content {
  padding: var(--space-3xl);
  border-radius: var(--radius-2xl);
  border: 1px solid rgba(255, 255, 255, 0.05);
  text-align: left;
}

.doc-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: var(--space-2xl);
  margin-bottom: var(--space-2xl);
}

.section-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: var(--space-sm);
}

.doc-header h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.last-updated {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-family: var(--font-mono);
}

/* Doc Sections */
.doc-section {
  margin-bottom: var(--space-3xl);
}

.doc-section h2 {
  font-size: var(--text-xl);
  color: var(--text-primary);
  margin-bottom: var(--space-md);
}

.doc-section p {
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
  margin-bottom: var(--space-md);
}

.doc-section ul {
  padding-left: var(--space-xl);
  margin-bottom: var(--space-md);
}

.doc-section li {
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.doc-section strong {
  color: var(--text-primary);
}

.legal-link {
  color: var(--color-primary-light);
  text-decoration: underline;
  transition: color var(--transition-fast);
}

.legal-link:hover {
  color: var(--color-accent);
}

/* Footer */
.footer {
  padding: var(--space-2xl) 0;
  border-top: 1px solid var(--border-subtle);
  background: rgba(10, 10, 26, 0.3);
  position: relative;
  z-index: 1;
}

.footer-brand p {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: var(--space-sm);
}

.footer-links {
  display: flex;
  gap: var(--space-xl);
}

.footer-links a {
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}

.footer-links a:hover {
  color: var(--text-primary);
}

/* Responsive */
@media (max-width: 900px) {
  .legal-layout {
    grid-template-columns: 1fr;
  }
  .legal-sidebar {
    display: none; /* Hide sticky index index on mobile */
  }
  .legal-container {
    margin-top: 100px;
  }
  .legal-content {
    padding: var(--space-xl);
  }
}
</style>
