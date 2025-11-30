"""Generation routes for handwriting generation."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from app.core.database import get_database
from app.core.firebase import get_current_user_id
from app.models.generation import (
    GenerateRequest,
    GenerateResponse,
    GenerationJobResultResponse,
    GenerationJobDocument,
)
from app.services.generation import get_generation_service

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post(
    "",
    response_model=GenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate handwritten text",
    description="Generate handwritten text using a trained style.",
)
async def generate_handwriting(
    request: GenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Generate handwritten text using a trained style.
    
    Returns a job ID that can be used to check the generation status.
    """
    # Verify the style exists and belongs to the user
    try:
        object_id = ObjectId(request.style_id)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid style ID format",
        )
    
    style = await db.styles.find_one({
        "_id": object_id,
        "user_id": user_id,
    })
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found",
        )
    
    # Check if style training is completed
    if style.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Style is not ready for generation. Current status: {style.get('status')}",
        )
    
    # Create generation job document
    now = datetime.utcnow()
    job_doc = GenerationJobDocument(
        user_id=user_id,
        style_id=request.style_id,
        text=request.text,
        output_format=request.output_format,
        status="pending",
        created_at=now,
    )
    
    # Insert into database
    result = await db.generation_jobs.insert_one(job_doc.model_dump())
    job_id = str(result.inserted_id)
    
    # TODO: Queue generation job in background
    
    return GenerateResponse(
        job_id=job_id,
        status="pending",
        message="Generation job queued successfully",
    )


@router.get(
    "/jobs/{job_id}/result",
    response_model=GenerationJobResultResponse,
    summary="Get generation job result",
    description="Get the result of a handwriting generation job.",
)
async def get_generation_result(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get the result of a generation job.
    """
    try:
        object_id = ObjectId(job_id)
    except (InvalidId, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid job ID format",
        )
    
    job = await db.generation_jobs.find_one({
        "_id": object_id,
        "user_id": user_id,
    })
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation job not found",
        )
    
    return GenerationJobResultResponse(
        job_id=job_id,
        status=job.get("status", "unknown"),
        output_url=job.get("output_url"),
        output_format=job.get("output_format"),
        error_message=job.get("error_message"),
        created_at=job.get("created_at"),
        completed_at=job.get("completed_at"),
    )
