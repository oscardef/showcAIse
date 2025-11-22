# showcAIse System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                                │
│                         (React Frontend)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  ┌───────┐  ┌────────┐│
│  │  Overview   │  │  Sentiment   │  │ Delivery │  │ Rec's │  │Transcr││
│  │             │  │  Analysis    │  │ Metrics  │  │       │  │ipt    ││
│  │ • Video     │  │ • Trends     │  │ • Charts │  │ • List│  │• Full ││
│  │ • Metrics   │  │ • Insights   │  │ • Pace   │  │ • Acts│  │  Text ││
│  │ • Top 3     │  │ • Moments ◄──┼──┼──────────┼──┼───────┼──┼───────┤│
│  └─────────────┘  └──────────────┘  └──────────┘  └───────┘  └────────┘│
│         │                  │                                     │       │
│         │                  │ Click "Play at 42s"                │       │
│         ▼                  ▼                                     │       │
│  ┌──────────────────────────────────────┐                       │       │
│  │       VideoPlayer Component          │                       │       │
│  │  • HTML5 video element               │                       │       │
│  │  • Programmatic seeking              │                       │       │
│  │  • currentTime prop → useEffect      │                       │       │
│  │  • onTimeUpdate callback             │                       │       │
│  └──────────────────────────────────────┘                       │       │
│         │                                                        │       │
└─────────┼────────────────────────────────────────────────────────┼───────┘
          │                                                        │
          │ GET /api/video/{session_id}                           │
          │                                                        │
┌─────────┼────────────────────────────────────────────────────────┼───────┐
│         │                BACKEND API                             │       │
│         │              (FastAPI Server)                          │       │
├─────────┼────────────────────────────────────────────────────────┼───────┤
│         ▼                                                        │       │
│  ┌─────────────────┐                                            │       │
│  │ Video Serving   │                                            │       │
│  │  Endpoint       │                                            │       │
│  │                 │                                            │       │
│  │ • FileResponse  │                                            │       │
│  │ • Accept-Ranges │                                            │       │
│  │ • Byte seeking  │                                            │       │
│  └────────┬────────┘                                            │       │
│           │                                                     │       │
│           │ reads from                                          │       │
│           ▼                                                     │       │
│  ┌──────────────────┐        ┌────────────────────┐            │       │
│  │  videos/         │        │   uploads/         │            │       │
│  │  (persistent)    │        │   (temporary)      │            │       │
│  │                  │        │                    │            │       │
│  │  abc123.mp4      │◄───────│  tempfile.mp4      │            │       │
│  │  def456.mp4      │ copy   └────────────────────┘            │       │
│  └──────────────────┘              ▲                            │       │
│           │                        │                            │       │
│           │                        │                            │       │
│  ┌────────▼─────────────────────────┼────────────────┐          │       │
│  │                                  │                 │          │       │
│  │         POST /api/upload         │                 │          │       │
│  │                                  │                 │          │       │
│  │  1. Save video to uploads/       │                 │          │       │
│  │  2. Copy to videos/              │                 │          │       │
│  │  3. Extract audio (FFmpeg)       │                 │          │       │
│  │  4. Transcribe (Whisper API) ────┼─────────────────┼──────────┼──────►│
│  │  5. Analyze speech               │                 │          │       │
│  │  6. Analyze sentiment ◄──────────┼─────────────────┘          │       │
│  │  7. Return session data          │                            │       │
│  └──────────────────────────────────┘                            │       │
│           │                                                       │       │
│           │                                                       │       │
└───────────┼───────────────────────────────────────────────────────┼───────┘
            │                                                       │
            ▼                                                       │
┌──────────────────────────────────────────────────────────────────┼───────┐
│                        analyzer.py                               │       │
│                    (Analysis Engine)                             │       │
├──────────────────────────────────────────────────────────────────┼───────┤
│                                                                   │       │
│  ┌──────────────────────────────────────────┐                    │       │
│  │  analyze_speech()                        │                    │       │
│  │                                          │                    │       │
│  │  • Transcription text analysis          │                    │       │
│  │  • Word count, WPM, fillers             │                    │       │
│  │  • Confidence scoring                   │                    │       │
│  │  • Timeline segments                    │                    │       │
│  │  • Recommendations                      │                    │       │
│  └──────────────────────────────────────────┘                    │       │
│                                                                   │       │
│  ┌──────────────────────────────────────────┐                    │       │
│  │  analyze_sentiment_and_tone()            │                    │       │
│  │                                          │                    │       │
│  │  Input: transcript + words               │◄───────────────────┘       │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 1. Sentence Splitting               │  │                            │
│  │  │    • Split by .!?                   │  │                            │
│  │  │    • Track cumulative word count    │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 2. Timestamp Calculation            │  │                            │
│  │  │    • word_position / total_words    │  │                            │
│  │  │    • * video_duration * 0.4         │  │                            │
│  │  │    • timestamp_start, timestamp_end │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 3. DistilBERT Model                 │  │                            │
│  │  │    • Lazy loaded on first use       │  │                            │
│  │  │    • Cached in memory               │  │                            │
│  │  │    • Returns sentiment + confidence │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                │                          │                            │
│  │                ▼                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 4. Segment Analysis                 │  │                            │
│  │  │    For each sentence:               │  │                            │
│  │  │    • Get sentiment (POS/NEG/NEUTRAL)│  │                            │
│  │  │    • Store confidence score         │  │                            │
│  │  │    • Store timestamps               │  │                            │
│  │  │    • Store text preview             │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 5. Moment Detection                 │  │                            │
│  │  │    • Filter NEGATIVE with conf>0.80 │  │                            │
│  │  │    • Sort by confidence DESC        │  │                            │
│  │  │    • Take top 5 → negative_moments  │  │                            │
│  │  │    • Filter POSITIVE with conf>0.95 │  │                            │
│  │  │    • Take top 3 → positive_peaks    │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 6. Trend Analysis                   │  │                            │
│  │  │    • Build sentiment_timeline       │  │                            │
│  │  │    • Compare first_third vs last_third│                            │
│  │  │    • Calculate direction:           │  │                            │
│  │  │      - improving (end > start + 0.2)│  │                            │
│  │  │      - declining (end < start - 0.2)│  │                            │
│  │  │      - stable (otherwise)           │  │                            │
│  │  │    • Calculate consistency (std dev)│  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  ┌────────────────────────────────────┐  │                            │
│  │  │ 7. Insights Generation              │  │                            │
│  │  │    if negative_ratio > 0.4:         │  │                            │
│  │  │      → warning (high severity)      │  │                            │
│  │  │    if direction == "declining":     │  │                            │
│  │  │      → warning (medium severity)    │  │                            │
│  │  │    if negative_moments > 0:         │  │                            │
│  │  │      → info (medium severity)       │  │                            │
│  │  │    if mostly positive:              │  │                            │
│  │  │      → success (low severity)       │  │                            │
│  │  └────────────────────────────────────┘  │                            │
│  │                                          │                            │
│  │  Output: {                               │                            │
│  │    overall_sentiment,                    │                            │
│  │    sentiment_score,                      │                            │
│  │    confidence,                           │                            │
│  │    tone,                                 │                            │
│  │    emotion_distribution: {pos, neg, neu},│                            │
│  │    segments: [...],                      │                            │
│  │    negative_moments: [...],              │                            │
│  │    positive_peaks: [...],                │                            │
│  │    trends: {                             │                            │
│  │      direction,                          │                            │
│  │      start_sentiment,                    │                            │
│  │      end_sentiment,                      │                            │
│  │      consistency                         │                            │
│  │    },                                    │                            │
│  │    insights: [...]                       │                            │
│  │  }                                       │                            │
│  └──────────────────────────────────────────┘                            │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                        DOCKER INFRASTRUCTURE                              │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────┐         ┌─────────────────────────┐         │
│  │   Frontend Container    │         │   Backend Container     │         │
│  │   (Node 18 Alpine)      │         │   (Python 3.12 Slim)    │         │
│  │                         │         │                         │         │
│  │  Port: 3000             │         │  Port: 8000             │         │
│  │  Hot Reload: ✓          │         │  Hot Reload: ✓          │         │
│  └─────────────────────────┘         └─────────────────────────┘         │
│             │                                     │                       │
│             │ Volume Mount                        │ Volume Mounts         │
│             ▼                                     ▼                       │
│  ┌─────────────────────────┐         ┌─────────────────────────┐         │
│  │  ./frontend → /app      │         │  ./backend → /app       │         │
│  │  (source code)          │         │  (source code)          │         │
│  └─────────────────────────┘         └─────────────────────────┘         │
│                                                   │                       │
│                                                   │ Named Volume          │
│                                                   ▼                       │
│                                      ┌──────────────────────────┐         │
│                                      │  huggingface_cache       │         │
│                                      │  (Docker Volume)         │         │
│                                      │                          │         │
│                                      │  → /root/.cache/         │         │
│                                      │    huggingface/          │         │
│                                      │                          │         │
│                                      │  • DistilBERT model      │         │
│                                      │    (~268 MB)             │         │
│                                      │  • Persists across       │         │
│                                      │    container restarts    │         │
│                                      └──────────────────────────┘         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW                                      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  User Action                 → API Call            → Processing          │
│  ────────────────────────────────────────────────────────────────────────│
│  1. Upload video.mp4         → POST /api/upload    → Save + Analyze      │
│  2. View results             → GET /api/results    → Return JSON         │
│  3. Click "Play at 42s"      → setVideoTime(42)    → useEffect triggers  │
│  4. Video seeks              → videoRef.currentTime → HTML5 API          │
│  5. Request video stream     → GET /api/video/abc  → FileResponse        │
│  6. Switch tab               → setActiveTab()      → Re-render           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                       TECHNOLOGY STACK                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Frontend:                                                                │
│    • React 18.2 (UI framework)                                           │
│    • Recharts 3.4.1 (data visualization)                                 │
│    • Axios 1.6.2 (HTTP client)                                           │
│                                                                           │
│  Backend:                                                                 │
│    • FastAPI 0.121.3 (web framework)                                     │
│    • Transformers 4.30.0+ (DistilBERT)                                   │
│    • PyTorch 2.0.0+ (ML runtime)                                         │
│    • FFmpeg (audio extraction)                                           │
│    • Together AI Whisper API (transcription)                             │
│                                                                           │
│  Infrastructure:                                                          │
│    • Docker Compose 3.8                                                  │
│    • Python 3.12 Slim                                                    │
│    • Node 18 Alpine                                                      │
│                                                                           │
│  ML Models:                                                               │
│    • DistilBERT-base-uncased-finetuned-sst-2-english                     │
│      (Sentiment Classification, 268 MB)                                  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Timestamp Estimation Approach
**Problem**: Whisper API returns text without word-level timestamps  
**Solution**: Calculate position ratio: `(cumulative_words / total_words) * duration * 0.4`  
**Trade-off**: Approximation, but good enough for seeking to general moments

### 2. Video Storage Strategy
**Problem**: Need persistent video access for playback  
**Solution**: Copy uploaded videos to `videos/` directory  
**Trade-off**: Disk space grows, need cleanup strategy  
**Alternative Considered**: Stream from uploads/ (rejected: files get deleted)

### 3. Sentiment Model Choice
**Problem**: Need fast, accurate sentiment analysis  
**Solution**: DistilBERT (lightweight, pre-trained on SST-2)  
**Trade-off**: 268 MB model size, but persistent volume solves re-download issue  
**Alternative Considered**: OpenAI API (rejected: cost, latency)

### 4. Frontend Architecture
**Problem**: Information overload on single page  
**Solution**: 5-tab interface with logical grouping  
**Trade-off**: More clicks to see all data  
**Benefit**: Clearer focus, better UX

### 5. Session Storage
**Problem**: Need to store analysis results  
**Solution**: In-memory dictionary (current)  
**Trade-off**: Data lost on restart, not production-ready  
**Future**: Redis or PostgreSQL for persistence
