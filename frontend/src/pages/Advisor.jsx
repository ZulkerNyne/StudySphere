import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { chatWithAdvisor, isLoggedIn } from '../api'
import Navbar from '../components/Navbar'
import './Advisor.css'

export default function Advisor() {
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoggedIn()) { navigate('/login'); return }
    setMessages([{
      role: 'assistant',
      text: "Hi! I'm your AI course advisor. I can help you find courses, check schedule conflicts, enroll in classes, or view your schedule. What would you like to do?",
    }])
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    const { ok, data } = await chatWithAdvisor(userMsg, history)
    setLoading(false)

    if (ok) {
      setMessages(prev => [...prev, { role: 'assistant', text: data.response }])
      setHistory(data.history || [])
    } else {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.error || 'Something went wrong. Please try again.',
      }])
    }
  }

  return (
    <div className="advisor-page">
      <Navbar />
      <div className="container advisor-container">
        <div className="chat-header">
          <h1>AI Course Advisor</h1>
          <p>Powered by Claude</p>
        </div>

        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role}`}>
              {msg.role === 'assistant' && (
                <div className="bubble-avatar">AI</div>
              )}
              <div className="bubble-text">{msg.text}</div>
            </div>
          ))}
          {loading && (
            <div className="chat-bubble assistant">
              <div className="bubble-avatar">AI</div>
              <div className="bubble-text typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <form className="chat-input" onSubmit={handleSend}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about courses, schedule, enrollment..."
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
