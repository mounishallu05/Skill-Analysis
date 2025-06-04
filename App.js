import React, { useState } from "react";
import UploadForm from "./components/UploadForm";
import ResultView from "./components/ResultView";
import SkillAnalysis from "./components/SkillAnalysis";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  return (
    <div className="App">
      <h1>LinkedIn Skill Analysis Bot</h1>
      <UploadForm setResult={setResult} setLoading={setLoading} />
      {loading && <div className="loading" />}
      {result && (
        <>
          <ResultView result={result} />
          <SkillAnalysis profileData={result.data} />
        </>
      )}
    </div>
  );
}

export default App; 