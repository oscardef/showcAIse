import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getAnalysisResults } from '../services/api';

interface Results {
  speech: any;
  vision: any;
  recommendations: string[];
  avatarVideoUrl?: string;
}

const ResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [results, setResults] = useState<Results | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResults = async () => {
      if (!sessionId) return;
      
      try {
        const data = await getAnalysisResults(sessionId);
        setResults(data);
      } catch (error) {
        console.error('Failed to fetch results:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading results...</div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl text-red-600">Failed to load results</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Analysis Results</h1>

      {/* Speech Analysis Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4">🗣️ Speech Analysis</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.speech?.wpm || 0}</div>
            <div className="text-sm text-gray-600">Words per minute</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.speech?.fillerCount || 0}</div>
            <div className="text-sm text-gray-600">Filler words</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.speech?.toneScore || 0}%</div>
            <div className="text-sm text-gray-600">Tone variation</div>
          </div>
        </div>
      </div>

      {/* Computer Vision Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4">👁️ Body Language Analysis</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.vision?.eyeContact || 0}%</div>
            <div className="text-sm text-gray-600">Eye contact</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.vision?.postureScore || 0}%</div>
            <div className="text-sm text-gray-600">Posture quality</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">{results.vision?.confidenceScore || 0}%</div>
            <div className="text-sm text-gray-600">Confidence level</div>
          </div>
        </div>
      </div>

      {/* Recommendations Section */}
      <div className="card mb-8">
        <h2 className="text-2xl font-semibold mb-4">💡 Recommendations</h2>
        <ul className="space-y-3">
          {results.recommendations?.map((rec, idx) => (
            <li key={idx} className="flex items-start">
              <span className="text-green-500 mr-2">✓</span>
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Avatar Video Section */}
      {results.avatarVideoUrl && (
        <div className="card">
          <h2 className="text-2xl font-semibold mb-4">🤖 Improved Avatar Version</h2>
          <video
            src={results.avatarVideoUrl}
            controls
            className="w-full rounded-lg"
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
};

export default ResultsPage;
