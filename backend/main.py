"""
showcAIse Backend - FastAPI server for presentation analysis
"""
import os
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from analyzer import extract_audio, transcribe_audio, analyze_speech
from avatar_generator import generate_avatar_video, extract_first_frame

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="showcAIse API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (replace with DB for production)
sessions: Dict[str, dict] = {}

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Create videos directory for serving video files
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)

# Create avatars directory for generated content
AVATARS_DIR = Path("avatars")
AVATARS_DIR.mkdir(exist_ok=True)


@app.get("/")
async def root():
    return {
        "service": "showcAIse API",
        "status": "running",
        "endpoints": ["/api/upload", "/api/session/{session_id}"]
    }


@app.post("/api/upload")
async def upload_video(video: UploadFile):
    """
    Upload video and analyze presentation
    Returns analysis results immediately
    """
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded video
    video_path = UPLOAD_DIR / f"{session_id}.mp4"
    stored_video_path = VIDEOS_DIR / f"{session_id}.mp4"
    audio_path = UPLOAD_DIR / f"{session_id}.wav"
    
    try:
        # Save video file
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        # Copy to videos directory for serving
        import shutil
        shutil.copy(str(video_path), str(stored_video_path))
        
        # Extract audio
        print(f"[{session_id}] Extracting audio...")
        extract_audio(str(video_path), str(audio_path))
        
        # Transcribe
        print(f"[{session_id}] Transcribing...")
        transcript = transcribe_audio(str(audio_path))
        
        # Analyze speech
        print(f"[{session_id}] Analyzing speech patterns...")
        analysis = analyze_speech(transcript)
        
        # Store results with video reference
        session_data = {
            "session_id": session_id,
            "status": "completed",
            "video_url": f"/api/video/{session_id}",
            "results": analysis
        }
        sessions[session_id] = session_data
        
        # Cleanup temporary files
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)
        
        return session_data
        
    except Exception as e:
        # Cleanup on error
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get analysis results for a session"""
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    return sessions[session_id]


@app.get("/api/video/{session_id}")
async def get_video(session_id: str):
    """Serve video file for playback with timestamp navigation"""
    video_path = VIDEOS_DIR / f"{session_id}.mp4"
    if not video_path.exists():
        raise HTTPException(404, "Video not found")
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        headers={"Accept-Ranges": "bytes"}
    )


@app.post("/api/avatar/generate/{session_id}")
async def generate_avatar(session_id: str, background_tasks: BackgroundTasks):
    """
    Generate improved avatar presentation based on analysis feedback.
    This creates a "perfect" version applying all recommendations.
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    
    session_data = sessions[session_id]
    analysis = session_data.get("results", {})
    
    # Extract reference frame from original video
    video_path = VIDEOS_DIR / f"{session_id}.mp4"
    reference_image = AVATARS_DIR / f"{session_id}_reference.jpg"
    
    if video_path.exists():
        extract_first_frame(video_path, reference_image)
    
    # Generate avatar video (async)
    print(f"[{session_id}] Starting avatar generation...")
    avatar_result = await generate_avatar_video(session_id, analysis, reference_image)
    
    # Store avatar data in session
    session_data["avatar"] = avatar_result
    sessions[session_id] = session_data
    
    return avatar_result


@app.get("/api/avatar/{session_id}")
async def get_avatar_status(session_id: str):
    """Get avatar generation status and results"""
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    
    session_data = sessions[session_id]
    avatar_data = session_data.get("avatar")
    
    if not avatar_data:
        raise HTTPException(404, "Avatar not generated yet. Call /api/avatar/generate first.")
    
    return avatar_data


@app.get("/api/avatar/audio/{session_id}")
async def get_avatar_audio(session_id: str):
    """Serve generated TTS audio for improved presentation"""
    audio_path = AVATARS_DIR / f"{session_id}_improved.wav"
    if not audio_path.exists():
        raise HTTPException(404, "Avatar audio not found")
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting showcAIse API on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
