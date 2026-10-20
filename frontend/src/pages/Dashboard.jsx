import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchCourses, enroll, getEnrollments, dropCourse, joinWaitlist, leaveWaitlist, getReviews, addReview, isLoggedIn } from '../api'
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
  const [reviewModal, setReviewModal] = useState(null)
  const [reviewData, setReviewData] = useState({ rating: 5, comment: '' })
  const [courseReviews, setCourseReviews] = useState(null)
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
    if (ok) {
      loadEnrollments()
      handleSearch({ preventDefault: () => {} })
    }
  }

  async function handleDrop(courseNumber) {
    setMessage('')
    const { ok, data } = await dropCourse(courseNumber)
    setMessage(ok ? data.message : data.error)
    if (ok) {
      loadEnrollments()
      handleSearch({ preventDefault: () => {} })
    }
  }

  async function handleJoinWaitlist(courseNumber) {
    setMessage('')
    const { ok, data } = await joinWaitlist(courseNumber)
    setMessage(ok ? data.message : data.error)
  }

  async function openReviews(courseNumber) {
    const { ok, data } = await getReviews(courseNumber)
    if (ok) {
      setCourseReviews(data)
      setReviewModal(courseNumber)
      setReviewData({ rating: 5, comment: '' })
    }
  }

  async function handleSubmitReview(e) {
    e.preventDefault()
    const { ok, data } = await addReview(reviewModal, reviewData.rating, reviewData.comment)
    if (ok) {
      openReviews(reviewModal)
      handleSearch({ preventDefault: () => {} })
    }
    setMessage(ok ? data.message : data.error)
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
                  <div className="course-badges">
                    <span className={`course-badge ${c.level === 'Graduate' ? 'badge-grad' : 'badge-undergrad'}`}>
                      {c.level}
                    </span>
                    {c.avg_rating && (
                      <span className="course-badge badge-rating" onClick={() => openReviews(c.course_number)}>
                        {'★'.repeat(Math.round(c.avg_rating))} {c.avg_rating} ({c.review_count})
                      </span>
                    )}
                  </div>
                </div>
                <h3>{c.course_name}</h3>
                <p className="course-prof">{c.professor_name}</p>
                <div className="course-meta">
                  <span>{c.days}</span>
                  <span>{c.start_time} - {c.end_time}</span>
                  <span>{c.credits} credits</span>
                  <span>{c.available_seats > 0 ? `${c.available_seats} seats left` : 'Full'}</span>
                  {c.waitlist_count > 0 && <span>{c.waitlist_count} waitlisted</span>}
                </div>
                {c.prerequisites && c.prerequisites.length > 0 && (
                  <div className="course-prereqs">
                    Prerequisites: {c.prerequisites.join(', ')}
                  </div>
                )}
                <div className="course-actions">
                  {enrolledNumbers.has(c.course_number) ? (
                    <>
                      <button className="btn btn-outline btn-sm" onClick={() => handleDrop(c.course_number)}>
                        Drop
                      </button>
                      <button className="btn btn-sm btn-ghost" onClick={() => openReviews(c.course_number)}>
                        Reviews
                      </button>
                    </>
                  ) : c.available_seats > 0 ? (
                    <>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleEnroll(c.course_number)}
                      >
                        Enroll
                      </button>
                      <button className="btn btn-sm btn-ghost" onClick={() => openReviews(c.course_number)}>
                        Reviews
                      </button>
                    </>
                  ) : (
                    <>
                      <button className="btn btn-outline btn-sm" onClick={() => handleJoinWaitlist(c.course_number)}>
                        Join Waitlist
                      </button>
                      <button className="btn btn-sm btn-ghost" onClick={() => openReviews(c.course_number)}>
                        Reviews
                      </button>
                    </>
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

      {reviewModal && courseReviews && (
        <div className="modal-overlay" onClick={() => setReviewModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setReviewModal(null)}>&times;</button>
            <h2>Reviews for {reviewModal}</h2>
            {courseReviews.average_rating && (
              <p className="review-avg">
                Average: {'★'.repeat(Math.round(courseReviews.average_rating))}{'☆'.repeat(5 - Math.round(courseReviews.average_rating))} {courseReviews.average_rating}/5 ({courseReviews.count} reviews)
              </p>
            )}

            <div className="review-list">
              {courseReviews.reviews.length === 0 && <p>No reviews yet. Be the first!</p>}
              {courseReviews.reviews.map(r => (
                <div key={r.id} className="review-item">
                  <div className="review-header">
                    <strong>{r.student_name}</strong>
                    <span>{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</span>
                  </div>
                  {r.comment && <p>{r.comment}</p>}
                  <span className="review-date">{new Date(r.created_at).toLocaleDateString()}</span>
                </div>
              ))}
            </div>

            {courseReviews.can_review ? (
              <form className="review-form" onSubmit={handleSubmitReview}>
                <h3>Write a Review</h3>
                <div className="star-picker">
                  {[1, 2, 3, 4, 5].map(n => (
                    <span
                      key={n}
                      className={`star ${n <= reviewData.rating ? 'active' : ''}`}
                      onClick={() => setReviewData(d => ({ ...d, rating: n }))}
                    >
                      ★
                    </span>
                  ))}
                </div>
                <textarea
                  value={reviewData.comment}
                  onChange={e => setReviewData(d => ({ ...d, comment: e.target.value }))}
                  placeholder="Share your experience..."
                  rows={3}
                />
                <button type="submit" className="btn btn-primary btn-sm">Submit Review</button>
              </form>
            ) : (
              <p className="review-notice">Enroll in this course to leave a review.</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
