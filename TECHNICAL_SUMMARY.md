# showcAIse - Technical Implementation Summary

## Architecture
- **Backend**: FastAPI (Python 3.11.6) on port 8000
- **Frontend**: React 18 (Node 18) on port 3000
- **Deployment**: Docker Compose with separate containers
- **Storage**: In-memory session storage (UUID-based)

## Core Pipeline

### 1. Video Upload & Analysis (`/api/upload`)
- **Audio Extraction**: FFmpeg → 16kHz mono WAV
- **Transcription**: Together AI Whisper Large V3 API
- **Analysis**: Multi-stage speech pattern analysis
- **Session**: UUID per upload, stored in-memory

### 2. Speech Analysis (`analyzer.py`)

#### ML Models Used
- **Whisper Large V3** (Together AI API) - Audio transcription
- **DistilBERT SST-2** (HuggingFace) - Sentence-level sentiment analysis
- **Coqui XTTS v2** (self-hosted) - Voice cloning (~2GB model)

#### Algorithmic Components (No ML)
- **Filler Detection**: Regex patterns (um, uh, like, you know, etc.)
- **Pacing Analysis**: WPM calculation (word_count / duration)
- **Confidence Scoring**: Formula-based (pacing + fillers + sentiment + clarity)

#### Key Features

**Filler Word Highlighting**
- Regex finds character positions: `[(start_char, end_char, "filler"), ...]`
- Frontend wraps positions in `<mark>` tags
- No ML required - pure string matching

**Timeline Segmentation**
- Chunks transcript into 20-50 word segments
- Detects transitions via keywords (however, therefore, first, etc.)
- **Timestamps**: Estimated via word position (0.4 sec/word = 150 WPM baseline)
- Adds 1-second buffer for video seeking

**Confidence Scoring Formula**
```
Base: 50 points
+ Pacing (±25): Optimal 130-160 WPM
+ Filler Control (±30): Penalized if >8% ratio
+ Sentiment (±20): From DistilBERT
+ Clarity (±15): Hedge words (kind of, I guess, maybe)
= Score: 0-100
```

**Sentiment Analysis**
- Sentence-by-sentence DistilBERT analysis
- Outputs: Overall sentiment, segment scores, temporal trends
- Timestamps: Same word-position estimation method

**Key Moments**
- **Strong**: Confidence ≥ 70
- **Weak**: Confidence < 50
- Returns top 5 of each with video timestamps

**Body Language**
- ⚠️ **HARDCODED DEMO DATA** - not real detection
- Placeholder JSON with fake scores
- Real implementation would need MediaPipe/OpenCV pose detection

### 3. Voice Cloning (`/api/voice-clone`)

**Model**: Coqui TTS XTTS v2 (multilingual, ~2GB)

**Process**:
1. Extract speaker audio from video (moviepy) → 22050 Hz WAV
2. Generate improved script:
   - Remove fillers via string replacement
   - Replace weak language ("I think" → "I believe")
   - Clean formatting
3. TTS synthesis: `tts.tts_to_file()` with speaker reference
4. Output: Cloned voice WAV file

**Demo Mode**: Serves hardcoded `demo_cloned.wav` if `use_demo=true`

### 4. Video Generation (`/api/video-generate`)
- **Current**: Placeholder, serves demo video
- **Planned**: Combine cloned audio + original video with moviepy
- Demo file: `demo_video.mp4`

## Technical Details for Q&A

### Dependencies
```
FastAPI, uvicorn, ffmpeg-python
transformers 4.49.0, torch 2.5.1, torchaudio 2.5.1
TTS 0.22.0 (Coqui), moviepy 2.2.1
soundfile 0.13.1, librosa, scipy
```

### Timestamp Accuracy
- Estimated via word position (0.4 sec/word)
- Not frame-accurate, within 1-2 seconds
- Real implementation would use Whisper word-level timestamps

### Performance
- **TTS model loading**: 2GB, ~5-10s first time (cached globally)
- **Voice cloning**: 30-60s per request
- **Sentiment model**: ~3s load time (cached)

### Known Issues
- moviepy 2.2.1 import change: `from moviepy import ...` (no .editor submodule)
- PyTorch 2.5+ requires `weights_only=False` for TTS
- torchaudio backend deprecated, uses soundfile directly

## Production Improvements Needed
- [ ] Replace in-memory sessions with database (Redis/PostgreSQL)
- [ ] Add GPU support for TTS (5-10x speedup)
- [ ] Use Whisper word-level timestamps
- [ ] Implement real video generation (moviepy editing)
- [ ] Add real body language detection (MediaPipe)
- [ ] Rate limiting and authentication
