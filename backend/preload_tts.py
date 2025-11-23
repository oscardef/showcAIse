"""
Pre-download TTS model to avoid repeated downloads during development
Run this once: python preload_tts.py
"""
import os
os.environ['COQUI_TOS_AGREED'] = '1'
os.environ['TORCHAUDIO_USE_BACKEND_DISPATCHER'] = '0'

# Verify soundfile is available
try:
    import soundfile as sf
    print(f"✓ soundfile version: {sf.__version__}")
except ImportError:
    print("⚠️  soundfile not installed!")
    exit(1)

# Set torchaudio backend to soundfile
try:
    import torchaudio
    torchaudio.set_audio_backend("soundfile")
    print(f"✓ torchaudio backend: soundfile")
except Exception as e:
    print(f"⚠️  Could not set torchaudio backend: {e}")

# Fix PyTorch weights_only issue
import torch
_original_torch_load = torch.load
def _torch_load_wrapper(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _torch_load_wrapper

from TTS.api import TTS

print("🎙️  Pre-downloading TTS model (XTTS v2, ~2GB)...")
print("This will be cached and reused in subsequent runs.")

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

print("✅ TTS model downloaded and cached successfully!")
print("Location: ~/.local/share/tts/")
print("\nYou can now run the server without re-downloading.")
