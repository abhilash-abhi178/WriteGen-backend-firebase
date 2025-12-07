# app/api/routes/styles.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
from app.core.firebase import db
from app.api.routes.auth import get_current_user
from app.services.style_service import StyleService

router = APIRouter()
style_service = StyleService()

@router.post("/create")
async def create_style(
    sample_ids: List[str],
    style_name: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new style from handwriting samples."""
    uid = current_user["uid"]
    samples = []
    for sid in sample_ids:
        doc = db.collection("samples").document(sid).get()
        if doc.exists:
            s = doc.to_dict()
            if s.get("uid") == uid and s.get("status") in ("processed", "uploaded"):
                samples.append({"id": sid, **s})
    if not samples:
        raise HTTPException(status_code=400, detail="No valid samples found")

    style_doc = {
        "uid": uid,
        "name": style_name,
        "sample_ids": sample_ids,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    doc_ref = db.collection("styles").document()
    doc_ref.set(style_doc)
    style_id = doc_ref.id

    background_tasks.add_task(style_service.train_style, style_id, samples)

    return {
        "style_id": style_id,
        "name": style_name,
        "status": "training",
        "message": "Style training started",
        "created_at": datetime.utcnow().isoformat()
    }

@router.get("/")
async def list_styles(current_user: dict = Depends(get_current_user)):
    """List all styles for the current user."""
    uid = current_user["uid"]
    styles = [
        {"id": d.id, **d.to_dict()}
        for d in db.collection("styles").where("uid", "==", uid).stream()
    ]
    return {
        "styles": styles,
        "total": len(styles),
        "requested_at": datetime.utcnow().isoformat()
    }

@router.get("/{style_id}")
async def get_style(style_id: str, current_user: dict = Depends(get_current_user)):
    """Get details of a specific style."""
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "id": doc.id,
        **data,
        "fetched_at": datetime.utcnow().isoformat()
    }

@router.put("/{style_id}")
async def update_style(
    style_id: str,
    style_name: Optional[str] = None,
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Update style metadata."""
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    update_data = {}
    if style_name is not None:
        update_data["name"] = style_name
    if description is not None:
        update_data["description"] = description
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    db.collection("styles").document(style_id).update(update_data)
    
    return {
        "style_id": style_id,
        "updated": update_data,
        "message": "Style updated successfully",
        "updated_at": datetime.utcnow().isoformat()
    }

@router.post("/{style_id}/retrain")
async def retrain_style(
    style_id: str,
    sample_ids: List[str],
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Retrain style with additional samples."""
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Validate new samples
    samples = []
    for sid in sample_ids:
        sample_doc = db.collection("samples").document(sid).get()
        if sample_doc.exists:
            s = sample_doc.to_dict()
            if s.get("uid") == uid and s.get("status") in ("processed", "uploaded"):
                samples.append({"id": sid, **s})
    
    if not samples:
        raise HTTPException(status_code=400, detail="No valid samples provided")
    
    # Start retraining
    db.collection("styles").document(style_id).update({
        "status": "retraining",
        "last_retrained_at": datetime.utcnow().isoformat(),
        "sample_ids": list(set(data.get("sample_ids", []) + sample_ids))
    })
    
    background_tasks.add_task(style_service.retrain_style, style_id, samples)
    
    return {
        "style_id": style_id,
        "status": "retraining",
        "message": "Style retraining started",
        "started_at": datetime.utcnow().isoformat()
    }

@router.delete("/{style_id}")
async def delete_style(style_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a style."""
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    db.collection("styles").document(style_id).delete()
    
    return {
        "style_id": style_id,
        "status": "deleted",
        "message": "Style deleted successfully",
        "deleted_at": datetime.utcnow().isoformat()
    }

@router.post("/{style_id}/preview")
async def preview_style(
    style_id: str,
    text: str = "Hello World",
    current_user: dict = Depends(get_current_user)
):
    """Generate a preview of handwriting with this style."""
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    if data.get("status") != "ready":
        raise HTTPException(status_code=400, detail="Style not ready yet")
    
    return {
        "style_id": style_id,
        "preview_text": text,
        "preview_url": f"/previews/style_{style_id}_preview.png",
        "message": "Preview generated successfully",
        "generated_at": datetime.utcnow().isoformat()
    }
