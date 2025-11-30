# app/api/routes/auth.py
from fastapi import APIRouter, Depends, Header, HTTPException
from typing import Optional
from app.core.firebase import verify_id_token, user_doc_ref

router = APIRouter()

def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Expects Authorization: Bearer <idToken>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    id_token = authorization.split(" ", 1)[1]

    try:
        decoded = verify_id_token(id_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token verification failed")

    uid = decoded.get("uid")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    doc = user_doc_ref(uid).get()
    user = doc.to_dict() if doc.exists else {"uid": uid, "email": decoded.get("email")}
    user["firebase_token_payload"] = decoded
    return user

@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
