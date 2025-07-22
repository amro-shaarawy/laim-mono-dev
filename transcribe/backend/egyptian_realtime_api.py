from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from transformers import AutoProcessor, AutoModel
import torch
import torchaudio
import os

# Path to your local model directory
MODEL_DIR = "facebook/seamless-m4t-v2-large"
TARGET_LANG = "arz"  # Egyptian Arabic

# Load model and processor once at startup
processor = AutoProcessor.from_pretrained(MODEL_DIR)
model = AutoModel.from_pretrained(MODEL_DIR)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

app = FastAPI()

@app.post("/transcribe")
async def transcribe(audio_file: UploadFile = File(...)):
    # Save uploaded file temporarily
    temp_path = "temp_audio.wav"
    with open(temp_path, "wb") as f:
        f.write(await audio_file.read())
    # Load and resample audio
    waveform, sample_rate = torchaudio.load(temp_path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
    # Prepare input
    audio_inputs = processor(audios=waveform.unsqueeze(0), return_tensors="pt", sampling_rate=16000)
    audio_inputs = {k: v.to(device) if isinstance(v, torch.Tensor) else v for k, v in audio_inputs.items()}
    # Inference
    output_tokens = model.generate(
        **audio_inputs,
        tgt_lang=TARGET_LANG,
        generate_speech=False
    )
    transcript = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)
    os.remove(temp_path)
    return JSONResponse({"transcript": transcript})