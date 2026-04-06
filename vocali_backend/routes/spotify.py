from fastapi import APIRouter

from ..services.spotify_serv import search_tracks


router = APIRouter()


@router.get("/search")
async def search_spotify(q: str, offset: int = 0, limit: int = 20):
    return await search_tracks(q, offset, limit)