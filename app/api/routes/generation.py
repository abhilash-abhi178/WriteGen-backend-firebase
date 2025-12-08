# app/api/routes/generation.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from typing import List, Optional, Dict
from pydantic import BaseModel
from app.api.routes.auth import get_current_user
# Use mock database fallback
try:
    from app.core.firebase import db
except:
    from app.core.mock_db import mock_db as db
from datetime import datetime
import uuid
try:
    from app.services.generation_service import GenerationService
except:
    GenerationService = None

router = APIRouter()
if GenerationService:
    generation_service = GenerationService()
else:
    generation_service = None


class DocumentCreate(BaseModel):
    title: str
    content: str
    fontSize: Optional[int] = 16
    lineHeight: Optional[float] = 1.5
    fontStyle: Optional[str] = "normal"


def run_generation_job(job_id: str):
    """Background task to run generation job."""
    gen_service = GenerationService()
    job_ref = db.collection("generation_jobs").document(job_id)
    try:
        job_ref.update({"status": "processing", "progress": 0.05})
        gen_service.generate_job_sync(job_id)
        job_ref.update({
            "status": "completed",
            "progress": 1.0,
            "completed_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        job_ref.update({
            "status": "error",
            "error": str(e),
            "failed_at": datetime.utcnow().isoformat()
        })


@router.post("/")
async def generate(
    style_id: str,
    text: str,
    pen_settings: Optional[Dict] = None,
    page_settings: Optional[Dict] = None,
    background_tasks: BackgroundTasks = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new handwriting generation job."""
    uid = current_user["uid"]
    
    # Validate style exists and belongs to user
    style_doc = db.collection("styles").document(style_id).get()
    if not style_doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    style_data = style_doc.to_dict()
    if style_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    job_id = uuid.uuid4().hex
    job_doc = {
        "uid": uid,
        "style_id": style_id,
        "text": text,
        "pen_settings": pen_settings or {},
        "page_settings": page_settings or {},
        "status": "queued",
        "progress": 0.0,
        "created_at": datetime.utcnow().isoformat()
    }
    db.collection("generation_jobs").document(job_id).set(job_doc)
    
    background_tasks.add_task(run_generation_job, job_id)
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Generation job created",
        "created_at": datetime.utcnow().isoformat()
    }


@router.get("/{job_id}")
async def get_generation_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of a generation job."""
    uid = current_user["uid"]
    job_doc = db.collection("generation_jobs").document(job_id).get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_doc.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {
        "job_id": job_id,
        "status": job_data.get("status"),
        "progress": job_data.get("progress", 0.0),
        "text": job_data.get("text"),
        "style_id": job_data.get("style_id"),
        "created_at": job_data.get("created_at"),
        "completed_at": job_data.get("completed_at"),
        "error": job_data.get("error")
    }


@router.get("/{job_id}/result")
async def get_generation_result(
    job_id: str,
    format: str = "png",
    current_user: dict = Depends(get_current_user)
):
    """Get the result of a completed generation job."""
    uid = current_user["uid"]
    job_doc = db.collection("generation_jobs").document(job_id).get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_doc.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    if job_data.get("status") != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Current status: {job_data.get('status')}"
        )
    
    result_url = job_data.get("result_url")
    if not result_url:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return {
        "job_id": job_id,
        "format": format,
        "result_url": result_url,
        "created_at": job_data.get("created_at"),
        "completed_at": job_data.get("completed_at")
    }


@router.post("/{job_id}/cancel")
async def cancel_generation_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a queued or processing generation job."""
    uid = current_user["uid"]
    job_doc = db.collection("generation_jobs").document(job_id).get()
    if not job_doc.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = job_doc.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    status = job_data.get("status")
    if status == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    elif status == "error":
        raise HTTPException(status_code=400, detail="Job already failed")
    
    db.collection("generation_jobs").document(job_id).update({
        "status": "cancelled",
        "cancelled_at": datetime.utcnow().isoformat()
    })
    
    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled successfully",
        "cancelled_at": datetime.utcnow().isoformat()
    }


@router.post("/batch")
async def batch_generate(
    style_id: str,
    texts: List[str],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Generate multiple handwriting documents in batch."""
    uid = current_user["uid"]
    
    # Validate style exists
    style_doc = db.collection("styles").document(style_id).get()
    if not style_doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    style_data = style_doc.to_dict()
    if style_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    batch_id = uuid.uuid4().hex
    job_ids = []
    
    for text in texts:
        job_id = uuid.uuid4().hex
        job_doc = {
            "uid": uid,
            "batch_id": batch_id,
            "style_id": style_id,
            "text": text,
            "status": "queued",
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat()
        }
        db.collection("generation_jobs").document(job_id).set(job_doc)
        job_ids.append(job_id)
        background_tasks.add_task(run_generation_job, job_id)
    
    return {
        "batch_id": batch_id,
        "job_ids": job_ids,
        "total": len(job_ids),
        "status": "queued",
        "message": f"{len(job_ids)} generation jobs queued",
        "created_at": datetime.utcnow().isoformat()
    }


@router.post("/create")
async def create_document(
    doc_data: DocumentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new document for handwriting generation."""
    user_id = current_user.get("user_id") or current_user.get("uid")
    
    document = {
        "uid": user_id,
        "title": doc_data.title,
        "content": doc_data.content,
        "fontSize": doc_data.fontSize,
        "lineHeight": doc_data.lineHeight,
        "fontStyle": doc_data.fontStyle,
        "status": "draft",
        "page_count": max(1, len(doc_data.content) // 500),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    doc_ref = db.collection("documents").document()
    doc_ref.set(document)
    
    return {
        "document_id": doc_ref.id,
        "id": doc_ref.id,
        "status": "created",
        "message": "Document created successfully"
    }


@router.get("/documents")
async def list_user_documents(current_user: dict = Depends(get_current_user)):
    """Get user's documents."""
    user_id = current_user.get("user_id") or current_user.get("uid")
    
    documents = []
    for doc in db.collection("documents").where("uid", "==", user_id).stream():
        doc_data = doc.to_dict()
        documents.append({
            "id": doc.id,
            "name": doc_data.get("title", "Untitled"),
            "lastModified": doc_data.get("updated_at", doc_data.get("created_at", "Unknown")),
            "status": doc_data.get("status", "draft")
        })
    
    return documents
