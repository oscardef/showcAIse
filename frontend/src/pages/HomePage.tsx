import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          Elevate Your Presentation Skills with AI
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Upload your presentation video and get instant feedback on your delivery, 
          body language, and speaking style. Watch an AI avatar demonstrate the improved version.
        </p>
        <Link to="/upload" className="btn-primary text-lg px-8 py-3">
          Start Analysis
        </Link>
      </div>

      {/* Features Grid */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="card text-center">
          <div className="text-4xl mb-4">🗣️</div>
          <h3 className="text-xl font-semibold mb-2">Speech Analysis</h3>
          <p className="text-gray-600">
            Get transcription, detect filler words, analyze speaking pace and tone variation
          </p>
        </div>

        <div className="card text-center">
          <div className="text-4xl mb-4">👁️</div>
          <h3 className="text-xl font-semibold mb-2">Computer Vision</h3>
          <p className="text-gray-600">
            Track eye contact, analyze posture, and measure confidence indicators
          </p>
        </div>

        <div className="card text-center">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-xl font-semibold mb-2">AI Avatar</h3>
          <p className="text-gray-600">
            Watch an AI avatar deliver your improved presentation with optimized delivery
          </p>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-white rounded-lg shadow-md p-8">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">1</span>
            </div>
            <h4 className="font-semibold mb-2">Upload Video</h4>
            <p className="text-sm text-gray-600">Record and upload your presentation video</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">2</span>
            </div>
            <h4 className="font-semibold mb-2">AI Analysis</h4>
            <p className="text-sm text-gray-600">Our AI analyzes speech, body language, and delivery</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">3</span>
            </div>
            <h4 className="font-semibold mb-2">Get Insights</h4>
            <p className="text-sm text-gray-600">Review detailed metrics and recommendations</p>
          </div>

          <div className="text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold text-blue-600">4</span>
            </div>
            <h4 className="font-semibold mb-2">Avatar Demo</h4>
            <p className="text-sm text-gray-600">See your improved presentation performed by AI</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
