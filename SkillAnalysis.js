import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8001";

export default function SkillAnalysis({ profileData }) {
  const [jobTitle, setJobTitle] = useState('');
  const [location, setLocation] = useState('');
  const [trends, setTrends] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchSkillTrends = async () => {
    if (!jobTitle) {
      setError('Please enter a job title');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_URL}/skills/trends`, {
        params: { job_title: jobTitle, location }
      });
      setTrends(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching skill trends');
    }
    setLoading(false);
  };

  const compareSkills = async () => {
    if (!jobTitle) {
      setError('Please enter a job title');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_URL}/skills/compare`, {
        params: {
          job_title: jobTitle,
          location,
          profile_url: profileData?.url
        }
      });
      setComparison(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error comparing skills');
    }
    setLoading(false);
  };

  return (
    <div className="skill-analysis">
      <h2>Skill Analysis</h2>
      
      <div className="search-section">
        <div>
          <label>Job Title:</label>
          <input
            type="text"
            value={jobTitle}
            onChange={(e) => setJobTitle(e.target.value)}
            placeholder="e.g., Software Engineer"
          />
        </div>
        <div>
          <label>Location (optional):</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g., San Francisco, CA"
          />
        </div>
        <div className="button-group">
          <button onClick={fetchSkillTrends} disabled={loading}>
            View Skill Trends
          </button>
          <button onClick={compareSkills} disabled={loading}>
            Compare Skills
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading" />}

      {trends && (
        <div className="trends-section">
          <h3>Skill Trends for {jobTitle}</h3>
          <div className="trends-grid">
            {trends.skill_trends.map((trend) => (
              <div key={trend.skill} className="trend-card">
                <h4>{trend.skill}</h4>
                <div className="trend-stats">
                  <span>Frequency: {trend.frequency}</span>
                  <span>Percentage: {trend.percentage}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {comparison && (
        <div className="comparison-section">
          <h3>Skill Comparison</h3>
          <div className="comparison-grid">
            <div className="comparison-card">
              <h4>Matching Skills</h4>
              <ul>
                {comparison.comparison.matching_skills.map((skill) => (
                  <li key={skill}>{skill}</li>
                ))}
              </ul>
            </div>
            <div className="comparison-card">
              <h4>Missing Skills</h4>
              <ul>
                {comparison.comparison.missing_skills.map((skill) => (
                  <li key={skill}>{skill}</li>
                ))}
              </ul>
            </div>
            <div className="comparison-card">
              <h4>Match Percentage</h4>
              <div className="match-percentage">
                {comparison.comparison.match_percentage}%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 