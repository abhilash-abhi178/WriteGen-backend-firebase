"""Sample and handwriting upload schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, UUID4


class SampleType(str, Enum):
    GENERAL_HANDWRITING = "general"
    SIGNATURE = "signature"
    SYMBOL_SAMPLE = "symbol"
    EQUATION_SAMPLE = "equation"


class ImageMeta(BaseModel):
    """Image metadata."""
    width_px: int
    height_px: int
    mime_type: str
    file_size_bytes: int


class SampleBase(BaseModel):
    """Base sample model."""
    sample_type: SampleType = SampleType.GENERAL_HANDWRITING
    content_tags: List[str] = []


class SampleCreate(SampleBase):
    """Sample creation schema (for upload requests)."""
    pass


class SampleResponse(SampleBase):
    """Sample response model."""
    sample_id: UUID4
    user_id: UUID4
    original_filename: str
    image_meta: ImageMeta
    s3_path: str
    transcription: str
    transcription_confidence: float
    uploaded_at: datetime
    ephemeral: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "sample_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440001",
                "original_filename": "handwriting.jpg",
                "sample_type": "general",
                "image_meta": {
                    "width_px": 2480,
                    "height_px": 3508,
                    "mime_type": "image/jpeg",
                    "file_size_bytes": 1024000
                },
                "transcription": "The quick brown fox...",
                "transcription_confidence": 0.92
            }
        }


class SampleUpdate(BaseModel):
    """Sample update schema."""
    transcription: Optional[str] = None
    content_tags: Optional[List[str]] = None
