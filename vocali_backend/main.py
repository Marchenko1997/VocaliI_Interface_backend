from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uvicorn
from contextlib import asynccontextmanager
from .database import init_db, get_session
from .routes import auth_router
from .models import Base


security = HTTPBearer()
app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)