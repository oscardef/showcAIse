import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import AnalysisProgress from '../components/AnalysisProgress';
import { connectWebSocket } from '../services/websocket';

interface AnalysisStatus {
  stage: string;
  progress: number;
  currentTask: string;
  status: string;
}

const AnalysisPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>({
    stage: 'processing',
    progress: 0,
    currentTask: 'Initializing analysis...',
    status: 'processing'
  });

  useEffect(() => {
    if (!sessionId) return;

    const socket = connectWebSocket(sessionId);

    socket.on('analysis_progress', (data: AnalysisStatus) => {
      setAnalysisStatus(data);
    });

    socket.on('analysis_complete', () => {
      navigate(`/results/${sessionId}`);
    });

    socket.on('analysis_error', (error: any) => {
      console.error('Analysis error:', error);
      alert('Analysis failed. Please try again.');
      navigate('/upload');
    });

    return () => {
      socket.disconnect();
    };
  }, [sessionId, navigate]);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Analyzing Your Presentation
        </h1>
        <p className="text-lg text-gray-600">
          Our AI is analyzing your video. This may take a few minutes...
        </p>
      </div>

      <div className="card">
        <AnalysisProgress
          stage={analysisStatus.stage}
          progress={analysisStatus.progress}
          currentTask={analysisStatus.currentTask}
        />
      </div>

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Session ID: {sessionId}</p>
        <p className="mt-2">Don't close this page while analysis is in progress</p>
      </div>
    </div>
  );
};

export default AnalysisPage;
