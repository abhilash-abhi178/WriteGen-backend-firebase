# app/models/sample.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class Sample(BaseModel):
    id: Optional[str]
    uid: str
    filename: str
    storage_path: str
    public_url: Optional[str]
    metadata: Optional[Dict[str, Any]]
    status: Optional[str]
    created_at: Optional[str]
