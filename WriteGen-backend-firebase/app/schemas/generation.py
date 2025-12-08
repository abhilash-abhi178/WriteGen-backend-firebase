# app/schemas/generation.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class GenerationRequest(BaseModel):
    style_id: str
    text: str
    settings: Optional[Dict[str, Any]] = {}
