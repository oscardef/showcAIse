# showcAIse - AI Presentation Coach 🎤

AI-powered presentation analysis tool built for a 10-hour hackathon. Upload a video, get instant feedback with actionable recommendations.

## 🚀 Quick Start (2 minutes with Docker)

### Prerequisites
- Docker Desktop ([Download here](https://www.docker.com/products/docker-desktop))
- Together AI API key

### Setup & Run

```bash
# 1. Clone repo
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse

# 2. Configure API key
cd backend
cp .env.example .env
# Edit .env and add your Together AI API key

# 3. Start with Docker Compose
cd ..
docker-compose up --build
```

**That's it!** Visit http://localhost:3000

### Docker Commands

```bash
# Start (background)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after changes
docker-compose up --build
```

## 💻 Manual Setup (Without Docker)

### Prerequisites
- Python 3.12+
- Node.js 18+
- FFmpeg installed

### Setup

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Configuration

**Method 1: Environment Variable**
```bash
export TOGETHER_API_KEY="your-api-key-here"
```

**Method 2: .env File (Recommended)**
```bash
cd backend
cp .env.example .env
# Edit .env and add your API key
```

### Run

```bash
# Terminal 1 - Backend
cd backend
python3.12 main.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

Visit http://localhost:3000

## 🎯 What It Does

**Current Features:**
- 🎤 **Speech Transcription** - Together AI Whisper large-v3 model
- 📊 **Timeline Visualization** - Interactive confidence & WPM charts
- 🎯 **Filler Detection** - Highlighted "um", "uh", "like", "you know" in transcript
- 🎖️ **Priority Actions** - Top 3 most critical improvements
- 💡 **15+ Recommendations** - With specific action steps
- 📈 **Detailed Metrics** - Sentence structure, power/weak words, passive voice
- 🔍 **Filler Breakdown** - See which filler words you use most
- ⚡ **Fast Analysis** - Complete results in ~30 seconds
- 🐳 **Docker Ready** - One command deployment

## 📁 Project Structure

```
showcAIse/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── analyzer.py          # Analysis engine (15+ checks)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main component
│   │   ├── Upload.js       # File upload UI
│   │   ├── Results.js      # Visualization dashboard
│   │   └── index.css
│   └── package.json
├── docker-compose.yml       # Multi-container orchestration
├── Dockerfile.backend
├── Dockerfile.frontend
└── .dockerignore
```

## 🐛 Troubleshooting

**Docker Issues:**

```bash
# Port conflicts
docker-compose down
lsof -ti:3000 -ti:8000 | xargs kill -9

# Rebuild containers
docker-compose up --build

# Clean everything
docker system prune -a
```

**Manual Setup Issues:**

**FFmpeg missing:**
```bash
# macOS: brew install ffmpeg
# Ubuntu: sudo apt-get install ffmpeg
# Windows: Download from ffmpeg.org
```

**API errors:**
- Verify your Together AI API key is correct
- Check .env file is in backend/ directory
- Ensure no extra spaces/newlines in key

**Module errors:**
```bash
# Backend: pip install -r requirements.txt
# Frontend: rm -rf node_modules && npm install
```

## 📊 API Reference

### POST /api/upload
Upload video for analysis.

**Request:**
- `file`: Video file (multipart/form-data)

**Response:**
```json
{
  "session_id": "uuid",
  "transcript": "Full transcription...",
  "word_count": 150,
  "sentence_count": 10,
  "avg_sentence_length": 15.0,
  "filler_count": 12,
  "wpm": 125,
  "duration": 72.0,
  "confidence": 0.92,
  "recommendations": [
    {
      "icon": "🎯",
      "title": "Reduce Filler Words",
      "description": "...",
      "severity": "high",
      "action": "Specific steps..."
    }
  ],
  "priority_actions": [
    {"title": "...", "action": "..."}
  ],
  "filler_positions": [[0, 10, "um"], ...],
  "filler_breakdown": {"um": 5, "uh": 3, "like": 4},
  "timeline": [
    {
      "segment": 1,
      "confidence": 0.95,
      "wpm": 130,
      "filler_count": 2
    }
  ],
  "metrics": {
    "avg_sentence_length": 15.0,
    "questions": 3,
    "power_words": 8,
    "weak_words": 5,
    "passive_voice": 2
  }
}
```

### GET /api/session/{session_id}
Retrieve previous analysis results.

## 🔧 Tech Stack

- **Backend:** FastAPI 0.121.3, Python 3.12, Together AI Whisper large-v3, FFmpeg
- **Frontend:** React 18.2, Recharts 3.4.1, Axios 1.6.2
- **Deployment:** Docker & Docker Compose
- **Storage:** In-memory sessions (hackathon speed)

## 📈 Analysis Features

- Speech transcription with timestamps
- Filler word detection (um, uh, like, you know, so, actually, basically, literally)
- Speaking pace (WPM) tracking
- Sentence structure analysis
- Weak vs power word detection
- Passive voice identification
- Repetitive sentence pattern detection
- Question usage analysis
- Timeline segmentation (10 segments)
- Priority action extraction

## 🤝 Team Setup

See [TEAM_SETUP.md](./TEAM_SETUP.md) for complete onboarding guide with Docker instructions.

## 🎯 Hackathon Strategy

**Hour 1-2:** Basic system ✅ (DONE!)
**Hour 3-4:** UI polish & visualizations ✅ (DONE!)
**Hour 5-6:** Advanced recommendations ✅ (DONE!)
**Hour 7-8:** Docker deployment ✅ (DONE!)
**Hour 9-10:** Testing, demo prep, presentation

**Next Phase:** Avatar generation or body language analysis

---

Built in 10 hours for the hackathon 🚀
