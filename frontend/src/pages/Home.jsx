import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import './Home.css'

export default function Home() {
  return (
    <div className="home">
      <Navbar />

      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-content">
            <span className="hero-badge">AI-POWERED LEARNING</span>
            <h1 className="hero-title">
              Discover the <em>freedom</em> of learning on your terms
            </h1>
            <p className="hero-subtitle">
              Get course search, AI advising, schedule management,
              and smart enrollment — all in one intelligent platform.
            </p>
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary btn-lg">
                Get Started Free
              </Link>
              <Link to="/login" className="btn btn-outline btn-lg">
                Sign In
              </Link>
            </div>
          </div>

          <div className="hero-cards">
            <div className="feature-card card-courses">
              <div className="card-inner">
                <h3>Course Search</h3>
                <p className="card-desc">
                  The all-in-one tool for searching, filtering, and discovering courses.
                  Keyword or AI — find freely across 500+ courses.
                </p>
                <div className="card-icons">
                  <span className="card-icon">&#128270;</span>
                  <span className="card-icon">&#9733;</span>
                  <span className="card-icon">&#128218;</span>
                </div>
                <div className="card-visual">
                  <div className="card-visual-img"></div>
                </div>
                <Link to="/dashboard" className="card-arrow">&rarr;</Link>
              </div>
            </div>
            <div className="feature-card card-advisor">
              <div className="card-texture"></div>
              <div className="card-inner">
                <span className="card-label">AI Advisor</span>
                <Link to="/advisor" className="card-arrow">&rarr;</Link>
              </div>
            </div>
            <div className="feature-card card-schedule">
              <div className="card-texture"></div>
              <div className="card-inner">
                <span className="card-label">Schedule</span>
                <Link to="/schedule" className="card-arrow">&rarr;</Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="features">
        <div className="container">
          <h2 className="section-title">Everything you need to succeed</h2>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">&#127891;</div>
              <h3>Smart Enrollment</h3>
              <p>Automatic time conflict detection and seat availability checks before you enroll.</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">&#129302;</div>
              <h3>AI Course Advisor</h3>
              <p>Ask questions in plain English. The advisor searches, checks conflicts, and enrolls for you.</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">&#128200;</div>
              <h3>Semantic Search</h3>
              <p>Find courses by concept, not just keywords. "Anything about neural networks" just works.</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">&#128197;</div>
              <h3>Visual Schedule</h3>
              <p>See your weekly timetable at a glance with color-coded course blocks.</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">&#128274;</div>
              <h3>Secure Auth</h3>
              <p>JWT authentication with bcrypt password hashing. Your data stays safe.</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">&#9881;</div>
              <h3>MCP Server</h3>
              <p>Expose tools to any LLM client via Model Context Protocol. Future-proof integration.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="cta">
        <div className="container cta-inner">
          <h2>Ready to transform your course planning?</h2>
          <p>Join Study Sphere and let AI handle the complexity.</p>
          <Link to="/register" className="btn btn-primary btn-lg">Create Your Account</Link>
        </div>
      </section>

      <footer className="footer">
        <div className="container footer-inner">
          <div className="footer-brand">
            <span className="logo-icon">&#9670;</span>
            <span>StudySphere</span>
          </div>
          <p>Built with Flask, React, Claude AI, ChromaDB & MCP</p>
        </div>
      </footer>
    </div>
  )
}
