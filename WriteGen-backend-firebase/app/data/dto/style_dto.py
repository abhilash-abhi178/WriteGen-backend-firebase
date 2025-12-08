from pydantic import BaseModel
from typing import Optional, Dict, List

class StyleDTO(BaseModel):
    id: Optional[str]
    uid: str
    name: str
    sample_ids: List[str]
    profile: Optional[Dict] = {}
    status: str = "trained"
