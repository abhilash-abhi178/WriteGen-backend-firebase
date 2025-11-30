# app/api/routes/export.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.routes.auth import get_current_user
from app.core.firebase import db
from app.services.export_service import ExportService

router = APIRouter()
export_service = ExportService()

@router.post("/pdf")
async def export_pdf(job_id: str, dpi: int = 300, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    if job_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    pdf_path, storage_path = export_service.export_pdf_sync(job_id, dpi=dpi)
    return {"pdf_url": storage_path}
