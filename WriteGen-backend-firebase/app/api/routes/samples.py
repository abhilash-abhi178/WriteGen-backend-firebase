# app/api/routes/samples.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
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
async def upload_samples(files: List[UploadFile] = File(...), current_user: dict = Depends(get_current_user)):
    uploaded = []
    uid = current_user["uid"]
    for f in files:
        suffix = f.filename.split(".")[-1]
        tmp_path = os.path.join(UPLOAD_TEMP, f"{uuid.uuid4().hex}.{suffix}")
        async with aiofiles.open(tmp_path, "wb") as out_file:
            content = await f.read()
            await out_file.write(content)

        blob_path = f"samples/{uid}/{datetime.utcnow().timestamp()}_{f.filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(tmp_path)
        # for development convenience; in prod use signed URLs or restricted rules
        blob.make_public()

        sample_doc = {
            "uid": uid,
            "filename": f.filename,
            "storage_path": blob_path,
            "public_url": blob.public_url,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat()
        }
        doc_ref = db.collection("samples").document()
        doc_ref.set(sample_doc)
        uploaded.append({"id": doc_ref.id, **sample_doc})

        try:
            os.remove(tmp_path)
        except:
            pass

    return {"uploaded_count": len(uploaded), "samples": uploaded}
