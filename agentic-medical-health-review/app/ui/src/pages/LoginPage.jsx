import { useEffect } from 'react'
import './LoginPage.css'

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID
const REDIRECT_URI = import.meta.env.VITE_GOOGLE_REDIRECT_URI

function getGoogleAuthUrl() {
  const params = new URLSearchParams({
    client_id: GOOGLE_CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    response_type: 'code',
    scope: 'openid email profile',
    access_type: 'offline',
    prompt: 'consent',
  })
  return `https://accounts.google.com/o/oauth2/v2/auth?${params}`
}

function LoginPage({ onLogin }) {
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    if (!code) return

    // Send code to backend — client_secret stays server-side
    fetch('/api/auth/google-callback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code }),
    })
      .then((res) => res.json())
      .then((profile) => {
        const name = profile.name || 'User'
        const initials = name.split(' ').map((n) => n[0]).join('').toUpperCase()
        onLogin({
          name,
          email: profile.email || '',
          picture: profile.picture || '',
          initials,
        })
        window.history.replaceState({}, '', '/')
      })
      .catch(() => {
        onLogin({ name: 'User', email: '', initials: 'U' })
        window.history.replaceState({}, '', '/')
      })
  }, [onLogin])

  const handleSignIn = () => {
    window.location.href = getGoogleAuthUrl()
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="logo-wrapper">
          <svg className="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#4A90D9" strokeWidth="3" />
            <path d="M30 50 L42 50 L46 35 L50 65 L54 35 L58 50 L70 50"
              fill="none" stroke="#4A90D9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="20" cy="20" r="4" fill="#34A853" />
            <circle cx="80" cy="20" r="4" fill="#4285F4" />
            <circle cx="20" cy="80" r="4" fill="#FBBC05" />
            <circle cx="80" cy="80" r="4" fill="#EA4335" />
          </svg>
        </div>
        <h1 className="app-title">
          HealthGlitterr <span className="title-accent">AI</span>
        </h1>
        <p className="app-subtitle">AI-Powered Medical Report Analysis</p>
        <p className="app-description">
          Upload your medical reports and get instant AI-powered insights, risk
          assessments, and personalized recommendations.
        </p>
        <button className="google-btn" onClick={handleSignIn}>
          <svg className="google-icon" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
          </svg>
          Sign in with Google
        </button>
        <p className="terms-text">
          By signing in, you agree to our{' '}
          <a href="#terms">Terms of Service</a> and{' '}
          <a href="#privacy">Privacy Policy</a>.
        </p>
      </div>
    </div>
  )
}

export default LoginPage
