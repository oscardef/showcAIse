import React, { useState, useRef } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function Upload({ onComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
    } else {
      alert('Please select a video file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('video', file);

    try {
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        },
      });

      onComplete(response.data);
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed. Please try again.');
      setUploading(false);
      setProgress(0);
    }
  };

  return (
    <div className="card">
      <h2>Upload Your Presentation Video</h2>
      
      <div
        className={`upload-zone ${dragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !uploading && fileInputRef.current.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={(e) => handleFileSelect(e.target.files[0])}
          style={{ display: 'none' }}
        />
        
        {!file ? (
          <>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>📹</div>
            <p style={{ fontSize: '18px', color: '#666' }}>
              Drag & drop your video here, or click to select
            </p>
            <p style={{ fontSize: '14px', color: '#999', marginTop: '10px' }}>
              Supports MP4, MOV, AVI (max 500MB)
            </p>
          </>
        ) : (
          <>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>✅</div>
            <p style={{ fontSize: '18px', color: '#333', fontWeight: 600 }}>
              {file.name}
            </p>
            <p style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </>
        )}
      </div>

      {uploading && (
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      )}

      <div style={{ textAlign: 'center', marginTop: '24px' }}>
        <button
          className="btn"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? 'Analyzing...' : 'Analyze Presentation'}
        </button>
      </div>

      <div style={{ marginTop: '32px', padding: '20px', background: '#f8f9ff', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '12px', color: '#333' }}>💡 Tips for Best Results:</h3>
        <ul style={{ color: '#666', lineHeight: '1.8', paddingLeft: '24px' }}>
          <li>Use good lighting and clear audio</li>
          <li>Keep videos between 30 seconds - 5 minutes</li>
          <li>Speak clearly and look at the camera</li>
          <li>MP4 format works best</li>
        </ul>
      </div>
    </div>
  );
}

export default Upload;
