import React, { useState } from 'react';
import MomentsAnalysis from './MomentsAnalysis';
import AvatarGenerator from './AvatarGenerator';

function Results({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('moments');

  if (!data || !data.results) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Analyzing your presentation...</p>
      </div>
    );
  }

  const { results, video_url } = data;
  const moments = results.key_clips || {};

  // Calculate overall stats
  const avgConfidence = results.confidence_score || 0;
  const strongCount = moments.strong_moments?.length || 0;
  const weakCount = moments.weak_moments?.length || 0;
  const overallRating = avgConfidence >= 70 ? 'Strong' : avgConfidence >= 50 ? 'Good' : 'Needs Work';
  const ratingColor = avgConfidence >= 70 ? '#10b981' : avgConfidence >= 50 ? '#f59e0b' : '#ef4444';

  const tabs = [
    { id: 'moments', label: 'Key Moments', count: strongCount + weakCount },
    { id: 'avatar', label: 'Avatar Generator' },
    { id: 'recommendations', label: 'Recommendations', count: results.recommendations?.length || 0 },
    { id: 'transcript', label: 'Transcript' }
  ];

  const renderMomentsTab = () => (
    <div className="tab-content-clean">
      <div className="overview-stats">
        <div className="stat-card">
          <div className="stat-label">Overall Performance</div>
          <div className="stat-value" style={{ color: ratingColor }}>{overallRating}</div>
          <div className="stat-meta">{avgConfidence}% confidence</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Strong Moments</div>
          <div className="stat-value" style={{ color: '#10b981' }}>{strongCount}</div>
          <div className="stat-meta">Areas you excelled</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Areas to Improve</div>
          <div className="stat-value" style={{ color: '#ef4444' }}>{weakCount}</div>
          <div className="stat-meta">Focus on these</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Duration</div>
          <div className="stat-value">{results.duration_minutes}</div>
          <div className="stat-meta">minutes</div>
        </div>
      </div>

      <MomentsAnalysis 
        moments={moments}
        videoUrl={video_url ? `http://localhost:8000${video_url}` : null}
      />
    </div>
  );

  const renderRecommendationsTab = () => {
    const recs = results.recommendations || [];
    const priorityRecs = recs.filter(r => r.severity === 'high' || r.severity === 'medium');
    const otherRecs = recs.filter(r => r.severity !== 'high' && r.severity !== 'medium');

    return (
      <div className="tab-content-clean">
        <div className="recommendations-clean">
          {priorityRecs.length > 0 && (
            <div className="recs-section">
              <h2>Priority Actions</h2>
              <div className="recs-list">
                {priorityRecs.map((rec, idx) => (
                  <div key={idx} className={`rec-item priority-${rec.severity}`}>
                    <div className="rec-title">{rec.title}</div>
                    <div className="rec-description">{rec.description}</div>
                    {rec.action && (
                      <div className="rec-action">
                        <strong>Action:</strong> {rec.action}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {otherRecs.length > 0 && (
            <div className="recs-section">
              <h2>Additional Improvements</h2>
              <div className="recs-list">
                {otherRecs.map((rec, idx) => (
                  <div key={idx} className="rec-item">
                    <div className="rec-title">{rec.title}</div>
                    <div className="rec-description">{rec.description}</div>
                    {rec.action && (
                      <div className="rec-action">
                        <strong>Action:</strong> {rec.action}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderTranscriptTab = () => {
    const highlightFillers = (text, positions) => {
      if (!positions || positions.length === 0) return text;

      const segments = [];
      let lastIndex = 0;

      positions.forEach(([start, end, filler]) => {
        if (start > lastIndex) {
          segments.push(<span key={`text-${lastIndex}`}>{text.substring(lastIndex, start)}</span>);
        }
        segments.push(
          <mark key={`filler-${start}`} className="filler-highlight">
            {text.substring(start, end)}
          </mark>
        );
        lastIndex = end;
      });

      if (lastIndex < text.length) {
        segments.push(<span key={`text-${lastIndex}`}>{text.substring(lastIndex)}</span>);
      }

      return segments;
    };

    return (
      <div className="tab-content-clean">
        <div className="transcript-section">
          <div className="transcript-stats">
            <span><strong>{results.word_count}</strong> words</span>
            <span><strong>{results.filler_count}</strong> filler words</span>
            <span><strong>{results.wpm}</strong> WPM average</span>
          </div>
          <div className="transcript-text">
            {highlightFillers(results.transcript, results.filler_positions)}
          </div>
          <div className="transcript-legend">
            <span className="legend-item">
              <mark className="filler-highlight">Highlighted</mark> = Filler word
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="results-container-clean">
      <div className="results-header-clean">
        <h1>Analysis Results</h1>
        <button className="back-btn" onClick={onBack}>← Analyze Another</button>
      </div>

      <div className="tabs-clean">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {tab.count !== undefined && <span className="tab-count">{tab.count}</span>}
          </button>
        ))}
      </div>

      <div className="tabs-content">
        {activeTab === 'moments' && renderMomentsTab()}
        {activeTab === 'avatar' && (
          <div className="tab-content-clean">
            <AvatarGenerator 
              sessionId={data.session_id}
              analysis={results}
            />
          </div>
        )}
        {activeTab === 'recommendations' && renderRecommendationsTab()}
        {activeTab === 'transcript' && renderTranscriptTab()}
      </div>
    </div>
  );
}

export default Results;
