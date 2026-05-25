<template>
  <div class="contact-page">
    <!-- Ambient Blobs -->
    <div class="contact-bg">
      <div class="contact-grid"></div>
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

    <!-- Contact Content Container -->
    <main class="contact-container container">
      <div class="contact-layout">
        <!-- Left Column: Contact Cards -->
        <div class="info-column">
          <div class="info-header" ref="infoHeader">
            <span class="section-tag gradient-text">GET IN TOUCH</span>
            <h1>Contact Our Studio</h1>
            <p>Have questions about watch folders, RAW pipeline compressions, or credit top-ups? We are here to help you automate your delivery workflow.</p>
          </div>

          <div class="info-cards-list">
            <!-- Studio Card -->
            <div class="contact-card glass-strong card-studio" ref="cardStudio">
              <div class="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary-light)" stroke-width="2">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/>
                </svg>
              </div>
              <div class="card-details">
                <h3>Studio Brand</h3>
                <span class="brand-name">AK <span class="gradient-text">Lumora</span></span>
                <span class="subtitle">Photography Automation Suite</span>
              </div>
            </div>

            <!-- Email Card -->
            <div class="contact-card glass-strong card-email" ref="cardEmail">
              <div class="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
                </svg>
              </div>
              <div class="card-details">
                <h3>Email Support</h3>
                <a :href="`mailto:${supportEmail}`" class="contact-link">{{ supportEmail }}</a>
                <span class="subtitle">Avg. Response: Under 12 Hours</span>
              </div>
            </div>

            <!-- Phone Card -->
            <div class="contact-card glass-strong card-phone" ref="cardPhone">
              <div class="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                  <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
                </svg>
              </div>
              <div class="card-details">
                <h3>Direct Phone</h3>
                <a :href="`tel:${supportPhone}`" class="contact-link">{{ supportPhone }}</a>
                <span class="subtitle">Mon - Sat, 9:00 AM - 6:00 PM IST</span>
              </div>
            </div>

            <!-- Address Card -->
            <div class="contact-card glass-strong card-address" ref="cardAddress">
              <div class="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255, 179, 71, 1)" stroke-width="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
                </svg>
              </div>
              <div class="card-details">
                <h3>Office Location</h3>
                <p class="address-text">Locality: {{ supportLocality }}</p>
                <p class="address-text">District: {{ supportDistrict }}</p>
                <p class="address-text">Pincode: {{ supportPincode }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Form & Testimonials -->
        <div class="form-column">
          <!-- Sleek Inquiry Form -->
          <div class="inquiry-box glass-strong" ref="inquiryBox">
            <h2 class="form-title">Send a Message</h2>
            <form @submit.prevent="handleSubmit" class="contact-form">
              <div class="form-group">
                <label for="name">Full Name</label>
                <input type="text" id="name" v-model="formData.name" placeholder="John Doe" class="glass-input" required>
              </div>
              <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" v-model="formData.email" placeholder="john@example.com" class="glass-input" required>
              </div>
              <div class="form-group">
                <label for="message">Message</label>
                <textarea id="message" v-model="formData.message" rows="4" placeholder="How can we help your studio today?" class="glass-input" required></textarea>
              </div>
              <button type="submit" class="btn btn-primary btn-block ripple submit-btn" :disabled="submitting">
                <span v-if="submitting">Sending Message...</span>
                <span v-else>Send Message</span>
              </button>
              <p v-if="submitted" class="success-message">✓ Thank you! Your message was sent successfully.</p>
            </form>
          </div>

          <!-- Featured Testimonial Card -->
          <div class="featured-reviews-block" ref="reviewsBlock">
            <h4 class="block-title">What Photographers Say</h4>
            <div class="testimonial-card glass">
              <div class="stars">
                <svg v-for="star in 5" :key="star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <p class="comment">"The client-side raw compression is absolute magic. We sync hundreds of ARW files over local event Wi-Fi without crushing our upload bandwidth. Saving on server flat rates with credit usage is a huge plus!"</p>
              <div class="user">
                <span class="name">Sarah M.</span>
                <span class="role">Event Photographer</span>
              </div>
            </div>
            <div class="testimonial-card glass" style="margin-top: var(--space-md);">
              <div class="stars">
                <svg v-for="star in 5" :key="star" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" class="star-icon">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                </svg>
              </div>
              <p class="comment">"AK Lumora completely revolutionized our wedding workflows. Monitored folders instantly compress RAWs on the spot and upload to Drive in seconds. Clients scan the QR code and download their portraits immediately!"</p>
              <div class="user">
                <span class="name">Arjun K.</span>
                <span class="role">Wedding Studio Lead</span>
              </div>
            </div>
          </div>
        </div>
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
          <a href="#" @click.prevent="$router.push('/terms')">Terms of Service</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { gsap } from 'gsap'

const supportEmail = import.meta.env.VITE_SUPPORT_EMAIL || 'abhishekar3690@gmail.com'
const supportPhone = import.meta.env.VITE_SUPPORT_PHONE || '+917356176925'
const supportLocality = import.meta.env.VITE_SUPPORT_ADDRESS_LOCALITY || 'Palarivattom, Kochi'
const supportDistrict = import.meta.env.VITE_SUPPORT_ADDRESS_DISTRICT || 'Ernakulam, Kerala'
const supportPincode = import.meta.env.VITE_SUPPORT_ADDRESS_PINCODE || '682025'

const infoHeader = ref(null)
const cardStudio = ref(null)
const cardEmail = ref(null)
const cardPhone = ref(null)
const cardAddress = ref(null)
const inquiryBox = ref(null)
const reviewsBlock = ref(null)

const formData = ref({
  name: '',
  email: '',
  message: ''
})

const submitting = ref(false)
const submitted = ref(false)

function handleSubmit() {
  submitting.value = true
  // Simulate API post
  setTimeout(() => {
    submitting.value = false
    submitted.value = true
    formData.value = { name: '', email: '', message: '' }
    setTimeout(() => {
      submitted.value = false
    }, 5000)
  }, 1000)
}

onMounted(() => {
  // GSAP animations for entering elements
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.from(infoHeader.value, { y: -20, opacity: 0, duration: 0.6 })
    .from([cardStudio.value, cardEmail.value, cardPhone.value, cardAddress.value], {
      x: -30,
      opacity: 0,
      duration: 0.6,
      stagger: 0.1
    }, '-=0.3')
    .from(inquiryBox.value, { y: 30, opacity: 0, duration: 0.7 }, '-=0.5')
    .from(reviewsBlock.value, { y: 20, opacity: 0, duration: 0.6 }, '-=0.3')
})
</script>

<style scoped>
.contact-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0A0A1A;
  color: var(--text-secondary);
}

/* Background layout similar to landing page */
.contact-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.contact-grid {
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
.contact-container {
  margin-top: 120px;
  flex: 1;
  position: relative;
  z-index: 1;
  padding-bottom: var(--space-4xl);
}

.contact-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3xl);
  align-items: start;
}

/* Left Column */
.info-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
  text-align: left;
}

.info-header h1 {
  font-size: clamp(2rem, 4vw, 3rem);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
  line-height: 1.1;
}

.info-header p {
  font-size: var(--text-base);
  color: var(--text-tertiary);
  line-height: var(--leading-relaxed);
}

.section-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: var(--space-sm);
}

.info-cards-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.contact-card {
  padding: var(--space-lg) var(--space-xl);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: flex-start;
  gap: var(--space-xl);
  transition: transform var(--transition-normal), border-color var(--transition-fast);
}

.contact-card:hover {
  transform: translateX(4px);
  border-color: rgba(255, 255, 255, 0.1);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.card-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-details h3 {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-tertiary);
  margin-bottom: 2px;
}

.brand-name {
  font-family: var(--font-display);
  font-size: var(--text-lg);
  font-weight: 800;
  color: var(--text-primary);
}

.contact-link {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.contact-link:hover {
  color: var(--color-primary-light);
}

.address-text {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}

.subtitle {
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

/* Right Column: Form & Testimonials */
.form-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-2xl);
  text-align: left;
}

.inquiry-box {
  padding: var(--space-2xl);
  border-radius: var(--radius-2xl);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.form-title {
  font-size: var(--text-xl);
  color: var(--text-primary);
  font-weight: 700;
  margin-bottom: var(--space-xl);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: var(--space-sm);
}

.contact-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--text-secondary);
}

.glass-input {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 12px var(--space-md);
  font-size: var(--text-sm);
  color: var(--text-primary);
  outline: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.glass-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.15);
}

textarea.glass-input {
  resize: vertical;
}

.submit-btn {
  padding: 12px;
  font-size: var(--text-sm);
  font-weight: 600;
}

.success-message {
  font-size: var(--text-sm);
  color: #10b981;
  margin-top: var(--space-sm);
  text-align: center;
  font-weight: 600;
}

/* Featured Reviews */
.featured-reviews-block {
  display: flex;
  flex-direction: column;
}

.block-title {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-tertiary);
  margin-bottom: var(--space-md);
}

.testimonial-card {
  padding: var(--space-lg);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.stars {
  display: flex;
  gap: 3px;
  margin-bottom: 8px;
}

.star-icon {
  color: #f59e0b;
}

.comment {
  font-size: var(--text-xs);
  line-height: 1.5;
  color: var(--text-secondary);
  margin-bottom: var(--space-md);
}

.user {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  font-weight: 600;
}

.user .name {
  color: var(--text-primary);
}

.user .role {
  color: var(--text-tertiary);
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
  .contact-layout {
    grid-template-columns: 1fr;
    gap: var(--space-2xl);
  }
  .contact-container {
    margin-top: 100px;
  }
}
</style>
