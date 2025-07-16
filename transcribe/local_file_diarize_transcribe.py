"""
realtime_diarize_transcribe.py

Real-time (chunked) speech-to-text and speaker diarization.
- Uses pyannote.audio for diarization
- Uses OpenAI Whisper for multilingual transcription and language detection
- Outputs speaker-labeled, language-tagged transcript segments in near real-time

Dependencies:
    pip install torch torchaudio openai-whisper pyannote.audio sounddevice numpy scipy

Usage:
    python realtime_diarize_transcribe.py
"""

import numpy as np
import sounddevice as sd
import whisper
from pyannote.audio import Pipeline
import queue
import time
import os
import tempfile
from scipy.io.wavfile import write

# ========== CONFIGURATION ==========
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 5  # seconds
WHISPER_MODEL_SIZE = "base"  # or "small", "medium", "large"

# ========== MODEL LOADING ==========
print("Loading models...")
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
print("Models loaded.")

# ========== AUDIO STREAM SETUP ==========
audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=audio_callback)

def process_chunk(chunk, sample_rate):
    # Save chunk to a temporary WAV file for pyannote
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        write(tmpfile.name, sample_rate, (chunk * 32767).astype(np.int16))
        tmp_wav = tmpfile.name

    # Diarization
    diarization = pipeline(tmp_wav)

    # Load audio for Whisper
    audio = chunk.flatten().astype(np.float32)
    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * sample_rate)
        end = int(turn.end * sample_rate)
        segment = audio[start:end]
        if len(segment) < sample_rate // 2:
            continue
        # Whisper expects 16kHz float32 numpy array
        result = whisper_model.transcribe(segment, language=None, task="transcribe")
        text = result["text"].strip()
        language = result["language"]
        results.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end,
            "language": language,
            "text": text
        })
        print(f"[Speaker {speaker}] ({language}) {turn.start:.2f}-{turn.end:.2f}s: {text}")
    os.remove(tmp_wav)
    return results

def main():
    print("Starting real-time transcription and diarization. Press Ctrl+C to stop.")
    stream.start()
    try:
        buffer = []
        start_time = time.time()
        while True:
            if not audio_queue.empty():
                chunk = audio_queue.get()
                buffer.append(chunk)
                # If enough audio for a chunk, process it
                if len(buffer) * chunk.shape[0] >= SAMPLE_RATE * CHUNK_DURATION:
                    audio_chunk = np.concatenate(buffer)[:SAMPLE_RATE * CHUNK_DURATION]
                    process_chunk(audio_chunk, SAMPLE_RATE)
                    # Remove processed samples from buffer
                    buffer = [np.concatenate(buffer)[SAMPLE_RATE * CHUNK_DURATION:]]
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        stream.stop()
        print("Stopped.")

if __name__ == "__main__":
    main()