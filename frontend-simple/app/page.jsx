'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [resumeText, setResumeText] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [jobRequirements, setJobRequirements] = useState('')
  const [jobBenefits, setJobBenefits] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResults(null)

    try {
      const response = await axios.post(`${API_URL}/predict`, {
        resume_text: resumeText,
        job_title: jobTitle,
        description: jobDescription,
        requirements: jobRequirements,
        benefits: jobBenefits
      })

      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to process request. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="main-container">
      <div className="header">
        <h1>Job Matcher AI</h1>
        <p>Match your resume with job postings using PhoBERT AI model</p>
      </div>

      <form onSubmit={handleSubmit} className="form-section">
        <div className="form-group">
          <label className="form-label">Resume Text</label>
          <textarea
            className="form-textarea"
            placeholder="Paste your resume text here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            required
          />
        </div>

        <div className="two-column">
          <div className="form-group">
            <label className="form-label">Job Title</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Senior Software Engineer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Benefits</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g., Health insurance, 401k, remote work"
              value={jobBenefits}
              onChange={(e) => setJobBenefits(e.target.value)}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Job Description</label>
          <textarea
            className="form-textarea"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label">Job Requirements</label>
          <textarea
            className="form-textarea"
            placeholder="List the job requirements here..."
            value={jobRequirements}
            onChange={(e) => setJobRequirements(e.target.value)}
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Processing...' : 'Analyze Match'}
        </button>
      </form>

      {error && (
        <div className="form-section">
          <div className="error">{error}</div>
        </div>
      )}

      {loading && (
        <div className="results-section">
          <div className="loading">Analyzing your resume against the job posting...</div>
        </div>
      )}

      {results && (
        <div className="results-section">
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem', fontWeight: '600' }}>
            Analysis Results
          </h2>

          {results.predicted_salary && (
            <div className="result-item">
              <div className="result-label">Predicted Salary Range</div>
              <div className="result-value">{results.predicted_salary}</div>
            </div>
          )}

          {results.match_score !== undefined && (
            <div className="result-item">
              <div className="result-label">Match Score</div>
              <div className="result-value">{Math.round(results.match_score * 100)}%</div>
            </div>
          )}

          {results.missing_skills && results.missing_skills.length > 0 && (
            <div className="result-item">
              <div className="result-label">Missing Skills</div>
              <div className="result-value">
                {results.missing_skills.map((skill, index) => (
                  <span
                    key={index}
                    style={{
                      display: 'inline-block',
                      background: '#e2e8f0',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '9999px',
                      marginRight: '0.5rem',
                      marginBottom: '0.5rem',
                      fontSize: '0.875rem'
                    }}
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {results.parsed_resume && (
            <div className="result-item">
              <div className="result-label">Parsed Resume Information</div>
              <div className="result-value" style={{ whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(results.parsed_resume, null, 2)}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}