# showcAIse - AI Presentation Coach

An AI-powered presentation coaching tool that analyzes voice, speech patterns, and body language, then generates an improved avatar version of your presentation.

## Features

- 🎥 **Video Upload & Processing** - Upload presentation videos with chunked transfer support
- 🗣️ **Speech Analysis** - Transcription, filler word detection, pacing analysis, tone variation
- 👁️ **Computer Vision** - Eye contact tracking, posture analysis, confidence indicators
- 🤖 **AI Avatar Generation** - Generate improved avatar versions of your presentation
- 📊 **Interactive Dashboard** - Timeline visuals, metrics, and personalized recommendations

## Architecture

Microservices architecture with 6 core services:

- **Frontend** - React-based UI for video upload and results visualization
- **API Gateway** - Authentication, routing, rate limiting
- **Video Processing** - FFmpeg-based video/audio extraction and processing
- **Speech Analysis** - Whisper transcription, filler detection, pace analysis (via Hugging Face/Together AI)
- **Computer Vision** - Eye tracking, posture detection using MediaPipe and ML models
- **Avatar Generation** - AI avatar synthesis for improved presentations
- **Analytics** - Aggregation, scoring, and recommendations

## Tech Stack

- **Frontend**: React + TailwindCSS
- **Backend**: FastAPI (Python)
- **Databases**: PostgreSQL, Redis
- **Storage**: MinIO (S3-compatible)
- **ML APIs**: Hugging Face, Together AI
- **Queue**: Celery + Redis
- **Infrastructure**: Docker Compose

## Prerequisites

- Docker & Docker Compose
- API Keys:
  - Hugging Face API key (for ML models)
  - Together AI API key (for inference)
  - Optional: D-ID or HeyGen API key (for avatar generation)

## Quick Start

1. **Clone and setup environment**:
```bash
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse
cp .env.example .env
# Edit .env with your API keys
```

2. **Start all services**:
```bash
docker-compose up -d
```

3. **Initialize database**:
```bash
./scripts/setup.sh
```

4. **Access the application**:
- Frontend: http://localhost:80
- API Gateway: http://localhost:8000
- MinIO Console: http://localhost:9001
- Grafana: http://localhost:3000

## Development

### Team Structure

- **Developer 1**: Frontend + UX
- **Developer 2**: API Gateway + Analytics
- **Developer 3**: Video Processing + Computer Vision
- **Developer 4**: Speech Analysis + Avatar Generation

### Running individual services

```bash
# Start only specific services
docker-compose up frontend api-gateway postgres redis

# View logs for a service
docker-compose logs -f speech-analysis

# Restart a service
docker-compose restart video-processing

# Run tests
docker-compose run --rm api-gateway pytest
```

### Development mode

```bash
# Use dev override for hot-reloading
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Project Structure

```
showcAIse/
├── frontend/              # React frontend
├── services/
│   ├── api-gateway/       # API routing & auth
│   ├── video-processing/  # Video/audio extraction
│   ├── speech-analysis/   # Transcription & speech metrics
│   ├── computer-vision/   # Eye tracking & posture
│   ├── avatar-generation/ # AI avatar synthesis
│   ├── analytics/         # Reporting & recommendations
│   └── shared/            # Common utilities
├── infrastructure/        # Nginx, monitoring configs
├── scripts/               # Setup and utility scripts
└── docs/                  # Documentation
```

## Documentation

- [API Documentation](docs/API.md)
- [Setup Guide](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Development Workflow](docs/DEVELOPMENT.md)

## License

MIT License - See LICENSE file for details

## Contributing

1. Create a feature branch from `main`
2. Implement your changes with tests
3. Submit a pull request with clear description

## Support

For issues and questions, please open a GitHub issue.
