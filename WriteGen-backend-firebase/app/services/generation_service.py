# app/services/generation_service.py
import os
import cv2
import numpy as np
from app.core.firebase import db, bucket
from datetime import datetime
from typing import Dict
from app.core.config import settings


class GenerationService:
    def __init__(self):
        self.output_dir = settings.temp_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _wrap_text(self, text: str, max_chars: int = 60) -> str:
        words = text.split()
        lines = []
        cur = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + (1 if cur else 0) > max_chars:
                lines.append(" ".join(cur))
                cur = [w]
                cur_len = len(w)
            else:
                cur.append(w)
                cur_len += len(w) + (1 if cur_len > 0 else 0)
        if cur:
            lines.append(" ".join(cur))
        return "\n".join(lines)

    def generate_job_sync(self, job_id: str):
        job_ref = db.collection("generation_jobs").document(job_id)
        job = job_ref.get().to_dict()
        uid = job["uid"]
        request = job.get("request", {})
        text = request.get("text", "Hello from WriteGen")[:400]

        # Create a large white canvas (A4 at 300 DPI -> 2480x3508)
        width, height = 2480, 3508
        canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

        wrapped = self._wrap_text(text, max_chars=80)
        # Draw lines with OpenCV
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        color = (0, 0, 0)
        line_height = 40
        x, y = 100, 150
        for i, line in enumerate(wrapped.split("\n")):
            pos = (x, y + i * line_height)
            cv2.putText(canvas, line, pos, font, font_scale, color, thickness=2, lineType=cv2.LINE_AA)

        output_path = os.path.join(self.output_dir, f"{job_id}.png")
        cv2.imwrite(output_path, canvas)

        storage_path = f"generated/{uid}/{job_id}.png"
        blob = bucket.blob(storage_path)
        blob.upload_from_filename(output_path)
        blob.make_public()

        job_ref.update({"result_url": blob.public_url, "result_storage_path": storage_path, "progress": 1.0, "status": "completed", "completed_at": datetime.utcnow().isoformat()})
        return {"result_url": blob.public_url}
