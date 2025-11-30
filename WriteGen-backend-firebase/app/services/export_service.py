# app/services/export_service.py
from app.core.firebase import db, bucket
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from app.core.config import settings

class ExportService:
    def __init__(self):
        self.output_dir = settings.temp_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_pdf_sync(self, job_id: str, dpi: int = 300):
        job_ref = db.collection("generation_jobs").document(job_id)
        job = job_ref.get().to_dict()
        uid = job["uid"]
        result_path = job.get("result_path") or job.get("result_storage_path") or job.get("result_url")
        # If result is an SVG stored in storage, download it — simplified: create simple pdf with text of job
        pdf_path = os.path.join(self.output_dir, f"{job_id}.pdf")
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 800, f"WriteGen Export for job {job_id}")
        c.drawString(100, 780, f"Generated: {datetime.utcnow().isoformat()}")
        c.save()

        storage_path = f"exports/{uid}/{job_id}.pdf"
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(pdf_path)
        blob.make_public()

        job_ref.update({"export_pdf": blob.public_url})
        return pdf_path, blob.public_url
