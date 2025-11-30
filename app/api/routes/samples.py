"""Sample routes for handling handwriting samples."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.core.firebase import get_current_user_id
from app.models.sample import SampleUploadRequest, SampleResponse, SampleDocument
from app.services.stroke_extraction import get_stroke_extraction_service

router = APIRouter(prefix="/samples", tags=["samples"])


@router.post(
    "/upload-from-url",
    response_model=SampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a handwriting sample from URL",
    description="Upload a handwriting sample image from a URL for stroke extraction.",
)
async def upload_sample_from_url(
    request: SampleUploadRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Upload a handwriting sample from a URL.
    
    The sample will be queued for stroke extraction processing.
    """
    # Validate the sample URL
    stroke_service = get_stroke_extraction_service()
    is_valid, error_msg = await stroke_service.validate_sample(str(request.url))
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg or "Invalid sample image",
        )
    
    # Create sample document
    now = datetime.utcnow()
    sample_doc = SampleDocument(
        user_id=user_id,
        url=str(request.url),
        description=request.description,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    
    # Insert into database
    result = await db.samples.insert_one(sample_doc.model_dump())
    sample_id = str(result.inserted_id)
    
    # TODO: Queue stroke extraction job in background
    
    return SampleResponse(
        id=sample_id,
        user_id=user_id,
        url=str(request.url),
        description=request.description,
        stroke_data=None,
        status="pending",
        created_at=now,
        updated_at=now,
    )
