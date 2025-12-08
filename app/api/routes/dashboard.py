from fastapi import APIRouter, Depends
from app.api.routes.auth import get_current_user
<<<<<<< HEAD
# Use mock database instead of Firebase for now
try:
    from app.core.firebase import db
    USE_FIREBASE = True
except Exception:
    from app.core.mock_db import mock_db as db
    USE_FIREBASE = False
=======
from app.core.firebase import db
>>>>>>> 8bbe03e4b99a93cdf9105046218a1a8d56789978
from datetime import datetime

router = APIRouter()


@router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get user-specific dashboard statistics."""
    user_id = current_user.get("user_id") or current_user.get("uid")
    
    # Count total documents
    docs_query = db.collection("documents").where("uid", "==", user_id).stream()
    total_documents = sum(1 for _ in docs_query)
    
    # Count documents created today
    today = datetime.utcnow().date()
    docs_today = 0
    for doc in db.collection("documents").where("uid", "==", user_id).stream():
        doc_data = doc.to_dict()
        created_at = doc_data.get("created_at")
        if created_at and isinstance(created_at, str):
            doc_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).date()
            if doc_date == today:
                docs_today += 1
    
    # Count pending drafts
    pending_query = db.collection("documents").where("uid", "==", user_id).where("status", "==", "draft").stream()
    pending_drafts = sum(1 for _ in pending_query)
    
    # Count total pages
    total_pages = 0
    for doc in db.collection("documents").where("uid", "==", user_id).stream():
        doc_data = doc.to_dict()
        total_pages += doc_data.get("page_count", 1)
    
    return {
        "totalDocuments": total_documents,
        "generatedToday": docs_today,
        "pendingDrafts": pending_drafts,
        "totalPages": total_pages
    }


@router.get("/auth/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile with style information."""
    user_id = current_user.get("user_id") or current_user.get("uid")
    
    # Check if user has uploaded samples
    samples_query = db.collection("samples").where("uid", "==", user_id).stream()
    has_samples = any(True for _ in samples_query)
    
    return {
        "id": user_id,
        "name": current_user.get("display_name") or current_user.get("email", "").split("@")[0],
        "email": current_user.get("email"),
        "hasStyleProfile": has_samples
    }


@router.get("/generation/documents")
async def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get user's documents."""
    user_id = current_user.get("user_id") or current_user.get("uid")
    
    documents = []
    for doc in db.collection("documents").where("uid", "==", user_id).stream():
        doc_data = doc.to_dict()
        documents.append({
            "id": doc.id,
            "name": doc_data.get("title", "Untitled"),
            "lastModified": doc_data.get("updated_at", doc_data.get("created_at", "Unknown")),
            "status": doc_data.get("status", "draft")
        })
    
    return documents
