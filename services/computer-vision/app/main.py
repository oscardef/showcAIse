from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import sys
sys.path.append('/app')

app = FastAPI(title="Computer Vision Service")


class AnalyzeRequest(BaseModel):
    session_id: str
    frame_paths: List[str]


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "computer-vision"}


@app.post("/analyze")
async def analyze_frames(request: AnalyzeRequest):
    """Analyze video frames for eye contact, posture, etc."""
    # TODO: Implement CV analysis using MediaPipe and HuggingFace models
    # - Eye contact detection (gaze estimation)
    # - Head posture analysis
    # - Confidence indicators
    
    return {
        "session_id": request.session_id,
        "status": "analyzed",
        "results": {
            "eye_contact": 65,
            "posture_score": 80,
            "confidence_score": 72
        }
    }
