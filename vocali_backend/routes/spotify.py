from fastapi import APIRouter, Query

from ..services.spotify_serv import search_tracks


router = APIRouter()


@router.get("/search")
async def search_spotify(
    q: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    return await search_tracks(q, offset, limit)