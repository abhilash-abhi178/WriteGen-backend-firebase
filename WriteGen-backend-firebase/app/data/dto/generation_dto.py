from pydantic import BaseModel
from typing import Dict, Any, Optional

class GenerationJobDTO(BaseModel):
    job_id: str
    uid: str
    request: Dict[str, Any]
    progress: float
    status: str
    result_url: Optional[str] = None
