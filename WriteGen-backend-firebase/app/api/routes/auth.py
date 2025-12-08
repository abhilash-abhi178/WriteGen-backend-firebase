"""Authentication routes (nested copy)."""

import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Header
from pydantic import EmailStr
import uuid

from app.core.config import settings
from app.schemas import user as user_schemas

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store (kept to mirror root behavior)
users_db = {}
tokens_db = {}


def create_jwt_token(user_id: str) -> str:
    """Create JWT token for user."""
    import jwt
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=settings.jwt_expiration_hours),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm
    )
    return token


def verify_token(token: str) -> dict:
    """Verify JWT token."""
    import jwt
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to get current user from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    user = users_db.get(user_id)
    
    if not user:
        user = {
            "user_id": user_id,
            "uid": user_id,
            "email": f"user_{user_id[:8]}@temp.com",
            "display_name": f"User {user_id[:8]}"
        }
        logger.warning(f"User {user_id} not found in memory, using token data")
    
    user["uid"] = user_id
    return user


@router.post("/signup", response_model=user_schemas.TokenResponse)
async def signup(req: user_schemas.UserCreate):
    """Register a new user."""
    logger.info(f"Signup request for {req.email}")
    
    for user in users_db.values():
        if user["email"] == req.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
    
    user_id = str(uuid.uuid4())
    user = {
        "user_id": user_id,
        "email": req.email,
        "display_name": req.display_name,
        "password_hash": req.password,  # In production: hash password
        "created_at": datetime.utcnow(),
        "email_verified": False,
        "subscription_plan": "free",
        "privacy": {
            "default_mode": "cloud",
            "allow_ephemeral": True,
            "allow_analytics": False
        }
    }
    
    users_db[user_id] = user
    
    access_token = create_jwt_token(user_id)
    refresh_token = str(uuid.uuid4())
    tokens_db[refresh_token] = {"user_id": user_id, "created_at": datetime.utcnow()}
    
    logger.info(f"User {user_id} registered successfully")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration_hours * 3600
    }


@router.post("/login", response_model=user_schemas.TokenResponse)
async def login(req: user_schemas.UserLogin):
    """Login user."""
    logger.info(f"Login request for {req.email}")
    
    user = None
    for u in users_db.values():
        if u["email"] == req.email:
            user = u
            break
    
    if not user or user.get("password_hash") != req.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_jwt_token(user["user_id"])
    refresh_token = str(uuid.uuid4())
    tokens_db[refresh_token] = {
        "user_id": user["user_id"],
        "created_at": datetime.utcnow()
    }
    
    logger.info(f"User {user['user_id']} logged in")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration_hours * 3600
    }


@router.post("/refresh", response_model=user_schemas.TokenResponse)
async def refresh(refresh_token: str):
    """Refresh access token."""
    token_data = tokens_db.get(refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = token_data["user_id"]
    access_token = create_jwt_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration_hours * 3600
    }


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return user_schemas.UserResponse(
        user_id=current_user["user_id"],
        email=current_user["email"],
        display_name=current_user["display_name"],
        created_at=current_user["created_at"],
        email_verified=current_user.get("email_verified", False),
        privacy=current_user.get("privacy", {}),
        subscription_plan=current_user.get("subscription_plan", "free"),
        updated_at=current_user.get("updated_at", current_user["created_at"])
    )


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile with style status."""
    try:
        from app.core.firebase import db
    except:
        from app.core.mock_db import mock_db as db
    
    uid = current_user.get("user_id") or current_user.get("uid")
    
    has_style_profile = False
    try:
        styles = list(db.collection("styles").where("uid", "==", uid).stream())
        has_style_profile = len(styles) > 0
    except:
        pass
    
    return {
        "user_id": current_user.get("user_id"),
        "email": current_user.get("email"),
        "display_name": current_user.get("display_name"),
        "created_at": current_user.get("created_at"),
        "email_verified": current_user.get("email_verified", False),
        "privacy": current_user.get("privacy", {}),
        "subscription_plan": current_user.get("subscription_plan", "free"),
        "updated_at": current_user.get("updated_at", current_user.get("created_at")),
        "hasStyleProfile": has_style_profile,
        "style_status": "active" if has_style_profile else "pending"
    }
