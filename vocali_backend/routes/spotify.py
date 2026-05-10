from fastapi import APIRouter, Query

from ..services.spotify_serv import search_tracks, get_artist_by_id

router = APIRouter()


@router.get("/search")
async def search_spotify(
    q: str,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=50),
):
    return await search_tracks(q, offset, limit)


@router.get("/artist-image")
async def get_artist_image(id: str):
    data = await get_artist_by_id(id)

    image_url = (
        data["images"][0]["url"]
        if data.get("images")
        else ""
    )

    return {"image": image_url}