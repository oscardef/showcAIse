#!/usr/bin/env python3
"""
Voice Cloning Demo - Clone voice from sample video and generate presentation speech
"""

from TTS.api import TTS

# Sample presentation script
presentation_script = """
Welcome to today's presentation on artificial intelligence and voice synthesis. 
In this demo, we'll explore how modern AI technology can clone and replicate human voices with remarkable accuracy.
Voice cloning has numerous applications, from content creation to accessibility features.
The technology behind this uses advanced neural networks trained on multilingual datasets.
Thank you for watching this demonstration of AI-powered voice synthesis.
"""

# Initialize TTS model with XTTS v2
print("Loading TTS model...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)

# Generate speech by cloning the voice from the sample video
print("Generating speech with cloned voice...")
tts.tts_to_file(
    text=presentation_script.strip(),
    file_path="presentation_output.wav",
    speaker_wav="speaker_sample.wav",
    language="en"
)

print("Voice cloning complete! Output saved to: presentation_output.wav")