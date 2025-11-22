#!/bin/bash

# showcAIse Setup Script
# Initializes the development environment

set -e

echo "🚀 Setting up showcAIse development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys before continuing."
    exit 0
fi

# Pull required images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start infrastructure services first
echo "🗄️  Starting infrastructure services..."
docker-compose up -d postgres redis minio

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo "💾 Initializing database..."
docker-compose exec -T postgres psql -U ${POSTGRES_USER:-showcaise_user} -d ${POSTGRES_DB:-showcaise} -f /docker-entrypoint-initdb.d/init.sql || true

# Create MinIO bucket
echo "🪣 Creating MinIO bucket..."
docker-compose exec -T minio mc alias set local http://localhost:9000 ${MINIO_ACCESS_KEY:-minioadmin} ${MINIO_SECRET_KEY:-minioadmin_secret_change_me} || true
docker-compose exec -T minio mc mb local/${MINIO_BUCKET:-showcaise-videos} || true

# Start all services
echo "🚀 Starting all services..."
docker-compose up -d

echo "✅ Setup complete!"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:       http://localhost:80"
echo "   API Gateway:    http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   MinIO Console:  http://localhost:9001"
echo "   Grafana:        http://localhost:3000"
echo "   Prometheus:     http://localhost:9090"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
