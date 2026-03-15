import { useState } from 'react'
import './ConsentModal.css'

const ROLES = [
  { value: 'patient', label: '🧑‍⚕️ Patient' },
  { value: 'caregiver', label: '🤝 Caregiver' },
  { value: 'doctor', label: '👨‍⚕️ Doctor / Healthcare Professional' },
]

const LANGUAGES = [
  { value: 'en', label: '🇬🇧 English' },
  { value: 'hi', label: '🇮🇳 हिंदी (Hindi)' },
  { value: 'mr', label: '🇮🇳 मराठी (Marathi)' },
  { value: 'ta', label: '🇮🇳 தமிழ் (Tamil)' },
]

function ConsentModal({ user, onConsent }) {
  const [role, setRole] = useState('')
  const [language, setLanguage] = useState('en')
  const [agreed, setAgreed] = useState(false)

  const canSubmit = role && language && agreed

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!canSubmit || submitting) return
    setSubmitting(true)
    setError('')
    try {
      const res = await fetch('/api/users/consent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: user?.email || '',
          name: user?.name || '',
          role,
          language,
        }),
      })
      if (!res.ok) throw new Error('Failed to save consent')
      onConsent({ role, language, consentedAt: new Date().toISOString() })
    } catch (err) {
      setError('Could not save consent. Please try again.')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="consent-overlay">
      <div className="consent-modal">
        {/* Header */}
        <div className="consent-header">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="40" height="40">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#4A90D9" strokeWidth="3" />
            <path d="M30 50 L42 50 L46 35 L50 65 L54 35 L58 50 L70 50"
              fill="none" stroke="#4A90D9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div>
            <h2 className="consent-title">Welcome, {user?.name || 'User'}</h2>
            <p className="consent-subtitle">Before we get started, we need a few details.</p>
          </div>
        </div>

        {/* Role Selection */}
        <div className="consent-section">
          <label className="consent-label">Your Role</label>
          <div className="role-options">
            {ROLES.map((r) => (
              <button
                key={r.value}
                className={`role-chip ${role === r.value ? 'selected' : ''}`}
                onClick={() => setRole(r.value)}
              >
                {r.label}
              </button>
            ))}
          </div>
        </div>

        {/* Language Selection */}
        <div className="consent-section">
          <label className="consent-label">Preferred Language</label>
          <select
            className="consent-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>{l.label}</option>
            ))}
          </select>
        </div>

        {/* Privacy Agreement */}
        <div className="consent-section">
          <label className="consent-label">Data Privacy & Consent</label>
          <div className="consent-box">
            <p>By using HealthGlitterr AI, you acknowledge and agree to the following:</p>
            <ul>
              <li>Your uploaded medical reports will be processed by AI to extract health parameters and provide insights.</li>
              <li>Your data is encrypted and stored securely in our database.</li>
              <li>We do not share your personal health information with third parties.</li>
              <li>Uploaded files are deleted from the server after processing.</li>
              <li>This application provides informational insights only and is <strong>not a substitute for professional medical advice</strong>.</li>
              <li>You may request deletion of your data at any time.</li>
            </ul>
          </div>
        </div>

        {/* Checkbox */}
        <label className="consent-check">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
          />
          <span>I agree to the data privacy policy and consent to share my medical data for analysis.</span>
        </label>

        {/* Error */}
        {error && <p className="consent-error">{error}</p>}

        {/* Submit */}
        <button
          className={`consent-submit ${canSubmit && !submitting ? '' : 'disabled'}`}
          onClick={handleSubmit}
          disabled={!canSubmit || submitting}
        >
          {submitting ? 'Saving…' : 'I Agree'}
        </button>
      </div>
    </div>
  )
}

export default ConsentModal
