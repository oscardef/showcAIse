# Development Workflow

## Team Structure

- **Developer 1**: Frontend + UX
- **Developer 2**: API Gateway + Analytics
- **Developer 3**: Video Processing + Computer Vision
- **Developer 4**: Speech Analysis + Avatar Generation

## Getting Started

### 1. Clone and Setup

```bash
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse
cp .env.example .env
# Add your API keys to .env
./scripts/setup.sh
```

### 2. Start Development Environment

```bash
# Hot-reloading mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts source code as volumes for live updates without rebuilding.

## Development Guidelines

### Code Organization

Each service follows this structure:
```
service-name/
├── Dockerfile
├── requirements.txt
├── app/
│   ├── main.py          # FastAPI app entry point
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   └── utils/           # Helper functions
└── tests/
    └── test_*.py
```

### Coding Standards

#### Python
- Follow PEP 8 style guide
- Use type hints
- Document functions with docstrings
- Use async/await for I/O operations

```python
from typing import Optional
from pydantic import BaseModel

class VideoRequest(BaseModel):
    """Request model for video upload."""
    session_id: str
    video_path: Optional[str] = None
```

#### TypeScript/React
- Use functional components with hooks
- Type all props and state
- Use meaningful component names

```typescript
interface VideoUploadProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onUpload, isUploading }) => {
  // Component code
};
```

### Git Workflow

#### Branch Naming
- `feature/<service>/<description>` - New features
- `fix/<service>/<description>` - Bug fixes
- `docs/<description>` - Documentation updates

Examples:
```bash
git checkout -b feature/frontend/video-upload-ui
git checkout -b fix/api-gateway/auth-token-expiry
git checkout -b docs/setup-instructions
```

#### Commit Messages

Follow conventional commits:
```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```bash
git commit -m "feat(frontend): add video upload progress bar"
git commit -m "fix(api-gateway): resolve CORS issue with WebSocket"
git commit -m "docs(setup): update environment variable instructions"
```

#### Pull Request Process

1. Create feature branch
2. Make changes and commit
3. Push to origin
4. Open PR with description:
   - What changed
   - Why it changed
   - How to test
5. Request review from relevant team member
6. Address feedback
7. Merge after approval

### Testing

#### Run Tests

```bash
# Individual service
docker-compose run --rm api-gateway pytest

# All services
docker-compose run --rm api-gateway pytest
docker-compose run --rm video-processing pytest
# ... repeat for each service
```

#### Writing Tests

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Debugging

#### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api-gateway

# Last 100 lines
docker-compose logs --tail=100 video-processing
```

#### Enter Container

```bash
docker-compose exec api-gateway bash
```

#### Debug Python Service

Add breakpoint in code:
```python
import pdb; pdb.set_trace()
```

Run service in interactive mode:
```bash
docker-compose run --rm --service-ports api-gateway
```

### Working on Your Service

#### Frontend Developer

Files: `frontend/`

```bash
# Start only frontend and dependencies
docker-compose up frontend api-gateway postgres redis

# Install new package
docker-compose exec frontend npm install <package>

# Run tests
docker-compose exec frontend npm test
```

#### Backend Developer

Files: `services/<your-service>/`

```bash
# Start your service and dependencies
docker-compose up <your-service> postgres redis minio

# Install new Python package
# 1. Add to requirements.txt
# 2. Rebuild
docker-compose build <your-service>

# Run tests
docker-compose run --rm <your-service> pytest
```

### Common Tasks

#### Add New API Endpoint

1. Create router file: `app/routers/new_feature.py`
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

2. Register in `app/main.py`:
```python
from app.routers import new_feature

app.include_router(new_feature.router, prefix="/api/v1/feature", tags=["feature"])
```

#### Add New Database Table

1. Update `infrastructure/postgres/init.sql`:
```sql
CREATE TABLE IF NOT EXISTS new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
```

2. Restart PostgreSQL:
```bash
docker-compose restart postgres
```

#### Update Shared Utilities

Files: `services/shared/`

After modifying shared code, rebuild all services:
```bash
docker-compose build
```

### Integration Testing

Test full workflow:

```bash
# 1. Upload video via API
curl -X POST -F "video=@test.mp4" http://localhost:8000/api/v1/videos/upload

# 2. Check status
curl http://localhost:8000/api/v1/analysis/<session_id>/status

# 3. Get results
curl http://localhost:8000/api/v1/analysis/<session_id>/results
```

### Performance Profiling

#### Python Services

Add profiling:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

#### Frontend

Use React DevTools Profiler for component rendering analysis.

### Database Migrations

For schema changes:

1. Update `infrastructure/postgres/init.sql`
2. Create migration script in `scripts/migrations/`
3. Run migration:
```bash
docker-compose exec postgres psql -U showcaise_user -d showcaise -f /path/to/migration.sql
```

### Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (fresh start)
docker-compose down -v

# Remove dangling images
docker image prune -f
```

## Troubleshooting

### Service Won't Start

1. Check logs: `docker-compose logs <service>`
2. Verify dependencies in requirements.txt
3. Ensure .env variables are set
4. Try rebuild: `docker-compose build <service>`

### Can't Connect to Database

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U showcaise_user -d showcaise
```

### Port Conflicts

Edit `docker-compose.yml` to change port mappings:
```yaml
ports:
  - "8080:8000"  # Change 8080 to available port
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a --volumes
```

## Best Practices

1. **Keep services independent** - Minimal coupling
2. **Use shared utilities** - Don't duplicate code
3. **Document APIs** - Update API.md
4. **Write tests** - At least for critical paths
5. **Log effectively** - Use structured logging
6. **Handle errors gracefully** - Return meaningful messages
7. **Validate inputs** - Use Pydantic models
8. **Monitor performance** - Check Prometheus metrics
9. **Secure secrets** - Never commit .env files
10. **Review PRs thoroughly** - Quality over speed

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Hugging Face API Docs](https://huggingface.co/docs/api-inference)
- [Together AI Docs](https://docs.together.ai/)
