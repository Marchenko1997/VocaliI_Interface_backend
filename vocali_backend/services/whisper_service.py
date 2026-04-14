import os
import tempfile
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    ext = filename.split(".")[-1] if "." in filename else "webm"
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(filename, f),
            )
        return response.text
    finally:
        os.unlink(tmp_path)