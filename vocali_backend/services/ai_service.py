import httpx
import os
import json

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def parse_playlist_intent(prompt: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a music assistant. Parse the user's playlist request and return JSON only.

IMPORTANT: Calculate tracks_needed based on duration (average track = 3 minutes):
- 30 minutes = 10 tracks
- 1 hour = 20 tracks
- 2 hours = 40 tracks
- 3 hours = 60 tracks

For search_query: use genre + mood keywords in English, never use the word 'playlist'.

Return exactly this JSON:
{
  "search_query": "spotify search string",
  "genre": "detected genre",
  "bpm_hint": "slow/medium/fast",
  "duration_minutes": 120,
  "tracks_needed": 40
}"""
                    },
                    {"role": "user", "content": prompt}
                ],
                
            }
        )
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)