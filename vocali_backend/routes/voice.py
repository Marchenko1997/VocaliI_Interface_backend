from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.whisper_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe")
async def transcribe_voice_command(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()

    if len(audio_bytes) < 1000:
        return {"text": ""}

    try:
        text = await transcribe_audio(audio_bytes, audio.filename or "audio.webm")
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")