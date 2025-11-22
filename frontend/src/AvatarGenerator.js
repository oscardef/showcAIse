import React, { useState } from 'react';
import axios from 'axios';

const AvatarGenerator = ({ sessionId, analysis }) => {
  const [generating, setGenerating] = useState(false);
  const [avatarResult, setAvatarResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerateAvatar = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await axios.post(
        `http://localhost:8000/api/avatar/generate/${sessionId}`
      );
      setAvatarResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Avatar generation failed');
      console.error('Avatar generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  if (!sessionId) {
    return null;
  }

  return (
    <div className="avatar-generator">
      <div className="avatar-header">
        <h2>✨ Avatar Reconstruction</h2>
        <p>Generate a "perfect" presentation with all improvements applied</p>
      </div>

      {!avatarResult && !generating && (
        <div className="avatar-intro">
          <div className="avatar-features">
            <h3>What You'll Get:</h3>
            <ul>
              <li>✓ All filler words removed ("um", "uh", "like")</li>
              <li>✓ Optimal pacing at 145 WPM</li>
              <li>✓ Confident language (no hedge words)</li>
              <li>✓ Professional delivery</li>
              <li>✓ Clean, polished script</li>
            </ul>
          </div>

          <button 
            className="generate-avatar-btn"
            onClick={handleGenerateAvatar}
            disabled={generating}
          >
            Generate Perfect Avatar Presentation
          </button>
        </div>
      )}

      {generating && (
        <div className="avatar-loading">
          <div className="loader"></div>
          <h3>Generating Your Perfect Presentation...</h3>
          <p>This may take 30-60 seconds</p>
          <div className="loading-steps">
            <div className="step">✓ Analyzing feedback</div>
            <div className="step">✓ Removing fillers</div>
            <div className="step">✓ Optimizing language</div>
            <div className="step active">⏳ Generating audio...</div>
          </div>
        </div>
      )}

      {error && (
        <div className="avatar-error">
          <h3>Generation Error</h3>
          <p>{error}</p>
          <button onClick={handleGenerateAvatar}>Try Again</button>
        </div>
      )}

      {avatarResult && (
        <div className="avatar-result">
          <div className="result-header">
            <h3>🎉 Perfect Presentation Generated!</h3>
            <span className="status-badge success">{avatarResult.status}</span>
          </div>

          {/* Improvements Summary */}
          <div className="improvements-applied">
            <h4>Improvements Applied:</h4>
            <ul>
              {avatarResult.improvements?.map((improvement, idx) => (
                <li key={idx}>{improvement}</li>
              ))}
            </ul>
          </div>

          {/* Before/After Stats */}
          <div className="stats-comparison">
            <div className="stat-column before">
              <h4>Original</h4>
              <div className="stat-item">
                <span className="label">WPM:</span>
                <span className="value">{avatarResult.original_stats?.wpm || 0}</span>
              </div>
              <div className="stat-item">
                <span className="label">Confidence:</span>
                <span className="value">{avatarResult.original_stats?.confidence || 0}%</span>
              </div>
              <div className="stat-item">
                <span className="label">Fillers:</span>
                <span className="value">{avatarResult.original_stats?.filler_count || 0}</span>
              </div>
            </div>

            <div className="arrow">→</div>

            <div className="stat-column after">
              <h4>Perfect Version</h4>
              <div className="stat-item">
                <span className="label">WPM:</span>
                <span className="value improved">{avatarResult.improved_stats?.wpm || 145}</span>
              </div>
              <div className="stat-item">
                <span className="label">Confidence:</span>
                <span className="value improved">{avatarResult.improved_stats?.confidence || 85}%</span>
              </div>
              <div className="stat-item">
                <span className="label">Fillers:</span>
                <span className="value improved">{avatarResult.improved_stats?.filler_count || 0}</span>
              </div>
            </div>
          </div>

          {/* Improved Script */}
          <div className="improved-script">
            <h4>Improved Script:</h4>
            <div className="script-preview">
              {avatarResult.improved_script}
            </div>
            <div className="timing-info">
              Duration: {avatarResult.timing_info?.duration_seconds}s 
              ({avatarResult.timing_info?.word_count} words at {avatarResult.timing_info?.target_wpm} WPM)
            </div>
          </div>

          {/* Audio Player (if available) */}
          {avatarResult.audio_url && (
            <div className="audio-player">
              <h4>🎧 Perfect Audio:</h4>
              <audio controls src={`http://localhost:8000${avatarResult.audio_url}`}>
                Your browser does not support audio playback.
              </audio>
            </div>
          )}

          {/* Download Options */}
          <div className="download-options">
            <button className="download-btn" onClick={() => {
              const element = document.createElement('a');
              const file = new Blob([avatarResult.improved_script], {type: 'text/plain'});
              element.href = URL.createObjectURL(file);
              element.download = 'improved_script.txt';
              element.click();
            }}>
              Download Script
            </button>
            
            {avatarResult.audio_url && (
              <a 
                href={`http://localhost:8000${avatarResult.audio_url}`}
                download="improved_audio.wav"
                className="download-btn"
              >
                Download Audio
              </a>
            )}
          </div>

          {avatarResult.mode === 'script_only' && (
            <div className="info-note">
              <p><strong>Note:</strong> TTS audio generation failed (model may be loading). 
              The improved script is ready - you can try generating audio again, or use the script as-is.</p>
            </div>
          )}
          
          {avatarResult.mode === 'audio_generated' && (
            <div className="success-note">
              <p>✅ <strong>Phase 1 Complete:</strong> Improved script with TTS audio generated! 
              Voice cloning (Phase 2) and avatar video (Phase 3) coming soon.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AvatarGenerator;
