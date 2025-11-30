# app/ai/models/style_profile.py
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class StyleProfile:
    user_id: str
    name: str
    profile: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {"user_id": self.user_id, "name": self.name, "profile": self.profile}
