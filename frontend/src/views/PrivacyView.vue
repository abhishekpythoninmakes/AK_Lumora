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
          <h4 class="sidebar-title">Privacy Index</h4>
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
            <span class="section-tag gradient-text">LEGAL COMPLIANCE</span>
            <h1>Privacy Policy</h1>
            <p class="last-updated">Last Updated: May 25, 2026</p>
          </div>

          <section id="introduction" class="doc-section">
            <h2>Introduction</h2>
            <p>Welcome to AK Lumora. We are committed to protecting your privacy and ensuring you have a secure experience when automating your photography studio pipelines, watch folders, and client slideshow presentations.</p>
            <p>This Privacy Policy explains how we collect, use, and safeguard your studio and account data. By using AK Lumora, you agree to the terms described in this policy.</p>
            
            <div class="callout glass">
              <div class="callout-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary-light)" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
              </div>
              <div class="callout-text">
                <strong>Our Zero-Host Storage Principle:</strong> We never copy, store, or inspect your RAW photos or compressed JPEG files on our servers. All compression happens locally inside your browser, and uploads are routed directly to your own Google Drive.
              </div>
            </div>
          </section>

          <section id="information" class="doc-section">
            <h2>1. Information We Collect</h2>
            <p>To deliver a highly automated synchronization pipeline, we collect specific account configurations:</p>
            <ul>
              <li><strong>Profile Data:</strong> Your Google account email, name, and profile icon linked during OAuth signup to create your studio profile.</li>
              <li><strong>Google API Tokens:</strong> Securely encrypted authentication tokens required to connect watch folders directly to your Google Drive folders.</li>
              <li><strong>Metadata Logs:</strong> File names, sync statuses, upload speeds, and credit logs to render your live dashboard charts and reports.</li>
            </ul>
          </section>

          <section id="google-data" class="doc-section">
            <h2>2. Google API Data Usage</h2>
            <p>AK Lumora connects directly with Google Drive to store your synchronized photography folders. We request limited read/write scopes strictly to upload your compressed images, check destination folder IDs, and generate secure client download links.</p>
            <p>AK Lumora's use and transfer of information received from Google APIs will adhere to the <a href="https://developers.google.com/terms/api-services-user-data-policy" target="_blank" class="legal-link">Google API Services User Data Policy</a>, including the Limited Use requirements.</p>
          </section>

          <section id="zero-host" class="doc-section">
            <h2>3. Local WebAssembly & RAW Files</h2>
            <p>Our website utilizes client-side high-speed JPEG binary parsing and compression libraries inside your browser:</p>
            <ul>
              <li>RAW files monitored in your local watch folders remain entirely local on your machine.</li>
              <li>Our scripts execute inside your browser Sandbox to extract JPEG previews from `.NEF`, `.CR2`, `.CR3`, `.ARW`, or `.DNG` files, resizing and compressing them on your processor.</li>
              <li>This prevents massive files (e.g., 50MB RAW files) from eating your internet bandwidth or bloating server costs, putting 100% control back in your hands.</li>
            </ul>
          </section>

          <section id="data-security" class="doc-section">
            <h2>4. Security & Encryption</h2>
            <p>We implement standard security measures to protect your access credentials:</p>
            <ul>
              <li>All server communication is strictly encrypted via secure HTTPS channels.</li>
              <li>Google OAuth tokens are stored in an AES-256 encrypted format in our database.</li>
              <li>User passwords and local authentication tokens are stored securely with bcrypt hashing values.</li>
            </ul>
          </section>

          <section id="user-rights" class="doc-section">
            <h2>5. Your Rights & Data Deletion</h2>
            <p>You have full ownership of your studio data and synced cloud settings at all times:</p>
            <ul>
              <li><strong>Revoking Access:</strong> You can disconnect your Google Drive integrations at any time directly through the dashboard configuration section.</li>
              <li><strong>Account Deletion:</strong> You can request immediate permanent deletion of your studio account, logs, and Google OAuth associations by contacting our compliance department.</li>
            </ul>
          </section>

          <section id="contact" class="doc-section">
            <h2>6. Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, your studio data privacy, or Google integration scopes, please reach out to us:</p>
            <div class="contact-box glass">
              <p><strong>AK Lumora Privacy Office</strong></p>
              <p>Email: <a :href="`mailto:${supportEmail}`" class="legal-link">{{ supportEmail }}</a></p>
              <p>Phone: <a :href="`tel:${supportPhone}`" class="legal-link">{{ supportPhone }}</a></p>
              <p style="margin-top: 10px;"><strong>Studio Address:</strong></p>
              <p>Locality: {{ supportLocality }}</p>
              <p>District: {{ supportDistrict }}</p>
              <p>Pincode: {{ supportPincode }}</p>
            </div>
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
          <a href="#" @click.prevent="$router.push('/terms')">Terms of Service</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { gsap } from 'gsap'

const activeSection = ref('introduction')

const supportEmail = import.meta.env.VITE_SUPPORT_EMAIL || 'abhishekar3690@gmail.com'
const supportPhone = import.meta.env.VITE_SUPPORT_PHONE || '+917356176925'
const supportLocality = import.meta.env.VITE_SUPPORT_ADDRESS_LOCALITY || 'Palarivattom, Kochi'
const supportDistrict = import.meta.env.VITE_SUPPORT_ADDRESS_DISTRICT || 'Ernakulam, Kerala'
const supportPincode = import.meta.env.VITE_SUPPORT_ADDRESS_PINCODE || '682025'

const indexItems = [
  { id: 'introduction', num: '00', title: 'Introduction' },
  { id: 'information', num: '01', title: 'Information Collection' },
  { id: 'google-data', num: '02', title: 'Google API Usage' },
  { id: 'zero-host', num: '03', title: 'Zero-Host Storage' },
  { id: 'data-security', num: '04', title: 'Security & Safety' },
  { id: 'user-rights', num: '05', title: 'Your Rights & Controls' },
  { id: 'contact', num: '06', title: 'Contact & Support' },
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

/* Callouts */
.callout {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(108, 99, 255, 0.15);
  margin: var(--space-xl) 0;
  background: rgba(108, 99, 255, 0.02) !important;
}

.callout-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.callout-text {
  font-size: var(--text-sm);
  line-height: 1.5;
  color: var(--text-secondary);
}

.legal-link {
  color: var(--color-primary-light);
  text-decoration: underline;
  transition: color var(--transition-fast);
}

.legal-link:hover {
  color: var(--color-accent);
}

/* Contact Box */
.contact-box {
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: var(--space-md);
}

.contact-box p {
  margin-bottom: 6px;
  font-size: var(--text-sm);
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
