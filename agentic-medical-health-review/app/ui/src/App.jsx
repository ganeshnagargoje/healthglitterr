import { useState, useEffect, useRef } from 'react'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ProfilePage from './pages/ProfilePage'
import ConsentModal from './components/ConsentModal'
import ProfileModal from './components/ProfileModal'

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })
  const [consented, setConsented] = useState(() => localStorage.getItem('consented') === 'true')
  const [profileComplete, setProfileComplete] = useState(() => localStorage.getItem('profileComplete') === 'true')
  const [checking, setChecking] = useState(false)
  const [showProfile, setShowProfile] = useState(false)
  const checkedRef = useRef(false)

  // Check backend once after login — only runs once per user session
  useEffect(() => {
    if (!user || checkedRef.current) return
    if (consented && profileComplete) return

    checkedRef.current = true
    setChecking(true)

    Promise.all([
      fetch(`/api/users/consent-status?email=${encodeURIComponent(user.email)}`).then(r => r.json()).catch(() => ({})),
      fetch(`/api/users/profile?email=${encodeURIComponent(user.email)}`).then(r => r.json()).catch(() => ({})),
    ])
      .then(([consentData, profileData]) => {
        if (consentData.consented) {
          const updated = { ...user, role: consentData.role, language: consentData.preferred_language }
          setUser(updated)
          setConsented(true)
          localStorage.setItem('user', JSON.stringify(updated))
          localStorage.setItem('consented', 'true')
        }
        if (profileData.profile_complete) {
          setProfileComplete(true)
          localStorage.setItem('profileComplete', 'true')
        }
      })
      .finally(() => setChecking(false))
  }, [user?.email])

  const handleLogin = (userData) => {
    checkedRef.current = false
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleConsent = (consentData) => {
    const updated = { ...user, ...consentData }
    setUser(updated)
    setConsented(true)
    localStorage.setItem('user', JSON.stringify(updated))
    localStorage.setItem('consented', 'true')
  }

  const handleProfileSave = (profileData) => {
    const updated = { ...user, ...profileData }
    setUser(updated)
    setProfileComplete(true)
    localStorage.setItem('user', JSON.stringify(updated))
    localStorage.setItem('profileComplete', 'true')
  }

  const handleLogout = () => {
    checkedRef.current = false
    setUser(null)
    setConsented(false)
    setProfileComplete(false)
    setShowProfile(false)
    localStorage.removeItem('user')
    localStorage.removeItem('consented')
    localStorage.removeItem('profileComplete')
  }

  if (!user) return <LoginPage onLogin={handleLogin} />
  if (checking) return null
  if (!consented) return <ConsentModal user={user} onConsent={handleConsent} />
  if (!profileComplete) return <ProfileModal user={user} onSave={handleProfileSave} />
  if (showProfile) {
    return (
      <ProfilePage
        user={user}
        onBack={() => setShowProfile(false)}
        onUpdate={(data) => {
          const updated = { ...user, ...data }
          setUser(updated)
          localStorage.setItem('user', JSON.stringify(updated))
        }}
      />
    )
  }

  return <Dashboard user={user} onLogout={handleLogout} onProfileClick={() => setShowProfile(true)} />
}

export default App
