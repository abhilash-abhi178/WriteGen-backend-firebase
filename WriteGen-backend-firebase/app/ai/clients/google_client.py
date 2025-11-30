# minimal Google Generative AI client using httpx (replace with official sdk if desired)
import os
import httpx
from typing import Dict, Any, Optional

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

class GoogleAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GOOGLE_API_KEY
        self._base = "https://generativelanguage.googleapis.com/v1beta2"

    async def _post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        params = {"key": self.api_key}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(f"{self._base}{path}", json=json, params=params)
            r.raise_for_status()
            return r.json()

    async def text_generate(self, prompt: str, model: str = "models/text-bison-001", max_output_tokens: int = 512) -> Dict[str, Any]:
        body = {"model": model, "prompt": {"text": prompt}, "maxOutputTokens": max_output_tokens}
        return await self._post("/models:generateText", body)
