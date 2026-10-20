import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSchedule, isLoggedIn } from '../api'
import Navbar from '../components/Navbar'
import './Schedule.css'

const DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
const HOURS = Array.from({ length: 13 }, (_, i) => i + 8) // 8 AM to 8 PM

const COLORS = [
  '#dbeafe', '#dcfce7', '#fef3c7', '#fce7f3', '#e0e7ff',
  '#cffafe', '#fde68a', '#d9f99d', '#fbcfe8', '#c7d2fe',
]

function parseTime(timeStr) {
  const [time, period] = timeStr.trim().split(' ')
  let [h, m] = time.split(':').map(Number)
  if (period === 'PM' && h !== 12) h += 12
  if (period === 'AM' && h === 12) h = 0
  return h + m / 60
}

export default function Schedule() {
  const [schedule, setSchedule] = useState({})
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoggedIn()) { navigate('/login'); return }
    loadSchedule()
  }, [])

  async function loadSchedule() {
    const { ok, data } = await getSchedule()
    if (ok) setSchedule(data)
    setLoading(false)
  }

  const allCourses = []
  const courseColors = {}
  let colorIdx = 0

  for (const day of DAYS) {
    if (schedule[day]) {
      for (const course of schedule[day]) {
        if (!courseColors[course.course_number]) {
          courseColors[course.course_number] = COLORS[colorIdx % COLORS.length]
          colorIdx++
        }
        allCourses.push({ ...course, day })
      }
    }
  }

  return (
    <div className="schedule-page">
      <Navbar />
      <div className="container schedule-container">
        <h1>Weekly Schedule</h1>

        {loading ? (
          <p>Loading schedule...</p>
        ) : allCourses.length === 0 ? (
          <div className="schedule-empty">
            <p>No courses in your schedule yet.</p>
            <a href="/dashboard" className="btn btn-primary">Browse Courses</a>
          </div>
        ) : (
          <div className="schedule-grid">
            <div className="grid-header">
              <div className="time-label"></div>
              {DAYS.map(day => (
                <div key={day} className="day-header">{day}</div>
              ))}
            </div>

            <div className="grid-body">
              <div className="time-column">
                {HOURS.map(h => (
                  <div key={h} className="time-slot">
                    {h <= 12 ? h : h - 12} {h < 12 ? 'AM' : 'PM'}
                  </div>
                ))}
              </div>

              {DAYS.map(day => (
                <div key={day} className="day-column">
                  {HOURS.map(h => (
                    <div key={h} className="grid-cell"></div>
                  ))}

                  {(schedule[day] || []).map(course => {
                    const start = parseTime(course.start_time)
                    const end = parseTime(course.end_time)
                    const top = (start - 8) * 60
                    const height = (end - start) * 60

                    return (
                      <div
                        key={course.course_number}
                        className="course-block"
                        style={{
                          top: `${top}px`,
                          height: `${height}px`,
                          background: courseColors[course.course_number],
                        }}
                      >
                        <strong>{course.course_number}</strong>
                        <span>{course.course_name}</span>
                        <span className="block-time">
                          {course.start_time} - {course.end_time}
                        </span>
                      </div>
                    )
                  })}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
