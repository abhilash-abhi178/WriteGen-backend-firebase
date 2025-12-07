# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import auth, samples, styles, generation, export

app = FastAPI(title="WriteGen - Handwriting API (Firebase)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(auth.router, prefix="/api/auth")
app.include_router(samples.router, prefix="/api/samples")
app.include_router(styles.router, prefix="/api/styles")
app.include_router(generation.router, prefix="/api/generate")
app.include_router(export.router, prefix="/api/export")

@app.get("/")
async def root():
    return {"message": "WriteGen API", "status": "running"}
