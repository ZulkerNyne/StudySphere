import { Link, useNavigate } from 'react-router-dom'
import { isLoggedIn, logout } from '../api'
import './Navbar.css'

export default function Navbar() {
  const navigate = useNavigate()
  const loggedIn = isLoggedIn()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">&#9670;</span>
          <span className="logo-text">StudySphere</span>
        </Link>

        <div className="navbar-links">
          <Link to="/dashboard">Courses</Link>
          <Link to="/schedule">Schedule</Link>
          <Link to="/advisor">AI Advisor</Link>
        </div>

        <div className="navbar-actions">
          {loggedIn ? (
            <>
              <Link to="/profile" className="btn btn-outline">My Profile</Link>
              <button className="btn btn-outline" onClick={handleLogout}>Sign Out</button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">Sign In</Link>
              <Link to="/register" className="btn btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
