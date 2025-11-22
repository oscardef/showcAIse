# showcAIse - AI Presentation Coach 🎤

Analyze your presentation skills with AI: speech patterns, filler words, pacing, and get actionable feedback.

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- FFmpeg (`brew install ffmpeg` on Mac)
- Together AI API key (shared via Discord)

### Setup & Run

```bash
# 1. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure API Key (IMPORTANT!)
# Option A: Export in terminal (temporary, for testing)
export TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4

# Option B: Create .env file (recommended, persists between sessions)
cp .env.example .env
# Then edit .env and paste the API key from Discord

# 3. Start backend (runs on port 8000)
python main.py

# 4. Frontend Setup (new terminal)
cd frontend
npm install
npm start  # Opens http://localhost:3000
```

### Test It!
1. Open http://localhost:3000
2. Upload a short video (30 sec - 2 min recommended)
3. Wait ~30 seconds for analysis
4. View your results!

## 🎯 What It Does

**Current Features:**
- ✅ Video upload (drag & drop)
- ✅ Audio extraction (FFmpeg)
- ✅ Speech transcription (Whisper API or mock)
- ✅ Filler word detection (um, uh, like, etc.)
- ✅ Speaking pace analysis (WPM)
- ✅ AI-generated recommendations

**Coming Soon:**
- 🚧 Body language analysis (eye contact, posture)
- 🚧 Timeline visualization
- 🚧 Export PDF reports

## 📁 Project Structure

```
showcAIse/
├── backend/          # FastAPI server
│   ├── main.py       # API endpoints
│   ├── analyzer.py   # Speech analysis logic
│   └── requirements.txt
├── frontend/         # React app
│   ├── src/
│   │   ├── App.tsx
│   │   ├── Upload.tsx
│   │   └── Results.tsx
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Backend API Key Setup

**Method 1: Environment Variable (Quick Test)**
```bash
# Mac/Linux
export TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4

# Windows (PowerShell)
$env:TOGETHER_API_KEY="tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4"

# Windows (CMD)
set TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4
```

**Method 2: .env File (Recommended for Team)**
```bash
# 1. Go to backend directory
cd backend

# 2. Copy the template
cp .env.example .env

# 3. Edit backend/.env and add the API key from Discord:
TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4
PORT=8000
```

**Note for Team:**
- ✅ `.env` is gitignored - safe to add API key locally
- ✅ Share the key via Discord, not GitHub
- ✅ Each teammate creates their own `.env` file
- ✅ `.env.example` shows the format (no real key)

### Frontend Configuration (Optional)
```bash
# Create frontend/.env.local if needed
REACT_APP_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

**"FFmpeg not found"**
```bash
# Mac
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

**"Port already in use"**
```bash
# Backend: Change PORT in backend/main.py
# Frontend: Run with PORT=3001 npm start
```

**"Module not found" errors**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

## 🎬 Development Tips

**Use short test videos:**
- Start with 30-60 second clips
- Keep under 5 minutes for testing
- MP4 format works best

**Without API key:**
- System works with mock data
- Great for UI/UX development
- Add real API key when ready

**Team workflow:**
- One person: Backend features
- One person: Frontend UI/UX
- One person: Analysis algorithms
- One person: Testing & documentation

## 📊 API Reference

### Upload Video
```bash
POST /api/upload
Content-Type: multipart/form-data

FormData: video=@presentation.mp4

Response:
{
  "session_id": "abc123",
  "status": "completed",
  "results": {
    "transcript": "Hello everyone...",
    "word_count": 245,
    "filler_count": 8,
    "wpm": 147,
    "recommendations": [...]
  }
}
```

### Get Session Results
```bash
GET /api/session/{session_id}

Response: Same as upload response
```

## 🚀 Deployment (Optional)

**Backend:**
- Railway.app (recommended)
- Render.com
- Fly.io

**Frontend:**
- Vercel (recommended)
- Netlify
- GitHub Pages

## 🤝 Contributing

This is a hackathon project! Feel free to:
- Add new analysis features
- Improve UI/UX
- Fix bugs
- Add tests

## 📝 License

MIT License - Use freely for your projects!

## 🎯 Hackathon Strategy

**Hour 1-2:** Get basic system working (this is done!)
**Hour 3-4:** Polish UI, add graphs/charts
**Hour 5-6:** Add one advanced feature (body language OR avatar)
**Hour 7-8:** Testing, bug fixes, sample videos
**Hour 9-10:** Demo prep, presentation slides

**Demo Tips:**
- Use a good sample video showing clear improvements
- Practice your pitch (2-3 minutes)
- Show before/after metrics
- Emphasize AI/ML components

Good luck! 🎤✨
