import React from "react";

export default function ResultView({ result }) {
  if (result.error) {
    return <div style={{ color: "red" }}>{result.error}</div>;
  }
  if (!result.data) return null;

  const { name, headline, location, about, skills, experience, education } = result.data;

  return (
    <div className="result">
      <h2>Profile Analysis</h2>
      <p><strong>Name:</strong> {name}</p>
      <p><strong>Headline:</strong> {headline}</p>
      <p><strong>Location:</strong> {location}</p>
      <p><strong>About:</strong> {about}</p>
      <h3>Skills</h3>
      <ul>
        {skills && skills.map((skill) => <li key={skill}>{skill}</li>)}
      </ul>
      <h3>Experience</h3>
      <ul>
        {experience && experience.map((exp, idx) => (
          <li key={idx}>
            <strong>{exp.title}</strong> at {exp.company} ({exp.duration})<br />
            {exp.description}
          </li>
        ))}
      </ul>
      <h3>Education</h3>
      <ul>
        {education && education.map((edu, idx) => (
          <li key={idx}>
            <strong>{edu.degree}</strong> at {edu.school}<br />
            {edu.description}
          </li>
        ))}
      </ul>
    </div>
  );
} 