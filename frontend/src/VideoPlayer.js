import React, { useRef, useEffect } from 'react';

function VideoPlayer({ videoUrl, currentTime, onTimeUpdate }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && currentTime !== undefined) {
      const video = videoRef.current;
      // Only seek if the difference is significant (more than 1 second)
      // This prevents constant seeking which can cause lag
      if (Math.abs(video.currentTime - currentTime) > 1) {
        video.currentTime = currentTime;
      }
    }
  }, [currentTime]);

  const handleTimeUpdate = () => {
    if (videoRef.current && onTimeUpdate) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };

  if (!videoUrl) return null;

  return (
    <div className="video-player-container">
      <video
        ref={videoRef}
        className="video-player"
        controls
        preload="metadata"
        playsInline
        onTimeUpdate={handleTimeUpdate}
      >
        <source src={videoUrl} type="video/mp4" />
        Your browser does not support video playback.
      </video>
    </div>
  );
}

export default VideoPlayer;
