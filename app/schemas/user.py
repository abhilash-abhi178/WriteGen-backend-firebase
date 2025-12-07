"""User and Authentication schemas."""

from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, UUID4


class ProcessingMode(str, Enum):
    CLOUD = "cloud"
    HYBRID = "hybrid"
    LOCAL_ONLY = "local_only"


class SubscriptionPlan(str, Enum):
    FREE = "free"
    HOBBY = "hobby"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class PrivacySettings(BaseModel):
    """User privacy and processing preferences."""
    default_mode: ProcessingMode = ProcessingMode.CLOUD
    allow_ephemeral: bool = True
    allow_analytics: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "default_mode": "cloud",
                "allow_ephemeral": True,
                "allow_analytics": False
            }
        }


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    display_name: str
    

class UserCreate(UserBase):
    """User creation schema."""
    password: str
    

class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response model."""
    user_id: UUID4
    created_at: datetime
    email_verified: bool
    avatar_url: Optional[str] = None
    privacy: PrivacySettings
    subscription_plan: SubscriptionPlan
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "display_name": "Alice Writer",
                "created_at": "2025-01-15T10:30:00Z",
                "email_verified": True,
                "privacy": {"default_mode": "cloud"}
            }
        }


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserUpdate(BaseModel):
    """User update schema."""
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    privacy: Optional[PrivacySettings] = None
