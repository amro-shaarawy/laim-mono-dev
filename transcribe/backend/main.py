from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import tempfile
import os

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FASTER_WHISPER_URL = "http://localhost:5000/inference"

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_data = bytearray()
    try:
        while True:
            chunk = await websocket.receive_bytes()
            audio_data.extend(chunk)
            # For demo: after receiving a chunk, transcribe and send result
            # In production, use streaming or chunked approach
            if len(audio_data) > 16000 * 5:  # ~5 seconds of 16kHz mono audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                async with httpx.AsyncClient() as client:
                    with open(tmp_path, "rb") as f:
                        files = {"audio_file": (os.path.basename(tmp_path), f, "audio/wav")}
                        response = await client.post(FASTER_WHISPER_URL, files=files)
                        if response.status_code == 200:
                            transcript = response.json().get("text", "")
                            await websocket.send_text(transcript)
                        else:
                            await websocket.send_text("[Error: Transcription failed]")
                os.remove(tmp_path)
                audio_data = bytearray()
    except WebSocketDisconnect:
        pass 