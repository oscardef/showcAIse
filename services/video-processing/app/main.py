from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('/app')

from app.tasks import process_video_task

app = FastAPI(title="Video Processing Service")


class ProcessRequest(BaseModel):
    session_id: str
    video_path: str


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-processing"}


@app.post("/process")
async def process_video(request: ProcessRequest):
    """Start video processing task."""
    try:
        # Trigger Celery task
        task = process_video_task.delay(request.session_id, request.video_path)
        
        return {
            "session_id": request.session_id,
            "task_id": task.id,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
