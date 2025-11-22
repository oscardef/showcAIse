# showcAIse 🎤

AI-powered presentation analysis tool that provides instant feedback on your speaking performance. Upload a video and get detailed insights on delivery, pacing, confidence, and areas to improve.

## ✨ Features

- **Smart Analysis**: Detects strong moments and areas for improvement
- **Confidence Scoring**: Advanced algorithm analyzing pace, fillers, sentiment, and language quality
- **Segment-Specific Feedback**: Play and review individual moments with categorized insights
- **Avatar Generator** ✨ NEW: Generate a "perfect" presentation with all improvements applied
- **Clean Professional UI**: Focused 4-tab interface (Moments, Avatar Generator, Recommendations, Transcript)
- **Video Playback**: Segment-only player that isolates specific moments for focused review
- **Actionable Recommendations**: Specific, prioritized suggestions for improvement

## 🚀 Quick Start

### Prerequisites
- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))
- Together AI API key ([Get one here](https://together.ai))
- Hugging Face API token ([Get one here](https://huggingface.co/settings/tokens)) - for avatar generation

### Setup & Run

```bash
# 1. Clone and navigate
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse

# 2. Configure API keys
cd backend
cp .env.example .env
# Edit .env and add:
# TOGETHER_API_KEY="your-together-key"
# HF_API_TOKEN="your-huggingface-token"

# 3. Start with Docker
cd ..
docker compose up --build
```

**That's it!** Visit http://localhost:3000

### Docker Commands

```bash
# Start containers
docker compose up -d

# View logs
docker compose logs -f

# Stop containers
docker compose down

# Rebuild after code changes
docker compose up --build
```

## 💻 Manual Setup (Without Docker)

### Prerequisites
- Python 3.12+
- Node.js 18+
- FFmpeg ([Install guide](https://ffmpeg.org/download.html))

### Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env: TOGETHER_API_KEY="your-key-here"

# Run
python main.py
```

Backend runs at http://localhost:8000

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at http://localhost:3000

## 📊 How It Works

### Analysis Pipeline

1. **Video Upload** → Extracts audio with FFmpeg
2. **Transcription** → Together AI Whisper large-v3 model
3. **Smart Segmentation** → Breaks transcript into natural speaking chunks
4. **Confidence Scoring** → Analyzes each segment:
   - **Pacing** (±25 points): Optimal 130-160 WPM
   - **Filler Words** (±30 points): Strict thresholds (4%, 8%, 15%)
   - **Sentiment** (±20 points): Positive/negative/neutral tone
   - **Language Quality** (±15 points): Hedge words ("I guess", "kind of")
5. **Moment Detection** → Identifies strong (≥70%) and weak (<50%) moments
6. **Categorization** → Tags moments by type:
   - Strong: "Confident language", "Clean delivery", "Perfect pacing"
   - Weak: "Excessive fillers", "Uncertain tone", "Poor pacing"
7. **Recommendations** → Generates specific, actionable improvement suggestions

### Scoring System

**Base Score**: 50 points (neutral starting point)

**Adjustments:**
- Good pacing (130-160 WPM): +25
- Too fast/slow: -20
- Minimal fillers (<4%): +30
- Excessive fillers (>15%): -35
- Positive sentiment: +20
- Negative/uncertain tone: -25
- Hedge words (>2): -15

**Result**: 0-100 confidence score
- **70-100**: Strong moment
- **50-69**: Adequate
- **0-49**: Needs improvement

## 🎯 What You Get

### Results Dashboard

**1. Moments Tab** (Main Focus)
- Overview stats (performance score, strong/weak counts, duration)
- **Strong Moments**: What made them effective with categories
- **Weak Moments**: Specific issues + improvement suggestions
- Segment-only video player (plays just that moment)

**2. Avatar Generator Tab** ✨ NEW
- Generate a "perfect" presentation applying all feedback
- Removes all filler words automatically
- Optimizes pacing to ideal 145 WPM
- Replaces weak/uncertain language with confident alternatives
- Generates improved script with TTS audio
- Shows before/after stats comparison
- Download improved script and audio

**3. Recommendations Tab**
- Priority actions (top 3 critical improvements)
- Additional suggestions with specific steps

**4. Transcript Tab**
- Full text with filler word highlighting
- Easy reference for detailed review

## 🏗️ Tech Stack

**Backend**
- FastAPI 0.121.3 (Python 3.12)
- Together AI Whisper API (transcription)
- Transformers 4.30+ (DistilBERT sentiment)
- FFmpeg (audio extraction)

**Frontend**
- React 18.2
- Clean, professional UI (no rounded corners, minimal nesting)
- Segment-isolated video player

**Deployment**
- Docker & Docker Compose
- Multi-container architecture
- Hot reload for development

## 📁 Project Structure

```
showcAIse/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── analyzer.py          # Core analysis engine
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main app component
│   │   ├── Upload.js       # Video upload interface
│   │   ├── ResultsClean.js # Results dashboard
│   │   ├── MomentsAnalysis.js # Moments display
│   │   └── clean.css       # Professional styling
│   └── package.json
├── docker-compose.yml       # Container orchestration
├── Dockerfile.backend
└── Dockerfile.frontend
```

## 🔧 API Reference

### POST /api/upload
Upload video for analysis

**Request**: `multipart/form-data` with video file

**Response**:
```json
{
  "session_id": "abc-123",
  "transcript": "Full transcription...",
  "word_count": 150,
  "wpm": 145,
  "duration": 62.4,
  "overall_confidence": 72,
  "key_clips": {
    "strong_moments": [
      {
        "segment_num": 3,
        "confidence": 85,
        "start_time": 15,
        "end_time": 32,
        "text": "Segment text...",
        "categories": ["Confident language", "Perfect pacing"],
        "metrics": {"wpm": 145, "fillers": 0, "sentiment": 0.85}
      }
    ],
    "weak_moments": [
      {
        "segment_num": 7,
        "confidence": 42,
        "issues": ["Excessive filler words", "Uncertain tone"],
        "suggestions": ["Reduce fillers by pausing...", "Use more confident language..."],
        "metrics": {"wpm": 98, "fillers": 8, "sentiment": -0.45}
      }
    ]
  },
  "recommendations": [...],
  "timeline": [...]
}
```

## 🐛 Troubleshooting

### Docker Issues

```bash
# Port conflicts (3000 or 8000 in use)
docker compose down
lsof -ti:3000 -ti:8000 | xargs kill -9
docker compose up -d

# Rebuild from scratch
docker compose down
docker compose up --build

# Clean everything
docker system prune -a
```

### API Key Issues

1. Verify key is correct (no extra spaces/newlines)
2. Check `.env` file is in `backend/` directory
3. Restart containers after changing `.env`:
   ```bash
   docker compose down
   docker compose up -d
   ```

### FFmpeg Missing (Manual Setup)

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Module Errors

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules
npm install
```

## 🎓 Algorithm Details

### Timestamp Accuracy

Uses time-based calculation (0.4 seconds per word) instead of ratio-based positioning. Adds 1-second buffer for accuracy.

```python
start_second = int((cumulative_words * 0.4)) - 1
end_second = int((cumulative_words * 0.4)) + 1
```

### Segment-Only Video Player

- Automatically starts at segment start time
- Pauses at segment end time
- Prevents seeking outside segment boundaries
- Visual indicator shows segment timing
- Loops back to start when finished

### Hedge Word Detection

Identifies uncertain language:
- "kind of", "sort of"
- "I guess", "I don't know"
- "maybe", "probably"
- Penalty: -15 points if >2 occurrences

### Filler Detection

Tracks common fillers:
- "um", "uh", "like", "you know"
- "so", "actually", "basically", "literally"

Thresholds:
- <4%: No penalty (natural)
- 4-8%: -10 points (mild)
- 8-15%: -25 points (moderate)
- >15%: -35 points (severe)

## 📝 Development Notes

### Recent Improvements (v2.1)

**Algorithm Accuracy**
- Changed confidence base from 70→50 (more realistic)
- Added sentiment integration (±20 points)
- Stricter filler thresholds
- Hedge word detection

**UI Redesign**
- Reduced from 6 tabs → 3 tabs
- Removed all rounded corners (flat professional design)
- Eliminated card nesting
- Prominent upload header
- Segment-focused video player

**Timestamp Fix**
- Switched to time-based calculation
- Added accuracy buffers
- Segment-only playback with boundaries

### Known Limitations

1. Sentiment analysis per segment (may be slow for long videos)
2. Hedge word detection is regex-based (context-independent)
3. Timestamps accurate within ±1 second

### Future Enhancements

- Caching for sentiment analysis
- Context-aware hedge word detection
- User feedback loop for threshold tuning
- Body language analysis (computer vision)
- Comparative analytics (track improvement over time)

---

**Built with ❤️ for better presentations**

Visit http://localhost:3000 to get started!
