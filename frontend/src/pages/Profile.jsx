import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProfile, getFees, getDropHistory, isLoggedIn } from '../api'
import Navbar from '../components/Navbar'
import './Profile.css'

export default function Profile() {
  const [profile, setProfile] = useState(null)
  const [fees, setFees] = useState(null)
  const [history, setHistory] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoggedIn()) {
      navigate('/login')
      return
    }
    loadData()
  }, [])

  async function loadData() {
    const [p, f, h] = await Promise.all([getProfile(), getFees(), getDropHistory()])
    if (p.ok) setProfile(p.data)
    if (f.ok) setFees(f.data)
    if (h.ok) setHistory(h.data)
  }

  if (!profile) return <div className="profile-page"><Navbar /><div className="container"><p>Loading...</p></div></div>

  return (
    <div className="profile-page">
      <Navbar />
      <div className="container profile-container">
        <h1 className="profile-heading">Academic Profile</h1>

        <div className="profile-grid">
          <div className="profile-card info-card">
            <h2>Student Information</h2>
            <div className="info-rows">
              <div className="info-row"><span className="info-label">Name</span><span>{profile.name}</span></div>
              <div className="info-row"><span className="info-label">Student ID</span><span>{profile.student_id}</span></div>
              <div className="info-row"><span className="info-label">Email</span><span>{profile.email}</span></div>
              <div className="info-row"><span className="info-label">Program</span><span>{profile.program}</span></div>
              <div className="info-row"><span className="info-label">Degree Level</span><span className="badge">{profile.degree_status}</span></div>
              <div className="info-row"><span className="info-label">Enrollment Status</span><span className="badge badge-accent">{profile.status}</span></div>
            </div>
          </div>

          <div className="profile-card limits-card">
            <h2>Enrollment Limits</h2>
            <div className="limit-visual">
              <div className="limit-bar-bg">
                <div
                  className="limit-bar-fill"
                  style={{ width: `${(profile.enrolled_count / profile.max_courses) * 100}%` }}
                />
              </div>
              <p className="limit-text">
                {profile.enrolled_count} / {profile.max_courses} courses enrolled
              </p>
              <p className="limit-subtext">
                {profile.max_courses - profile.enrolled_count} slots remaining ({profile.status})
              </p>
            </div>
          </div>
        </div>

        {fees && (
          <div className="profile-card fees-card">
            <h2>Tuition Fees</h2>
            <div className="fees-summary">
              <div className="fee-stat">
                <span className="fee-amount">${fees.fee_per_credit}</span>
                <span className="fee-label">per credit</span>
              </div>
              <div className="fee-stat">
                <span className="fee-amount">{fees.total_credits}</span>
                <span className="fee-label">total credits</span>
              </div>
              <div className="fee-stat fee-total">
                <span className="fee-amount">${fees.total_fee.toLocaleString()}</span>
                <span className="fee-label">total tuition</span>
              </div>
            </div>
            {fees.courses.length > 0 && (
              <table className="fees-table">
                <thead>
                  <tr><th>Course</th><th>Name</th><th>Credits</th><th>Fee</th></tr>
                </thead>
                <tbody>
                  {fees.courses.map(c => (
                    <tr key={c.course_number}>
                      <td>{c.course_number}</td>
                      <td>{c.course_name}</td>
                      <td>{c.credits}</td>
                      <td>${c.fee.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        {history.length > 0 && (
          <div className="profile-card history-card">
            <h2>Drop History</h2>
            <table className="fees-table">
              <thead>
                <tr><th>Course</th><th>Name</th><th>Enrolled</th><th>Dropped</th></tr>
              </thead>
              <tbody>
                {history.map((h, i) => (
                  <tr key={i}>
                    <td>{h.course_number}</td>
                    <td>{h.course_name}</td>
                    <td>{new Date(h.enrolled_at).toLocaleDateString()}</td>
                    <td>{h.dropped_at ? new Date(h.dropped_at).toLocaleDateString() : '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
