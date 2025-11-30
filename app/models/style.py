"""Style models for handwriting styles."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class StyleCreateRequest(BaseModel):
    """Request model for creating a new style."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Name of the style")
    sample_ids: List[str] = Field(..., min_length=1, description="List of sample IDs to train the style on")
    description: Optional[str] = Field(None, description="Optional description of the style")


class StyleResponse(BaseModel):
    """Response model for a handwriting style."""
    
    id: str = Field(..., description="Unique style identifier")
    user_id: str = Field(..., description="User who created the style")
    name: str = Field(..., description="Style name")
    sample_ids: List[str] = Field(..., description="Sample IDs used for training")
    description: Optional[str] = Field(None, description="Style description")
    status: str = Field(..., description="Training status: pending, training, completed, failed")
    model_path: Optional[str] = Field(None, description="Path to trained model")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class StyleStatusResponse(BaseModel):
    """Response model for style training status."""
    
    id: str = Field(..., description="Style identifier")
    status: str = Field(..., description="Training status")
    progress: Optional[float] = Field(None, description="Training progress percentage (0-100)")
    message: Optional[str] = Field(None, description="Status message or error details")


class StyleDocument(BaseModel):
    """MongoDB document model for styles."""
    
    user_id: str
    name: str
    sample_ids: List[str]
    description: Optional[str] = None
    status: str = "pending"
    progress: Optional[float] = None
    message: Optional[str] = None
    model_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
