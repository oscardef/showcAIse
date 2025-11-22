"""
showcAIse Backend - FastAPI server for presentation analysis
"""
import os
import uuid
from pathlib import Path
from typing import Dict
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from analyzer import * 

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
    Returns analysis results immediately, including landmarks.json content
    """
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save uploaded video
    video_path = UPLOAD_DIR / f"{session_id}.mp4"
    audio_path = UPLOAD_DIR / f"{session_id}.wav"
    landmarks_path = UPLOAD_DIR / f"{session_id}_landmarks.json"
    
    try:
        # Save video file
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        # Extract audio
        print(f"[{session_id}] Extracting audio...")
        extract_audio(str(video_path), str(audio_path))
        
        # Transcribe
        print(f"[{session_id}] Transcribing...")
        transcript = transcribe_audio(str(audio_path))
        
        # Analyze speech
        print(f"[{session_id}] Analyzing speech patterns...")
        analysis = analyze_speech(transcript)
        
        
        # Analyze video and save landmarks.json
        print(f"[{session_id}] Analyzing video for landmarks...")
        landmarks = analyze_video(str(video_path))
        #save_feedback_to_file(landmarks.get("body_language", {}), f"body_language_feedback.txt")
        # Save landmarks to file
        import json
        with open(landmarks_path, "w") as lf:
            json.dump(landmarks, lf)
        
        # Read landmarks.json content
        with open(landmarks_path, "r") as lf:
            landmarks_json = json.load(lf)
        
        summary = []
        for i, frame in enumerate(landmarks_json):
            if i % 5 != 0: continue  # downsample to 5–6 fps is enough
            p = frame['pose_landmarks']
            f = frame['face_landmarks']

        # Example metrics we care about
        left_shoulder  = p[11]
        right_shoulder = p[12]
        left_hip       = p[23]
        right_hip      = p[24]
        nose           = p[0]
        mid_hip = {'x': (left_hip['x']+right_hip['x'])/2,
                    'y': (left_hip['y']+right_hip['y'])/2,
                    'z': (left_hip['z']+right_hip['z'])/2}

        summary.append({
            "frame": i,
            "timestamp_sec": i / 30.0,
            "shoulder_width": dist(left_shoulder, right_shoulder),
            "hip_width": dist(left_hip, right_hip),
            "body_tilt_deg": angle_at(mid_hip, left_shoulder, right_shoulder),
            "leaning_forward": nose['z'],  # negative = closer to camera
            "left_hand_raise": p[15]['y'],  # lower y = higher on screen
            "right_hand_raise": p[16]['y'],
            "openness_score": dist(left_shoulder, left_hip) + dist(right_shoulder, right_hip),  # rough proxy
            "face_visibility": f[0]['visibility'] if f else 0,
        })

        text_for_llm = json.dumps(summary, indent=2)

        with open('text_for_llm', "w", encoding="utf-8") as f:
            json.dump(text_for_llm, f, ensure_ascii=False, indent=2)
            
        # Store results
        session_data = {
            "session_id": session_id,
            "status": "completed",
            "results": analysis,
            "landmarks": landmarks_json
        }
        sessions[session_id] = session_data
        
        # Cleanup files
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)
        landmarks_path.unlink(missing_ok=True)
        
        return session_data
        
    except Exception as e:
        # Cleanup on error
        video_path.unlink(missing_ok=True)
        audio_path.unlink(missing_ok=True)
        landmarks_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Analysis failed: {str(e)}")

        
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



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting showcAIse API on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
