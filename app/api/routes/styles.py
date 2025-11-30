"""Style routes for handling handwriting styles."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.core.database import get_database
from app.core.firebase import get_current_user_id
from app.models.style import (
    StyleCreateRequest,
    StyleResponse,
    StyleStatusResponse,
    StyleDocument,
)
from app.services.style_training import get_style_training_service

router = APIRouter(prefix="/styles", tags=["styles"])


@router.post(
    "/create",
    response_model=StyleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new handwriting style",
    description="Create a new handwriting style from sample IDs and queue for training.",
)
async def create_style(
    request: StyleCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Create a new handwriting style from samples.
    
    The style will be queued for training using the provided samples.
    """
    # Verify all sample IDs exist and belong to the user
    sample_ids = request.sample_ids
    
    for sample_id in sample_ids:
        try:
            sample = await db.samples.find_one({
                "_id": ObjectId(sample_id),
                "user_id": user_id,
            })
            if not sample:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sample {sample_id} not found or does not belong to user",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sample ID: {sample_id}",
            )
    
    # Create style document
    now = datetime.utcnow()
    style_doc = StyleDocument(
        user_id=user_id,
        name=request.name,
        sample_ids=sample_ids,
        description=request.description,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    
    # Insert into database
    result = await db.styles.insert_one(style_doc.model_dump())
    style_id = str(result.inserted_id)
    
    # TODO: Queue style training job in background
    
    return StyleResponse(
        id=style_id,
        user_id=user_id,
        name=request.name,
        sample_ids=sample_ids,
        description=request.description,
        status="pending",
        model_path=None,
        created_at=now,
        updated_at=now,
    )


@router.get(
    "/{style_id}/status",
    response_model=StyleStatusResponse,
    summary="Get style training status",
    description="Get the training status of a handwriting style.",
)
async def get_style_status(
    style_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Get the training status of a style.
    """
    try:
        style = await db.styles.find_one({
            "_id": ObjectId(style_id),
            "user_id": user_id,
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid style ID",
        )
    
    if not style:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Style not found",
        )
    
    return StyleStatusResponse(
        id=style_id,
        status=style.get("status", "unknown"),
        progress=style.get("progress"),
        message=style.get("message"),
    )
