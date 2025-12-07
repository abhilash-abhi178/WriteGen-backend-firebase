# app/api/routes/samples.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid
from app.core.firebase import bucket, db
from app.api.routes.auth import get_current_user
import aiofiles
import os

router = APIRouter()
UPLOAD_TEMP = os.getenv("TEMP_DIR", "/tmp/writegen_uploads")
os.makedirs(UPLOAD_TEMP, exist_ok=True)

@router.post("/upload")
async def upload_samples(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload handwriting samples for style training."""
    uploaded = []
    uid = current_user["uid"]
    
    for f in files:
        # Validate file type
        if f.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {f.content_type}. Allowed: JPEG, PNG, WebP"
            )
        
        suffix = f.filename.split(".")[-1]
        tmp_path = os.path.join(UPLOAD_TEMP, f"{uuid.uuid4().hex}.{suffix}")
        
        async with aiofiles.open(tmp_path, "wb") as out_file:
            content = await f.read()
            if len(content) > 50 * 1024 * 1024:  # 50MB limit
                raise HTTPException(status_code=413, detail="File too large")
            await out_file.write(content)

        blob_path = f"samples/{uid}/{datetime.utcnow().timestamp()}_{f.filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(tmp_path)
        blob.make_public()

        sample_doc = {
            "uid": uid,
            "filename": f.filename,
            "storage_path": blob_path,
            "public_url": blob.public_url,
            "status": "uploaded",
            "size_bytes": len(content),
            "created_at": datetime.utcnow().isoformat()
        }
        doc_ref = db.collection("samples").document()
        doc_ref.set(sample_doc)
        uploaded.append({
            "id": doc_ref.id,
            "filename": sample_doc["filename"],
            "status": sample_doc["status"],
            "created_at": sample_doc["created_at"]
        })

        try:
            os.remove(tmp_path)
        except:
            pass

    return {
        "uploaded_count": len(uploaded),
        "samples": uploaded,
        "message": f"{len(uploaded)} samples uploaded successfully",
        "uploaded_at": datetime.utcnow().isoformat()
    }


@router.get("/")
async def list_samples(current_user: dict = Depends(get_current_user)):
    """List all samples uploaded by current user."""
    uid = current_user["uid"]
    samples = [
        {
            "id": d.id,
            "filename": d.get("filename"),
            "status": d.get("status"),
            "created_at": d.get("created_at")
        }
        for d in db.collection("samples").where("uid", "==", uid).stream()
    ]
    return {
        "samples": samples,
        "total": len(samples),
        "requested_at": datetime.utcnow().isoformat()
    }


@router.get("/{sample_id}")
async def get_sample(sample_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific sample."""
    uid = current_user["uid"]
    doc = db.collection("samples").document(sample_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return {
        "id": doc.id,
        "filename": data.get("filename"),
        "status": data.get("status"),
        "public_url": data.get("public_url"),
        "created_at": data.get("created_at"),
        "updated_at": data.get("updated_at")
    }


@router.put("/{sample_id}")
async def update_sample(
    sample_id: str,
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update sample metadata (e.g., mark as processed)."""
    uid = current_user["uid"]
    doc = db.collection("samples").document(sample_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    update_data = {}
    if status and status in ["uploaded", "processing", "processed", "error"]:
        update_data["status"] = status
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    db.collection("samples").document(sample_id).update(update_data)
    
    return {
        "id": sample_id,
        "updated": update_data,
        "message": "Sample updated successfully",
        "updated_at": datetime.utcnow().isoformat()
    }


@router.delete("/{sample_id}")
async def delete_sample(sample_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a sample."""
    uid = current_user["uid"]
    doc = db.collection("samples").document(sample_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Delete from cloud storage
    try:
        blob = bucket.blob(data.get("storage_path"))
        blob.delete()
    except:
        pass
    
    # Delete from database
    db.collection("samples").document(sample_id).delete()
    
    return {
        "id": sample_id,
        "status": "deleted",
        "message": "Sample deleted successfully",
        "deleted_at": datetime.utcnow().isoformat()
    }
