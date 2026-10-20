import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchCourses, enroll, getEnrollments, dropCourse, isLoggedIn } from '../api'
import Navbar from '../components/Navbar'
import './Dashboard.css'

export default function Dashboard() {
  const [query, setQuery] = useState('')
  const [semester, setSemester] = useState('')
  const [level, setLevel] = useState('')
  const [mode, setMode] = useState('keyword')
  const [courses, setCourses] = useState([])
  const [enrolled, setEnrolled] = useState([])
  const [message, setMessage] = useState('')
  const [searching, setSearching] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoggedIn()) { navigate('/login'); return }
    loadEnrollments()
  }, [])

  async function loadEnrollments() {
    const { ok, data } = await getEnrollments()
    if (ok) setEnrolled(data)
  }

  async function handleSearch(e) {
    e.preventDefault()
    setSearching(true)
    setMessage('')
    const { ok, data } = await searchCourses(query, semester, level, mode)
    setSearching(false)
    if (ok) setCourses(data)
  }

  async function handleEnroll(courseNumber) {
    setMessage('')
    const { ok, data } = await enroll(courseNumber)
    setMessage(ok ? data.message : data.error)
    if (ok) loadEnrollments()
  }

  async function handleDrop(courseNumber) {
    setMessage('')
    const { ok, data } = await dropCourse(courseNumber)
    setMessage(ok ? data.message : data.error)
    if (ok) loadEnrollments()
  }

  const enrolledNumbers = new Set(enrolled.map(e => e.course_number))

  return (
    <div className="dashboard-page">
      <Navbar />
      <div className="container dashboard-container">
        <div className="dashboard-main">
          <h1>Course Catalog</h1>

          <form className="search-bar" onSubmit={handleSearch}>
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search courses, professors, or topics..."
              className="search-input"
            />
            <select value={semester} onChange={e => setSemester(e.target.value)}>
              <option value="">All Semesters</option>
              <option value="Fall">Fall</option>
              <option value="Winter">Winter</option>
            </select>
            <select value={level} onChange={e => setLevel(e.target.value)}>
              <option value="">All Levels</option>
              <option value="Undergraduate">Undergraduate</option>
              <option value="Graduate">Graduate</option>
            </select>
            <select value={mode} onChange={e => setMode(e.target.value)}>
              <option value="keyword">Keyword</option>
              <option value="semantic">Semantic</option>
            </select>
            <button type="submit" className="btn btn-primary" disabled={searching}>
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {message && <div className="dashboard-message">{message}</div>}

          <div className="course-list">
            {courses.map(c => (
              <div key={c.course_number} className="course-card">
                <div className="course-header">
                  <span className="course-number">{c.course_number}</span>
                  <span className={`course-badge ${c.level === 'Graduate' ? 'badge-grad' : 'badge-undergrad'}`}>
                    {c.level}
                  </span>
                </div>
                <h3>{c.course_name}</h3>
                <p className="course-prof">{c.professor_name}</p>
                <div className="course-meta">
                  <span>{c.days}</span>
                  <span>{c.start_time} - {c.end_time}</span>
                  <span>{c.credits} credits</span>
                  <span>{c.available_seats} seats left</span>
                </div>
                <div className="course-actions">
                  {enrolledNumbers.has(c.course_number) ? (
                    <button className="btn btn-outline btn-sm" onClick={() => handleDrop(c.course_number)}>
                      Drop
                    </button>
                  ) : (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => handleEnroll(c.course_number)}
                      disabled={c.available_seats === 0}
                    >
                      {c.available_seats === 0 ? 'Full' : 'Enroll'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="dashboard-sidebar">
          <h2>My Courses ({enrolled.length})</h2>
          {enrolled.length === 0 ? (
            <p className="sidebar-empty">No courses enrolled yet. Search and enroll above.</p>
          ) : (
            <div className="enrolled-list">
              {enrolled.map(e => (
                <div key={e.course_number} className="enrolled-item">
                  <div>
                    <strong>{e.course_number}</strong>
                    <p>{e.course_name}</p>
                    <span className="enrolled-time">{e.days} &middot; {e.start_time}</span>
                  </div>
                  <button className="btn-drop" onClick={() => handleDrop(e.course_number)}>
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}
