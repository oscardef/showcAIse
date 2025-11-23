#!/bin/bash

# Voice Cloning Integration Test Script
# Run this after starting docker compose

echo "🧪 Testing Voice Cloning Integration"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if containers are running
echo "1. Checking Docker containers..."
if docker compose ps | grep -q "backend.*Up"; then
    echo -e "${GREEN}✓ Backend container running${NC}"
else
    echo -e "${RED}✗ Backend container not running${NC}"
    echo "Run: docker compose up -d"
    exit 1
fi

if docker compose ps | grep -q "frontend.*Up"; then
    echo -e "${GREEN}✓ Frontend container running${NC}"
else
    echo -e "${RED}✗ Frontend container not running${NC}"
    echo "Run: docker compose up -d"
    exit 1
fi

echo ""

# Check backend health
echo "2. Checking backend API..."
BACKEND_STATUS=$(curl -s http://localhost:8000/ | grep -o "running" || echo "error")
if [ "$BACKEND_STATUS" = "running" ]; then
    echo -e "${GREEN}✓ Backend API responding${NC}"
else
    echo -e "${RED}✗ Backend API not responding${NC}"
    exit 1
fi

echo ""

# Check if TTS model directory exists
echo "3. Checking TTS cache..."
TTS_CACHE=$(docker compose exec -T backend ls /root/.local/share/tts/ 2>/dev/null | wc -l)
if [ $TTS_CACHE -gt 0 ]; then
    echo -e "${GREEN}✓ TTS cache exists (model may be cached)${NC}"
else
    echo -e "${YELLOW}⚠ TTS cache empty (model will download on first use)${NC}"
    echo "  Tip: Pre-download with: docker compose exec backend python preload_tts.py"
fi

echo ""

# Check voice cloning endpoint
echo "4. Checking voice cloning endpoint..."
echo -e "${YELLOW}→ This requires a valid session_id from uploaded video${NC}"
echo "  Upload a video first, then test: curl -X POST http://localhost:8000/api/voice-clone/{session_id}"

echo ""

# Check frontend
echo "5. Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ Frontend accessible at http://localhost:3000${NC}"
else
    echo -e "${RED}✗ Frontend not accessible${NC}"
    exit 1
fi

echo ""

# Check volumes
echo "6. Checking Docker volumes..."
if docker volume ls | grep -q "tts_cache"; then
    echo -e "${GREEN}✓ TTS cache volume exists${NC}"
else
    echo -e "${RED}✗ TTS cache volume missing${NC}"
fi

if docker volume ls | grep -q "huggingface_cache"; then
    echo -e "${GREEN}✓ Hugging Face cache volume exists${NC}"
else
    echo -e "${RED}✗ Hugging Face cache volume missing${NC}"
fi

echo ""
echo "===================================="
echo "✅ Basic checks complete!"
echo ""
echo "📝 Manual Testing Steps:"
echo "1. Open http://localhost:3000"
echo "2. Upload a video with audio"
echo "3. Wait for analysis to complete"
echo "4. Click 'Generate Improved Voice Clone' button"
echo "5. Wait 1-2 minutes (2-3 min first time)"
echo "6. Verify audio player appears"
echo "7. Play audio and download WAV file"
echo ""
echo "🔍 Monitor logs with:"
echo "   docker compose logs -f backend"
echo ""
