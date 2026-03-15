import { useState } from 'react'
import '../components/ConsentModal.css'

const GENDERS = [
  { value: 'Male', label: '♂ Male' },
  { value: 'Female', label: '♀ Female' },
  { value: 'Other', label: '⚧ Other' },
]

function ProfileModal({ user, onSave }) {
  // Pre-fill first/last from Google name
  const nameParts = (user?.name || '').split(' ')
  const [firstName, setFirstName] = useState(nameParts[0] || '')
  const [lastName, setLastName] = useState(nameParts.slice(1).join(' ') || '')
  const [birthDate, setBirthDate] = useState('')
  const [gender, setGender] = useState('')
  const [heightCm, setHeightCm] = useState('')
  const [weightKg, setWeightKg] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const canSubmit = firstName && lastName && birthDate && gender && heightCm && weightKg

  const handleSubmit = async () => {
    if (!canSubmit || submitting) return
    setSubmitting(true)
    setError('')
    try {
      const res = await fetch('/api/users/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: user?.email || '',
          first_name: firstName,
          last_name: lastName,
          birth_date: birthDate,
          gender,
          height_cm: parseFloat(heightCm),
          weight_kg: parseFloat(weightKg),
        }),
      })
      if (!res.ok) throw new Error('Failed to save profile')
      onSave({
        firstName, lastName, birthDate, gender,
        heightCm: parseFloat(heightCm),
        weightKg: parseFloat(weightKg),
        profileComplete: true,
      })
    } catch (err) {
      setError('Could not save profile. Please try again.')
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="consent-overlay">
      <div className="consent-modal">
        <div className="consent-header">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="40" height="40">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#4A90D9" strokeWidth="3" />
            <path d="M30 50 L42 50 L46 35 L50 65 L54 35 L58 50 L70 50"
              fill="none" stroke="#4A90D9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <div>
            <h2 className="consent-title">Complete Your Profile</h2>
            <p className="consent-subtitle">We need a few details for accurate health analysis.</p>
          </div>
        </div>

        <div className="consent-section" style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ flex: 1 }}>
            <label className="consent-label">First Name</label>
            <input type="text" className="consent-select" value={firstName}
              onChange={(e) => setFirstName(e.target.value)} placeholder="First name" />
          </div>
          <div style={{ flex: 1 }}>
            <label className="consent-label">Last Name</label>
            <input type="text" className="consent-select" value={lastName}
              onChange={(e) => setLastName(e.target.value)} placeholder="Last name" />
          </div>
        </div>

        <div className="consent-section">
          <label className="consent-label">Date of Birth</label>
          <input type="date" className="consent-select" value={birthDate}
            onChange={(e) => setBirthDate(e.target.value)} />
        </div>

        <div className="consent-section">
          <label className="consent-label">Gender</label>
          <div className="role-options">
            {GENDERS.map((g) => (
              <button key={g.value}
                className={`role-chip ${gender === g.value ? 'selected' : ''}`}
                onClick={() => setGender(g.value)}>
                {g.label}
              </button>
            ))}
          </div>
        </div>

        <div className="consent-section" style={{ display: 'flex', gap: '0.75rem' }}>
          <div style={{ flex: 1 }}>
            <label className="consent-label">Height (cm)</label>
            <input type="number" className="consent-select" placeholder="e.g. 175"
              value={heightCm} onChange={(e) => setHeightCm(e.target.value)} min="50" max="250" />
          </div>
          <div style={{ flex: 1 }}>
            <label className="consent-label">Weight (kg)</label>
            <input type="number" className="consent-select" placeholder="e.g. 70"
              value={weightKg} onChange={(e) => setWeightKg(e.target.value)} min="10" max="300" />
          </div>
        </div>

        {error && <p className="consent-error">{error}</p>}

        <button
          className={`consent-submit ${canSubmit && !submitting ? '' : 'disabled'}`}
          onClick={handleSubmit}
          disabled={!canSubmit || submitting}
        >
          {submitting ? 'Saving…' : 'Save Profile'}
        </button>
      </div>
    </div>
  )
}

export default ProfileModal
