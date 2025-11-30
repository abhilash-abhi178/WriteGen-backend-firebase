# app/api/routes/styles.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from datetime import datetime
from app.core.firebase import db
from app.api.routes.auth import get_current_user
from app.services.style_service import StyleService

router = APIRouter()
style_service = StyleService()

@router.post("/create")
async def create_style(sample_ids: List[str], style_name: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
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

    return {"style_id": style_id, "status": "training", "message": "Style training started"}

@router.get("/")
async def list_styles(current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    styles = [d.to_dict() | {"id": d.id} for d in db.collection("styles").where("uid", "==", uid).stream()]
    return {"styles": styles}

@router.get("/{style_id}")
async def get_style(style_id: str, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    doc = db.collection("styles").document(style_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Style not found")
    data = doc.to_dict()
    if data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"id": doc.id, **data}
