import os
import tempfile
import ffmpeg
from celery import Task
import sys
sys.path.append('/app')

from shared.messaging import celery_app, redis_client
from shared.storage import storage_client


@celery_app.task(bind=True)
def process_video_task(self: Task, session_id: str, video_path: str):
    """Process video: extract audio and frames."""
    
    try:
        # Update status
        redis_client.hset(f"session:{session_id}", "status", "processing")
        redis_client.hset(f"session:{session_id}", "stage", "processing")
        redis_client.hset(f"session:{session_id}", "progress", "10")
        
        # Download video from storage
        with tempfile.TemporaryDirectory() as tmpdir:
            video_file = os.path.join(tmpdir, "input.mp4")
            audio_file = os.path.join(tmpdir, "audio.wav")
            frames_dir = os.path.join(tmpdir, "frames")
            os.makedirs(frames_dir)
            
            # Download video
            storage_client.download_file(video_path, video_file)
            
            # Extract audio
            ffmpeg.input(video_file).output(audio_file, acodec='pcm_s16le', ar='16000').run()
            
            # Upload audio
            audio_path = f"audio/{session_id}/audio.wav"
            storage_client.upload_file(audio_path, audio_file, "audio/wav")
            
            redis_client.hset(f"session:{session_id}", "audio_path", audio_path)
            redis_client.hset(f"session:{session_id}", "progress", "30")
            
            # Extract frames (2 fps)
            ffmpeg.input(video_file).output(
                os.path.join(frames_dir, "frame_%04d.jpg"),
                vf='fps=2'
            ).run()
            
            # Upload frames
            frame_files = sorted(os.listdir(frames_dir))
            frame_paths = []
            for frame_file in frame_files:
                frame_path = f"frames/{session_id}/{frame_file}"
                storage_client.upload_file(
                    frame_path,
                    os.path.join(frames_dir, frame_file),
                    "image/jpeg"
                )
                frame_paths.append(frame_path)
            
            redis_client.hset(f"session:{session_id}", "frame_paths", ",".join(frame_paths))
            redis_client.hset(f"session:{session_id}", "progress", "50")
            redis_client.hset(f"session:{session_id}", "status", "processed")
            
        return {"status": "success", "session_id": session_id}
        
    except Exception as e:
        redis_client.hset(f"session:{session_id}", "status", "failed")
        redis_client.hset(f"session:{session_id}", "error", str(e))
        raise
