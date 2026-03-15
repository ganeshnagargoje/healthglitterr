import { useState, useEffect } from 'react'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ConsentModal from './components/ConsentModal'

function App() {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })

  const [consented, setConsented] = useState(() => {
    return localStorage.getItem('consented') === 'true'
  })

  const [checkingConsent, setCheckingConsent] = useState(false)

  // After login, check backend for existing consent
  useEffect(() => {
    if (!user || consented) return

    setCheckingConsent(true)
    fetch(`/api/users/consent-status?email=${encodeURIComponent(user.email)}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.consented) {
          const updatedUser = {
            ...user,
            role: data.role,
            language: data.preferred_language,
          }
          setUser(updatedUser)
          setConsented(true)
          localStorage.setItem('user', JSON.stringify(updatedUser))
          localStorage.setItem('consented', 'true')
        }
      })
      .catch(() => {
        // If backend is unreachable, fall through to show modal
      })
      .finally(() => setCheckingConsent(false))
  }, [user, consented])

  const handleLogin = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const handleConsent = (consentData) => {
    const updatedUser = { ...user, ...consentData }
    setUser(updatedUser)
    setConsented(true)
    localStorage.setItem('user', JSON.stringify(updatedUser))
    localStorage.setItem('consented', 'true')
  }

  const handleLogout = () => {
    setUser(null)
    setConsented(false)
    localStorage.removeItem('user')
    localStorage.removeItem('consented')
  }

  if (!user) {
    return <LoginPage onLogin={handleLogin} />
  }

  if (checkingConsent) {
    return null // brief blank while checking — avoids flash of consent modal
  }

  if (!consented) {
    return <ConsentModal user={user} onConsent={handleConsent} />
  }

  return <Dashboard user={user} onLogout={handleLogout} />
}

export default App
