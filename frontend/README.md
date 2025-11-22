# Frontend Service

React-based frontend for the showcAIse AI Presentation Coach.

## Features

- Video upload with chunked transfer and progress tracking
- Real-time analysis progress via WebSocket
- Interactive dashboard with timeline visualizations
- Results breakdown: speech metrics, CV insights, recommendations
- Avatar video playback and comparison

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Environment Variables

See `.env.example` in root directory. Frontend uses:
- `REACT_APP_API_URL` - API Gateway URL
- `REACT_APP_WS_URL` - WebSocket URL for real-time updates
