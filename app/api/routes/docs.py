from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
from app.core.firebase import db

router = APIRouter()

@router.get("/")
async def my_docs(current_user=Depends(get_current_user)):
    uid = current_user["uid"]
    docs = [
        {"id": d.id, **d.to_dict()}
        for d in db.collection("documents").where("uid", "==", uid).stream()
    ]
    return {"documents": docs}
