# showcAIse Project - Quick Reference

## 🚀 Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your API keys

# 2. Run setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Access application
open http://localhost
```

## 📁 Project Structure

```
showcAIse/
├── frontend/                    # React frontend (Developer 1)
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   └── services/           # API clients
│   └── Dockerfile
│
├── services/                   # Backend microservices
│   ├── api-gateway/           # Entry point (Developer 2)
│   ├── video-processing/      # FFmpeg processing (Developer 3)
│   ├── speech-analysis/       # Speech analysis (Developer 4)
│   ├── computer-vision/       # CV analysis (Developer 3)
│   ├── avatar-generation/     # Avatar generation (Developer 4)
│   ├── analytics/             # Aggregation (Developer 2)
│   └── shared/                # Common utilities
│
├── infrastructure/            # Config files
│   ├── nginx/                # Reverse proxy
│   ├── postgres/             # Database schema
│   └── monitoring/           # Prometheus config
│
├── scripts/                  # Utility scripts
│   ├── setup.sh             # Initial setup
│   └── seed-db.sh           # Sample data
│
└── docs/                    # Documentation
    ├── API.md              # API reference
    ├── SETUP.md            # Setup guide
    ├── ARCHITECTURE.md     # System design
    └── DEVELOPMENT.md      # Dev workflow
```

## 🔑 Required API Keys

Add these to `.env`:
- `HUGGINGFACE_API_KEY` - For Whisper transcription, ML models
- `TOGETHER_AI_API_KEY` - For fast inference
- `DID_API_KEY` or `HEYGEN_API_KEY` - For avatar generation (optional)

## 🛠️ Development Commands

```bash
# Start with hot-reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# View logs
docker-compose logs -f [service-name]

# Run tests
docker-compose run --rm api-gateway pytest

# Restart service
docker-compose restart [service-name]

# Stop everything
docker-compose down

# Clean slate (removes data)
docker-compose down -v
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost | Main application |
| API Gateway | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| MinIO Console | http://localhost:9001 | Object storage |
| Grafana | http://localhost:3000 | Monitoring |
| Prometheus | http://localhost:9090 | Metrics |

## 👥 Team Ownership

| Developer | Services | Focus |
|-----------|----------|-------|
| Dev 1 | Frontend | Video upload UI, results dashboard, UX |
| Dev 2 | API Gateway, Analytics | Routing, auth, aggregation, recommendations |
| Dev 3 | Video Processing, Computer Vision | FFmpeg, eye tracking, posture analysis |
| Dev 4 | Speech Analysis, Avatar Generation | Transcription, filler detection, avatar API |

## 📊 Analysis Pipeline

```
1. Upload Video → API Gateway
2. Extract Audio + Frames → Video Processing
3. Parallel Analysis:
   - Speech Analysis (Whisper API)
   - Computer Vision (MediaPipe)
4. Aggregate Results → Analytics
5. Generate Avatar → Avatar Generation
6. Display Results → Frontend
```

## 🔧 Technology Stack

- **Frontend**: React, TypeScript, TailwindCSS
- **Backend**: FastAPI (Python 3.11)
- **ML APIs**: Hugging Face, Together AI
- **Storage**: MinIO (S3-compatible)
- **Database**: PostgreSQL
- **Cache/Queue**: Redis, Celery
- **Monitoring**: Prometheus, Grafana
- **Infrastructure**: Docker Compose

## 📝 Next Steps

1. **Configure API Keys** - Add to `.env` file
2. **Review Documentation** - Read `docs/SETUP.md`
3. **Start Development** - Run `docker-compose up`
4. **Implement Services** - Each developer works on assigned services
5. **Test Integration** - Upload video, verify pipeline

## 🆘 Common Issues

**Port conflicts**: Change ports in `docker-compose.yml`
**Services not starting**: Check logs with `docker-compose logs`
**API keys not working**: Verify `.env` format (no quotes)
**Out of memory**: Increase Docker memory allocation

## 📚 Documentation

- **Setup**: `docs/SETUP.md`
- **API Reference**: `docs/API.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Development**: `docs/DEVELOPMENT.md`

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/service/description`
2. Make changes and test
3. Commit: `git commit -m "feat(service): description"`
4. Push and create PR

---

**Built with ❤️ for better presentations**
