import base64
import time
import httpx
import os
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# кеш токена
spotify_token_cache = {
    "access_token": None,
    "expires_at": 0
}


async def get_spotify_token():
   
    if (
        spotify_token_cache["access_token"]
        and time.time() < spotify_token_cache["expires_at"]
    ):
        return spotify_token_cache["access_token"]

 
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )

    data = response.json()


    spotify_token_cache["access_token"] = data["access_token"]
    spotify_token_cache["expires_at"] = time.time() + data["expires_in"] - 60

    return spotify_token_cache["access_token"]


async def search_tracks(q: str, offset: int = 0, limit: int = 20):
    token = await get_spotify_token()

    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.spotify.com/v1/search",
            params={
                "q": q,
                "type": "track",
                "limit": limit,      
                "offset": offset,    
            },
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

    return res.json()