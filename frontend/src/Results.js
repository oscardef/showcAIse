import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

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

  // Helper to highlight filler words in transcript
  const highlightFillers = (transcript, fillerPositions) => {
    if (!fillerPositions || fillerPositions.length === 0) {
      return <span>{transcript}</span>;
    }

    const segments = [];
    let lastIndex = 0;

    fillerPositions.forEach(([start, end, filler]) => {
      // Add text before filler
      if (start > lastIndex) {
        segments.push(
          <span key={`text-${lastIndex}`}>
            {transcript.substring(lastIndex, start)}
          </span>
        );
      }
      // Add highlighted filler
      segments.push(
        <mark key={`filler-${start}`} className="filler-highlight">
          {transcript.substring(start, end)}
        </mark>
      );
      lastIndex = end;
    });

    // Add remaining text
    if (lastIndex < transcript.length) {
      segments.push(
        <span key={`text-${lastIndex}`}>
          {transcript.substring(lastIndex)}
        </span>
      );
    }

    return <>{segments}</>;
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#3b82f6';
      case 'success': return '#10b981';
      default: return '#6b7280';
    }
  };

  return (
    <div>
      <div className="results-header">
        <h1>📊 Presentation Analysis</h1>
        <div className="score-badge" style={{ 
          backgroundColor: results.confidence_score > 70 ? '#10b981' : results.confidence_score > 50 ? '#f59e0b' : '#ef4444'
        }}>
          Confidence: {results.confidence_score}%
        </div>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-value">{results.word_count}</div>
          <div className="metric-label">Total Words</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{results.wpm}</div>
          <div className="metric-label">Words/Minute</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{results.filler_count}</div>
          <div className="metric-label">Filler Words</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{results.duration_minutes}m</div>
          <div className="metric-label">Duration</div>
        </div>
      </div>

      {/* Timeline Charts */}
      {results.timeline && results.timeline.length > 0 && (
        <div className="chart-section">
          <h2>📈 Performance Over Time</h2>
          
          <div className="chart-container">
            <h3>Confidence Timeline</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={results.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="segment" label={{ value: 'Segment', position: 'insideBottom', offset: -5 }} />
                <YAxis label={{ value: 'Confidence %', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="confidence" stroke="#8b5cf6" strokeWidth={2} name="Confidence Score" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <h3>Speaking Pace & Fillers</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={results.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="segment" label={{ value: 'Segment', position: 'insideBottom', offset: -5 }} />
                <YAxis yAxisId="left" label={{ value: 'WPM', angle: -90, position: 'insideLeft' }} />
                <YAxis yAxisId="right" orientation="right" label={{ value: 'Fillers', angle: 90, position: 'insideRight' }} />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="wpm" fill="#3b82f6" name="Words/Minute" />
                <Bar yAxisId="right" dataKey="filler_count" fill="#ef4444" name="Filler Words" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Priority Actions */}
      {results.priority_actions && results.priority_actions.length > 0 && (
        <div className="priority-section">
          <h2>🎯 Top 3 Priority Actions</h2>
          <div className="priority-list">
            {results.priority_actions.map((action, idx) => (
              <div key={idx} className="priority-item">
                <div className="priority-number">{idx + 1}</div>
                <div>
                  <h4>{action.title}</h4>
                  <p className="action-text">{action.action}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Recommendations */}
      <div className="recommendations-section">
        <h2>💡 Detailed Recommendations</h2>
        <div className="recommendations-list">
          {results.recommendations.map((rec, idx) => (
            <div 
              key={idx} 
              className="recommendation-card"
              style={{ borderLeftColor: getSeverityColor(rec.severity) }}
            >
              <div className="recommendation-icon">{rec.icon}</div>
              <div className="recommendation-content">
                <h3>{rec.title}</h3>
                <p>{rec.description}</p>
                {rec.action && (
                  <div className="action-box">
                    <strong>Action:</strong> {rec.action}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Additional Metrics */}
      {results.metrics && (
        <div className="metrics-section">
          <h2>📊 Speech Metrics</h2>
          <div className="metrics-details">
            <div className="metric-item">
              <span className="metric-icon">📏</span>
              <div>
                <div className="metric-number">{results.avg_sentence_length}</div>
                <div className="metric-desc">Avg Sentence Length</div>
              </div>
            </div>
            <div className="metric-item">
              <span className="metric-icon">❓</span>
              <div>
                <div className="metric-number">{results.metrics.questions}</div>
                <div className="metric-desc">Questions Asked</div>
              </div>
            </div>
            <div className="metric-item">
              <span className="metric-icon">💪</span>
              <div>
                <div className="metric-number">{results.metrics.power_words}</div>
                <div className="metric-desc">Power Words</div>
              </div>
            </div>
            <div className="metric-item">
              <span className="metric-icon">⚠️</span>
              <div>
                <div className="metric-number">{results.metrics.weak_words}</div>
                <div className="metric-desc">Weak Phrases</div>
              </div>
            </div>
          </div>
          
          {results.filler_breakdown && Object.keys(results.filler_breakdown).length > 0 && (
            <div className="filler-breakdown">
              <h3>Top Filler Words</h3>
              <div className="filler-items">
                {Object.entries(results.filler_breakdown).map(([word, count]) => (
                  <div key={word} className="filler-item">
                    <span className="filler-word">"{word}"</span>
                    <span className="filler-badge">{count}x</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Transcript with Highlighted Fillers */}
      <div className="transcript-section">
        <h2>📝 Transcript</h2>
        <div className="transcript-box">
          {highlightFillers(results.transcript, results.filler_positions)}
        </div>
        <div className="filler-legend">
          <mark className="filler-highlight">Highlighted</mark> = Filler words detected
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: '30px' }}>
        <button className="btn" onClick={onBack}>
          Analyze Another Video
        </button>
      </div>
    </div>
  );
}

export default Results;
