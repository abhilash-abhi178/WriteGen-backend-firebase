# app/ai/models/stroke.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Stroke:
    path: str
    bbox: Optional[List[int]] = None
    closed: bool = False
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self):
        return {"path": self.path, "bbox": self.bbox, "closed": self.closed, "meta": self.meta or {}}
