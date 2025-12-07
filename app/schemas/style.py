"""Style and handwriting model schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, UUID4


class PrivacyLevel(str, Enum):
    PRIVATE = "private"
    SHARED_WITH_ORG = "shared_with_org"
    PUBLIC = "public"


class PenType(str, Enum):
    BALLPOINT = "ballpoint"
    GEL = "gel"
    FOUNTAIN = "fountain"
    FELT_TIP = "felt_tip"


class EmbeddingMeta(BaseModel):
    """Style embedding metadata."""
    embedding_b64: str
    slant_angle_deg: float
    avg_stroke_width_px: float
    pressure_intensity: float  # 0.0 to 1.0
    pen_type: str
    covered_glyphs: List[str]
    sample_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "embedding_b64": "base64_encoded_512d_vector",
                "slant_angle_deg": 12.5,
                "avg_stroke_width_px": 1.2,
                "pressure_intensity": 0.8,
                "pen_type": "ballpoint",
                "covered_glyphs": ["a", "b", "c", "0", "1", "∫"],
                "sample_count": 2
            }
        }


class StyleSettings(BaseModel):
    """Style customization settings."""
    realism: float = 0.8  # 0.0 to 1.0
    imperfection: float = 0.5  # 0.0 to 1.0
    ink_color: str = "black"
    stroke_thickness: float = 1.0  # 0.5 to 3.0 mm
    batch_adapter_steps: int = 500


class StyleBase(BaseModel):
    """Base style model."""
    name: str
    privacy: PrivacyLevel = PrivacyLevel.PRIVATE
    settings: StyleSettings


class StyleCreate(StyleBase):
    """Style creation schema."""
    sample_ids: List[UUID4]
    processing_mode: str = "cloud"


class StyleResponse(StyleBase):
    """Style response model."""
    style_id: UUID4
    user_id: UUID4
    embedding_meta: EmbeddingMeta
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    is_signature_style: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "style_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "name": "My Formal Handwriting",
                "privacy": "private",
                "settings": {
                    "realism": 0.8,
                    "imperfection": 0.5,
                    "ink_color": "black"
                }
            }
        }


class StyleUpdate(BaseModel):
    """Style update schema."""
    name: Optional[str] = None
    settings: Optional[StyleSettings] = None
    privacy: Optional[PrivacyLevel] = None


class StylePreset(BaseModel):
    """Pre-made style preset."""
    preset_id: UUID4
    name: str
    embedding_meta: EmbeddingMeta
    is_public: bool = True
