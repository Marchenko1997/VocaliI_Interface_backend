from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..services.ai_service import parse_playlist_intent
from ..services.spotify_serv import search_tracks
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
        ai_params = await parse_playlist_intent(request.prompt)
        
        tracks_needed = ai_params.get("tracks_needed", 20)
        search_query = ai_params.get("search_query", request.prompt)
        
   
        all_tracks = []
        offset = 0
        batch_size = 10
        
        while len(all_tracks) < tracks_needed:
            spotify_result = await search_tracks(
                q=search_query,
                limit=batch_size,
                offset=offset
            )
            
            items = spotify_result.get("tracks", {}).get("items", [])
            if not items:
                break  
                
            for item in items:
                all_tracks.append({
                    "id": item["id"],
                    "name": item["name"],
                    "artist": item["artists"][0]["name"],
                    "album": item["album"]["name"],
                    "duration_ms": item["duration_ms"],
                    "preview_url": item.get("preview_url"),
                    "image": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                    "uri": item["uri"]
                })
            
            offset += batch_size
        
        return {
            "ai_params": ai_params,
            "tracks": all_tracks[:tracks_needed]  
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))