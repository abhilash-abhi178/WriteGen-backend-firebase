"""Sample upload and management routes."""

import logging
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from datetime import datetime

from app.api.routes.auth import get_current_user
from app.schemas import sample as sample_schemas
from app.services.image_processor import ImageProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/samples", tags=["samples"])

# Mock storage
samples_db = {}
image_processor = ImageProcessor()


@router.post("/upload", response_model=sample_schemas.SampleResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_sample(
    file: UploadFile = File(...),
    sample_type: str = "general",
    content_tags: List[str] = [],
    current_user: dict = Depends(get_current_user)
):
    """Upload handwriting sample for style training."""
    logger.info(f"Upload sample from user {current_user['user_id']}: {file.filename}")
    
    # Validate file
    if file.size > settings.max_sample_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.max_sample_size_mb}MB limit"
        )
    
    if file.content_type not in ["image/jpeg", "image/png", "image/tiff"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, TIFF images supported"
        )
    
    # Read file
    contents = await file.read()
    
    # Process image
    image = await image_processor.load_from_bytes(contents)
    image_meta = await image_processor.get_image_meta(image, file.filename)
    
    # Auto-OCR/HWR for transcription
    transcription = "Sample handwriting text"  # Mock HWR
    confidence = 0.85
    
    # Store sample
    sample_id = str(uuid.uuid4())
    sample = {
        "sample_id": sample_id,
        "user_id": current_user["user_id"],
        "original_filename": file.filename,
        "sample_type": sample_type,
        "image_meta": image_meta,
        "s3_path": f"samples/{current_user['user_id']}/{sample_id}.jpg",
        "transcription": transcription,
        "transcription_confidence": confidence,
        "content_tags": content_tags,
        "uploaded_at": datetime.utcnow(),
        "ephemeral": False
    }
    
    samples_db[sample_id] = sample
    logger.info(f"Sample {sample_id} uploaded successfully")
    
    return sample_schemas.SampleResponse(**sample)


@router.get("/", response_model=List[sample_schemas.SampleResponse])
async def list_samples(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    """List user's handwriting samples."""
    user_samples = [
        s for s in samples_db.values()
        if s["user_id"] == current_user["user_id"]
    ]
    return [sample_schemas.SampleResponse(**s) for s in user_samples[skip:skip+limit]]


@router.get("/{sample_id}", response_model=sample_schemas.SampleResponse)
async def get_sample(
    sample_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific sample."""
    sample = samples_db.get(sample_id)
    
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sample not found"
        )
    
    if sample["user_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access"
        )
    
    return sample_schemas.SampleResponse(**sample)


@router.put("/{sample_id}", response_model=sample_schemas.SampleResponse)
async def update_sample(
    sample_id: str,
    update: sample_schemas.SampleUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update sample (e.g., correct transcription)."""
    sample = samples_db.get(sample_id)
    
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if sample["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    if update.transcription:
        sample["transcription"] = update.transcription
    if update.content_tags:
        sample["content_tags"] = update.content_tags
    
    samples_db[sample_id] = sample
    logger.info(f"Sample {sample_id} updated")
    
    return sample_schemas.SampleResponse(**sample)


@router.delete("/{sample_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sample(
    sample_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete sample."""
    sample = samples_db.get(sample_id)
    
    if not sample:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    if sample["user_id"] != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    del samples_db[sample_id]
    logger.info(f"Sample {sample_id} deleted")
    
    return None
