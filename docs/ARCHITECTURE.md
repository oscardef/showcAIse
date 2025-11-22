# Architecture Documentation

## System Overview

showcAIse is a microservices-based AI presentation coaching platform that analyzes presentation videos and provides actionable feedback.

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│              Nginx (Port 80)                 │
│  - Reverse Proxy                             │
│  - Rate Limiting                             │
│  - Load Balancing                            │
└────────┬────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│Frontend │ │   API Gateway    │
│ (React) │ │    (FastAPI)     │
└─────────┘ └────────┬─────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌──────────────┐ ┌──────────┐ ┌───────────┐
│Video Process │ │  Speech  │ │ Computer  │
│   Service    │ │ Analysis │ │  Vision   │
└──────┬───────┘ └────┬─────┘ └─────┬─────┘
       │              │              │
       └──────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌────────────┐  ┌──────────┐  ┌─────────────┐
│  Avatar    │  │Analytics │  │  Postgres   │
│Generation  │  │  Service │  │   Redis     │
└────────────┘  └──────────┘  │   MinIO     │
                               └─────────────┘
```

## Services

### 1. Frontend (React + TypeScript)
**Purpose**: User interface for video upload and results visualization

**Technology**:
- React 18
- TypeScript
- TailwindCSS
- Socket.io Client (WebSocket)

**Responsibilities**:
- Video upload with progress tracking
- Real-time analysis status updates
- Results dashboard and visualizations
- Avatar video playback

### 2. API Gateway (FastAPI)
**Purpose**: Single entry point for all client requests

**Technology**:
- FastAPI
- Python 3.11
- WebSocket support

**Responsibilities**:
- Authentication and authorization (JWT)
- Request routing to microservices
- Rate limiting
- CORS handling
- Real-time updates via WebSocket

**Endpoints**:
- `/api/v1/auth/*` - Authentication
- `/api/v1/videos/*` - Video upload
- `/api/v1/analysis/*` - Analysis results
- `/ws/*` - WebSocket connections

### 3. Video Processing Service (FastAPI + Celery)
**Purpose**: Video upload handling and preprocessing

**Technology**:
- FastAPI
- FFmpeg
- OpenCV
- Celery workers

**Responsibilities**:
- Video format validation
- Audio track extraction (16kHz WAV)
- Frame extraction (2 fps for CV analysis)
- Upload to MinIO storage
- Trigger downstream analysis services

**Processing Pipeline**:
1. Download video from MinIO
2. Extract audio → `audio/{session_id}/audio.wav`
3. Extract frames → `frames/{session_id}/frame_*.jpg`
4. Upload artifacts to MinIO
5. Notify speech and CV services

### 4. Speech Analysis Service (FastAPI)
**Purpose**: Analyze speech patterns and content

**Technology**:
- FastAPI
- Hugging Face API (Whisper for transcription)
- Together AI API
- Librosa (audio processing)

**Responsibilities**:
- Speech-to-text transcription
- Filler word detection ("um", "uh", "like")
- Speaking pace calculation (WPM)
- Tone variation analysis
- Pause detection

**Analysis Outputs**:
- Full transcript
- Words per minute
- Filler word count and timestamps
- Tone variation score (0-100)

### 5. Computer Vision Service (FastAPI)
**Purpose**: Analyze body language and visual cues

**Technology**:
- FastAPI
- MediaPipe (pose estimation, face mesh)
- OpenCV
- Hugging Face models (optional)

**Responsibilities**:
- Eye contact estimation (gaze tracking)
- Head posture analysis
- Facial expression detection
- Confidence indicators over time

**Analysis Outputs**:
- Eye contact percentage
- Posture quality score (0-100)
- Confidence score (0-100)
- Frame-by-frame metrics

### 6. Avatar Generation Service (FastAPI + Celery)
**Purpose**: Generate improved avatar presentation video

**Technology**:
- FastAPI
- D-ID API / HeyGen API
- Hugging Face models (alternative)

**Responsibilities**:
- Take improved transcript
- Apply pacing adjustments
- Generate avatar video with better delivery
- Upload to MinIO

**Integration Options**:
1. **D-ID API** - Commercial, high quality
2. **HeyGen API** - Alternative commercial option
3. **Hugging Face** - Open-source models (SadTalker, Wav2Lip)

### 7. Analytics Service (FastAPI)
**Purpose**: Aggregate results and generate recommendations

**Technology**:
- FastAPI
- PostgreSQL
- OpenAI API (optional, for recommendations)

**Responsibilities**:
- Combine speech and vision metrics
- Calculate overall scores
- Generate personalized recommendations
- Store results in database
- Historical trend analysis

**Recommendation Engine**:
- Rule-based recommendations
- Optional: GPT-4 for personalized advice

## Data Layer

### PostgreSQL
**Purpose**: Persistent storage for structured data

**Schema**:
- `users` - User accounts
- `sessions` - Analysis sessions
- `speech_analysis` - Speech metrics
- `vision_analysis` - CV metrics
- `recommendations` - Generated advice
- `avatar_videos` - Avatar video metadata

### Redis
**Purpose**: Cache, message queue, real-time state

**Usage**:
- Session state (`session:{id}`)
- Analysis results cache (`results:{id}`)
- Celery task queue
- Pub/Sub for WebSocket updates

### MinIO (S3-Compatible)
**Purpose**: Object storage for videos and artifacts

**Buckets**:
- `videos/` - Original uploaded videos
- `audio/` - Extracted audio files
- `frames/` - Extracted video frames
- `avatars/` - Generated avatar videos

**Lifecycle Policies**:
- Delete original videos after 30 days
- Delete processed frames after 24 hours
- Keep avatars indefinitely

## Communication Patterns

### Synchronous (HTTP/REST)
- Frontend ↔ API Gateway
- API Gateway ↔ Services

### Asynchronous (Celery + Redis)
- Video processing tasks
- Avatar generation tasks

### Real-time (WebSocket)
- Analysis progress updates
- Status notifications

### Pub/Sub (Redis)
- Service-to-service event notifications
- WebSocket message broadcasting

## Security

### Authentication
- JWT tokens (HS256 algorithm)
- 60-minute token expiration
- Refresh token support

### Authorization
- Session-based access control
- Users can only access their own sessions

### Data Protection
- Private MinIO buckets
- Presigned URLs for temporary access
- Environment-based secrets

### Rate Limiting
- 60 requests/minute per IP (API Gateway)
- Configurable per endpoint

## Scalability

### Horizontal Scaling
- All services are stateless (except databases)
- Scale services independently via `docker-compose.yml`:
  ```yaml
  deploy:
    replicas: 3
  ```

### Load Balancing
- Nginx distributes requests
- Docker Compose round-robin for services

### Resource Allocation
- Video processing: CPU-intensive (2+ cores)
- Speech/CV analysis: API calls (light)
- Avatar generation: Queue-based (1 worker sufficient)

## Monitoring

### Metrics (Prometheus)
- Request rates and latencies
- Queue depths
- Error rates
- Resource usage (CPU, memory)

### Dashboards (Grafana)
- Service health overview
- API performance
- Processing pipeline metrics

### Logging
- Structured JSON logs
- Centralized via Docker logs
- Optional: ELK stack integration

## Deployment

### Development
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose up -d
```

### Kubernetes (Future)
- Helm charts for production deployment
- Auto-scaling based on queue depth
- Multi-region support

## Technology Choices

### Why Microservices?
- Independent scaling of services
- Technology flexibility per service
- Fault isolation
- Team parallelization (4 developers)

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type safety with Pydantic
- WebSocket support

### Why Docker Compose?
- Simple local development
- Production-like environment
- Easy CI/CD integration

### Why Hugging Face/Together AI?
- No GPU infrastructure needed
- State-of-the-art models
- Cost-effective for MVP
- Easy API integration

## Future Enhancements

1. **Real-time Analysis** - Webcam analysis during practice
2. **Advanced Recommendations** - GPT-4 powered coaching
3. **Historical Tracking** - Progress over time
4. **Team Features** - Share presentations, peer feedback
5. **Mobile App** - Native iOS/Android apps
6. **Live Presentation** - Real-time feedback during actual presentations
