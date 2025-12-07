# app/api/routes/export.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.routes.auth import get_current_user
from app.core.firebase import db
from app.services.export_service import ExportService
from datetime import datetime

router = APIRouter()
export_service = ExportService()

@router.post("/pdf")
async def export_pdf(job_id: str, dpi: int = 300, current_user: dict = Depends(get_current_user)):
    """Export generation job result as PDF."""
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    if job_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    try:
        pdf_path, storage_url = export_service.export_pdf_sync(job_id, dpi=dpi)
        return {
            "format": "pdf",
            "job_id": job_id,
            "download_url": storage_url,
            "dpi": dpi,
            "exported_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/png")
async def export_png(job_id: str, dpi: int = 300, current_user: dict = Depends(get_current_user)):
    """Export generation job result as PNG image."""
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    if job_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    try:
        png_path, storage_url = export_service.export_png_sync(job_id, dpi=dpi)
        return {
            "format": "png",
            "job_id": job_id,
            "download_url": storage_url,
            "dpi": dpi,
            "exported_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.post("/svg")
async def export_svg(job_id: str, current_user: dict = Depends(get_current_user)):
    """Export generation job result as SVG vector format."""
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    if job_data.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    try:
        svg_path, storage_url = export_service.export_svg_sync(job_id)
        return {
            "format": "svg",
            "job_id": job_id,
            "download_url": storage_url,
            "exported_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{job_id}/status")
async def export_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """Get export job status."""
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    exports = {}
    if job_data.get("export_pdf"):
        exports["pdf"] = job_data.get("export_pdf")
    if job_data.get("export_png"):
        exports["png"] = job_data.get("export_png")
    if job_data.get("export_svg"):
        exports["svg"] = job_data.get("export_svg")
    
    return {
        "job_id": job_id,
        "generation_status": job_data.get("status"),
        "exports": exports,
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/{job_id}/download")
async def download_export(
    job_id: str,
    format: str = "pdf",
    current_user: dict = Depends(get_current_user)
):
    """Download exported file in specified format."""
    uid = current_user["uid"]
    job = db.collection("generation_jobs").document(job_id).get()
    if not job.exists:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = job.to_dict()
    if job_data.get("uid") != uid:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    format_key = f"export_{format}"
    if format_key not in job_data or not job_data.get(format_key):
        raise HTTPException(status_code=404, detail=f"Export not found for format: {format}")
    
    return {
        "job_id": job_id,
        "format": format,
        "download_url": job_data.get(format_key),
        "expires_in_hours": 24,
        "request_time": datetime.utcnow().isoformat()
    }

