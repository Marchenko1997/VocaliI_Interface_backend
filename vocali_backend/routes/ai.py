from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services.ai_service import parse_playlist_intent
from ..auth_utils import get_current_user 

router = APIRouter()

class PlaylistRequest(BaseModel):
    prompt: str

@router.post("/playlist")
async def generate_playlist(
    request: PlaylistRequest,
    current_user = Depends(get_current_user)
):
    try:
        result = await parse_playlist_intent(request.prompt)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))