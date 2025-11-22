# showcAIse API Documentation

## Overview

The showcAIse API provides endpoints for uploading presentation videos, tracking analysis progress, and retrieving results.

Base URL: `http://localhost:8000`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /api/v1/auth/login
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/register
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Video Upload

#### POST /api/v1/videos/upload
Upload a presentation video for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `video` (file)

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "message": "Video uploaded successfully"
}
```

#### GET /api/v1/videos/{session_id}/status
Get the status of a video upload.

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing"
}
```

### Analysis

#### GET /api/v1/analysis/{session_id}/status
Get the current analysis status and progress.

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": 65,
  "stage": "speech",
  "current_task": "Analyzing speech patterns..."
}
```

#### GET /api/v1/analysis/{session_id}/results
Get the complete analysis results (only available when analysis is complete).

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "speech": {
    "wpm": 150,
    "fillerCount": 5,
    "toneScore": 75,
    "transcript": "Full transcript..."
  },
  "vision": {
    "eyeContact": 65,
    "postureScore": 80,
    "confidenceScore": 72
  },
  "recommendations": [
    "Reduce filler words by 40%",
    "Maintain eye contact more consistently"
  ],
  "avatarVideoUrl": "https://..."
}
```

### WebSocket

#### WS /ws/{session_id}
Connect to receive real-time analysis updates.

**Message Types:**

1. **analysis_progress**
```json
{
  "stage": "speech",
  "progress": 50,
  "currentTask": "Transcribing audio...",
  "status": "processing"
}
```

2. **analysis_complete**
```json
{
  "status": "completed",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

3. **analysis_error**
```json
{
  "error": "Error message",
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Status Codes

- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are limited to 60 requests per minute per IP address.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```
