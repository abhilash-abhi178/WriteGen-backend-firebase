"""Firebase authentication and token verification."""

from typing import Optional
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings

# HTTP Bearer security scheme for Firebase tokens
security = HTTPBearer()

_firebase_initialized = False


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK."""
    global _firebase_initialized
    
    if _firebase_initialized:
        return
    
    settings = get_settings()
    
    if settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        firebase_admin.initialize_app(cred)
    else:
        # Use default credentials (for Cloud Run, etc.)
        firebase_admin.initialize_app()
    
    _firebase_initialized = True


def verify_firebase_token(token: str) -> dict:
    """
    Verify a Firebase ID token.
    
    Args:
        token: The Firebase ID token to verify.
        
    Returns:
        The decoded token claims.
        
    Raises:
        HTTPException: If token verification fails.
    """
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired",
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has been revoked",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Dependency to get the current authenticated user from Firebase token.
    
    Args:
        credentials: The HTTP authorization credentials containing the token.
        
    Returns:
        The decoded token claims containing user information.
    """
    token = credentials.credentials
    return verify_firebase_token(token)


async def get_current_user_id(
    current_user: dict = Depends(get_current_user),
) -> str:
    """
    Dependency to get just the user ID from the current user.
    
    Args:
        current_user: The decoded token claims.
        
    Returns:
        The user's Firebase UID.
    """
    return current_user.get("uid", "")
