# Demo Audio File

This directory contains cloned audio outputs from voice cloning.

## Demo Mode Setup

To use the demo audio feature without generating voice cloning each time:

1. **Place your demo audio file here:**
   ```
   backend/cloned_audio/demo_cloned.wav
   ```

2. **Use the demo mode in your API call:**
   ```bash
   POST /api/voice-clone/{session_id}?use_demo=true
   ```

3. **The demo audio will be served at:**
   ```
   GET /api/cloned-audio/demo
   ```

## File Format

- **Filename:** `demo_cloned.wav`
- **Format:** WAV audio file
- **Recommended:** 22050 Hz sample rate, mono or stereo

## How It Works

When `use_demo=true` is passed to the voice cloning endpoint:
- The system skips the actual voice cloning process
- Returns the pre-recorded demo audio file
- Still generates the improved script and improvements analysis
- Responds much faster (no TTS model loading required)

This is perfect for demos, testing, or when you want to showcase the feature without waiting for voice cloning to complete.
