import { useState, useRef, useEffect } from 'react'
import './Dashboard.css'

function Dashboard({ user, onLogout }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const fileInputRef = useRef(null)

  const initials = user?.initials || user?.name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'U'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => { scrollToBottom() }, [messages, isTyping])
  useEffect(() => { inputRef.current?.focus() }, [])

  const handleSend = () => {
    const text = input.trim()
    if (!text) return
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text }])
    setInput('')
    setIsTyping(true)
    // Simulate AI response — replace with real API call
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        text: getReply(text),
      }])
      setIsTyping(false)
    }, 1200)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'user',
      text: `📎 Uploaded: ${file.name}`,
      isFile: true,
      fileName: file.name,
    }])
    setIsTyping(true)
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        text: `I've received **${file.name}**. Analyzing your medical report...\n\n✅ Extraction complete. Here's a summary:\n\n• **Hemoglobin**: 14.2 g/dL (Normal)\n• **WBC Count**: 11,200 /μL (Slightly elevated)\n• **Platelets**: 250,000 /μL (Normal)\n• **Blood Glucose**: 142 mg/dL (High)\n\n⚠️ Your blood glucose is above the normal range. I'd recommend discussing this with your doctor.\n\nWould you like me to analyze trends or provide recommendations?`,
      }])
      setIsTyping(false)
    }, 2000)
    e.target.value = ''
  }

  // Empty state — no messages yet
  const showWelcome = messages.length === 0 && !isTyping

  return (
    <div className="chat-layout">
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-brand">
          <svg className="nav-logo" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#4A90D9" strokeWidth="3" />
            <path d="M30 50 L42 50 L46 35 L50 65 L54 35 L58 50 L70 50"
              fill="none" stroke="#4A90D9" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="20" cy="20" r="3" fill="#34A853" />
            <circle cx="80" cy="20" r="3" fill="#4285F4" />
            <circle cx="20" cy="80" r="3" fill="#FBBC05" />
            <circle cx="80" cy="80" r="3" fill="#EA4335" />
          </svg>
          <span className="nav-title">HealthGlitterr <span className="nav-accent">AI</span></span>
        </div>
        <div className="nav-actions">
          <div className="avatar">{initials}</div>
          <button className="signout-btn" onClick={onLogout}>Sign Out</button>
        </div>
      </nav>

      {/* Chat Area */}
      <div className="chat-area">
        {showWelcome ? (
          <div className="welcome">
            <svg className="welcome-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="64" height="64">
              <circle cx="50" cy="50" r="45" fill="none" stroke="#4A90D9" strokeWidth="2.5" />
              <path d="M30 50 L42 50 L46 35 L50 65 L54 35 L58 50 L70 50"
                fill="none" stroke="#4A90D9" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <h1 className="welcome-title">How can I help you today?</h1>
            <p className="welcome-sub">Upload a medical report or ask me about your health parameters.</p>
            <div className="suggestions">
              {['Analyze my latest blood report', 'Show my health trends', 'What does high LDL mean?', 'Give me diet recommendations'].map((s) => (
                <button key={s} className="suggestion-chip" onClick={() => { setInput(s) }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className={`msg-avatar ${msg.role}`}>
                  {msg.role === 'assistant' ? 'AI' : initials}
                </div>
                <div className="msg-content">
                  <span className="msg-name">{msg.role === 'assistant' ? 'HealthGlitterr AI' : user?.name || 'You'}</span>
                  <div className="msg-text">{msg.text}</div>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="message assistant">
                <div className="msg-avatar assistant">AI</div>
                <div className="msg-content">
                  <span className="msg-name">HealthGlitterr AI</span>
                  <div className="msg-text typing-dots"><span /><span /><span /></div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className="input-bar-wrapper">
        <div className="input-bar">
          <button className="attach-btn" onClick={() => fileInputRef.current?.click()} aria-label="Upload file">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
            </svg>
          </button>
          <input ref={fileInputRef} type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handleFileUpload} hidden />
          <textarea
            ref={inputRef}
            className="chat-input"
            placeholder="Ask about your health reports..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button className="send-btn" onClick={handleSend} disabled={!input.trim()} aria-label="Send">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </div>
        <p className="input-disclaimer">HealthGlitterr AI can make mistakes. Not a substitute for professional medical advice.</p>
      </div>
    </div>
  )
}

function getReply(text) {
  const l = text.toLowerCase()
  if (l.includes('hello') || l.includes('hi')) return "Hello! I'm your health assistant. You can upload a medical report or ask me anything about your health parameters."
  if (l.includes('upload') || l.includes('report')) return "Click the 📎 button to upload your medical report (PDF, PNG, JPG). I'll extract and analyze the parameters for you."
  if (l.includes('trend')) return "I can show trends for your health parameters over time. Upload multiple reports and I'll track changes in your key metrics."
  if (l.includes('cholesterol') || l.includes('ldl')) return "LDL (Low-Density Lipoprotein) is often called 'bad' cholesterol. Elevated levels increase cardiovascular risk. Normal range is below 100 mg/dL. Lifestyle changes like diet and exercise can help lower it."
  if (l.includes('diet') || l.includes('recommend')) return "Based on general health guidelines:\n\n• Increase fiber intake (fruits, vegetables, whole grains)\n• Reduce saturated fats and processed foods\n• Stay hydrated — aim for 8 glasses of water daily\n• Include omega-3 rich foods (fish, walnuts, flaxseed)\n• Limit sodium intake to under 2,300mg/day\n\nFor personalized recommendations, upload your latest report."
  if (l.includes('blood') || l.includes('analyze')) return "I'd be happy to analyze your blood report. Please upload the file using the 📎 button and I'll extract all parameters, check them against reference ranges, and provide insights."
  return "I can help you understand your lab reports, track health trends, and provide wellness insights. Try uploading a report or asking about specific health parameters."
}

export default Dashboard
