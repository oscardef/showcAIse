# Voice Cloning Quick Start Guide

## Overview

The voice cloning feature uses AI to generate an improved version of your presentation using your own voice. It removes filler words, replaces uncertain language, and maintains your natural speaking style.

## Prerequisites

✅ Video uploaded and analyzed  
✅ Docker containers running (`docker compose up`)  
✅ ~2GB free disk space (for TTS model cache)

## Step-by-Step Usage

### 1. Analyze Your Video

First, upload and analyze your presentation video as usual:

1. Go to http://localhost:3000
2. Upload your MP4 video
3. Wait for analysis to complete
4. Review the results

### 2. Generate Voice Clone

**Option A: From Overview Tab**
- Look for the purple "Voice Cloning" card
- Click "Generate Improved Voice Clone"

**Option B: From Voice Clone Tab**
- Click "Voice Clone" tab in navigation
- Click "Generate Improved Voice Clone"

### 3. Wait for Processing (1-2 minutes)

The AI will:
1. Extract audio from your video ✓
2. Generate improved script ✓
3. Clone your voice ✓
4. Create final audio ✓

**First time only**: Model download (~2GB) adds 2-3 minutes

### 4. Review Results

Once complete, you'll see:

**Audio Player**
- Play/pause controls
- Download button (WAV format)

**Improvements Summary**
- Original vs improved word count
- Number of fillers removed
- List of specific improvements

**Improved Script**
- Full cleaned transcript
- Compare with original in Transcript tab

### 5. Download Audio

Click "Download Audio" to get your improved audio file:
- Format: WAV (high quality)
- Filename: `improved_presentation_{session_id}.wav`
- Ready to use in video editing software

## What Gets Improved

### Removed Fillers
- "um", "uh", "like"
- "you know", "so"
- "actually", "basically", "literally"
- "kind of", "sort of"

### Replaced Uncertain Language
- "I think maybe" → "I believe"
- "I guess" → "I believe"
- "probably" → "will"
- "might be" → "is"
- "maybe" → "will"

### Cleaned Up
- Extra spaces
- Multiple punctuation marks
- Run-on sentences

## Using the Audio

### Create Video with Improved Audio

**Option 1: iMovie (Mac)**
1. Open iMovie
2. Import your original video (muted)
3. Import the cloned WAV file
4. Sync audio with video
5. Export final video

**Option 2: DaVinci Resolve (Free)**
1. Import original video
2. Mute original audio track
3. Import cloned WAV
4. Align audio with video
5. Export

**Option 3: FFmpeg (Command Line)**
```bash
# Replace audio in video
ffmpeg -i original_video.mp4 -i improved_audio.wav \
  -c:v copy -map 0:v:0 -map 1:a:0 \
  output_video.mp4
```

## Performance Tips

### Speed Up First Run

Pre-download TTS model before first use:

```bash
# Docker
docker compose exec backend python preload_tts.py

# Manual setup
cd backend
python preload_tts.py
```

### Optimize Docker

Increase memory allocation:
1. Docker Desktop → Settings → Resources
2. Set Memory to 4GB minimum
3. Apply & Restart

### Clear Cache (if needed)

```bash
# Remove cached model (if corrupted)
docker compose exec backend rm -rf /root/.local/share/tts/

# Restart and regenerate
docker compose restart backend
```

## Troubleshooting

### "Voice cloning failed"

**Check video has audio:**
```bash
docker compose exec backend python -c \
  "from moviepy.editor import VideoFileClip; \
   v = VideoFileClip('videos/YOUR_SESSION_ID.mp4'); \
   print('Has audio:', v.audio is not None)"
```

**Check logs:**
```bash
docker compose logs backend | grep -i "voice"
```

### "Out of memory"

1. Close other applications
2. Increase Docker memory limit
3. Try shorter videos (<5 min)

### Model download slow/fails

```bash
# Use faster mirror (if available)
export HF_ENDPOINT=https://hf-mirror.com
docker compose restart backend
```

### Audio quality issues

- Ensure original video audio is clear
- Minimum 16kHz sample rate recommended
- Mono or stereo both work

## Advanced Usage

### Custom Script Editing

If you want to edit the improved script before voice cloning:

1. Copy improved script from Voice Clone tab
2. Edit text as needed
3. Use external TTS tools (currently not supported in UI)

### Batch Processing

For multiple videos:

```bash
# Upload and analyze each video
# Call API programmatically

for video in *.mp4; do
  curl -F "video=@$video" http://localhost:8000/api/upload
  # Extract session_id from response
  # Wait 1-2 minutes
  curl -X POST http://localhost:8000/api/voice-clone/$session_id
done
```

## API Usage

### Using cURL

```bash
# 1. Upload video
SESSION_ID=$(curl -X POST -F "video=@presentation.mp4" \
  http://localhost:8000/api/upload | jq -r '.session_id')

# 2. Generate voice clone
curl -X POST http://localhost:8000/api/voice-clone/$SESSION_ID

# 3. Download audio
curl -O http://localhost:8000/api/cloned-audio/$SESSION_ID
```

### Using Python

```python
import requests

# Upload video
with open('presentation.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'video': f}
    )
    session_id = response.json()['session_id']

# Generate voice clone
response = requests.post(
    f'http://localhost:8000/api/voice-clone/{session_id}'
)

# Download audio
audio_url = response.json()['audio_url']
audio_data = requests.get(f'http://localhost:8000{audio_url}')

with open('improved_audio.wav', 'wb') as f:
    f.write(audio_data.content)
```

## Model Information

**Name**: Coqui TTS XTTS v2  
**Type**: Multilingual voice cloning  
**Size**: ~2GB  
**License**: Non-commercial (CPML)  
**Language**: English (multi-language supported)  
**Quality**: High-quality synthesis  
**Speed**: 1-2 minutes for 2-5 min audio

## Future Enhancements

Planned improvements:
- [ ] Video generation (auto-sync audio with video)
- [ ] Custom voice adjustment (pitch, speed)
- [ ] Multiple voice styles
- [ ] Real-time preview
- [ ] Batch processing UI
- [ ] Progress tracking during generation

## Support

Issues? Check:
1. Docker containers running: `docker compose ps`
2. Backend logs: `docker compose logs backend`
3. Frontend console: Browser DevTools
4. GitHub Issues: https://github.com/oscardef/showcAIse/issues

---

**Happy presenting! 🎤**
