import numpy as np
import whisper
from pyannote.audio import Pipeline
from resemblyzer import VoiceEncoder, preprocess_wav
from scipy.io import wavfile
import os

# ========== CONFIGURATION ==========
AUDIO_FILE = "your_audio.wav"  # Path to your audio file
WHISPER_MODEL_SIZE = "base"
ENROLL_DIR = "enrolled_speakers"

# ========== MODEL LOADING ==========
print("Loading models...")
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
encoder = VoiceEncoder()
print("Models loaded.")

# ========== SPEAKER ENROLLMENT ==========
def enroll_speaker(name, wav_path):
    wav = preprocess_wav(wav_path)
    embedding = encoder.embed_utterance(wav)
    os.makedirs(ENROLL_DIR, exist_ok=True)
    np.save(os.path.join(ENROLL_DIR, f"{name}.npy"), embedding)
    print(f"Speaker '{name}' enrolled.")

def load_enrolled_speakers():
    speakers = {}
    if not os.path.exists(ENROLL_DIR):
        return speakers
    for fname in os.listdir(ENROLL_DIR):
        if fname.endswith(".npy"):
            name = fname[:-4]
            embedding = np.load(os.path.join(ENROLL_DIR, fname))
            speakers[name] = embedding
    return speakers

def identify_speaker(embedding, enrolled_speakers, threshold=0.7):
    from scipy.spatial.distance import cdist
    if not enrolled_speakers:
        return "Unknown"
    names = list(enrolled_speakers.keys())
    embeddings = np.stack([enrolled_speakers[n] for n in names])
    dists = cdist([embedding], embeddings, metric="cosine")[0]
    min_idx = np.argmin(dists)
    if dists[min_idx] < threshold:
        return names[min_idx]
    return "Unknown"

# ========== MAIN PIPELINE ==========
def process_audio_file(audio_file):
    enrolled_speakers = load_enrolled_speakers()
    # Diarization
    diarization = pipeline({"audio": audio_file})
    # Read audio
    sr, audio = wavfile.read(audio_file)
    if audio.ndim > 1:
        audio = audio[:, 0]  # Use first channel if stereo
    audio = audio.astype(np.float32) / np.max(np.abs(audio))
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = int(turn.start * sr)
        end = int(turn.end * sr)
        segment = audio[start:end]
        if len(segment) < sr:
            continue
        embedding = encoder.embed_utterance(segment)
        speaker_name = identify_speaker(embedding, enrolled_speakers)
        # Whisper expects 16kHz mono float32 numpy array
        result = whisper_model.transcribe(segment, language=None, task="transcribe")
        text = result["text"].strip()
        language = result["language"]
        print(f"[{speaker_name}] ({language}): {text}")

if __name__ == "__main__":
    process_audio_file(AUDIO_FILE)