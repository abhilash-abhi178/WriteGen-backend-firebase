# app/services/generation_service.py
import svgwrite
import os
from app.core.firebase import db, bucket
from datetime import datetime
from typing import Dict
from app.core.config import settings

class GenerationService:
    def __init__(self):
        self.output_dir = settings.temp_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_job_sync(self, job_id: str):
        job_ref = db.collection("generation_jobs").document(job_id)
        job = job_ref.get().to_dict()
        uid = job["uid"]
        request = job.get("request", {})
        text = request.get("text", "Hello from WriteGen")

        output_path = os.path.join(self.output_dir, f"{job_id}.svg")
        dwg = svgwrite.Drawing(output_path, size=("2480px", "3508px"))
        dwg.add(dwg.text(text[:400], insert=(100, 100), font_size="20px"))
        dwg.save()

        storage_path = f"generated/{uid}/{job_id}.svg"
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(output_path)
        blob.make_public()

        job_ref.update({"result_url": blob.public_url, "result_storage_path": storage_path, "progress": 1.0, "status": "completed", "completed_at": datetime.utcnow().isoformat()})
        return {"result_url": blob.public_url}
