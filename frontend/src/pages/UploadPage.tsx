import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import VideoUpload from '../components/VideoUpload';
import { uploadVideo } from '../services/api';

const UploadPage: React.FC = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const navigate = useNavigate();

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const sessionId = await uploadVideo(file, (progress) => {
        setUploadProgress(progress);
      });

      // Navigate to analysis page
      navigate(`/analysis/${sessionId}`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload video. Please try again.');
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Upload Your Presentation
        </h1>
        <p className="text-lg text-gray-600">
          Record a short video of yourself presenting and we'll analyze your delivery
        </p>
      </div>

      <div className="card">
        <VideoUpload
          onUpload={handleUpload}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
        />

        <div className="mt-8 space-y-4">
          <h3 className="font-semibold text-lg">Tips for best results:</h3>
          <ul className="list-disc list-inside space-y-2 text-gray-700">
            <li>Ensure good lighting and clear audio</li>
            <li>Position yourself in the center of the frame</li>
            <li>Keep the video between 1-10 minutes</li>
            <li>Look at the camera to simulate eye contact</li>
            <li>Speak clearly and at a natural pace</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
