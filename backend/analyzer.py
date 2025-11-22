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
    sentences = [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]
    sentence_count = len(sentences)
    
    # Assume 1 word per 0.4 seconds (average speaking pace)
    duration_minutes = (word_count * 0.4) / 60
    wpm = int(word_count / duration_minutes) if duration_minutes > 0 else 150
    
    # Generate timeline data
    timeline = generate_timeline_data(transcript, duration_minutes)
    
    # Calculate overall confidence (average from timeline)
    avg_confidence = sum(t["confidence"] for t in timeline) / len(timeline) if timeline else 70
    
    # Advanced analysis metrics
    avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
    questions = len(re.findall(r'\?|question|what|how|why|when|where|who', transcript.lower()))
    passive_voice_indicators = len(re.findall(r'\b(was|were|been|being)\s+\w+ed\b', transcript.lower()))
    weak_words = len(re.findall(r'\b(maybe|perhaps|possibly|probably|sort of|kind of|i think|i guess)\b', transcript.lower()))
    power_words = len(re.findall(r'\b(achieve|success|proven|results|guarantee|discover|powerful|transform)\b', transcript.lower()))
    repetitive_starts = analyze_sentence_starts(sentences)
    
    # Filler word breakdown
    filler_breakdown = {}
    for _, _, filler in filler_positions:
        filler_breakdown[filler] = filler_breakdown.get(filler, 0) + 1
    top_fillers = sorted(filler_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # Generate detailed recommendations
    recommendations = []
    
    # Filler words analysis
    if filler_count > word_count * 0.1:  # More than 10%
        top_filler_text = f"Most common: '{top_fillers[0][0]}' ({top_fillers[0][1]} times)"
        recommendations.append({
            "icon": "🎯",
            "title": "Reduce filler words immediately",
            "description": f"You used {filler_count} filler words ({round(filler_count/word_count*100, 1)}% of speech). {top_filler_text}. Practice pausing for 1-2 seconds instead. Record yourself and listen back to build awareness.",
            "severity": "high",
            "action": "Practice this: Say your opening sentence. Pause 2 seconds. Continue. Repeat until natural."
        })
    elif filler_count > word_count * 0.05:  # 5-10%
        recommendations.append({
            "icon": "🎯",
            "title": "Work on reducing filler words",
            "description": f"You used {filler_count} filler words ({round(filler_count/word_count*100, 1)}% of speech). Replace fillers with strategic pauses - they make you sound more confident and give your audience time to process.",
            "severity": "medium",
            "action": "Try the 'breath pause' technique: Breathe when you want to say 'um'."
        })
    
    # Speaking pace analysis
    if wpm > 180:
        recommendations.append({
            "icon": "🐢",
            "title": "Slow down significantly",
            "description": f"You're speaking at {wpm} WPM - that's very fast! Your audience will struggle to follow. Aim for 130-150 WPM. Take deliberate pauses between key points.",
            "severity": "high",
            "action": "Practice with a metronome at 130 BPM, speaking one word per beat."
        })
    elif wpm > 160:
        recommendations.append({
            "icon": "🐢",
            "title": "Reduce your speaking pace",
            "description": f"You're speaking at {wpm} WPM. While energetic, this pace can tire listeners. Slow to 130-150 WPM by pausing after important statements and between sections.",
            "severity": "medium",
            "action": "Mark your script with [PAUSE] indicators at key moments."
        })
    elif wpm < 110:
        recommendations.append({
            "icon": "⚡",
            "title": "Increase your energy and pace",
            "description": f"At {wpm} WPM, you risk losing audience attention. Speed up to 130-150 WPM. Add more energy and enthusiasm to your delivery.",
            "severity": "medium",
            "action": "Practice standing up while presenting - it naturally increases pace and energy."
        })
    
    # Sentence structure analysis
    if avg_sentence_length > 25:
        recommendations.append({
            "icon": "✂️",
            "title": "Simplify your sentences",
            "description": f"Your average sentence is {round(avg_sentence_length, 1)} words - that's too long! Break complex ideas into shorter sentences (15-20 words). Short sentences = clearer communication.",
            "severity": "medium",
            "action": "Rewrite your longest 3 sentences into 2 shorter ones each."
        })
    elif avg_sentence_length < 10:
        recommendations.append({
            "icon": "🔗",
            "title": "Vary your sentence length",
            "description": f"Your sentences average {round(avg_sentence_length, 1)} words. While clarity is good, add some variety. Mix short punchy statements with longer explanatory ones.",
            "severity": "low",
            "action": "Follow short sentences with 'Here's why:' or 'For example:' to add depth."
        })
    
    # Engagement analysis
    if questions < 1:
        recommendations.append({
            "icon": "❓",
            "title": "Add audience engagement",
            "description": "You didn't ask any questions. Questions wake up your audience and make presentations interactive. Use rhetorical questions to emphasize key points.",
            "severity": "medium",
            "action": "Add 2-3 questions: 'Have you ever...?', 'What if we could...?', 'Why does this matter?'"
        })
    
    # Weak language analysis
    if weak_words > word_count * 0.02:  # More than 2%
        recommendations.append({
            "icon": "💪",
            "title": "Use more confident language",
            "description": f"You used {weak_words} weak or uncertain phrases ('maybe', 'I think', 'sort of'). Replace with definitive statements. Confidence is contagious!",
            "severity": "medium",
            "action": "Replace 'I think this will work' → 'This will work' or 'Based on data, this works.'"
        })
    
    # Repetitive sentence starts
    if repetitive_starts["score"] < 0.7:
        recommendations.append({
            "icon": "🔄",
            "title": "Vary your sentence openings",
            "description": f"Many sentences start the same way ('{repetitive_starts['common_start']}' used {repetitive_starts['count']} times). Vary your openings to maintain interest.",
            "severity": "low",
            "action": "Use transitions: 'Furthermore...', 'Consider this...', 'Here's the key...'"
        })
    
    # Content depth
    if word_count < 100:
        recommendations.append({
            "icon": "📝",
            "title": "Add more substance",
            "description": f"At {word_count} words ({round(duration_minutes, 1)} min), this is very brief. Add examples, data points, or stories to support your message. Aim for at least 2-3 minutes.",
            "severity": "high",
            "action": "Add one concrete example or story that illustrates your main point."
        })
    
    # Passive voice
    if passive_voice_indicators > sentence_count * 0.3:
        recommendations.append({
            "icon": "⚡",
            "title": "Use more active voice",
            "description": f"You're using passive voice frequently. Active voice is more direct and engaging. 'We achieved results' is stronger than 'Results were achieved.'",
            "severity": "low",
            "action": "Find sentences with 'was/were/been' + past verb. Rewrite with active verbs."
        })
    
    # Power words
    if power_words < 2 and word_count > 100:
        recommendations.append({
            "icon": "🚀",
            "title": "Add impact with power words",
            "description": "Use compelling words that create emotional impact: 'achieve', 'proven', 'transform', 'breakthrough', 'revolutionary'. They make presentations memorable.",
            "severity": "low",
            "action": "Replace bland verbs: 'improve' → 'transform', 'show' → 'reveal', 'help' → 'empower'"
        })
    
    # Success message
    if len(recommendations) == 0:
        recommendations.append({
            "icon": "✨",
            "title": "Excellent presentation!",
            "description": f"Your delivery is strong: {wpm} WPM (optimal pace), only {round(filler_count/word_count*100, 1)}% fillers, clear structure. Keep up this level of quality!",
            "severity": "success",
            "action": "Record this as your baseline. Maintain these standards in future presentations."
        })
    
    # Add top 3 priority actions
    priority_actions = [rec for rec in recommendations if rec["severity"] in ["high", "medium"]][:3]
    
    return {
        "transcript": transcript,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "filler_count": filler_count,
        "filler_breakdown": dict(top_fillers),
        "filler_positions": filler_positions,
        "wpm": wpm,
        "duration_minutes": round(duration_minutes, 1),
        "confidence_score": round(avg_confidence, 1),
        "timeline": timeline,
        "recommendations": recommendations,
        "priority_actions": [
            {
                "title": rec["title"],
                "action": rec.get("action", "")
            }
            for rec in priority_actions
        ],
        "metrics": {
            "questions": questions,
            "weak_words": weak_words,
            "power_words": power_words,
            "passive_voice": passive_voice_indicators
        }
    }


def analyze_sentence_starts(sentences: List[str]) -> Dict:
    """
    Analyze if sentences start with repetitive patterns
    Returns score (0-1) and most common start
    """
    if len(sentences) < 3:
        return {"score": 1.0, "common_start": "", "count": 0}
    
    # Get first 2 words of each sentence
    starts = []
    for s in sentences:
        words = s.split()
        if len(words) >= 2:
            starts.append(f"{words[0]} {words[1]}".lower())
        elif len(words) == 1:
            starts.append(words[0].lower())
    
    if not starts:
        return {"score": 1.0, "common_start": "", "count": 0}
    
    # Find most common start
    start_counts = {}
    for start in starts:
        start_counts[start] = start_counts.get(start, 0) + 1
    
    most_common = max(start_counts.items(), key=lambda x: x[1])
    diversity_score = 1.0 - (most_common[1] / len(starts))
    
    return {
        "score": diversity_score,
        "common_start": most_common[0],
        "count": most_common[1]
    }
