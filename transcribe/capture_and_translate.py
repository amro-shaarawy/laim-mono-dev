import sounddevice as sd
import numpy as np
import torch
import queue
import os
import torchaudio
import time
from datetime import datetime
from gradio_client import Client, handle_file

# Audio settings
SAMPLE_RATE = 16000
CHUNK_DURATION = 5  # seconds - as requested
CHUNK_SAMPLES = SAMPLE_RATE * CHUNK_DURATION
CHANNELS = 1

# Gradio API client
API_URL = "http://127.0.0.1:7860/"
TARGET_LANGUAGE = "arz"  # Egyptian Arabic

# Initialize Gradio client
client = Client(API_URL)

# Queue for audio chunks
q = queue.Queue()

# Phrases to filter out
FILTERED_PHRASES = ["أنا مش عارفة، أنا مش عارفة، أنا مش عارفة"]

def callback(indata, frames, time, status):
    """Callback function for the audio stream"""
    if status:
        print(f"Status: {status}")
    q.put(indata.copy())

def print_recording_indicator(is_recording=True):
    """Print a clear visual indicator that recording is active"""
    if is_recording:
        print("\n🔴 RECORDING NOW - Please speak... 🎤")
        # Print a progress bar for the current chunk
        for i in range(CHUNK_DURATION):
            remaining = CHUNK_DURATION - i
            bar = "█" * i + "░" * remaining
            print(f"\r[{bar}] {remaining} seconds remaining", end="")
            time.sleep(1)
        print("\r" + " " * 50, end="\r")  # Clear the line
    else:
        print("\n⏸️  Processing audio... (not recording)")

def should_display_result(result):
    """Check if the result should be displayed based on filter criteria"""
    if not result:
        return False
        
    # Check if result contains any filtered phrases
    for phrase in FILTERED_PHRASES:
        if phrase in result:
            print("\n[Filtered output - contains filtered phrase]")
            return False
            
    return True

def main():
    print("\n=== Audio Capture and Transcription ===\n")
    print("Recording and transcribing in real time. Press Ctrl+C to stop.")
    print(f"Capturing {CHUNK_DURATION}-second chunks at {SAMPLE_RATE}Hz")
    print(f"Target language: Egyptian Arabic (arz)\n")
    print("Note: Some outputs may be filtered based on content")
    
    # Countdown before starting
    print("\nPreparing to record...")
    for i in range(3, 0, -1):
        print(f"Starting in {i}...")
        time.sleep(1)
    
    try:
        # Start the audio input stream
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
            buffer = np.empty((0, CHANNELS), dtype=np.float32)
            chunk_idx = 0
            
            # Initial recording indicator
            print_recording_indicator(True)
            
            while True:
                # Get audio chunk from queue
                audio_chunk = q.get()
                
                # Add to buffer
                buffer = np.concatenate((buffer, audio_chunk), axis=0)
                
                # Process complete chunks
                while len(buffer) >= CHUNK_SAMPLES:
                    # Extract a chunk
                    chunk = buffer[:CHUNK_SAMPLES]
                    buffer = buffer[CHUNK_SAMPLES:]
                    
                    # Indicate we're processing (not recording)
                    print_recording_indicator(False)
                    
                    # Save chunk as WAV file
                    timestamp = datetime.now().strftime("%H%M%S")
                    chunk_path = f"temp_chunk_{timestamp}.wav"
                    torchaudio.save(chunk_path, torch.from_numpy(chunk.T), SAMPLE_RATE)
                    
                    # Send to Gradio API
                    try:
                        print(f"Sending chunk {chunk_idx} to API...")
                        result = client.predict(
                            handle_file(chunk_path),
                            TARGET_LANGUAGE,
                            api_name="/handle_translation"
                        )
                        
                        # Only display result if it passes the filter
                        if should_display_result(result):
                            print(f"\n[{chunk_idx}] {timestamp}: {result}\n")
                    except Exception as e:
                        print(f"API request error: {e}")
                    
                    # Clean up
                    try:
                        os.remove(chunk_path)
                    except:
                        pass
                    
                    chunk_idx += 1
                    
                    # Indicate we're recording again
                    print_recording_indicator(True)
                    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()