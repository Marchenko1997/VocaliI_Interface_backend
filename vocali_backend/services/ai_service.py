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
                        "content": """You are a music assistant. Parse the user's playlist request and return JSON only:
                        {
                          "search_query": "spotify search string",
                          "genre": "lofi/chill/etc",
                          "bpm_hint": "slow/medium/fast",
                          "duration_minutes": 120,
                          "tracks_needed": 30
                        }"""
                    },
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
        )
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)  