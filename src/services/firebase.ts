import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getAnalytics } from 'firebase/analytics';

// Firebase configuration
// To use Firebase:
// 1. Create a Firebase project at https://console.firebase.google.com/
// 2. Enable Authentication (Email/Password)
// 3. Enable Firestore Database
// 4. Copy your config values to .env.local file:
//    VITE_FIREBASE_API_KEY=your_api_key
//    VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
//    VITE_FIREBASE_PROJECT_ID=your_project_id
//    VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
//    VITE_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
//    VITE_FIREBASE_APP_ID=your_app_id

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase only if config is provided
let app;
let auth;
let db;
let analytics;

try {
  if (firebaseConfig.apiKey) {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);

    // Analytics only works in production
    if (typeof window !== 'undefined' && import.meta.env.PROD) {
      analytics = getAnalytics(app);
    }
  }
} catch (error) {
  console.warn('Firebase not configured. Please add your Firebase config to .env.local');
}

export { auth, db, analytics };
