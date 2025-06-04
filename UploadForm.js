import React, { useRef, useState } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8001";

export default function UploadForm({ setResult, setLoading }) {
  const fileInput = useRef();
  const [profileUrl, setProfileUrl] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError("");

    try {
      let response;
      if (fileInput.current.files.length > 0) {
        const formData = new FormData();
        formData.append("pdf_file", fileInput.current.files[0]);
        response = await axios.post(`${API_URL}/analyze/profile`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      } else if (profileUrl) {
        response = await axios.post(`${API_URL}/analyze/profile`, { profile_url: profileUrl });
      } else {
        setError("Please provide a LinkedIn URL or upload a PDF.");
        setLoading(false);
        return;
      }
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error analyzing profile. Please try again.");
      setResult({ error: err.response?.data?.detail || "Error analyzing profile." });
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <div>
        <label>LinkedIn Profile URL:</label>
        <input
          type="url"
          value={profileUrl}
          onChange={(e) => setProfileUrl(e.target.value)}
          placeholder="https://www.linkedin.com/in/username/"
        />
      </div>
      <div>
        <label>Or Upload LinkedIn PDF:</label>
        <input type="file" ref={fileInput} accept="application/pdf" />
      </div>
      <button type="submit">Analyze</button>
    </form>
  );
} 