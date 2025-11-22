import React from 'react';

interface AnalysisProgressProps {
  stage: string;
  progress: number;
  currentTask: string;
}

const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ stage, progress, currentTask }) => {
  const stages = [
    { name: 'Upload', key: 'upload' },
    { name: 'Video Processing', key: 'processing' },
    { name: 'Speech Analysis', key: 'speech' },
    { name: 'Computer Vision', key: 'vision' },
    { name: 'Generating Report', key: 'report' },
  ];

  const currentStageIndex = stages.findIndex(s => s.key === stage);

  return (
    <div className="w-full space-y-6">
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>

      {/* Stage indicators */}
      <div className="flex justify-between items-center">
        {stages.map((s, index) => (
          <div key={s.key} className="flex flex-col items-center flex-1">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all
                ${index < currentStageIndex ? 'bg-green-500 text-white' :
                  index === currentStageIndex ? 'bg-blue-600 text-white animate-pulse' :
                  'bg-gray-300 text-gray-600'}`}
            >
              {index < currentStageIndex ? '✓' : index + 1}
            </div>
            <div className={`mt-2 text-sm font-medium ${index === currentStageIndex ? 'text-blue-600' : 'text-gray-600'}`}>
              {s.name}
            </div>
          </div>
        ))}
      </div>

      {/* Current task */}
      <div className="text-center">
        <p className="text-gray-700 font-medium">{currentTask}</p>
        <p className="text-sm text-gray-500 mt-1">{progress}% complete</p>
      </div>
    </div>
  );
};

export default AnalysisProgress;
