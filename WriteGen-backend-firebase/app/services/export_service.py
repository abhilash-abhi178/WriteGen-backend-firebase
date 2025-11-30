# app/services/export_service.py
import os
import cv2
from PIL import Image
from app.core.firebase import db, bucket
from datetime import datetime
from app.core.config import settings


class ExportService:
    def __init__(self):
        self.output_dir = settings.temp_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export_pdf_sync(self, job_id: str, dpi: int = 300):
        job_ref = db.collection("generation_jobs").document(job_id)
        job = job_ref.get().to_dict()
        uid = job.get("uid")
        result_storage = job.get("result_storage_path")
        result_url = job.get("result_url")
        pdf_path = os.path.join(self.output_dir, f"{job_id}.pdf")

        # Determine local image path
        local_image = os.path.join(self.output_dir, f"{job_id}_result.png")
        image_used = None

        # If there's a storage path, download the blob
        if result_storage:
            try:
                blob = bucket.blob(result_storage)
                blob.download_to_filename(local_image)
                image_used = local_image
            except Exception:
                image_used = None

        # If we have a direct URL or download failed, and a local path exists, try that
        if not image_used:
            # job may contain a local path
            potential = job.get("result_path") or job.get("result_local_path")
            if potential and os.path.exists(potential):
                image_used = potential

        # If still no image but there is a public URL, we won't fetch externally here — fall back to metadata-only pdf
        if image_used and os.path.exists(image_used):
            # Read with OpenCV, convert to RGB and save as PDF via PIL
            img = cv2.imread(image_used)
            if img is not None:
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(img_rgb)
                pil_img.save(pdf_path, "PDF", resolution=dpi)
            else:
                # fallback to simple text pdf
                pil_img = Image.new("RGB", (1240, 1754), color=(255, 255, 255))
                Image.Image.save(pil_img, pdf_path, "PDF", resolution=dpi)
        else:
            # Create a simple PDF with job metadata
            pil_img = Image.new("RGB", (1240, 1754), color=(255, 255, 255))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(pil_img)
            draw.text((50, 100), f"WriteGen Export for job {job_id}", fill=(0, 0, 0))
            draw.text((50, 140), f"Generated: {datetime.utcnow().isoformat()}", fill=(0, 0, 0))
            pil_img.save(pdf_path, "PDF", resolution=dpi)

        storage_path = f"exports/{uid}/{job_id}.pdf"
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(pdf_path)
        blob.make_public()

        job_ref.update({"export_pdf": blob.public_url})
        return pdf_path, blob.public_url
