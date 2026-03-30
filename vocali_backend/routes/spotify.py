from fastapi import APIRouter

from ..services.spotify_serv import search_tracks


router = APIRouter()


@router.get("/search")
async def search_spotify(q: str):
    return await search_tracks(q)