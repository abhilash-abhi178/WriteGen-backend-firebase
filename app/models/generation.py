"""Generation job models for handwriting generation."""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request model for generating handwritten text."""
    
    style_id: str = Field(..., description="ID of the style to use for generation")
    text: str = Field(..., min_length=1, max_length=10000, description="Text to convert to handwriting")
    output_format: Literal["pdf", "svg", "png"] = Field("pdf", description="Output format for the generated handwriting")


class GenerateResponse(BaseModel):
    """Response model for generation job creation."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    message: str = Field(..., description="Status message")


class GenerationJobResultResponse(BaseModel):
    """Response model for generation job result."""
    
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    output_url: Optional[str] = Field(None, description="URL to download the generated output")
    output_format: Optional[str] = Field(None, description="Output format")
    error_message: Optional[str] = Field(None, description="Error message if job failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Job completion timestamp")


class GenerationJobDocument(BaseModel):
    """MongoDB document model for generation jobs."""
    
    user_id: str
    style_id: str
    text: str
    output_format: str = "pdf"
    status: str = "pending"
    output_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
