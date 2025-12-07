# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid, os, shutil, time
from . import storage, style_extractor, stroke_generator, renderer, tasks, auth, schemas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "storage", "samples")
OUT_DIR = os.path.join(BASE_DIR, "..", "storage", "out")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

app = FastAPI(title="WriteGen Backend - FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory DB for demo (swap for Mongo/Postgres in prod)
DB = {
    "users": {},
    "styles": {},
    "jobs": {}
}

# ---------- AUTH ----------
@app.post("/api/auth/register")
async def register(req: auth.RegisterRequest):
    user = auth.create_user(req.email, req.password)
    return {"email": user["email"], "user_id": user["id"]}

@app.post("/api/auth/login")
async def login(req: auth.LoginRequest):
    token = auth.login_user(req.email, req.password)
    return {"access_token": token, "token_type": "bearer"}

# ---------- SAMPLES UPLOAD ----------
@app.post("/api/samples/upload")
async def upload_sample(file: UploadFile = File(...), token: str = Form(None)):
    # basic auth check
    if not auth.verify_token(token):
        raise HTTPException(401, "Unauthorized")
    uid = str(uuid.uuid4())
    filename = f"{uid}_{file.filename}"
    outpath = os.path.join(UPLOAD_DIR, filename)
    with open(outpath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    # store metadata
    DB["jobs"][uid] = {"type":"sample", "path": outpath, "status":"uploaded", "created_at": time.time()}
    return {"id": uid, "filename": filename, "path": outpath}

# ---------- CREATE STYLE ----------
class CreateStylePayload(BaseModel):
    sample_ids: list
    options: dict = {}

@app.post("/api/style/create")
async def create_style(payload: CreateStylePayload, background_tasks: BackgroundTasks, token: str = Form(None)):
    if not auth.verify_token(token):
        raise HTTPException(401, "Unauthorized")
    # gather sample paths
    sample_paths = []
    for sid in payload.sample_ids:
        job = DB["jobs"].get(sid)
        if not job:
            raise HTTPException(404, f"sample {sid} not found")
        sample_paths.append(job["path"])
    style_id = str(uuid.uuid4())
    DB["styles"][style_id] = {"status":"queued", "created_at": time.time()}
    # schedule background training/extraction
    background_tasks.add_task(tasks.run_style_extraction, style_id, sample_paths, payload.options, DB)
    return {"style_id": style_id}

@app.get("/api/style/{style_id}/status")
async def style_status(style_id: str):
    s = DB["styles"].get(style_id)
    if not s: raise HTTPException(404, "style not found")
    return {"style_id": style_id, "status": s.get("status"), "meta": s.get("meta")}

# ---------- GENERATE ----------
class GeneratePayload(BaseModel):
    style_id: str
    content: str
    page_template: str = "ruled"
    pen_type: str = "ballpoint"
    ink_color: str = "#000000"
    thickness: float = 1.0
    options: dict = {}

@app.post("/api/generate")
async def generate(payload: GeneratePayload, background_tasks: BackgroundTasks, token: str = Form(None)):
    if not auth.verify_token(token):
        raise HTTPException(401, "Unauthorized")
    if payload.style_id not in DB["styles"] or DB["styles"][payload.style_id].get("status") != "ready":
        raise HTTPException(400, "style not ready")
    job_id = str(uuid.uuid4())
    DB["jobs"][job_id] = {"type":"generate","status":"queued","created_at":time.time()}
    background_tasks.add_task(tasks.run_generate_job, job_id, payload.dict(), DB, OUT_DIR)
    return {"job_id": job_id}

@app.get("/api/job/{job_id}/status")
async def job_status(job_id: str):
    job = DB["jobs"].get(job_id)
    if not job:
        raise HTTPException(404, "job not found")
    return {"job_id": job_id, "status": job.get("status"), "result": job.get("result")}

@app.get("/api/job/{job_id}/result")
async def job_result(job_id: str):
    job = DB["jobs"].get(job_id)
    if not job or job.get("status") != "done":
        raise HTTPException(404, "result not available")
    # return file path or file
    result_path = job.get("result", {}).get("file")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(404, "result file not found")
    # serve as file (PNG/SVG/PDF)
    return FileResponse(result_path, media_type="application/octet-stream", filename=os.path.basename(result_path))

# quick health
@app.get("/api/health")
async def health():
    return {"status":"ok", "time": time.time()}
