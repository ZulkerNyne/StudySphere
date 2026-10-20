const API_BASE = '/api'

function getToken() {
  return localStorage.getItem('token')
}

function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function login(studentId, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ student_id: studentId, password }),
  })
  const data = await res.json()
  if (res.ok) {
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('studentId', data.student_id)
  }
  return { ok: res.ok, data }
}

export async function register(fields) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fields),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function searchCourses(query, semester, level, mode = 'keyword') {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  if (semester) params.set('semester', semester)
  if (level) params.set('level', level)
  if (mode) params.set('mode', mode)
  const res = await fetch(`${API_BASE}/courses?${params}`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getCourse(courseNumber) {
  const res = await fetch(`${API_BASE}/courses/${courseNumber}`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function enroll(courseNumber) {
  const res = await fetch(`${API_BASE}/enrollment/enroll`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ course_number: courseNumber }),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function dropCourse(courseNumber) {
  const res = await fetch(`${API_BASE}/enrollment/drop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ course_number: courseNumber }),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getEnrollments() {
  const studentId = localStorage.getItem('studentId')
  const res = await fetch(`${API_BASE}/enrollment/${studentId}`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getSchedule() {
  const studentId = localStorage.getItem('studentId')
  const res = await fetch(`${API_BASE}/schedule/${studentId}`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function chatWithAdvisor(message, history = []) {
  const res = await fetch(`${API_BASE}/advisor/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ message, history }),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getProfile() {
  const res = await fetch(`${API_BASE}/auth/profile`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getFees() {
  const res = await fetch(`${API_BASE}/enrollment/fees`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function swapCourse(dropCourseNum, enrollCourseNum) {
  const res = await fetch(`${API_BASE}/enrollment/swap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({ drop_course: dropCourseNum, enroll_course: enrollCourseNum }),
  })
  return { ok: res.ok, data: await res.json() }
}

export async function getDropHistory() {
  const studentId = localStorage.getItem('studentId')
  const res = await fetch(`${API_BASE}/enrollment/history/${studentId}`, {
    headers: authHeaders(),
  })
  return { ok: res.ok, data: await res.json() }
}

export function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('studentId')
}

export function isLoggedIn() {
  return !!localStorage.getItem('token')
}
