# app/api/routes/generation.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from app.api.routes.auth import get_current_user
from app.core.firebase import db
from datetime import datetime
import uuid
from app.services.generation_service import GenerationService

router = APIRouter()
generation_service = GenerationService()

@router.post("/")
async def generate(request: dict, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    job_id = uuid.uuid4().hex
    job_doc = {
        "uid": uid,
        "job_id": job_id,
        "request": request,
        "status": "queued",
        "created_at": datetime.utcnow().isoformat(),
        "progress": 0.0
    }
    db.collection("generation_jobs").document(job_id).set(job_doc)

    background_tasks.add_task(run_generation_job, job_id)

    return {"job_id": job_id, "status": "queued"}

def run_generation_job(job_id: str):
    gen_service = GenerationService()
    job_ref = db.collection("generation_jobs").document(job_id)
    job_doc = job_ref.get().to_dict()
    try:
        job_ref.update({"status": "processing", "progress": 0.05})
        gen_service.generate_job_sync(job_id)
        job_ref.update({"status": "completed", "progress": 1.0, "completed_at": datetime.utcnow().isoformat()})
    except Exception as e:
        job_ref.update({"status": "error", "error": str(e)})
