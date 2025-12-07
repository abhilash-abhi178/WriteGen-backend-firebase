from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_summary():
    return {"status": "ok", "summary": "Dashboard endpoint working!"}
