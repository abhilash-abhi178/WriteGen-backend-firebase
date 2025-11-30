from fastapi import APIRouter, HTTPException
router = APIRouter()

ADMIN_SECRET = "WRITEGEN_ADMIN_2024"

@router.get("/stats")
async def get_stats(secret: str):
    if secret != ADMIN_SECRET:
        return {"error": "Invalid secret"}
    return {"uptime": "Running", "users": 1203, "samples": 4834}
