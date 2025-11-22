# 🤝 Team Setup Guide

Hey team! Here's how to get showcAIse running on your machine.

## ⚡ Quick Setup (5 min)

### 1. Clone & Install Dependencies

```bash
# Clone the repo
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
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
source venv/bin/activate
python main.py  # Runs on http://localhost:8000

# Terminal 2: Frontend  
cd frontend
npm start  # Opens http://localhost:3000
```

## 🎯 Testing

1. Open http://localhost:3000
2. Upload a short test video (30 sec - 2 min)
3. Wait ~30 seconds for analysis
4. Check results!

## 🚨 Common Issues

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
```

**Frontend won't start**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## 📂 Project Structure

```
showcAIse/
├── backend/          # Python FastAPI server
│   ├── main.py       # API endpoints
│   ├── analyzer.py   # Speech analysis
│   ├── .env          # YOUR API KEY HERE (gitignored)
│   └── .env.example  # Template (shared on GitHub)
├── frontend/         # React app
│   ├── src/
│   │   ├── App.js
│   │   ├── Upload.js
│   │   └── Results.js
│   └── package.json
└── README.md
```

## 🔐 Security Note

- ✅ `.env` is gitignored - safe to add your API key
- ❌ Never commit `.env` to GitHub
- ✅ Always use `.env.example` for templates
- ✅ Share keys via Discord, not in code

## 🛠️ Development Workflow

1. **Pull latest changes:** `git pull`
2. **Create feature branch:** `git checkout -b feature-name`
3. **Make changes**
4. **Test locally**
5. **Commit & push:** `git add . && git commit -m "message" && git push`
6. **Create PR on GitHub**

## 💡 Next Features to Build

- [ ] Timeline visualization with charts
- [ ] Filler word highlighting
- [ ] Body language analysis (computer vision)
- [ ] Video player with annotations
- [ ] Export PDF reports

## 🆘 Need Help?

Ask in Discord! We're all learning together 🚀
