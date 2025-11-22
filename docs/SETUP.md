# Setup Guide

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 8GB+ RAM available for Docker
- 20GB+ disk space
- API Keys:
  - Hugging Face API key
  - Together AI API key
  - Optional: OpenAI API key, D-ID API key

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/oscardef/showcAIse.git
cd showcAIse
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required API Keys:**
```env
HUGGINGFACE_API_KEY=your_key_here
TOGETHER_AI_API_KEY=your_key_here
```

### 3. Run Setup Script

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

This will:
- Pull and build all Docker images
- Start infrastructure services (PostgreSQL, Redis, MinIO)
- Initialize the database
- Create storage buckets
- Start all application services

### 4. Access the Application

Once setup completes, access:

- **Frontend**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (user: minioadmin, password: from .env)
- **Grafana**: http://localhost:3000 (user: admin, password: from .env)

## Development Mode

For development with hot-reloading:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This mounts your local source code into containers for live updates.

## Manual Setup (Alternative)

If the script doesn't work, run these commands manually:

```bash
# Start infrastructure
docker-compose up -d postgres redis minio

# Wait for services (30 seconds)
sleep 30

# Initialize database
docker-compose exec postgres psql -U showcaise_user -d showcaise -f /docker-entrypoint-initdb.d/init.sql

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Verify Installation

Check all services are healthy:

```bash
docker-compose ps
```

All services should show "Up" status.

Test API:
```bash
curl http://localhost:8000/health
```

## Common Issues

### Port Already in Use

If ports 80, 8000, 5432, 6379, 9000, or 3000 are in use:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`

### Services Not Starting

Check logs:
```bash
docker-compose logs <service-name>
```

### Database Connection Issues

Restart PostgreSQL:
```bash
docker-compose restart postgres
```

### API Keys Not Working

Ensure `.env` file has correct format (no quotes around values):
```env
HUGGINGFACE_API_KEY=hf_xxxxx
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Updating

```bash
git pull
docker-compose build
docker-compose up -d
```

## Next Steps

- Review [Architecture Documentation](ARCHITECTURE.md)
- Check [API Documentation](API.md)
- Read [Development Workflow](DEVELOPMENT.md)
