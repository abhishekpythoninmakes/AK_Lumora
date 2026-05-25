import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyABRRpo-1zH80byy16zXU2dBZX4PR88874',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'ak-lumora.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'ak-lumora',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'ak-lumora.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '523412602299',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:523412602299:web:cc88ccd58553cebe8f989e',
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || 'G-TRVHD06SX1',
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider)
  const idToken = await result.user.getIdToken()
  return { user: result.user, idToken }
}

export async function signInWithEmail(email, password) {
  const result = await signInWithEmailAndPassword(auth, email, password)
  const idToken = await result.user.getIdToken()
  return { user: result.user, idToken }
}

export async function signUpWithEmail(email, password) {
  const result = await createUserWithEmailAndPassword(auth, email, password)
  const idToken = await result.user.getIdToken()
  return { user: result.user, idToken }
}

export { auth }
