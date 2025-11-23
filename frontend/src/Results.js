import React, { useState } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Area, AreaChart } from 'recharts';
import VideoPlayer from './VideoPlayer';
import ClipReview from './ClipReview';

function Results({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [videoTime, setVideoTime] = useState(0);
  const [voiceCloning, setVoiceCloning] = useState({
    loading: false,
    error: null,
    completed: false,
    audioUrl: null,
    improvedScript: null,
    improvements: null
  });

  if (!data || !data.results) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading results...</p>
        </div>
      </div>
    );
  }

  const { results, video_url } = data;
  const sentiment = results.sentiment_analysis || {};

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'keymoments', label: 'Key Moments' },
    { id: 'sentiment', label: 'Sentiment Analysis' },
    { id: 'delivery', label: 'Delivery Metrics' },
    { id: 'recommendations', label: 'Recommendations' },
    { id: 'voiceclone', label: 'AI Generation' },
    { id: 'transcript', label: 'Transcript' }
  ];

  const handleGenerateVoiceClone = async (useDemo = false) => {
    setVoiceCloning({ ...voiceCloning, loading: true, error: null });
    
    try {
      const url = `http://localhost:8000/api/voice-clone/${data.session_id}${useDemo ? '?use_demo=true' : ''}`;
      const response = await fetch(url, {
        method: 'POST'
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Voice cloning failed');
      }
      
      const result = await response.json();
      
      setVoiceCloning({
        loading: false,
        error: null,
        completed: true,
        audioUrl: `http://localhost:8000${result.audio_url}`,
        improvedScript: result.improved_script,
        improvements: result.improvements,
        demoMode: result.demo_mode || false
      });
      
      // Switch to AI Generation tab to show results
      setActiveTab('voiceclone');
      
    } catch (error) {
      console.error('Voice cloning error:', error);
      setVoiceCloning({
        ...voiceCloning,
        loading: false,
        error: error.message || 'Failed to generate voice clone'
      });
    }
  };

  const jumpToTimestamp = (seconds) => {
    setVideoTime(seconds);
    setActiveTab('overview');
  };

  const getSeverityColor = (severity) => {
    const colors = { high: '#ef4444', medium: '#f59e0b', low: '#3b82f6', success: '#10b981' };
    return colors[severity] || '#6b7280';
  };

  const highlightFillers = (transcript, fillerPositions) => {
    if (!fillerPositions || fillerPositions.length === 0) {
      return <span>{transcript}</span>;
    }

    const segments = [];
    let lastIndex = 0;

    fillerPositions.forEach(([start, end, filler]) => {
      if (start > lastIndex) {
        segments.push(<span key={`text-${lastIndex}`}>{transcript.substring(lastIndex, start)}</span>);
      }
      segments.push(<mark key={`filler-${start}`} className="filler-highlight">{transcript.substring(start, end)}</mark>);
      lastIndex = end;
    });

    if (lastIndex < transcript.length) {
      segments.push(<span key={`text-${lastIndex}`}>{transcript.substring(lastIndex)}</span>);
    }

    return <>{segments}</>;
  };

  const renderOverviewTab = () => (
    <div className="tab-content">
      {video_url && (
        <div className="video-section card">
          <h2>Your Presentation</h2>
          <VideoPlayer videoUrl={`http://localhost:8000${video_url}`} currentTime={videoTime} onTimeUpdate={setVideoTime} />
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric-card-modern">
          <div className="metric-label-top">Words</div>
          <div className="metric-value-large">{results.word_count}</div>
        </div>
        <div className="metric-card-modern">
          <div className="metric-label-top">Speaking Pace</div>
          <div className="metric-value-large">{results.wpm} <span className="unit">WPM</span></div>
        </div>
        <div className="metric-card-modern">
          <div className="metric-label-top">Filler Words</div>
          <div className="metric-value-large">{results.filler_count}</div>
        </div>
        <div className="metric-card-modern">
          <div className="metric-label-top">Duration</div>
          <div className="metric-value-large">{results.duration_minutes} <span className="unit">min</span></div>
        </div>
      </div>

      <div className="voice-clone-section card">
        <h2>🎤 AI Generation</h2>
        <p>Generate improved versions of your presentation</p>
        {!voiceCloning.completed && !voiceCloning.loading && (
          <div style={{ display: 'flex', gap: '12px', marginTop: '12px', flexWrap: 'wrap' }}>
            <button 
              className="btn-primary" 
              onClick={() => handleGenerateVoiceClone(false)}
            >
              Generate Voice Clone
            </button>
            <button 
              className="btn-secondary" 
              onClick={() => handleGenerateVoiceClone(true)}
              style={{ backgroundColor: '#6b7280' }}
            >
              Play Demo Audio
            </button>
          </div>
        )}
        {voiceCloning.loading && (
          <div className="loading" style={{ marginTop: '12px' }}>
            <div className="spinner"></div>
            <p>Generating... This may take 1-2 minutes</p>
          </div>
        )}
        {voiceCloning.error && (
          <div className="error-message" style={{ marginTop: '12px', color: '#ef4444' }}>
            ❌ {voiceCloning.error}
          </div>
        )}
        {voiceCloning.completed && (
          <div className="success-message" style={{ marginTop: '12px', color: '#10b981' }}>
            ✅ {voiceCloning.demoMode ? 'Demo audio loaded!' : 'Voice clone generated!'} Check the AI Generation tab to listen.
          </div>
        )}
      </div>

      <div className="quick-insights card">
        <h2>Key Insights</h2>
        <div className="insight-grid">
          <div className="insight-item">
            <div className="insight-label">Overall Confidence</div>
            <div className="insight-value" style={{ color: results.confidence_score > 70 ? '#10b981' : results.confidence_score > 50 ? '#f59e0b' : '#ef4444' }}>
              {results.confidence_score}%
            </div>
          </div>
          {sentiment.overall_sentiment && sentiment.overall_sentiment !== 'unavailable' && (
            <div className="insight-item">
              <div className="insight-label">Sentiment Tone</div>
              <div className="insight-value">{sentiment.tone}</div>
            </div>
          )}
          <div className="insight-item">
            <div className="insight-label">Avg Sentence Length</div>
            <div className="insight-value">{results.avg_sentence_length} words</div>
          </div>
        </div>
      </div>

      {results.priority_actions && results.priority_actions.length > 0 && (
        <div className="priority-actions-compact card">
          <h2>Top 3 Actions</h2>
          <div className="action-list-compact">
            {results.priority_actions.map((action, idx) => (
              <div key={idx} className="action-compact">
                <div className="action-number">{idx + 1}</div>
                <div>
                  <div className="action-title">{action.title}</div>
                  <div className="action-desc">{action.action}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const SENTIMENT_COLORS = { positive: '#10b981', negative: '#ef4444', neutral: '#6b7280' };

  const sentimentChartData = sentiment.emotion_distribution ? [
    { name: 'Positive', value: sentiment.emotion_distribution.positive },
    { name: 'Negative', value: sentiment.emotion_distribution.negative },
    { name: 'Neutral', value: sentiment.emotion_distribution.neutral }
  ].filter(item => item.value > 0) : [];

  const renderKeyMomentsTab = () => (
    <div className="tab-content">
      <ClipReview 
        keyClips={results.key_clips} 
        videoUrl={video_url ? `http://localhost:8000${video_url}` : null}
      />
    </div>
  );

  const renderSentimentTab = () => {
    if (!sentiment.overall_sentiment || sentiment.overall_sentiment === 'unavailable') {
      return <div className="tab-content"><div className="card">Sentiment analysis unavailable</div></div>;
    }

    return (
      <div className="tab-content">
        <div className="sentiment-overview-card card">
          <div className="sentiment-header-row">
            <div>
              <h2>Sentiment Analysis</h2>
              <div className="sentiment-tone-large">{sentiment.tone}</div>
              <div className="sentiment-score-text">
                Overall: <strong>{sentiment.overall_sentiment}</strong> ({(sentiment.sentiment_score * 100).toFixed(0)}% positive)
              </div>
              <div className="sentiment-confidence-text">
                Confidence: {(sentiment.confidence * 100).toFixed(0)}%
              </div>
            </div>
            {sentimentChartData.length > 0 && (
              <div className="sentiment-chart-container">
                <ResponsiveContainer width={250} height={250}>
                  <PieChart>
                    <Pie
                      data={sentimentChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value.toFixed(0)}%`}
                      outerRadius={90}
                      dataKey="value"
                    >
                      {sentimentChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name.toLowerCase()]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>

        {sentiment.trends && (
          <div className="sentiment-trends card">
            <h3>Sentiment Trends</h3>
            <div className="trend-badges">
              <div className="trend-badge">
                <span className="trend-label">Direction:</span>
                <span className={`trend-value ${sentiment.trends.direction}`}>{sentiment.trends.direction}</span>
              </div>
              <div className="trend-badge">
                <span className="trend-label">Consistency:</span>
                <span className="trend-value">{(sentiment.trends.consistency * 100).toFixed(0)}%</span>
              </div>
            </div>
            <p className="trend-description">
              {sentiment.trends.direction === 'declining' && 'Your sentiment weakens toward the end. Consider strengthening your conclusion.'}
              {sentiment.trends.direction === 'improving' && 'Great! Your presentation builds positive momentum.'}
              {sentiment.trends.direction === 'stable' && 'Your emotional tone remains consistent throughout.'}
            </p>
          </div>
        )}

        {sentiment.insights && sentiment.insights.length > 0 && (
          <div className="sentiment-insights card">
            <h3>Actionable Insights</h3>
            <div className="insights-list">
              {sentiment.insights.map((insight, idx) => (
                <div key={idx} className={`insight-card ${insight.type}`}>
                  <div className="insight-header-inline">
                    <span className="insight-title">{insight.title}</span>
                    <span className={`insight-severity ${insight.severity}`}>{insight.severity}</span>
                  </div>
                  <p className="insight-description">{insight.description}</p>
                  <div className="insight-action">Action: {insight.action}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {sentiment.negative_moments && sentiment.negative_moments.length > 0 && (
          <div className="moment-review card">
            <h3>Moments to Review ({sentiment.negative_moments.length})</h3>
            <p className="section-description">These segments show high-confidence negative sentiment. Click to watch and consider rephrasing.</p>
            <div className="moments-list">
              {sentiment.negative_moments.map((moment, idx) => (
                <div key={idx} className="moment-card negative">
                  <div className="moment-header">
                    <span className="moment-label">Segment {moment.segment}</span>
                    <button className="moment-play-btn" onClick={() => jumpToTimestamp(moment.timestamp_start)}>
                      Play at {moment.timestamp_start}s
                    </button>
                  </div>
                  <div className="moment-text">"{moment.text}"</div>
                  <div className="moment-confidence">Confidence: {(moment.confidence * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {sentiment.positive_peaks && sentiment.positive_peaks.length > 0 && (
          <div className="moment-review card">
            <h3>Your Best Moments ({sentiment.positive_peaks.length})</h3>
            <p className="section-description">These segments show strong positive delivery. Use these as reference for your style.</p>
            <div className="moments-list">
              {sentiment.positive_peaks.map((moment, idx) => (
                <div key={idx} className="moment-card positive">
                  <div className="moment-header">
                    <span className="moment-label">Segment {moment.segment}</span>
                    <button className="moment-play-btn" onClick={() => jumpToTimestamp(moment.timestamp_start)}>
                      Play at {moment.timestamp_start}s
                    </button>
                  </div>
                  <div className="moment-text">"{moment.text}"</div>
                  <div className="moment-confidence">Confidence: {(moment.confidence * 100).toFixed(0)}%</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderDeliveryTab = () => {
    // Find weakest and strongest moments
    let weakestMoment = null;
    let strongestMoment = null;
    
    if (results.timeline && results.timeline.length > 0) {
      weakestMoment = results.timeline.reduce((min, seg) => 
        seg.confidence < min.confidence ? seg : min, results.timeline[0]
      );
      strongestMoment = results.timeline.reduce((max, seg) => 
        seg.confidence > max.confidence ? seg : max, results.timeline[0]
      );
    }

    return (
      <div className="tab-content">
        {/* Confidence Explanation */}
        {results.confidence_explanation && (
          <div className="confidence-explanation-card card">
            <h2>📊 How Confidence is Calculated</h2>
            <p className="confidence-formula">{results.confidence_explanation}</p>
            <div className="confidence-breakdown">
              <div className="breakdown-item">
                <span className="breakdown-icon">🎯</span>
                <div>
                  <strong>Pacing (±20 points)</strong>
                  <p>Optimal: 130-160 WPM (conversational pace)</p>
                </div>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-icon">🎤</span>
                <div>
                  <strong>Filler Control (±30 points)</strong>
                  <p>Less than 5% filler words is ideal</p>
                </div>
              </div>
              <div className="breakdown-item">
                <span className="breakdown-icon">✍️</span>
                <div>
                  <strong>Structure (±10 points)</strong>
                  <p>Clear sentences with 15-20 words average</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Key Moments Summary */}
        {weakestMoment && strongestMoment && (
          <div className="key-moments-summary">
            <div className="moment-card weak-moment-card card">
              <h3>⚠️ Weakest Moment</h3>
              <div className="moment-details">
                <div className="moment-time">Segment #{weakestMoment.segment}</div>
                <div className="moment-confidence weak">{weakestMoment.confidence}%</div>
                <p className="moment-text">{weakestMoment.text_preview}</p>
                <p className="moment-explanation">{weakestMoment.confidence_explanation}</p>
              </div>
            </div>
            <div className="moment-card strong-moment-card card">
              <h3>✅ Strongest Moment</h3>
              <div className="moment-details">
                <div className="moment-time">Segment #{strongestMoment.segment}</div>
                <div className="moment-confidence strong">{strongestMoment.confidence}%</div>
                <p className="moment-text">{strongestMoment.text_preview}</p>
                <p className="moment-explanation">{strongestMoment.confidence_explanation}</p>
              </div>
            </div>
          </div>
        )}

        {/* Engagement Timeline Chart */}
        {results.timeline && results.timeline.length > 0 && (
          <div className="chart-section card">
            <h2>Performance Timeline</h2>
            <p className="chart-subtitle">Track your confidence and pacing throughout the presentation</p>
            
            <div className="chart-wrapper">
              <ResponsiveContainer width="100%" height={350}>
                <AreaChart data={results.timeline}>
                  <defs>
                    <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="segment" 
                    label={{ value: 'Segment', position: 'insideBottom', offset: -5 }} 
                  />
                  <YAxis domain={[0, 100]} label={{ value: 'Confidence (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload[0]) {
                        const data = payload[0].payload;
                        return (
                          <div className="custom-tooltip">
                            <p><strong>Segment {data.segment}</strong></p>
                            <p>Confidence: {data.confidence}%</p>
                            <p>WPM: {data.wpm}</p>
                            <p>Fillers: {data.filler_count}</p>
                            <p className="tooltip-explanation">{data.confidence_explanation}</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="confidence" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#confidenceGradient)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {results.metrics && (
          <div className="detailed-metrics card">
            <h2>Speech Analysis</h2>
            <div className="metrics-grid-detailed">
            <div className="metric-detail-card">
              <div className="metric-detail-value">{results.avg_sentence_length}</div>
              <div className="metric-detail-label">Avg Sentence Length</div>
            </div>
            <div className="metric-detail-card">
              <div className="metric-detail-value">{results.metrics.questions}</div>
              <div className="metric-detail-label">Questions Asked</div>
            </div>
            <div className="metric-detail-card">
              <div className="metric-detail-value">{results.metrics.power_words}</div>
              <div className="metric-detail-label">Power Words</div>
            </div>
            <div className="metric-detail-card">
              <div className="metric-detail-value">{results.metrics.weak_words}</div>
              <div className="metric-detail-label">Weak Phrases</div>
            </div>
          </div>
          
          {results.filler_breakdown && Object.keys(results.filler_breakdown).length > 0 && (
            <div className="filler-breakdown-section">
              <h3>Top Filler Words</h3>
              <div className="filler-tags">
                {Object.entries(results.filler_breakdown).map(([word, count]) => (
                  <div key={word} className="filler-tag">
                    <span className="filler-word">"{word}"</span>
                    <span className="filler-count">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          </div>
        )}
      </div>
    );
  };

  const renderRecommendationsTab = () => (
    <div className="tab-content">
      <div className="recommendations-list-clean card">
        <h2>Detailed Recommendations</h2>
        <p className="section-subtitle">Prioritized actions to improve your presentation delivery</p>
        {results.recommendations.map((rec, idx) => (
          <div key={idx} className="recommendation-item" style={{ borderLeftColor: getSeverityColor(rec.severity) }}>
            <div className="rec-header">
              <h3>{rec.title}</h3>
              <span className={`severity-badge ${rec.severity}`}>{rec.severity}</span>
            </div>
            <p className="rec-description">{rec.description}</p>
            {rec.action && (
              <div className="rec-action">
                <strong>Action:</strong> {rec.action}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderVoiceCloneTab = () => (
    <div className="tab-content">
      {!voiceCloning.completed && !voiceCloning.loading && (
        <div className="card">
          <h2>🎤 AI Generation</h2>
          <p>Generate improved versions of your presentation.</p>
          <p style={{ marginTop: '16px' }}>Voice cloning will:</p>
          <ul style={{ marginLeft: '20px', marginTop: '8px' }}>
            <li>Remove all filler words from your speech</li>
            <li>Replace uncertain language with confident phrasing</li>
            <li>Maintain your natural voice and speaking style</li>
            <li>Generate clean audio ready for video creation</li>
          </ul>
          <div style={{ display: 'flex', gap: '12px', marginTop: '20px', flexWrap: 'wrap' }}>
            <button 
              className="btn-primary" 
              onClick={() => handleGenerateVoiceClone(false)}
            >
              Generate Voice Clone
            </button>
            <button 
              className="btn-secondary" 
              onClick={() => handleGenerateVoiceClone(true)}
              style={{ backgroundColor: '#6b7280', color: 'white', padding: '12px 24px', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
            >
              Play Demo Audio
            </button>
          </div>
        </div>
      )}
      
      {voiceCloning.loading && (
        <div className="card">
          <div className="loading">
            <div className="spinner"></div>
            <h2>Generating...</h2>
            <p>This process takes 1-2 minutes. We're:</p>
            <ul style={{ textAlign: 'left', marginLeft: '40px', marginTop: '12px' }}>
              <li>Extracting your voice from the video</li>
              <li>Generating an improved script</li>
              <li>Cloning your voice with AI (TTS XTTS v2)</li>
              <li>Creating the final audio file</li>
            </ul>
          </div>
        </div>
      )}
      
      {voiceCloning.error && (
        <div className="card">
          <h2 style={{ color: '#ef4444' }}>❌ Generation Failed</h2>
          <p>{voiceCloning.error}</p>
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button 
              className="btn-primary" 
              onClick={() => handleGenerateVoiceClone(false)}
            >
              Try Again
            </button>
            <button 
              className="btn-secondary" 
              onClick={() => handleGenerateVoiceClone(true)}
              style={{ backgroundColor: '#6b7280', color: 'white', padding: '12px 24px', borderRadius: '8px', border: 'none', cursor: 'pointer' }}
            >
              Play Demo Audio
            </button>
          </div>
        </div>
      )}
      
      {voiceCloning.completed && voiceCloning.audioUrl && (
        <div className="tab-content">
          <div className="card">
            <h2>✅ {voiceCloning.demoMode ? 'Demo Audio' : 'Voice Clone Generated Successfully!'}</h2>
            <p>Listen to {voiceCloning.demoMode ? 'the demo' : 'your improved presentation'}:</p>
            
            <div style={{ marginTop: '20px', marginBottom: '20px' }}>
              <audio controls style={{ width: '100%', maxWidth: '600px' }}>
                <source src={voiceCloning.audioUrl} type="audio/wav" />
                Your browser does not support the audio element.
              </audio>
            </div>
            
            <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
              <a 
                href={voiceCloning.audioUrl} 
                download={`improved_presentation_${data.session_id}.wav`}
                className="btn-primary"
              >
                Download Audio
              </a>
            </div>
          </div>
          
          {voiceCloning.improvements && (
            <div className="card">
              <h2>📊 Improvements Made</h2>
              <div className="metrics-grid">
                <div className="metric-card-modern">
                  <div className="metric-label-top">Original Words</div>
                  <div className="metric-value-large">{voiceCloning.improvements.original_word_count}</div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-label-top">Improved Words</div>
                  <div className="metric-value-large">{voiceCloning.improvements.improved_word_count}</div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-label-top">Target WPM</div>
                  <div className="metric-value-large">{voiceCloning.improvements.target_wpm}</div>
                </div>
                <div className="metric-card-modern">
                  <div className="metric-label-top">Est. Duration</div>
                  <div className="metric-value-large">{voiceCloning.improvements.estimated_duration_seconds}s</div>
                </div>
              </div>
              
              {voiceCloning.improvements.improvements && voiceCloning.improvements.improvements.length > 0 && (
                <div style={{ marginTop: '20px' }}>
                  <h3>What Changed:</h3>
                  <ul style={{ marginLeft: '20px', marginTop: '12px' }}>
                    {voiceCloning.improvements.improvements.map((improvement, idx) => (
                      <li key={idx} style={{ marginBottom: '8px' }}>{improvement}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          
          {voiceCloning.improvedScript && (
            <div className="card">
              <h2>📝 Improved Script</h2>
              <div className="transcript-content" style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                {voiceCloning.improvedScript}
              </div>
              
              <div style={{ marginTop: '20px', padding: '12px', backgroundColor: '#fef3c7', borderRadius: '8px' }}>
                <strong>💡 Tip:</strong> Compare this with the original transcript in the Transcript tab to see all the improvements!
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderTranscriptTab = () => (
    <div className="tab-content">
      <div className="transcript-viewer card">
        <h2>Full Transcript</h2>
        <div className="transcript-content">
          {highlightFillers(results.transcript, results.filler_positions)}
        </div>
        <div className="transcript-legend">
          <mark className="filler-highlight">Yellow highlights</mark> indicate filler words detected in your speech
        </div>
      </div>
    </div>
  );

  return (
    <div className="results-page">
      <div className="results-header-modern">
        <div>
          <h1>Presentation Analysis</h1>
          <div className="header-meta">
            Analyzed {results.word_count} words in {results.duration_minutes} minutes
          </div>
        </div>
        <button className="btn-secondary" onClick={onBack}>
          Analyze New Video
        </button>
      </div>

      <div className="tabs-container">
        <div className="tabs-nav">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="tabs-body">
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'keymoments' && renderKeyMomentsTab()}
          {activeTab === 'sentiment' && renderSentimentTab()}
          {activeTab === 'delivery' && renderDeliveryTab()}
          {activeTab === 'recommendations' && renderRecommendationsTab()}
          {activeTab === 'voiceclone' && renderVoiceCloneTab()}
          {activeTab === 'transcript' && renderTranscriptTab()}
        </div>
      </div>
    </div>
  );
}

export default Results;
