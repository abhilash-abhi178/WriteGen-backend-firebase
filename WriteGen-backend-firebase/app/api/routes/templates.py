from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_templates():
    return {
        "templates": [
            {"id": "ruled", "name": "Ruled Paper"},
            {"id": "grid", "name": "Grid Paper"},
            {"id": "blank", "name": "Blank Page"},
            {"id": "exam", "name": "Exam Sheet"},
        ]
    }
