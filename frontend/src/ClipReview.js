import React, { useState, useRef, useEffect } from 'react';

const ClipReview = ({ keyClips, videoUrl }) => {
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

  const playClip = (clip) => {
    setPlayingClip(clip);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!keyClips || (!keyClips.good_clips?.length && !keyClips.bad_clips?.length)) {
    return null;
  }

  return (
    <div className="clip-review-container">
      <div className="clip-review-header">
        <h2>📹 Key Moments Review</h2>
        <p className="clip-explanation">{keyClips.explanation}</p>
      </div>

      {/* Inline video player for clips */}
      {playingClip && (
        <div className="clip-player-overlay">
          <div className="clip-player-content">
            <div className="clip-player-header">
              <h3>{playingClip.title}</h3>
              <button 
                className="close-clip-btn"
                onClick={() => {
                  if (videoRef.current) {
                    videoRef.current.pause();
                  }
                  setPlayingClip(null);
                }}
              >
                ✕
              </button>
            </div>
            <video
              ref={videoRef}
              className="clip-video-player"
              controls
              src={videoUrl}
            />
            <div className="clip-info">
              <p className="clip-time">
                {formatTime(playingClip.start_time)} - {formatTime(playingClip.end_time)} 
                ({playingClip.duration}s)
              </p>
              <p className="clip-text">{playingClip.text_preview}</p>
            </div>
          </div>
        </div>
      )}

      {/* Good clips section */}
      {keyClips.good_clips && keyClips.good_clips.length > 0 && (
        <div className="clips-section good-clips-section">
          <h3 className="clips-heading">
            <span className="clips-icon">✅</span>
            Strong Moments ({keyClips.good_clips.length})
          </h3>
          <div className="clips-grid">
            {keyClips.good_clips.map((clip, idx) => (
              <div key={idx} className="clip-card good-clip">
                <div className="clip-card-header">
                  <h4>{clip.title}</h4>
                  <div className="clip-confidence good-confidence">
                    {clip.confidence}%
                  </div>
                </div>
                <p className="clip-preview">{clip.text_preview}</p>
                <div className="clip-details">
                  <p className="clip-reason">{clip.why_good}</p>
                  <div className="clip-meta">
                    <span className="clip-time-badge">
                      {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                    </span>
                    <span className="clip-duration">{clip.duration}s</span>
                  </div>
                </div>
                <button
                  className="play-clip-btn good-btn"
                  onClick={() => playClip(clip)}
                >
                  ▶ Watch This Moment
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bad clips section */}
      {keyClips.bad_clips && keyClips.bad_clips.length > 0 && (
        <div className="clips-section bad-clips-section">
          <h3 className="clips-heading">
            <span className="clips-icon">⚠️</span>
            Needs Improvement ({keyClips.bad_clips.length})
          </h3>
          <div className="clips-grid">
            {keyClips.bad_clips.map((clip, idx) => (
              <div key={idx} className="clip-card bad-clip">
                <div className="clip-card-header">
                  <h4>{clip.title}</h4>
                  <div className="clip-confidence bad-confidence">
                    {clip.confidence}%
                  </div>
                </div>
                <p className="clip-preview">{clip.text_preview}</p>
                <div className="clip-details">
                  <p className="clip-reason">{clip.why_bad}</p>
                  <div className="clip-meta">
                    <span className="clip-time-badge">
                      {formatTime(clip.start_time)} - {formatTime(clip.end_time)}
                    </span>
                    <span className="clip-duration">{clip.duration}s</span>
                  </div>
                </div>
                <button
                  className="play-clip-btn bad-btn"
                  onClick={() => playClip(clip)}
                >
                  ▶ Watch & Learn
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClipReview;
