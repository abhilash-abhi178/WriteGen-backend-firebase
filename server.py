# server.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api.routes import auth, samples, styles, generation, export, dashboard

app = FastAPI(title="WriteGen - Handwriting API (Firebase)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(samples.router, prefix="/api/samples", tags=["samples"])
app.include_router(styles.router, prefix="/api/styles", tags=["styles"])
app.include_router(generation.router, prefix="/api/generate", tags=["generation"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "WriteGen API (Firebase)", "version": "1.0.0"}
