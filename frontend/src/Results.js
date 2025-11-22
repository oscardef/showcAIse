import React from 'react';

function Results({ data, onBack }) {
  if (!data || !data.results) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  const { results } = data;

  return (
    <div>
      <div className="card">
        <button className="btn" onClick={onBack} style={{ marginBottom: '20px' }}>
          ← Back to Upload
        </button>
        
        <h2>📊 Analysis Results</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginTop: '30px' }}>
          <div className="metric">
            <div className="metric-value">{results.word_count}</div>
            <div className="metric-label">Total Words</div>
          </div>
          
          <div className="metric">
            <div className="metric-value">{results.filler_count}</div>
            <div className="metric-label">Filler Words</div>
          </div>
          
          <div className="metric">
            <div className="metric-value">{results.wpm}</div>
            <div className="metric-label">Words Per Minute</div>
          </div>
          
          <div className="metric">
            <div className="metric-value">{results.duration_minutes}</div>
            <div className="metric-label">Duration (min)</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>📝 Transcript</h2>
        <div className="transcript">
          {results.transcript}
        </div>
      </div>

      <div className="card">
        <h2>💡 Recommendations</h2>
        {results.recommendations.map((rec, idx) => (
          <div key={idx} className="recommendation">
            <span className="recommendation-icon">
              {rec.includes('🎯') ? '🎯' : 
               rec.includes('🐢') ? '🐢' : 
               rec.includes('⚡') ? '⚡' : 
               rec.includes('📝') ? '📝' : 
               rec.includes('❓') ? '❓' : '✨'}
            </span>
            <div style={{ flex: 1 }}>
              {rec.replace(/^[🎯🐢⚡📝❓✨]\s*/, '')}
            </div>
          </div>
        ))}
      </div>

      <div style={{ textAlign: 'center', marginTop: '20px' }}>
        <button className="btn" onClick={onBack}>
          Analyze Another Video
        </button>
      </div>
    </div>
  );
}

export default Results;
