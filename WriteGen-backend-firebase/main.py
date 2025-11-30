
from fastapi import FastAPI
from api.upload import router as upload_router
from api.styles import router as styles_router
from api.generate import router as generate_router

app = FastAPI(
    title="WriteGen Backend",
    description="AI Handwriting Generator Backend",
    version="1.0.0"
)

# Include all API endpoints
app.include_router(upload_router, prefix="/api/samples")
app.include_router(styles_router, prefix="/api/styles")
app.include_router(generate_router, prefix="/api/generate")

@app.get("/")
def home():
    return {"status": "running", "message": "WriteGen backend active"}
