# app/ai/models/generation_job.py
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class GenerationJob:
    job_id: str
    user_id: str
    style_id: str
    text: str
    settings: Dict[str, Any] = field(default_factory=dict)
    status: str = "queued"
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    result_path: str = None
    error: str = None

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "user_id": self.user_id,
            "style_id": self.style_id,
            "text": self.text,
            "settings": self.settings,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "result_path": self.result_path,
            "error": self.error
        }
