"""
Authentication dependencies for dependency injection
Location: app/api/dependencies.py
"""

import logging
from typing import Optional
from fastapi import Header, HTTPException, status
from app.core.auth import JWTHandler

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Dependency to extract and verify current user from JWT token
    Usage: @router.get("/protected", dependencies=[Depends(get_current_user)])
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <token>"
        )
    
    token = authorization.split(" ", 1)[1]
    
    try:
        payload = JWTHandler.verify_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        return {
            "user_id": user_id,
            "uid": user_id,  # Backward compatibility
            "token": token
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed"
        )


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Optional authentication - returns None if not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
