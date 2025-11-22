"""
Speech analysis module - Extract audio, transcribe, and analyze patterns
"""
import os
import re
import requests
from typing import Dict, List, Tuple
import ffmpeg
from transformers import pipeline


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


# Initialize sentiment analyzer globally (lazy loading)
_sentiment_analyzer = None

def get_sentiment_analyzer():
    """Lazy load sentiment analyzer"""
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            print("🎭 Loading sentiment analysis model...")
            _sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            print("✅ Sentiment model loaded")
        except Exception as e:
            print(f"⚠️  Failed to load sentiment model: {e}")
            _sentiment_analyzer = None
    return _sentiment_analyzer


def analyze_sentiment_and_tone(transcript: str, words: List[str]) -> Dict:
    """
    Enhanced sentiment analysis with temporal patterns and actionable insights
    Returns detailed sentiment metrics, trends, and specific moments for review
    """
    analyzer = get_sentiment_analyzer()
    
    if not analyzer:
        return {
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 0.5,
            "confidence": 0.0,
            "tone": "unavailable",
            "emotion_distribution": {},
            "segments": [],
            "trends": {},
            "insights": []
        }
    
    # Split into sentences for granular analysis
    sentences = re.split(r'[.!?]+', transcript)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if not sentences:
        return {
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 0.5,
            "confidence": 0.0,
            "tone": "neutral",
            "emotion_distribution": {},
            "segments": [],
            "trends": {},
            "insights": []
        }
    
    try:
        # Calculate words per sentence for timestamp estimation
        total_words = len(words)
        words_per_sentence = total_words / len(sentences) if sentences else 0
        cumulative_words = 0
        
        # Analyze sentiment for each sentence
        segment_results = []
        positive_count = 0
        negative_count = 0
        total_score = 0
        sentiment_timeline = []
        negative_moments = []
        positive_peaks = []
        
        for i, sentence in enumerate(sentences):
            try:
                # Estimate timestamp based on word position
                sentence_word_count = len(sentence.split())
                start_second = int((cumulative_words / total_words) * len(words) * 0.4) if total_words > 0 else 0
                end_second = int(((cumulative_words + sentence_word_count) / total_words) * len(words) * 0.4) if total_words > 0 else 0
                cumulative_words += sentence_word_count
                
                result = analyzer(sentence[:512])[0]
                sentiment = result['label']
                score = result['score']
                
                segment_data = {
                    "segment": i + 1,
                    "sentiment": sentiment,
                    "confidence": round(score, 3),
                    "text": sentence[:100] + "..." if len(sentence) > 100 else sentence,
                    "timestamp_start": start_second,
                    "timestamp_end": end_second,
                    "duration": end_second - start_second
                }
                
                if sentiment == 'POSITIVE':
                    positive_count += 1
                    total_score += score
                    sentiment_timeline.append(1)
                    if score > 0.95:
                        positive_peaks.append(segment_data)
                else:
                    negative_count += 1
                    total_score += (1 - score)
                    sentiment_timeline.append(-1)
                    if score > 0.80:  # High confidence negative
                        negative_moments.append(segment_data)
                
                segment_results.append(segment_data)
            except Exception as e:
                print(f"Segment {i} error: {e}")
                sentiment_timeline.append(0)
                continue
        
        # Calculate metrics
        total_segments = len(segment_results)
        if total_segments == 0:
            return {
                "overall_sentiment": "NEUTRAL",
                "sentiment_score": 0.5,
                "confidence": 0.0,
                "tone": "neutral",
                "emotion_distribution": {},
                "segments": [],
                "trends": {},
                "insights": []
            }
        
        positive_ratio = positive_count / total_segments
        negative_ratio = negative_count / total_segments
        avg_confidence = total_score / total_segments
        
        # Analyze sentiment trends (beginning vs end)
        first_third = sentiment_timeline[:len(sentiment_timeline)//3]
        last_third = sentiment_timeline[-len(sentiment_timeline)//3:]
        
        trend_start = sum(first_third) / len(first_third) if first_third else 0
        trend_end = sum(last_third) / len(last_third) if last_third else 0
        trend_direction = "improving" if trend_end > trend_start + 0.2 else ("declining" if trend_end < trend_start - 0.2 else "stable")
        
        # Determine overall sentiment and tone
        if positive_ratio > 0.65:
            overall_sentiment = "POSITIVE"
            tone = "Confident and engaging"
        elif positive_ratio < 0.35:
            overall_sentiment = "NEGATIVE"
            tone = "Uncertain or defensive"
        else:
            overall_sentiment = "NEUTRAL"
            tone = "Measured and balanced"
        
        # Generate actionable insights
        insights = []
        
        if negative_ratio > 0.4:
            insights.append({
                "type": "warning",
                "title": "High negative sentiment detected",
                "description": f"{int(negative_ratio * 100)}% of your presentation conveys uncertainty or negativity",
                "action": "Review the highlighted moments and rephrase using affirmative language",
                "severity": "high"
            })
        
        if trend_direction == "declining":
            insights.append({
                "type": "warning",
                "title": "Sentiment declines toward the end",
                "description": "Your closing leaves a weaker impression than your opening",
                "action": "Strengthen your conclusion with confident, forward-looking statements",
                "severity": "medium"
            })
        
        if len(negative_moments) > 0:
            insights.append({
                "type": "info",
                "title": f"{len(negative_moments)} moments need attention",
                "description": "These segments show high-confidence negative sentiment",
                "action": "Click 'Review Moments' to watch and improve these specific parts",
                "severity": "medium"
            })
        
        if positive_ratio > 0.7 and trend_direction != "declining":
            insights.append({
                "type": "success",
                "title": "Strong positive delivery",
                "description": "Your presentation conveys confidence and engagement throughout",
                "action": "Maintain this energy and consider this your baseline for future presentations",
                "severity": "low"
            })
        
        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": round(positive_ratio, 3),
            "confidence": round(avg_confidence, 3),
            "tone": tone,
            "emotion_distribution": {
                "positive": round(positive_ratio * 100, 1),
                "negative": round(negative_ratio * 100, 1),
                "neutral": round((1 - positive_ratio - negative_ratio) * 100, 1)
            },
            "segments": segment_results,
            "negative_moments": negative_moments[:5],  # Top 5 negative moments
            "positive_peaks": positive_peaks[:3],  # Top 3 positive peaks
            "trends": {
                "direction": trend_direction,
                "start_sentiment": round(trend_start, 2),
                "end_sentiment": round(trend_end, 2),
                "consistency": round(1 - abs(trend_end - trend_start), 2)
            },
            "insights": insights
        }
    except Exception as e:
        print(f"Sentiment analysis error: {e}")
        return {
            "overall_sentiment": "NEUTRAL",
            "sentiment_score": 0.5,
            "confidence": 0.0,
            "tone": "neutral",
            "emotion_distribution": {},
            "segments": [],
            "trends": {},
            "insights": []
        }


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


def detect_key_segments(transcript: str, words: List[str], duration_minutes: float) -> List[Dict]:
    """
    Intelligently segment presentation into key parts based on:
    - Sentence boundaries (natural breaks)
    - Topic shifts (new paragraphs, transition words)
    - Performance changes (filler spikes, pace changes)
    
    Similar to how chess.com detects key moves, we detect key moments
    """
    sentences = [s.strip() for s in re.split(r'[.!?]+', transcript) if s.strip()]
    if not sentences:
        return []
    
    segments = []
    current_segment_sentences = []
    current_word_count = 0
    cumulative_words = 0
    
    # Target 20-50 words per segment (natural speaking chunks)
    min_words_per_segment = 20
    max_words_per_segment = 50
    
    for i, sentence in enumerate(sentences):
        sentence_words = sentence.split()
        sentence_word_count = len(sentence_words)
        
        # Check for topic transition indicators
        transition_words = ['however', 'therefore', 'furthermore', 'additionally', 'finally', 
                          'first', 'second', 'third', 'next', 'moving on', 'in conclusion',
                          'let me', 'now', 'so', 'but', 'and now']
        has_transition = any(sentence.lower().startswith(tw) for tw in transition_words)
        
        # Add sentence to current segment
        current_segment_sentences.append(sentence)
        current_word_count += sentence_word_count
        
        # Decide whether to close this segment
        should_close = False
        
        # Close if we hit max words
        if current_word_count >= max_words_per_segment:
            should_close = True
        # Close if we have enough words AND found a transition
        elif current_word_count >= min_words_per_segment and has_transition:
            should_close = True
        # Close if this is the last sentence
        elif i == len(sentences) - 1:
            should_close = True
        
        if should_close and current_segment_sentences:
            segment_text = '. '.join(current_segment_sentences) + '.'
            segment_words = segment_text.split()
            
            # Calculate timestamp
            start_second = int((cumulative_words / len(words)) * duration_minutes * 60) if len(words) > 0 else 0
            cumulative_words += current_word_count
            end_second = int((cumulative_words / len(words)) * duration_minutes * 60) if len(words) > 0 else 0
            
            segments.append({
                'text': segment_text,
                'word_count': current_word_count,
                'start_time': start_second,
                'end_time': end_second,
                'duration': end_second - start_second
            })
            
            current_segment_sentences = []
            current_word_count = 0
    
    return segments


def calculate_confidence_with_explanation(segment_text: str, segment_wpm: int, segment_words: List[str]) -> Tuple[int, str]:
    """
    Calculate confidence score with explanation of the algorithm.
    
    Confidence Score Breakdown:
    - Base: 70 points
    - Pacing (±20): Optimal WPM = 130-160 (conversational)
    - Filler Words (±30): No fillers = bonus, >10% = major penalty  
    - Sentence Length (±10): 15-20 words average is ideal
    
    Total range: 0-100
    """
    confidence = 70
    explanations = []
    
    # 1. Pacing Analysis (±20 points)
    if 130 <= segment_wpm <= 160:
        confidence += 20
        explanations.append(f"✓ Perfect pace ({segment_wpm} WPM)")
    elif 110 <= segment_wpm < 130 or 160 < segment_wpm <= 180:
        confidence += 10
        explanations.append(f"~ Good pace ({segment_wpm} WPM)")
    elif segment_wpm > 200:
        confidence -= 20
        explanations.append(f"✗ Too fast ({segment_wpm} WPM, aim for 130-160)")
    elif segment_wpm < 100:
        confidence -= 20
        explanations.append(f"✗ Too slow ({segment_wpm} WPM, aim for 130-160)")
    else:
        explanations.append(f"~ Pace: {segment_wpm} WPM")
    
    # 2. Filler Words Analysis (±30 points)
    filler_positions = find_filler_positions(segment_text)
    filler_count = len(filler_positions)
    filler_ratio = filler_count / len(segment_words) if segment_words else 0
    
    if filler_count == 0:
        confidence += 10
        explanations.append("✓ No filler words")
    elif filler_ratio > 0.1:
        confidence -= 30
        explanations.append(f"✗ Too many fillers ({filler_count}, {int(filler_ratio*100)}% of words)")
    elif filler_ratio > 0.05:
        confidence -= 15
        explanations.append(f"~ Some fillers ({filler_count}, {int(filler_ratio*100)}% of words)")
    else:
        explanations.append(f"✓ Minimal fillers ({filler_count})")
    
    # 3. Sentence Structure (±10 points)
    sentences = [s.strip() for s in re.split(r'[.!?]+', segment_text) if s.strip()]
    if sentences:
        avg_sentence_len = len(segment_words) / len(sentences)
        if 15 <= avg_sentence_len <= 20:
            confidence += 10
            explanations.append("✓ Clear sentence structure")
        elif avg_sentence_len > 25:
            confidence -= 10
            explanations.append(f"~ Long sentences (avg {int(avg_sentence_len)} words)")
    
    confidence = max(0, min(100, confidence))
    explanation = " | ".join(explanations)
    
    return confidence, explanation


def generate_timeline_data(transcript: str, duration_minutes: float) -> List[Dict]:
    """
    Generate timeline data using intelligent segmentation
    """
    words = transcript.split()
    segments = detect_key_segments(transcript, words, duration_minutes)
    
    if not segments:
        # Fallback to simple single segment
        return [{
            "segment": 1,
            "wpm": 150,
            "confidence": 70,
            "confidence_explanation": "Unable to segment",
            "filler_count": 0,
            "start_time": 0,
            "end_time": int(duration_minutes * 60),
            "duration": int(duration_minutes * 60),
            "text_preview": transcript[:100] + '...' if len(transcript) > 100 else transcript
        }]
    
    timeline = []
    for i, seg in enumerate(segments):
        segment_words = seg['text'].split()
        segment_duration_min = seg['duration'] / 60
        segment_wpm = int(len(segment_words) / segment_duration_min) if segment_duration_min > 0 else 150
        
        # Calculate confidence with explanation
        confidence, explanation = calculate_confidence_with_explanation(
            seg['text'], segment_wpm, segment_words
        )
        
        # Count fillers
        filler_positions = find_filler_positions(seg['text'])
        filler_count = len(filler_positions)
        
        timeline.append({
            "segment": i + 1,
            "wpm": segment_wpm,
            "confidence": confidence,
            "confidence_explanation": explanation,
            "filler_count": filler_count,
            "start_time": seg['start_time'],
            "end_time": seg['end_time'],
            "duration": seg['duration'],
            "text_preview": seg['text'][:100] + '...' if len(seg['text']) > 100 else seg['text']
        })
    
    return timeline


def identify_key_clips(timeline: List[Dict], transcript: str) -> Dict:
    """
    Identify notable clips (both excellent and poor moments) for focused review.
    Like chess.com showing key moves, we show key speaking moments.
    """
    if not timeline:
        return {"good_clips": [], "bad_clips": [], "explanation": ""}
    
    # Sort by confidence to find extremes
    sorted_segments = sorted(timeline, key=lambda x: x['confidence'])
    
    # Good clips: top 3 highest confidence segments
    good_clips = []
    for seg in sorted_segments[-3:][::-1]:  # Reverse to show best first
        if seg['confidence'] >= 75:  # Only include truly good segments
            good_clips.append({
                "segment_num": seg['segment'],
                "confidence": seg['confidence'],
                "start_time": seg['start_time'],
                "end_time": seg['end_time'],
                "duration": seg['duration'],
                "text_preview": seg['text_preview'],
                "why_good": seg['confidence_explanation'],
                "title": f"Strong Moment #{seg['segment']}"
            })
    
    # Bad clips: bottom 3 lowest confidence segments  
    bad_clips = []
    for seg in sorted_segments[:3]:
        if seg['confidence'] < 60:  # Only include problematic segments
            bad_clips.append({
                "segment_num": seg['segment'],
                "confidence": seg['confidence'],
                "start_time": seg['start_time'],
                "end_time": seg['end_time'],
                "duration": seg['duration'],
                "text_preview": seg['text_preview'],
                "why_bad": seg['confidence_explanation'],
                "title": f"Needs Work - Segment #{seg['segment']}"
            })
    
    explanation = f"Found {len(good_clips)} strong moments and {len(bad_clips)} moments that need improvement."
    
    return {
        "good_clips": good_clips,
        "bad_clips": bad_clips,
        "explanation": explanation
    }


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
    
    # Generate timeline data with intelligent segmentation
    timeline = generate_timeline_data(transcript, duration_minutes)
    
    # Calculate overall confidence (average from timeline)
    avg_confidence = sum(t["confidence"] for t in timeline) / len(timeline) if timeline else 70
    
    # Identify key clips for review
    key_clips = identify_key_clips(timeline, transcript)
    
    # Sentiment and tone analysis
    sentiment_analysis = analyze_sentiment_and_tone(transcript, words)
    
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
        "confidence_explanation": "Confidence = Pacing (±20) + Filler Control (±30) + Clear Structure (±10) from base of 70. Range: 0-100.",
        "timeline": timeline,
        "key_clips": key_clips,
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
        },
        "sentiment_analysis": sentiment_analysis
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
