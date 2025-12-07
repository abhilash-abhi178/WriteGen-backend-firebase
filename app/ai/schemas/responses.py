# app/ai/schemas/responses.py
from pydantic import BaseModel
from typing import Any, Dict, Optional

class GenerateResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    result_path: Optional[str] = None
    error: Optional[str] = None

class StyleProfileResponse(BaseModel):
    style_id: str
    user_id: str
    profile: Dict[str, Any]
