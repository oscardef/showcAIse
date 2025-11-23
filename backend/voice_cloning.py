"""
Voice Cloning Module - Clone voice from video and generate improved presentation speech
"""
import os
from pathlib import Path
from typing import Dict

# Agree to Coqui TTS non-commercial license
os.environ['COQUI_TOS_AGREED'] = '1'

# Fix PyTorch 2.6+ weights_only issue for TTS model loading
import torch
_original_torch_load = torch.load
def _torch_load_wrapper(*args, **kwargs):
    # Force weights_only=False for TTS compatibility
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _torch_load_wrapper

# Disable torchcodec in torchaudio to avoid compatibility issues
os.environ['TORCHAUDIO_USE_BACKEND_DISPATCHER'] = '0'

# Ensure soundfile is available (required for audio loading without torchcodec)
try:
    import soundfile as sf
    print(f"✓ soundfile version: {sf.__version__}")
except ImportError:
    print("⚠️  WARNING: soundfile not installed, voice cloning will fail!")
    print("   Install with: pip install soundfile")

# Import torchaudio (will use soundfile automatically if available)
try:
    import torchaudio
    # Newer torchaudio versions don't have set_audio_backend
    # They automatically use soundfile if torchcodec is not available
    if hasattr(torchaudio, 'set_audio_backend'):
        torchaudio.set_audio_backend("soundfile")
        print(f"✓ torchaudio backend explicitly set to: soundfile")
    else:
        print(f"✓ torchaudio will use soundfile automatically")
except Exception as e:
    print(f"⚠️  torchaudio import warning: {e}")

# Use moviepy.editor like in your working code
from moviepy.editor import VideoFileClip
from TTS.api import TTS


# Global TTS model instance (lazy loading)
_tts_model = None


def get_tts_model():
    """Lazy load TTS model to save memory"""
    global _tts_model
    if _tts_model is None:
        print("🎙️  Loading TTS model (XTTS v2, ~2GB)...")
        _tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
        print("✅ TTS model loaded successfully")
    return _tts_model


def extract_speaker_audio(video_path: str, output_path: str) -> bool:
    """
    Extract audio from video file and save as WAV for voice cloning
    Uses soundfile directly to avoid torchcodec code paths
    Returns True if successful, False otherwise
    """
    try:
        print(f"📹 Extracting speaker audio from: {video_path}")
        
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            print("⚠️  Video has no audio track")
            video.close()
            return False
        
        audio = video.audio
        
        # Write audio using soundfile directly to bypass torchcodec
        import numpy as np
        import soundfile as sf
        
        # Get audio as numpy array
        audio_array = audio.to_soundarray(fps=22050)
        
        # Ensure it's in the right format (if stereo, keep stereo; if mono, keep mono)
        if len(audio_array.shape) == 1:
            # Mono audio
            audio_data = audio_array
        else:
            # Stereo or multi-channel - keep as is
            audio_data = audio_array
        
        # Write directly with soundfile (bypasses all torchcodec paths)
        sf.write(output_path, audio_data, 22050, subtype='PCM_16')
        
        video.close()
        print(f"✅ Speaker audio extracted to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Audio extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def generate_improved_script(analysis: Dict) -> str:
    """
    Generate an improved presentation script based on analysis results
    Removes fillers, improves weak language, and optimizes pacing
    """
    transcript = analysis.get("transcript", "")
    
    if not transcript:
        return ""
    
    # Start with original transcript
    improved_script = transcript
    
    # Remove filler words
    filler_words = [
        "um", "uh", "like", "you know", "so", "actually", 
        "basically", "literally", "kind of", "sort of"
    ]
    
    for filler in filler_words:
        # Remove standalone fillers with various punctuation
        improved_script = improved_script.replace(f" {filler} ", " ")
        improved_script = improved_script.replace(f" {filler},", ",")
        improved_script = improved_script.replace(f" {filler}.", ".")
        improved_script = improved_script.replace(f"{filler.capitalize()} ", "")
        improved_script = improved_script.replace(f", {filler},", ",")
    
    # Replace weak/uncertain language with confident alternatives
    replacements = {
        "I think maybe": "I believe",
        "I guess": "I believe",
        "probably": "will",
        "might be": "is",
        "could be": "is",
        "maybe": "will",
        "I don't know": "",
        "kind of": "",
        "sort of": "",
    }
    
    for weak, strong in replacements.items():
        improved_script = improved_script.replace(weak, strong)
        improved_script = improved_script.replace(weak.capitalize(), strong.capitalize())
    
    # Clean up extra spaces and punctuation
    while "  " in improved_script:
        improved_script = improved_script.replace("  ", " ")
    
    improved_script = improved_script.replace(" ,", ",")
    improved_script = improved_script.replace(" .", ".")
    improved_script = improved_script.replace(",,", ",")
    improved_script = improved_script.replace("..", ".")
    
    return improved_script.strip()


def clone_voice_and_generate_speech(
    session_id: str,
    improved_script: str,
    speaker_audio_path: str,
    output_path: str
) -> bool:
    """
    Use voice cloning to generate speech audio with the improved script
    
    Args:
        session_id: Session identifier for logging
        improved_script: The improved presentation script
        speaker_audio_path: Path to the extracted speaker audio (WAV)
        output_path: Path to save the generated audio (WAV)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"[{session_id}] 🎤 Starting voice cloning...")
        
        # Load TTS model
        tts = get_tts_model()
        
        # Generate speech with cloned voice
        print(f"[{session_id}] 🗣️  Generating speech with cloned voice...")
        tts.tts_to_file(
            text=improved_script.strip(),
            file_path=output_path,
            speaker_wav=speaker_audio_path,
            language="en"
        )
        
        print(f"[{session_id}] ✅ Voice cloning complete! Output saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"[{session_id}] ❌ Voice cloning failed: {str(e)}")
        return False


def get_improvement_summary(original_analysis: Dict, improved_script: str) -> Dict:
    """
    Generate a summary of improvements made to the presentation
    """
    original_transcript = original_analysis.get("transcript", "")
    filler_count = original_analysis.get("filler_count", 0)
    original_wpm = original_analysis.get("wpm", 0)
    
    improvements = []
    
    if filler_count > 0:
        improvements.append(f"Removed {filler_count} filler words")
    
    # Count word improvements
    original_words = len(original_transcript.split())
    improved_words = len(improved_script.split())
    
    if original_words > improved_words:
        reduction = original_words - improved_words
        improvements.append(f"Reduced script by {reduction} words ({reduction/original_words*100:.1f}%)")
    
    improvements.append("Replaced uncertain language with confident phrasing")
    improvements.append("Optimized sentence structure for clarity")
    
    # Estimate new WPM (assuming 145 WPM as target)
    target_wpm = 145
    estimated_duration = improved_words / target_wpm * 60  # in seconds
    
    return {
        "improvements": improvements,
        "original_word_count": original_words,
        "improved_word_count": improved_words,
        "original_wpm": original_wpm,
        "target_wpm": target_wpm,
        "estimated_duration_seconds": round(estimated_duration, 1)
    }
