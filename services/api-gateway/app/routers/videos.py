from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import uuid
import aiohttp
import sys
sys.path.append('/app')

from shared.storage import storage_client
from shared.messaging import redis_client

router = APIRouter()


@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    """Upload video file and create analysis session."""
    
    # Validate file type
    if not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Save video to storage
    object_name = f"videos/{session_id}/{video.filename}"
    
    try:
        # Read file content
        content = await video.read()
        
        # Upload to MinIO
        storage_client.upload_bytes(
            object_name,
            content,
            content_type=video.content_type
        )
        
        # Store session metadata in Redis
        redis_client.hset(
            f"session:{session_id}",
            mapping={
                "video_path": object_name,
                "filename": video.filename,
                "status": "uploaded",
                "content_type": video.content_type
            }
        )
        
        # Trigger video processing (call video-processing service)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://video-processing:8000/process",
                json={"session_id": session_id, "video_path": object_name}
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=500, detail="Failed to start processing")
        
        return {
            "session_id": session_id,
            "status": "processing",
            "message": "Video uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{session_id}/status")
async def get_video_status(session_id: str):
    """Get video processing status."""
    status = redis_client.hget(f"session:{session_id}", "status")
    
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session_id": session_id, "status": status}
