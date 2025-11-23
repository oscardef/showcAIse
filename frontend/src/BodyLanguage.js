import React from 'react';

function BodyLanguage() {
  // Hardcoded body language data
  const bodyLanguageData = {
    "overall_score_out_of_10": 7.2,
    "summary": "The speaker showed a relatively consistent posture, but with some noticeable shifts in body tilt and leaning. Hand gestures were fairly active, but could benefit from more purposeful movement. Overall, the speaker's openness and confidence were evident, but could be enhanced with more varied energy levels.",
    "eye_contact": {
      "score": "8/10",
      "feedback": "The speaker's overall posture and body orientation suggest a good level of engagement with the audience. To improve, focus on maintaining a gentle, occasional gaze around the room to connect with different audience members."
    },
    "posture": {
      "score": "6.5/10",
      "feedback": "The speaker's body tilt averaged around 30°, which is slightly forward. This could be improved by maintaining a more upright posture, with occasional gentle leans forward for emphasis. Notice that the shoulder width remained relatively consistent, indicating a stable upper body position."
    },
    "gestures": {
      "score": "8/10",
      "feedback": "The speaker's hand raises were fairly active, with an average left hand raise of 1.9 and right hand raise of 1.95. To take it to the next level, practice incorporating more purposeful gestures, such as using open palms for emphasis or illustrating points with sweeping motions."
    },
    "openness_and_confidence": {
      "score": "7.5/10",
      "feedback": "The openness score averaged around 2.3, indicating a relatively good level of openness and confidence. To improve, focus on varying your tone, pace, and volume to convey enthusiasm and conviction. Also, practice using more expansive gestures to convey a sense of authority and confidence."
    },
    "movement_and_energy": {
      "score": "5.5/10",
      "feedback": "The speaker's movement and energy levels were relatively static, with some minor shifts in body tilt and leaning. To improve, practice incorporating subtle pacing, such as taking a few steps to the side or using gentle gestures to add emphasis. This will help maintain the audience's engagement and attention."
    },
    "specific_moments": [
      {
        "timestamp_sec": 1.0,
        "issue": "Noticeable decrease in openness score",
        "suggestion": "Take a deep breath and refocus on your message to regain confidence and enthusiasm"
      },
      {
        "timestamp_sec": 1.5,
        "issue": "Slight increase in body tilt",
        "suggestion": "Make a conscious effort to straighten up and maintain a more upright posture"
      }
    ],
    "three_biggest_things_to_improve": [
      "1. Maintain a more upright posture, with occasional gentle leans forward for emphasis",
      "2. Incorporate more purposeful gestures, such as using open palms for emphasis or illustrating points with sweeping motions",
      "3. Vary energy levels by incorporating subtle pacing, such as taking a few steps to the side or using gentle gestures to add emphasis"
    ]
  };

  const getScoreColor = (score) => {
    const numericScore = parseFloat(score);
    if (numericScore >= 8) return '#10b981';
    if (numericScore >= 6) return '#f59e0b';
    return '#ef4444';
  };

  const categories = [
    { key: 'eye_contact', label: 'Eye Contact' },
    { key: 'posture', label: 'Posture' },
    { key: 'gestures', label: 'Gestures' },
    { key: 'openness_and_confidence', label: 'Openness & Confidence' },
    { key: 'movement_and_energy', label: 'Movement & Energy' }
  ];

  return (
    <div className="tab-content-clean">
      {/* Overall Score */}
      <div className="stat-card">
        <h2 style={{ marginBottom: '24px' }}>Body Language Analysis</h2>
        <div className="body-language-overall">
          <div className="overall-score-display">
            <div className="score-circle" style={{ 
              borderColor: getScoreColor(bodyLanguageData.overall_score_out_of_10),
              color: getScoreColor(bodyLanguageData.overall_score_out_of_10)
            }}>
              <span className="score-number">{bodyLanguageData.overall_score_out_of_10}</span>
              <span className="score-label">/10</span>
            </div>
          </div>
          <p className="overall-summary">{bodyLanguageData.summary}</p>
        </div>
      </div>

      {/* Category Scores */}
      <div className="body-language-categories">
        {categories.map(category => {
          const data = bodyLanguageData[category.key];
          return (
            <div key={category.key} className="stat-card category-card">
              <div className="category-header">
                <h3>{category.label}</h3>
                <span 
                  className="category-score"
                  style={{ color: getScoreColor(data.score) }}
                >
                  {data.score}
                </span>
              </div>
              <p className="category-feedback">{data.feedback}</p>
            </div>
          );
        })}
      </div>

      {/* Specific Moments to Improve */}
      {bodyLanguageData.specific_moments && bodyLanguageData.specific_moments.length > 0 && (
        <div className="stat-card">
          <h2 style={{ marginBottom: '20px' }}>Specific Moments to Review</h2>
          <div className="specific-moments-list">
            {bodyLanguageData.specific_moments.map((moment, idx) => (
              <div key={idx} className="specific-moment-card">
                <div className="moment-timestamp">
                  {moment.timestamp_sec}s
                </div>
                <div className="moment-details">
                  <div className="moment-issue">
                    <strong>Issue:</strong> {moment.issue}
                  </div>
                  <div className="moment-suggestion">
                    <strong>Suggestion:</strong> {moment.suggestion}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Top 3 Improvements */}
      <div className="stat-card">
        <h2 style={{ marginBottom: '20px' }}>Top 3 Things to Improve</h2>
        <div className="top-improvements-list">
          {bodyLanguageData.three_biggest_things_to_improve.map((improvement, idx) => (
            <div key={idx} className="improvement-item">
              <div className="improvement-number">{idx + 1}</div>
              <div className="improvement-text">{improvement.replace(/^\d+\.\s*/, '')}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default BodyLanguage;
