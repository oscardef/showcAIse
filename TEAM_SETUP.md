# 🤝 Team Setup Guide

Hey team! Here's how to get showcAIse running on your machine.

## 🐳 Docker Setup (Recommended - 2 minutes)

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- Together AI API key (from Discord)

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse

# 2. Configure API key
cd backend
cp .env.example .env
# Edit .env and paste the API key from Discord:
# TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4

# 3. Start everything with Docker Compose
cd ..
docker-compose up --build
```

**That's it!** The app will be running at:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000

### Docker Commands Reference

```bash
# Start services (first time or after code changes)
docker-compose up --build

# Start services (without rebuilding)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild specific service
docker-compose build backend
docker-compose build frontend

# Restart a service
docker-compose restart backend
```

## 💻 Manual Setup (Without Docker)

### 1. Clone & Install Dependencies

```bash
# Clone the repo
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse

# Backend setup
cd backend
pip install -r requirements.txt

# Frontend setup (new terminal)
cd frontend
npm install
```

### 2. Get API Key from Discord

Check our Discord channel for the Together AI API key:
```
TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4
```

### 3. Configure API Key

**Option A: Quick Test (Terminal)**
```bash
export TOGETHER_API_KEY=tgp_v1_jWkCnxJNapoEtWiHYDWIoGDQn4VTUuiVZyr29ToaWi4
```

**Option B: Persistent (Recommended)**
```bash
cd backend
cp .env.example .env
# Edit .env and paste the API key
```

### 4. Run the App

```bash
# Terminal 1: Backend
cd backend
python3.12 main.py  # Runs on http://localhost:8000

# Terminal 2: Frontend  
cd frontend
npm start  # Opens http://localhost:3000
```

## 🎯 Testing

1. Open http://localhost:3000
2. Upload a short test video (30 sec - 2 min)
3. Wait ~30 seconds for analysis
4. Check the results dashboard:
   - **Timeline Charts:** Confidence & WPM over time
   - **Priority Actions:** Top 3 improvements
   - **Recommendations:** 15+ detailed suggestions
   - **Metrics:** Sentence structure, power/weak words
   - **Filler Breakdown:** Which fillers you use most
   - **Transcript:** Full text with highlighted fillers

## 🚨 Common Issues

### Docker Issues

**Port already in use:**
```bash
docker-compose down
lsof -ti:3000 -ti:8000 | xargs kill -9
docker-compose up
```

**Permission denied:**
```bash
sudo docker-compose up --build
```

**Out of disk space:**
```bash
docker system prune -a  # Remove unused images/containers
```

**Container won't start:**
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Manual Setup Issues

**"Module not found" error**
```bash
cd backend
pip install -r requirements.txt
```

**"FFmpeg not found"**
```bash
# Mac
brew install ffmpeg

# Ubuntu/Linux
sudo apt install ffmpeg

# Windows
# Download from: https://ffmpeg.org/download.html
```

**"Port already in use"**
```bash
# Kill the process
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Frontend won't start**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

**API Key Issues:**
- Make sure you copied the FULL key from Discord
- Check for extra spaces/newlines
- Verify .env file is in backend/ directory
- No quotes needed around the key value

## 📂 Project Structure

```
showcAIse/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── analyzer.py          # Speech analysis engine
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # API keys (DO NOT COMMIT)
│   └── .env.example         # Template
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main component
│   │   ├── Upload.js       # Drag-drop upload
│   │   ├── Results.js      # Analysis visualization
│   │   └── index.css       # Styles
│   └── package.json
├── docker-compose.yml       # Multi-container setup
├── Dockerfile.backend       # Backend container
├── Dockerfile.frontend      # Frontend container
└── TEAM_SETUP.md           # This file
```

## 🔐 Security Note

- ✅ `.env` is gitignored - safe to add your API key
- ❌ Never commit `.env` to GitHub
- ✅ Always use `.env.example` for templates
- ✅ Share keys via Discord, not in code

## 🛠️ Development Workflow

### With Docker (Hot Reload Enabled)

1. **Start services:** `docker-compose up`
2. **Edit code:** Changes auto-reload
   - Backend: Volume mounted, Python restarts on save
   - Frontend: React hot reload active
3. **View logs:** `docker-compose logs -f backend` or `frontend`
4. **Restart if needed:** `docker-compose restart backend`
5. **Test changes:** Browser automatically refreshes

### Without Docker

1. **Pull latest changes:** `git pull`
2. **Create feature branch:** `git checkout -b feature-name`
3. **Make changes**
4. **Test locally**
5. **Commit & push:** `git add . && git commit -m "message" && git push`
6. **Create PR on GitHub**

## 💡 Features Already Built ✅

- ✅ Timeline visualization with interactive charts (Recharts)
- ✅ Filler word highlighting in transcript
- ✅ 15+ recommendation types with action steps
- ✅ Priority actions section (top 3)
- ✅ Detailed metrics (sentence structure, power/weak words)
- ✅ Filler breakdown by type
- ✅ WPM and confidence tracking
- ✅ Docker deployment with hot reload

## 🚀 Next Features to Build

- [ ] Body language analysis (computer vision)
- [ ] Video player with timestamp annotations
- [ ] Avatar generation with improved delivery
- [ ] Export PDF reports
- [ ] Comparison view (before/after)
- [ ] Script improvement generator

## 🆘 Need Help?

Ask in Discord! We're all learning together 🚀
