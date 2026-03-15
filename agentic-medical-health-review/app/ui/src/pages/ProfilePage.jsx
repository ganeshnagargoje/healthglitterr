import { useState, useEffect } from 'react'
import '../components/ConsentModal.css'
import './ProfilePage.css'

const GENDERS = [
  { value: 'Male', label: '♂ Male' },
  { value: 'Female', label: '♀ Female' },
  { value: 'Other', label: '⚧ Other' },
]

function ProfilePage({ user, onBack, onUpdate }) {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [gender, setGender] = useState('')
  const [heightCm, setHeightCm] = useState('')
  const [weightKg, setWeightKg] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const initials = user?.initials || user?.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'

  // Load profile from backend
  useEffect(() => {
    fetch(`/api/users/profile?email=${encodeURIComponent(user?.email || '')}`)
      .then(res => res.json())
      .then(data => {
        setFirstName(data.first_name || user?.name?.split(' ')[0] || '')
        setLastName(data.last_name || user?.name?.split(' ').slice(1).join(' ') || '')
        setBirthDate(data.birth_date || '')
        setGender(data.gender || '')
        setHeightCm(data.height_cm || '')
        setWeightKg(data.weight_kg || '')
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user])

  const handleSave = async () => {
    setSaving(true)
    setError('')
    setSaved(false)
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
      if (!res.ok) throw new Error('Failed to save')
      onUpdate({
        firstName, lastName, birthDate, gender,
        heightCm: parseFloat(heightCm),
        weightKg: parseFloat(weightKg),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError('Could not save profile.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return null

  return (
    <div className="profile-page">
      <nav className="navbar">
        <div className="nav-brand">
          <button className="back-btn" onClick={onBack}>← Back</button>
          <span className="nav-title">My Profile</span>
        </div>
        <div className="nav-actions">
          <div className="avatar">{initials}</div>
        </div>
      </nav>

      <div className="profile-content">
        <div className="consent-modal" style={{ margin: '2rem auto' }}>
          <div className="consent-header">
            <div className="avatar" style={{ width: 56, height: 56, fontSize: '1.2rem' }}>{initials}</div>
            <div>
              <h2 className="consent-title">{user?.name || 'User'}</h2>
              <p className="consent-subtitle">{user?.email}</p>
            </div>
          </div>

          <div className="consent-section" style={{ display: 'flex', gap: '0.75rem' }}>
            <div style={{ flex: 1 }}>
              <label className="consent-label">First Name</label>
              <input type="text" className="consent-select" value={firstName}
                onChange={(e) => setFirstName(e.target.value)} />
            </div>
            <div style={{ flex: 1 }}>
              <label className="consent-label">Last Name</label>
              <input type="text" className="consent-select" value={lastName}
                onChange={(e) => setLastName(e.target.value)} />
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
              <input type="number" className="consent-select" value={heightCm}
                onChange={(e) => setHeightCm(e.target.value)} min="50" max="250" />
            </div>
            <div style={{ flex: 1 }}>
              <label className="consent-label">Weight (kg)</label>
              <input type="number" className="consent-select" value={weightKg}
                onChange={(e) => setWeightKg(e.target.value)} min="10" max="300" />
            </div>
          </div>

          {error && <p className="consent-error">{error}</p>}
          {saved && <p style={{ color: '#34A853', fontSize: '0.85rem', margin: '0 0 0.75rem' }}>Profile saved.</p>}

          <button className={`consent-submit ${saving ? 'disabled' : ''}`}
            onClick={handleSave} disabled={saving}>
            {saving ? 'Saving…' : 'Save Changes'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
