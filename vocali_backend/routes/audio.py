from sqlalchemy import select
from fastapi import UploadFile, File, APIRouter, Depends, HTTPException
import os
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials

from ..models import AudioFile
from ..database import get_session
from ..security import security
from ..auth_utils import get_current_user
from ..schemas import AudioFileOut, AudioMetadata, Transcription


router = APIRouter()

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    user = await get_current_user(credentials.credentials, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # создаём папку если нет
    os.makedirs("uploads", exist_ok=True)

    file_key = str(uuid.uuid4())
    file_location = f"uploads/{file_key}_{file.filename}"

    # сохраняем файл
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    audio = AudioFile(
        user_id=user.id,
        file_key=file_key,
        file_name=file.filename,
        file_size=len(content),
        format=file.filename.split(".")[-1],
        duration=0

    )

    session.add(audio)
    await session.commit()
    await session.refresh(audio)

    return {"message": "File uploaded"}


@router.get("/files", response_model=list[AudioFileOut])
async def get_audio_files(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    user = await get_current_user(credentials.credentials, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(
        select(AudioFile).where(AudioFile.user_id == user.id)
    )

    files = result.scalars().all()

    return [
    AudioFileOut(
        userId=user.id,
        fileKey=file.file_key,
        fileName=file.file_name,
        fileSize=file.file_size,
        duration=file.duration or 0,
        format=file.format,
        uploadedAt=file.uploaded_at,
        lastModified=file.uploaded_at,
        status="ready",
        metadata=AudioMetadata(
            originalName=file.file_name,
            duration=file.duration or 0,
            extension=file.format,
            transcription=Transcription(
                language="en",
                text="",
                status="pending"
            ),
            fileSize=file.file_size,
            format=file.format,
            uploadedAt=file.uploaded_at,
            mimeType="audio/mpeg"
        ),
        downloadUrl=f"http://localhost:8000/uploads/{file.file_key}_{file.file_name}"
    )
    for file in files
]


