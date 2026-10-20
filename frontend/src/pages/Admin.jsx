import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAdminDashboard, getAdminStudents, getAdminCourses, toggleAdmin, isLoggedIn } from '../api'
import Navbar from '../components/Navbar'
import './Admin.css'

export default function Admin() {
  const [dashboard, setDashboard] = useState(null)
  const [students, setStudents] = useState([])
  const [courses, setCourses] = useState([])
  const [tab, setTab] = useState('overview')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [courseFilter, setCourseFilter] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoggedIn()) { navigate('/login'); return }
    loadDashboard()
  }, [])

  async function loadDashboard() {
    const { ok, data } = await getAdminDashboard()
    if (!ok) {
      setError(data.error || 'Admin access required')
      return
    }
    setDashboard(data)
  }

  async function loadStudents() {
    const { ok, data } = await getAdminStudents()
    if (ok) setStudents(data)
  }

  async function loadCourses() {
    const { ok, data } = await getAdminCourses()
    if (ok) setCourses(data)
  }

  async function handleToggleAdmin(studentId) {
    const { ok, data } = await toggleAdmin(studentId)
    setMessage(ok ? data.message : data.error)
    if (ok) loadStudents()
  }

  function switchTab(t) {
    setTab(t)
    if (t === 'students' && students.length === 0) loadStudents()
    if (t === 'courses' && courses.length === 0) loadCourses()
  }

  if (error) {
    return (
      <div className="admin-page">
        <Navbar />
        <div className="container admin-container">
          <div className="admin-error">{error}</div>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return (
      <div className="admin-page">
        <Navbar />
        <div className="container admin-container"><p>Loading...</p></div>
      </div>
    )
  }

  const filteredCourses = courseFilter
    ? courses.filter(c =>
        c.course_number.toLowerCase().includes(courseFilter.toLowerCase()) ||
        c.course_name.toLowerCase().includes(courseFilter.toLowerCase())
      )
    : courses

  return (
    <div className="admin-page">
      <Navbar />
      <div className="container admin-container">
        <h1>Admin Dashboard</h1>

        <div className="admin-tabs">
          <button className={tab === 'overview' ? 'active' : ''} onClick={() => switchTab('overview')}>Overview</button>
          <button className={tab === 'students' ? 'active' : ''} onClick={() => switchTab('students')}>Students</button>
          <button className={tab === 'courses' ? 'active' : ''} onClick={() => switchTab('courses')}>Courses</button>
        </div>

        {message && <div className="admin-message">{message}</div>}

        {tab === 'overview' && (
          <div className="admin-overview">
            <div className="stat-grid">
              <div className="stat-card">
                <span className="stat-number">{dashboard.total_students}</span>
                <span className="stat-label">Students</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{dashboard.total_courses}</span>
                <span className="stat-label">Courses</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{dashboard.active_enrollments}</span>
                <span className="stat-label">Active Enrollments</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{dashboard.total_waitlisted}</span>
                <span className="stat-label">Waitlisted</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{dashboard.total_reviews}</span>
                <span className="stat-label">Reviews</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{dashboard.full_courses}</span>
                <span className="stat-label">Full Courses</span>
              </div>
            </div>

            <div className="admin-grid">
              <div className="admin-card">
                <h3>Students by Degree</h3>
                <div className="breakdown-list">
                  <div className="breakdown-row">
                    <span>Undergraduate</span>
                    <span className="breakdown-val">{dashboard.students_by_degree.Undergraduate}</span>
                  </div>
                  <div className="breakdown-row">
                    <span>Graduate</span>
                    <span className="breakdown-val">{dashboard.students_by_degree.Graduate}</span>
                  </div>
                </div>
              </div>

              <div className="admin-card">
                <h3>Students by Status</h3>
                <div className="breakdown-list">
                  <div className="breakdown-row">
                    <span>Full-time</span>
                    <span className="breakdown-val">{dashboard.students_by_status['Full-time']}</span>
                  </div>
                  <div className="breakdown-row">
                    <span>Part-time</span>
                    <span className="breakdown-val">{dashboard.students_by_status['Part-time']}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="admin-card">
              <h3>Departments</h3>
              <div className="dept-grid">
                {dashboard.departments.map(d => (
                  <div key={d.name} className="dept-chip">
                    <strong>{d.name}</strong>
                    <span>{d.courses} courses</span>
                  </div>
                ))}
              </div>
            </div>

            {dashboard.top_courses.length > 0 && (
              <div className="admin-card">
                <h3>Most Popular Courses</h3>
                <table className="admin-table">
                  <thead>
                    <tr><th>Course</th><th>Name</th><th>Enrolled</th></tr>
                  </thead>
                  <tbody>
                    {dashboard.top_courses.map(c => (
                      <tr key={c.course_number}>
                        <td>{c.course_number}</td>
                        <td>{c.course_name}</td>
                        <td>{c.enrollments}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {tab === 'students' && (
          <div className="admin-card">
            <h3>All Students ({students.length})</h3>
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th><th>Name</th><th>Email</th><th>Program</th>
                  <th>Degree</th><th>Status</th><th>Enrolled</th><th>Admin</th>
                </tr>
              </thead>
              <tbody>
                {students.map(s => (
                  <tr key={s.student_id}>
                    <td>{s.student_id}</td>
                    <td>{s.name}</td>
                    <td>{s.email}</td>
                    <td>{s.program}</td>
                    <td>{s.degree_status}</td>
                    <td>{s.status}</td>
                    <td>{s.enrolled_count}</td>
                    <td>
                      <button
                        className={`btn btn-sm ${s.is_admin ? 'btn-primary' : 'btn-outline'}`}
                        onClick={() => handleToggleAdmin(s.student_id)}
                      >
                        {s.is_admin ? 'Admin' : 'User'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'courses' && (
          <div className="admin-card">
            <h3>All Courses ({courses.length})</h3>
            <input
              type="text"
              className="admin-search"
              placeholder="Filter courses..."
              value={courseFilter}
              onChange={e => setCourseFilter(e.target.value)}
            />
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Course</th><th>Name</th><th>Professor</th><th>Level</th>
                  <th>Semester</th><th>Seats</th><th>Enrolled</th><th>Waitlisted</th><th>Rating</th>
                </tr>
              </thead>
              <tbody>
                {filteredCourses.map(c => (
                  <tr key={c.course_number}>
                    <td>{c.course_number}</td>
                    <td>{c.course_name}</td>
                    <td>{c.professor_name}</td>
                    <td>{c.level}</td>
                    <td>{c.semester}</td>
                    <td>{c.available_seats}/{c.total_seats}</td>
                    <td>{c.enrolled}</td>
                    <td>{c.waitlisted}</td>
                    <td>{c.avg_rating ? `${c.avg_rating}/5` : '-'}</td>
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
