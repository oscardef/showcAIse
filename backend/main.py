"""
showcAIse Backend - FastAPI server for presentation analysis
"""
import os
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from analyzer import extract_audio, transcribe_audio, analyze_speech

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

# Create cloned_audio directory for voice cloning outputs
CLONED_AUDIO_DIR = Path("cloned_audio")
CLONED_AUDIO_DIR.mkdir(exist_ok=True)


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


@app.post("/api/voice-clone/{session_id}")
async def generate_voice_clone(session_id: str):
    """
    Generate improved presentation with voice cloning
    1. Extract audio from original video
    2. Generate improved script from analysis
    3. Clone voice and generate new audio
    """
    from voice_cloning import (
        extract_speaker_audio,
        generate_improved_script,
        clone_voice_and_generate_speech,
        get_improvement_summary
    )
    
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    
    session_data = sessions[session_id]
    analysis = session_data.get("results", {})
    
    # Check if already generated
    if session_data.get("cloned_audio_generated"):
        return {
            "status": "already_generated",
            "audio_url": f"/api/cloned-audio/{session_id}",
            "improved_script": session_data.get("improved_script"),
            "improvements": session_data.get("improvements")
        }
    
    try:
        # Paths
        video_path = VIDEOS_DIR / f"{session_id}.mp4"
        speaker_audio_path = CLONED_AUDIO_DIR / f"{session_id}_speaker.wav"
        cloned_audio_path = CLONED_AUDIO_DIR / f"{session_id}_cloned.wav"
        
        if not video_path.exists():
            raise HTTPException(404, "Original video not found")
        
        # Step 1: Extract speaker audio from video
        print(f"[{session_id}] Extracting speaker audio...")
        if not extract_speaker_audio(str(video_path), str(speaker_audio_path)):
            raise HTTPException(500, "Failed to extract audio from video")
        
        # Step 2: Generate improved script
        print(f"[{session_id}] Generating improved script...")
        improved_script = generate_improved_script(analysis)
        
        if not improved_script:
            raise HTTPException(500, "Failed to generate improved script")
        
        # Step 3: Clone voice and generate speech
        print(f"[{session_id}] Cloning voice and generating speech...")
        success = clone_voice_and_generate_speech(
            session_id=session_id,
            improved_script=improved_script,
            speaker_audio_path=str(speaker_audio_path),
            output_path=str(cloned_audio_path)
        )
        
        if not success:
            raise HTTPException(500, "Voice cloning failed")
        
        # Generate improvement summary
        improvements = get_improvement_summary(analysis, improved_script)
        
        # Update session data
        session_data["cloned_audio_generated"] = True
        session_data["improved_script"] = improved_script
        session_data["improvements"] = improvements
        session_data["cloned_audio_url"] = f"/api/cloned-audio/{session_id}"
        
        # Cleanup speaker audio (keep only the cloned output)
        speaker_audio_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "audio_url": f"/api/cloned-audio/{session_id}",
            "improved_script": improved_script,
            "improvements": improvements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{session_id}] Voice cloning error: {str(e)}")
        raise HTTPException(500, f"Voice cloning failed: {str(e)}")


@app.get("/api/cloned-audio/{session_id}")
async def get_cloned_audio(session_id: str):
    """Serve cloned audio file"""
    audio_path = CLONED_AUDIO_DIR / f"{session_id}_cloned.wav"
    if not audio_path.exists():
        raise HTTPException(404, "Cloned audio not found")
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting showcAIse API on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
