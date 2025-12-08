# async client wrapper for OpenAI usage (text + images)
import os
import asyncio
from typing import Any, Dict, Optional
import httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self._base = "https://api.openai.com/v1"

    async def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self._base}{path}", json=json, headers=headers)
            r.raise_for_status()
            return r.json()

    async def create_image(self, prompt: str, size: str = "1024x1024", n: int = 1) -> Dict[str, Any]:
        """
        Example minimal wrapper for image generation (DALL·E style).
        """
        payload = {"prompt": prompt, "n": n, "size": size}
        return await self._post("/images/generations", payload)

    async def create_text_completion(self, prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 512) -> Dict[str, Any]:
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.2
        }
        return await self._post("/completions", payload)
