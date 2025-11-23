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

# Demo audio file path (for demo purposes)
DEMO_AUDIO_PATH = CLONED_AUDIO_DIR / "demo_cloned.wav"

# Create cloned_video directory for video generation outputs
CLONED_VIDEO_DIR = Path("cloned_video")
CLONED_VIDEO_DIR.mkdir(exist_ok=True)

# Demo video file path (for demo purposes)
DEMO_VIDEO_PATH = CLONED_VIDEO_DIR / "demo_video.mp4"


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
async def generate_voice_clone(session_id: str, use_demo: bool = False):
    """
    Generate improved presentation with voice cloning
    1. Extract audio from original video
    2. Generate improved script from analysis
    3. Clone voice and generate new audio
    
    Args:
        session_id: The session ID for the analysis
        use_demo: If True, use the hardcoded demo audio file instead of generating
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
            "improvements": session_data.get("improvements"),
            "demo_mode": session_data.get("demo_mode", False)
        }
    
    # If demo mode is enabled and demo file exists, use it
    if use_demo and DEMO_AUDIO_PATH.exists():
        print(f"[{session_id}] Using demo audio file...")
        
        # Generate improved script for demo purposes
        improved_script = generate_improved_script(analysis)
        improvements = get_improvement_summary(analysis, improved_script)
        
        # Update session data to point to demo audio
        session_data["cloned_audio_generated"] = True
        session_data["improved_script"] = improved_script
        session_data["improvements"] = improvements
        session_data["cloned_audio_url"] = "/api/cloned-audio/demo"
        session_data["demo_mode"] = True
        
        return {
            "status": "success",
            "audio_url": "/api/cloned-audio/demo",
            "improved_script": improved_script,
            "improvements": improvements,
            "demo_mode": True
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
        session_data["demo_mode"] = False
        
        # Cleanup speaker audio (keep only the cloned output)
        speaker_audio_path.unlink(missing_ok=True)
        
        return {
            "status": "success",
            "audio_url": f"/api/cloned-audio/{session_id}",
            "improved_script": improved_script,
            "improvements": improvements,
            "demo_mode": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{session_id}] Voice cloning error: {str(e)}")
        raise HTTPException(500, f"Voice cloning failed: {str(e)}")


@app.get("/api/cloned-audio/{session_id}")
async def get_cloned_audio(session_id: str):
    """Serve cloned audio file (or demo audio if session_id is 'demo')"""
    # Special handling for demo audio
    if session_id == "demo":
        if not DEMO_AUDIO_PATH.exists():
            raise HTTPException(404, "Demo audio not found. Please place demo_cloned.wav in backend/cloned_audio/")
        return FileResponse(
            path=str(DEMO_AUDIO_PATH),
            media_type="audio/wav"
        )
    
    # Regular session audio
    audio_path = CLONED_AUDIO_DIR / f"{session_id}_cloned.wav"
    if not audio_path.exists():
        raise HTTPException(404, "Cloned audio not found")
    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav"
    )


@app.post("/api/video-generate/{session_id}")
async def generate_video(session_id: str, use_demo: bool = False):
    """
    Generate video from improved audio and original video
    
    Args:
        session_id: The session ID for the analysis
        use_demo: If True, use the hardcoded demo video file instead of generating
    """
    if session_id not in sessions:
        raise HTTPException(404, "Session not found")
    
    session_data = sessions[session_id]
    
    # Check if already generated
    if session_data.get("video_generated"):
        return {
            "status": "already_generated",
            "video_url": session_data.get("cloned_video_url"),
            "demo_mode": session_data.get("video_demo_mode", False)
        }
    
    # If demo mode is enabled and demo file exists, use it
    if use_demo and DEMO_VIDEO_PATH.exists():
        print(f"[{session_id}] Using demo video file...")
        
        # Update session data to point to demo video
        session_data["video_generated"] = True
        session_data["cloned_video_url"] = "/api/cloned-video/demo"
        session_data["video_demo_mode"] = True
        
        return {
            "status": "success",
            "video_url": "/api/cloned-video/demo",
            "demo_mode": True
        }
    
    try:
        # Check if audio was generated
        if not session_data.get("cloned_audio_generated"):
            raise HTTPException(400, "Please generate voice clone first")
        
        # For now, return success with a placeholder
        # Video generation would combine cloned audio with video editing
        session_data["video_generated"] = True
        session_data["cloned_video_url"] = "/api/cloned-video/demo"
        session_data["video_demo_mode"] = False
        
        return {
            "status": "success",
            "video_url": "/api/cloned-video/demo",
            "demo_mode": False,
            "message": "Video generation coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[{session_id}] Video generation error: {str(e)}")
        raise HTTPException(500, f"Video generation failed: {str(e)}")


@app.get("/api/cloned-video/{session_id}")
async def get_cloned_video(session_id: str):
    """Serve cloned video file (or demo video if session_id is 'demo')"""
    # Special handling for demo video
    if session_id == "demo":
        if not DEMO_VIDEO_PATH.exists():
            raise HTTPException(404, "Demo video not found. Please place demo_video.mp4 in backend/cloned_video/")
        return FileResponse(
            path=str(DEMO_VIDEO_PATH),
            media_type="video/mp4"
        )
    
    # Regular session video
    video_path = CLONED_VIDEO_DIR / f"{session_id}_cloned.mp4"
    if not video_path.exists():
        raise HTTPException(404, "Cloned video not found")
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting showcAIse API on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
