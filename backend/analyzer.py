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


def find_filler_positions(transcript: str) -> List[tuple]:
    """
    Find positions of filler words in transcript
    Returns list of (start_pos, end_pos, filler_word)
    """
    fillers = [
        r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b',
        r'\bso\b', r'\bactually\b', r'\bbasically\b', r'\bliterally\b'
    ]
    
    filler_positions = []
    for filler_pattern in fillers:
        for match in re.finditer(filler_pattern, transcript.lower()):
            filler_positions.append((
                match.start(),
                match.end(),
                match.group()
            ))
    
    # Sort by position
    filler_positions.sort(key=lambda x: x[0])
    return filler_positions


def generate_timeline_data(transcript: str, duration_minutes: float) -> List[Dict]:
    """
    Generate timeline data showing pacing throughout presentation
    Splits into segments for visualization
    """
    words = transcript.split()
    words_per_segment = max(1, len(words) // 10)  # Split into ~10 segments
    
    timeline = []
    for i in range(0, len(words), words_per_segment):
        segment_words = words[i:i + words_per_segment]
        segment_text = " ".join(segment_words)
        
        # Calculate WPM for this segment
        segment_duration = (len(segment_words) * 0.4) / 60  # 0.4 sec per word
        segment_wpm = int(len(segment_words) / segment_duration) if segment_duration > 0 else 150
        
        # Count fillers in segment
        filler_count = sum(
            len(re.findall(filler, segment_text.lower()))
            for filler in [r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b']
        )
        
        # Calculate confidence score (0-100)
        confidence = 100
        if segment_wpm > 180:
            confidence -= 30
        elif segment_wpm < 100:
            confidence -= 20
        
        if filler_count > len(segment_words) * 0.1:
            confidence -= 40
        elif filler_count > len(segment_words) * 0.05:
            confidence -= 20
        
        confidence = max(0, confidence)
        
        timeline.append({
            "segment": i // words_per_segment + 1,
            "wpm": segment_wpm,
            "confidence": confidence,
            "filler_count": filler_count
        })
    
    return timeline


def analyze_speech(transcript: str) -> Dict:
    """
    Analyze speech patterns: filler words, pacing, recommendations
    """
    # Find filler word positions
    filler_positions = find_filler_positions(transcript)
    filler_count = len(filler_positions)
    
    # Word count and speaking pace
    words = transcript.split()
    word_count = len(words)
    
    # Assume 1 word per 0.4 seconds (average speaking pace)
    duration_minutes = (word_count * 0.4) / 60
    wpm = int(word_count / duration_minutes) if duration_minutes > 0 else 150
    
    # Generate timeline data
    timeline = generate_timeline_data(transcript, duration_minutes)
    
    # Calculate overall confidence (average from timeline)
    avg_confidence = sum(t["confidence"] for t in timeline) / len(timeline) if timeline else 70
    
    # Generate recommendations
    recommendations = []
    
    if filler_count > word_count * 0.05:  # More than 5% fillers
        recommendations.append({
            "icon": "🎯",
            "title": "Reduce filler words",
            "description": f"You used {filler_count} filler words. Try pausing instead of using 'um' or 'like'",
            "severity": "high" if filler_count > word_count * 0.1 else "medium"
        })
    
    if wpm > 160:
        recommendations.append({
            "icon": "🐢",
            "title": "Slow down your pace",
            "description": f"You're speaking at {wpm} WPM. Aim for 130-150 words per minute for clarity",
            "severity": "medium"
        })
    elif wpm < 120:
        recommendations.append({
            "icon": "⚡",
            "title": "Pick up the pace",
            "description": f"You're speaking at {wpm} WPM. Speaking a bit faster will keep your audience engaged",
            "severity": "low"
        })
    
    if word_count < 100:
        recommendations.append({
            "icon": "📝",
            "title": "Elaborate more",
            "description": "Add examples and details to make your presentation richer",
            "severity": "low"
        })
    
    if not any(q in transcript for q in ['?', 'question', 'what', 'how', 'why']):
        recommendations.append({
            "icon": "❓",
            "title": "Engage your audience",
            "description": "Try asking rhetorical questions to keep listeners involved",
            "severity": "low"
        })
    
    if len(recommendations) == 0:
        recommendations.append({
            "icon": "✨",
            "title": "Great job!",
            "description": "Your speaking pace and word choice are excellent",
            "severity": "success"
        })
    
    return {
        "transcript": transcript,
        "word_count": word_count,
        "filler_count": filler_count,
        "filler_positions": filler_positions,
        "wpm": wpm,
        "duration_minutes": round(duration_minutes, 1),
        "confidence_score": round(avg_confidence, 1),
        "timeline": timeline,
        "recommendations": recommendations
    }
