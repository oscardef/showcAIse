import React, { useState, useRef, useEffect } from 'react';

const MomentsAnalysis = ({ moments, videoUrl }) => {
  const [playingClip, setPlayingClip] = useState(null);
  const videoRef = useRef(null);

  useEffect(() => {
    if (playingClip && videoRef.current) {
      const video = videoRef.current;
      video.currentTime = playingClip.start_time;
      video.play();

      const handleTimeUpdate = () => {
        if (video.currentTime >= playingClip.end_time) {
          video.pause();
          setPlayingClip(null);
        }
      };

      video.addEventListener('timeupdate', handleTimeUpdate);
      return () => video.removeEventListener('timeupdate', handleTimeUpdate);
    }
  }, [playingClip]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!moments || (!moments.strong_moments?.length && !moments.weak_moments?.length)) {
    return <div className="no-moments">No significant moments detected</div>;
  }

  return (
    <div className="moments-analysis">
      {/* Inline video player */}
      {playingClip && (
        <div className="clip-overlay" onClick={() => {
          if (videoRef.current) videoRef.current.pause();
          setPlayingClip(null);
        }}>
          <div className="clip-player" onClick={(e) => e.stopPropagation()}>
            <div className="clip-header">
              <h3>Segment #{playingClip.segment_num}</h3>
              <button className="close-btn" onClick={() => {
                if (videoRef.current) videoRef.current.pause();
                setPlayingClip(null);
              }}>✕</button>
            </div>
            <video ref={videoRef} controls src={videoUrl} />
            <div className="clip-info">
              <p className="clip-time">{formatTime(playingClip.start_time)} - {formatTime(playingClip.end_time)}</p>
              <p className="clip-text">"{playingClip.text}"</p>
            </div>
          </div>
        </div>
      )}

      {/* Strong Moments */}
      {moments.strong_moments && moments.strong_moments.length > 0 && (
        <div className="moments-section">
          <h2 className="section-title strong">✓ Strong Moments ({moments.strong_moments.length})</h2>
          <div className="moments-list">
            {moments.strong_moments.map((moment, idx) => (
              <div key={idx} className="moment-item strong-moment">
                <div className="moment-header">
                  <div className="moment-title">
                    <span className="segment-badge">#{moment.segment_num}</span>
                    <span className="confidence-score strong">{moment.confidence}%</span>
                  </div>
                  <button className="play-btn" onClick={() => setPlayingClip(moment)}>
                    ▶ Watch
                  </button>
                </div>
                <div className="moment-text">"{moment.text}"</div>
                <div className="moment-categories">
                  {moment.categories.map((cat, i) => (
                    <span key={i} className="category-tag strong">{cat}</span>
                  ))}
                </div>
                <div className="moment-metrics">
                  <span>{moment.metrics.wpm} WPM</span>
                  <span>{moment.metrics.fillers} fillers</span>
                  {moment.metrics.sentiment !== null && (
                    <span>Sentiment: {(moment.metrics.sentiment * 100).toFixed(0)}%</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Weak Moments */}
      {moments.weak_moments && moments.weak_moments.length > 0 && (
        <div className="moments-section">
          <h2 className="section-title weak">⚠ Areas to Improve ({moments.weak_moments.length})</h2>
          <div className="moments-list">
            {moments.weak_moments.map((moment, idx) => (
              <div key={idx} className="moment-item weak-moment">
                <div className="moment-header">
                  <div className="moment-title">
                    <span className="segment-badge">#{moment.segment_num}</span>
                    <span className="confidence-score weak">{moment.confidence}%</span>
                  </div>
                  <button className="play-btn" onClick={() => setPlayingClip(moment)}>
                    ▶ Watch
                  </button>
                </div>
                <div className="moment-text">"{moment.text}"</div>
                <div className="moment-categories">
                  {moment.categories.map((cat, i) => (
                    <span key={i} className="category-tag weak">{cat}</span>
                  ))}
                </div>
                <div className="moment-issues">
                  <strong>Issues:</strong>
                  <ul>
                    {moment.issues && moment.issues.map((issue, i) => (
                      <li key={i}>{issue}</li>
                    ))}
                  </ul>
                </div>
                <div className="moment-suggestions">
                  <strong>How to improve:</strong>
                  <ul>
                    {moment.suggestions && moment.suggestions.map((sug, i) => (
                      <li key={i}>{sug}</li>
                    ))}
                  </ul>
                </div>
                <div className="moment-metrics">
                  <span>{moment.metrics.wpm} WPM</span>
                  <span>{moment.metrics.fillers} fillers</span>
                  {moment.metrics.sentiment !== null && (
                    <span>Sentiment: {(moment.metrics.sentiment * 100).toFixed(0)}%</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default MomentsAnalysis;
