# app/ai/schemas/requests.py
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class GenerateRequest(BaseModel):
    user_id: str
    style_id: str
    text: str
    settings: Optional[Dict[str, Any]] = {}

class TrainStyleRequest(BaseModel):
    user_id: str
    sample_paths: List[str]
    name: Optional[str] = "default"
