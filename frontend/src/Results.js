import React, { useState } from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Area, AreaChart } from 'recharts';
import VideoPlayer from './VideoPlayer';
import ClipReview from './ClipReview';

function Results({ data, onBack }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [videoTime, setVideoTime] = useState(0);

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
    { id: 'transcript', label: 'Transcript' }
  ];

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
          {activeTab === 'transcript' && renderTranscriptTab()}
        </div>
      </div>
    </div>
  );
}

export default Results;
