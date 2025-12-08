from fastapi import APIRouter, UploadFile, File, Depends
from app.core.firebase import bucket, db
from app.api.routes.auth import get_current_user
import uuid
import aiofiles
import os

router = APIRouter()

TEMP_DIR = "/tmp/writegen_signature"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/create")
async def upload_signature(file: UploadFile = File(...), current_user=Depends(get_current_user)):
    uid = current_user["uid"]
    suffix = file.filename.split(".")[-1]
    tmp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.{suffix}")

    async with aiofiles.open(tmp_path, "wb") as f:
        await f.write(await file.read())

    blob_path = f"signatures/{uid}/{uuid.uuid4().hex}.{suffix}"
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(tmp_path)
    blob.make_public()

    doc_ref = db.collection("signatures").document()
    doc_ref.set({
        "uid": uid,
        "url": blob.public_url,
        "storage_path": blob_path
    })

    return {"signature_id": doc_ref.id, "url": blob.public_url}
