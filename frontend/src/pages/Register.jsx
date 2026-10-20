import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register } from '../api'
import Navbar from '../components/Navbar'
import './Auth.css'

export default function Register() {
  const [form, setForm] = useState({
    student_id: '',
    name: '',
    email: '',
    password: '',
    program: 'Computer Science',
    degree_status: 'Undergraduate',
    status: 'Full-time',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  function update(field, value) {
    setForm(prev => ({ ...prev, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    const { ok, data } = await register(form)
    setLoading(false)
    if (ok) {
      navigate('/login')
    } else {
      setError(data.error || 'Registration failed')
    }
  }

  return (
    <div className="auth-page">
      <Navbar />
      <div className="auth-container">
        <div className="auth-card auth-card-wide">
          <h1>Create your account</h1>
          <p className="auth-subtitle">Get started with Study Sphere</p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>Student ID</label>
                <input type="text" value={form.student_id} onChange={e => update('student_id', e.target.value)} placeholder="e.g. STU001" required />
              </div>
              <div className="form-group">
                <label>Full Name</label>
                <input type="text" value={form.name} onChange={e => update('name', e.target.value)} placeholder="Your full name" required />
              </div>
            </div>

            <label>Email</label>
            <input type="email" value={form.email} onChange={e => update('email', e.target.value)} placeholder="you@university.edu" required />

            <label>Password</label>
            <input type="password" value={form.password} onChange={e => update('password', e.target.value)} placeholder="At least 6 characters" required />

            <div className="form-row">
              <div className="form-group">
                <label>Program</label>
                <select value={form.program} onChange={e => update('program', e.target.value)}>
                  <option>Computer Science</option>
                  <option>Mathematics</option>
                  <option>Physics</option>
                  <option>Biology</option>
                  <option>Chemistry</option>
                  <option>Engineering</option>
                  <option>Economics</option>
                </select>
              </div>
              <div className="form-group">
                <label>Degree Level</label>
                <select value={form.degree_status} onChange={e => update('degree_status', e.target.value)}>
                  <option>Undergraduate</option>
                  <option>Graduate</option>
                </select>
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
