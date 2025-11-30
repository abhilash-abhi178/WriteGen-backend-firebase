"""Sample models for handwriting samples."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class SampleUploadRequest(BaseModel):
    """Request model for uploading a sample from URL."""
    
    url: HttpUrl = Field(..., description="URL of the handwriting sample image")
    description: Optional[str] = Field(None, description="Optional description of the sample")


class SampleResponse(BaseModel):
    """Response model for a handwriting sample."""
    
    id: str = Field(..., description="Unique sample identifier")
    user_id: str = Field(..., description="User who uploaded the sample")
    url: str = Field(..., description="URL of the sample image")
    description: Optional[str] = Field(None, description="Sample description")
    stroke_data: Optional[dict] = Field(None, description="Extracted stroke data")
    status: str = Field(..., description="Processing status: pending, processing, completed, failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class SampleDocument(BaseModel):
    """MongoDB document model for samples."""
    
    user_id: str
    url: str
    description: Optional[str] = None
    stroke_data: Optional[dict] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
