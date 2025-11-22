"""
Speech analysis module - Extract audio, transcribe, and analyze patterns
"""
import os
import re
import requests
from typing import Dict, List
import ffmpeg


def extract_audio(video_path: str, audio_path: str) -> None:
    """Extract audio from video using FFmpeg"""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        raise Exception(f"FFmpeg error: {e.stderr.decode()}")


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using Together AI's Whisper API
    Falls back to mock data if no API key
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    
    if not api_key:
        print("⚠️  No TOGETHER_API_KEY found, using mock transcript")
        return """Hello everyone, um, today I want to talk about, like, 
        our quarterly results. So, um, we achieved a fifteen percent growth, 
        which is, you know, pretty significant. Uh, the team worked really hard 
        and, like, we're seeing great traction in the market. Um, moving forward, 
        we plan to, uh, expand into new territories and, you know, scale our operations."""
    
    try:
        print("🎤 Transcribing with Together AI Whisper...")
        
        # Together AI uses OpenAI-compatible API format
        with open(audio_path, "rb") as audio_file:
            response = requests.post(
                "https://api.together.xyz/v1/audio/transcriptions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
                files={
                    "file": audio_file,
                },
                data={
                    "model": "openai/whisper-large-v3",
                }
            )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("text", "")
        else:
            print(f"⚠️  Together AI error: {response.status_code} - {response.text}")
            raise Exception(f"API error: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Transcription error: {e}, using mock transcript")
        return """Hello everyone, um, today I want to talk about our project. 
        The results have been, like, really good and we're excited about the future."""


def analyze_speech(transcript: str) -> Dict:
    """
    Analyze speech patterns: filler words, pacing, recommendations
    """
    # Common filler words
    fillers = [
        r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b',
        r'\bso\b', r'\bactually\b', r'\bbasically\b', r'\bliterally\b'
    ]
    
    # Count filler words
    filler_count = 0
    for filler in fillers:
        filler_count += len(re.findall(filler, transcript.lower()))
    
    # Word count and speaking pace
    words = transcript.split()
    word_count = len(words)
    
    # Assume 1 word per 0.4 seconds (average speaking pace)
    duration_minutes = (word_count * 0.4) / 60
    wpm = int(word_count / duration_minutes) if duration_minutes > 0 else 150
    
    # Generate recommendations
    recommendations = []
    
    if filler_count > word_count * 0.05:  # More than 5% fillers
        recommendations.append(
            "🎯 Reduce filler words: Try pausing instead of using 'um' or 'like'"
        )
    
    if wpm > 160:
        recommendations.append(
            "🐢 Slow down: You're speaking quite fast. Aim for 130-150 words per minute"
        )
    elif wpm < 120:
        recommendations.append(
            "⚡ Pick up the pace: Speaking a bit faster will keep your audience engaged"
        )
    
    if word_count < 100:
        recommendations.append(
            "📝 Elaborate more: Add examples and details to make your presentation richer"
        )
    
    if not any(q in transcript for q in ['?', 'question', 'what', 'how', 'why']):
        recommendations.append(
            "❓ Engage your audience: Try asking rhetorical questions"
        )
    
    if recommendations == []:
        recommendations.append(
            "✨ Great job! Your speaking pace and word choice are excellent"
        )
    
    return {
        "transcript": transcript,
        "word_count": word_count,
        "filler_count": filler_count,
        "wpm": wpm,
        "duration_minutes": round(duration_minutes, 1),
        "recommendations": recommendations
    }
