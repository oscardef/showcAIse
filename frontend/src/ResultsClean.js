import React, { useState } from 'react';
import axios from 'axios';
import MomentsAnalysis from './MomentsAnalysis';

function Results({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('moments');
  const [voiceCloning, setVoiceCloning] = useState({
    loading: false,
    generated: false,
    audioUrl: null,
    improvedScript: null,
    improvements: null,
    error: null
  });

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
    { id: 'voice-clone', label: '🎤 Voice Clone', icon: '✨' },
    { id: 'recommendations', label: 'Recommendations', count: results.recommendations?.length || 0 },
    { id: 'transcript', label: 'Transcript' }
  ];

  const handleGenerateVoiceClone = async () => {
    setVoiceCloning({ ...voiceCloning, loading: true, error: null });
    
    try {
      const response = await axios.post(
        `http://localhost:8000/api/voice-clone/${data.session_id}`
      );
      
      setVoiceCloning({
        loading: false,
        generated: true,
        audioUrl: response.data.audio_url,
        improvedScript: response.data.improved_script,
        improvements: response.data.improvements,
        error: null
      });
    } catch (error) {
      setVoiceCloning({
        ...voiceCloning,
        loading: false,
        error: error.response?.data?.detail || 'Voice cloning failed'
      });
    }
  };

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

  const renderVoiceCloneTab = () => {
    return (
      <div className="tab-content-clean">
        <div className="voice-clone-section">
          <div className="voice-clone-header">
            <h2>🎤 AI Voice Cloning</h2>
            <p>Generate an improved version of your presentation using voice cloning technology</p>
          </div>

          {!voiceCloning.generated && !voiceCloning.loading && (
            <div className="voice-clone-intro">
              <div className="feature-list">
                <h3>What you'll get:</h3>
                <ul>
                  <li>✅ Improved script with fillers removed</li>
                  <li>✅ Confident language replacing uncertain phrases</li>
                  <li>✅ Optimized pacing and structure</li>
                  <li>✅ Your voice cloned to deliver the improved script</li>
                </ul>
              </div>
              <button 
                className="generate-voice-btn"
                onClick={handleGenerateVoiceClone}
              >
                🎙️ Generate Improved Presentation
              </button>
            </div>
          )}

          {voiceCloning.loading && (
            <div className="voice-clone-loading">
              <div className="spinner"></div>
              <p>Cloning your voice and generating improved presentation...</p>
              <p className="loading-note">This may take 30-60 seconds</p>
            </div>
          )}

          {voiceCloning.error && (
            <div className="voice-clone-error">
              <h3>❌ Error</h3>
              <p>{voiceCloning.error}</p>
              <button onClick={handleGenerateVoiceClone}>Try Again</button>
            </div>
          )}

          {voiceCloning.generated && (
            <div className="voice-clone-result">
              <div className="result-header">
                <h3>✅ Voice Clone Generated!</h3>
              </div>

              {voiceCloning.improvements && (
                <div className="improvements-summary">
                  <h4>Improvements Applied:</h4>
                  <ul>
                    {voiceCloning.improvements.improvements.map((imp, idx) => (
                      <li key={idx}>{imp}</li>
                    ))}
                  </ul>
                  <div className="stats-comparison">
                    <div className="stat-item">
                      <span className="label">Words:</span>
                      <span className="value">
                        {voiceCloning.improvements.original_word_count} → {voiceCloning.improvements.improved_word_count}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="label">Target Duration:</span>
                      <span className="value">
                        {voiceCloning.improvements.estimated_duration_seconds}s
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div className="audio-player-section">
                <h4>🎧 Improved Presentation Audio:</h4>
                <audio 
                  controls 
                  src={`http://localhost:8000${voiceCloning.audioUrl}`}
                  className="cloned-audio-player"
                >
                  Your browser does not support audio playback.
                </audio>
                <a 
                  href={`http://localhost:8000${voiceCloning.audioUrl}`}
                  download="improved_presentation.wav"
                  className="download-audio-btn"
                >
                  ⬇️ Download Audio
                </a>
              </div>

              {voiceCloning.improvedScript && (
                <div className="improved-script">
                  <h4>📝 Improved Script:</h4>
                  <div className="script-text">
                    {voiceCloning.improvedScript}
                  </div>
                </div>
              )}
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
        {activeTab === 'voice-clone' && renderVoiceCloneTab()}
        {activeTab === 'recommendations' && renderRecommendationsTab()}
        {activeTab === 'transcript' && renderTranscriptTab()}
      </div>
    </div>
  );
}

export default Results;
