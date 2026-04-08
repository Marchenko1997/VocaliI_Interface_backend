from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uvicorn
from contextlib import asynccontextmanager
from .database import init_db, get_session

from .models import Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .routes.auth import router as auth_router
from .routes.audio import router as audio_router
from .routes.spotify import router as spotify_router
from .routes.ai import router as ai_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(audio_router, prefix="/audio", tags=["audio"])
app.include_router(spotify_router, prefix="/spotify", tags=["spotify"])
app.include_router(ai_router, prefix="/ai", tags=["ai"]) 


@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)