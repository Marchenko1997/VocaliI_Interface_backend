import os
import tempfile
from groq import Groq


client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5,
)

SUPPORTED_FORMATS = ["webm", "mp4", "mp3", "wav", "ogg", "m4a", "flac"]

async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    ext = filename.split(".")[-1].lower() if "." in filename else "webm"
    if ext not in SUPPORTED_FORMATS:
        ext = "webm"

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=(f"audio.{ext}", f),
            )
        return response.text
    except Exception as e:
        print(f"Groq transcription error: {e}")
        raise
    finally:
        os.unlink(tmp_path)