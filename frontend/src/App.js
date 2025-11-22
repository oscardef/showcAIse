import React, { useState } from 'react';
import Upload from './Upload';
import Results from './Results';

function App() {
  const [view, setView] = useState('upload'); // 'upload' or 'results'
  const [results, setResults] = useState(null);

  const handleUploadComplete = (data) => {
    setResults(data);
    setView('results');
  };

  const handleBackToUpload = () => {
    setView('upload');
    setResults(null);
  };

  return (
    <div className="container">
      <h1>🎤 showcAIse</h1>
      {view === 'upload' ? (
        <Upload onComplete={handleUploadComplete} />
      ) : (
        <Results data={results} onBack={handleBackToUpload} />
      )}
    </div>
  );
}

export default App;
