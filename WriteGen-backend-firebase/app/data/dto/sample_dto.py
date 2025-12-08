from pydantic import BaseModel
from typing import Optional, Dict, Any

class SampleDTO(BaseModel):
    id: Optional[str]
    uid: str
    filename: str
    storage_path: str
    public_url: Optional[str]
    transcript: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    processed_path: Optional[str] = None
    status: str = "uploaded"
