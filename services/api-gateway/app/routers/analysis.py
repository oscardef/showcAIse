from fastapi import APIRouter, HTTPException
import sys
sys.path.append('/app')

from shared.messaging import redis_client

router = APIRouter()


@router.get("/{session_id}/status")
async def get_analysis_status(session_id: str):
    """Get analysis status for a session."""
    status = redis_client.hgetall(f"session:{session_id}")
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": status.get("status", "unknown"),
        "progress": int(status.get("progress", 0)),
        "stage": status.get("stage", ""),
        "current_task": status.get("current_task", "")
    }


@router.get("/{session_id}/results")
async def get_analysis_results(session_id: str):
    """Get full analysis results for a session."""
    status = redis_client.hget(f"session:{session_id}", "status")
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")
    
    # Fetch results from Redis
    results = redis_client.hgetall(f"results:{session_id}")
    
    if not results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return {
        "session_id": session_id,
        "speech": {
            "wpm": int(results.get("speech_wpm", 0)),
            "fillerCount": int(results.get("speech_filler_count", 0)),
            "toneScore": int(results.get("speech_tone_score", 0)),
            "transcript": results.get("speech_transcript", "")
        },
        "vision": {
            "eyeContact": int(results.get("vision_eye_contact", 0)),
            "postureScore": int(results.get("vision_posture_score", 0)),
            "confidenceScore": int(results.get("vision_confidence_score", 0))
        },
        "recommendations": results.get("recommendations", "").split("|"),
        "avatarVideoUrl": results.get("avatar_video_url")
    }
