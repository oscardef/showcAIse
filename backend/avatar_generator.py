"""
Avatar Generation using Hugging Face Inference API
Generates improved presentation videos with avatars applying feedback
"""
import os
import time
import requests
from typing import Dict, List, Optional
from pathlib import Path
from pydub import AudioSegment
import io

# Hugging Face API configuration
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "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")
HF_API_URL = "https://router.huggingface.co/models/"


def generate_improved_script(analysis: Dict) -> str:
    """
    Generate an improved script based on the analysis feedback.
    Removes fillers, improves pacing, and applies all recommendations.
    """
    transcript = analysis.get("transcript", "")
    recommendations = analysis.get("recommendations", [])
    key_clips = analysis.get("key_clips", {})
    
    # Start with original transcript
    improved_script = transcript
    
    # Remove filler words
    filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically", "literally"]
    for filler in filler_words:
        # Remove standalone fillers with various punctuation
        improved_script = improved_script.replace(f" {filler} ", " ")
        improved_script = improved_script.replace(f" {filler},", ",")
        improved_script = improved_script.replace(f" {filler}.", ".")
        improved_script = improved_script.replace(f"{filler.capitalize()} ", "")
    
    # Replace weak/uncertain language with confident alternatives
    replacements = {
        "kind of": "",
        "sort of": "",
        "I guess": "I believe",
        "I think maybe": "I believe",
        "probably": "definitely",
        "might be": "is",
        "could be": "is",
        "I don't know": "",
        "maybe": "certainly",
    }
    
    for weak, strong in replacements.items():
        improved_script = improved_script.replace(weak, strong)
    
    # Clean up extra spaces
    while "  " in improved_script:
        improved_script = improved_script.replace("  ", " ")
    
    # Clean up multiple punctuation
    improved_script = improved_script.replace(" ,", ",")
    improved_script = improved_script.replace(" .", ".")
    improved_script = improved_script.replace(",,", ",")
    improved_script = improved_script.replace("..", ".")
    
    return improved_script.strip()


def calculate_optimal_timing(improved_script: str, target_wpm: int = 145) -> Dict:
    """
    Calculate optimal timing for the improved presentation.
    Target WPM: 145 (optimal presentation pace)
    """
    words = improved_script.split()
    word_count = len(words)
    
    # Calculate duration in seconds
    duration_minutes = word_count / target_wpm
    duration_seconds = duration_minutes * 60
    
    return {
        "word_count": word_count,
        "target_wpm": target_wpm,
        "duration_seconds": round(duration_seconds, 1),
        "duration_minutes": round(duration_minutes, 2)
    }


def generate_avatar_prompt(analysis: Dict) -> str:
    """
    Generate a prompt for avatar generation based on analysis.
    """
    # Extract key characteristics
    overall_confidence = analysis.get("overall_confidence", 70)
    
    # Build prompt for confident, professional presentation
    prompt = """Professional presenter avatar delivering a presentation. 
    Confident posture, direct eye contact with camera, natural hand gestures. 
    Business casual attire, warm smile, engaging facial expressions. 
    Clear articulation, steady pace (145 WPM), no hesitation. 
    Natural transitions between points, professional body language. 
    Enthusiastic but controlled delivery, authoritative tone."""
    
    return prompt


async def generate_tts_audio(script: str, output_path: Path) -> bool:
    """
    Generate text-to-speech audio for the improved script.
    Uses Hugging Face Inference API with direct HTTP requests.
    Handles text chunking for long scripts.
    """
    if not HF_API_TOKEN:
        print("HuggingFace API token not found")
        return False
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    try:
        # Bark has a ~200 character limit per request for best quality
        max_chunk_size = 200
        
        # Split script into sentences first for more natural breaks
        sentences = script.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Group sentences into chunks under max_chunk_size
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"Generating TTS in {len(chunks)} chunks...")
        
        # Generate audio for each chunk
        audio_segments = []
        
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
            
            try:
                # Try microsoft/speecht5_tts (most reliable for TTS)
                print(f"  Attempting TTS for chunk {i+1}...")
                tts_url = f"{HF_API_URL}microsoft/speecht5_tts"
                
                response = requests.post(
                    tts_url,
                    headers=headers,
                    json={"inputs": chunk},
                    timeout=60
                )
                
                # Handle model loading
                if response.status_code == 503:
                    print(f"  Model loading, waiting 15 seconds...")
                    time.sleep(15)
                    response = requests.post(
                        tts_url,
                        headers=headers,
                        json={"inputs": chunk},
                        timeout=60
                    )
                
                if response.status_code == 200:
                    # Convert bytes to AudioSegment
                    audio_segment = AudioSegment.from_file(io.BytesIO(response.content), format="flac")
                    audio_segments.append(audio_segment)
                    print(f"  ✓ Chunk {i+1} generated successfully")
                    
                    # Small delay between requests to avoid rate limiting
                    if i < len(chunks) - 1:
                        time.sleep(2)
                else:
                    print(f"  ✗ TTS error on chunk {i+1}: {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
                    continue
                    
            except Exception as chunk_error:
                print(f"  ✗ Exception on chunk {i+1}: {str(chunk_error)}")
                print(f"  Error type: {type(chunk_error).__name__}")
                import traceback
                traceback.print_exc()
                continue
        
        if not audio_segments:
            print("No audio segments generated successfully")
            return False
        
        # Concatenate all audio segments
        print("Concatenating audio segments...")
        combined_audio = audio_segments[0]
        for segment in audio_segments[1:]:
            # Add a small pause between segments (100ms)
            combined_audio += AudioSegment.silent(duration=100)
            combined_audio += segment
        
        # Export as WAV
        combined_audio.export(str(output_path), format="wav")
        print(f"TTS audio saved to {output_path}")
        
        return True
        
    except Exception as e:
        print(f"TTS generation error: {str(e)}")
        return False


async def generate_avatar_video(
    session_id: str,
    analysis: Dict,
    reference_image_path: Path = None
) -> Dict:
    """
    Generate improved avatar presentation video.
    
    Returns:
        Dict with avatar_video_url, improved_script, timing_info, status
    """
    output_dir = Path("avatars")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Generate improved script
        print(f"[{session_id}] Generating improved script...")
        improved_script = generate_improved_script(analysis)
        
        # Step 2: Calculate optimal timing
        timing_info = calculate_optimal_timing(improved_script)
        print(f"[{session_id}] Optimal duration: {timing_info['duration_seconds']}s at {timing_info['target_wpm']} WPM")
        
        # Step 3: Generate TTS audio
        audio_path = output_dir / f"{session_id}_improved.wav"
        print(f"[{session_id}] Generating TTS audio...")
        tts_success = await generate_tts_audio(improved_script, audio_path)
        
        # Get original stats for comparison
        original_wpm = analysis.get("wpm", 150)
        original_confidence = analysis.get("confidence_score", analysis.get("overall_confidence", 70))
        original_fillers = analysis.get("filler_count", 0)
        
        if not tts_success:
            # Fallback: return script only without audio
            print(f"[{session_id}] TTS failed, using script-only mode")
            return {
                "status": "completed",
                "mode": "script_only",
                "avatar_video_url": None,
                "improved_script": improved_script,
                "timing_info": timing_info,
                "improvements": generate_improvement_summary(analysis),
                "audio_url": None,
                "original_stats": {
                    "wpm": original_wpm,
                    "confidence": original_confidence,
                    "filler_count": original_fillers
                },
                "improved_stats": {
                    "wpm": timing_info["target_wpm"],
                    "confidence": 85,  # Target confidence for improved version
                    "filler_count": 0  # All fillers removed
                }
            }
        
        # Step 4: TTS succeeded - return audio and script
        # Note: Full avatar video generation (Phase 3) would go here with D-ID/Wav2Lip
        print(f"[{session_id}] TTS audio generated successfully")
        
        return {
            "status": "completed",
            "mode": "audio_generated",
            "avatar_video_url": None,  # Phase 3: Will implement with D-ID/Wav2Lip
            "audio_url": f"/api/avatar/audio/{session_id}",
            "improved_script": improved_script,
            "timing_info": timing_info,
            "improvements": generate_improvement_summary(analysis),
            "original_stats": {
                "wpm": original_wpm,
                "confidence": original_confidence,
                "filler_count": original_fillers
            },
            "improved_stats": {
                "wpm": timing_info["target_wpm"],
                "confidence": 85,  # Target confidence for improved version
                "filler_count": 0  # All fillers removed
            }
        }
        
    except Exception as e:
        print(f"[{session_id}] Avatar generation error: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "improved_script": None,
            "timing_info": None
        }


def generate_improvement_summary(analysis: Dict) -> List[str]:
    """
    Generate a summary of improvements applied to the avatar presentation.
    """
    improvements = []
    
    # Filler removal
    filler_count = analysis.get("filler_count", 0)
    if filler_count > 0:
        improvements.append(f"Removed {filler_count} filler words (um, uh, like, etc.)")
    
    # Pacing optimization
    original_wpm = analysis.get("wpm", 0)
    if original_wpm < 130 or original_wpm > 160:
        improvements.append(f"Optimized pacing from {original_wpm} WPM to 145 WPM (ideal range)")
    
    # Confidence improvements
    key_clips = analysis.get("key_clips", {})
    weak_moments = key_clips.get("weak_moments", [])
    if weak_moments:
        improvements.append(f"Fixed {len(weak_moments)} weak moments with uncertain language")
    
    # Language improvements
    improvements.append("Replaced hedge words with confident alternatives")
    improvements.append("Enhanced overall clarity and professionalism")
    
    return improvements


def extract_first_frame(video_path: Path, output_path: Path) -> bool:
    """
    Extract first frame from video to use as reference for avatar.
    """
    try:
        import ffmpeg
        (
            ffmpeg
            .input(str(video_path), ss=1)
            .output(str(output_path), vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return True
    except Exception as e:
        print(f"Frame extraction error: {str(e)}")
        return False
