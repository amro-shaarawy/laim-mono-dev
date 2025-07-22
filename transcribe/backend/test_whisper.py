import whisper

# Path to your audio file
audio_path = r"C:\Users\amros\Downloads\test_audio.mp3"

# Load the turbo model (or use "small", "medium", etc. as needed)
model = whisper.load_model("turbo")

# Transcribe the audio
result = model.transcribe(audio_path)

# Print the transcription
print(result["text"])

# Save the transcription to a file
with open("transcription.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])