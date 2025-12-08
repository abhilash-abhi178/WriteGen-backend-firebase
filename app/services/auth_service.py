"""
Authentication business logic service
Location: app/services/auth_service.py
"""

import logging
import uuid
from typing import Optional
from datetime import datetime
from app.core.auth import JWTHandler, PasswordHandler

logger = logging.getLogger(__name__)


class AuthService:
    """Business logic for authentication operations"""
    
    def __init__(self, db):
        """
        Initialize AuthService
        Args:
            db: Firebase database instance or mock database
        """
        self.db = db
        self.users_collection = "users"
    
    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        display_name: str
    ) -> dict:
        """
        Create a new user account
        
        Args:
            email: User email
            password: Plain text password
            name: User full name
            display_name: Display name for UI
        
        Returns:
            dict with user_id and token
        
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing = list(
            self.db.collection(self.users_collection)
            .where("email", "==", email)
            .stream()
        )
        
        if existing:
            raise ValueError(f"User with email {email} already exists")
        
        # Create user ID
        user_id = str(uuid.uuid4())
        
        # Hash password
        hashed_password = PasswordHandler.hash_password(password)
        
        # Create user document
        user_data = {
            "user_id": user_id,
            "uid": user_id,
            "email": email,
            "name": name,
            "display_name": display_name,
            "password_hash": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "email_verified": False,
            "is_active": True,
            "subscription_plan": "free",
            "preferences": {}
        }
        
        # Save to database
        doc_ref = self.db.collection(self.users_collection).document(user_id)
        doc_ref.set(user_data)
        
        logger.info(f"User created: {email}")
        
        # Generate token
        token = JWTHandler.create_token(user_id)
        
        return {
            "user_id": user_id,
            "access_token": token,
            "token_type": "bearer"
        }
    
    def authenticate_user(self, email: str, password: str) -> dict:
        """
        Authenticate user with email and password
        
        Args:
            email: User email
            password: Plain text password
        
        Returns:
            dict with user_id and token
        
        Raises:
            ValueError: If user not found or password incorrect
        """
        # Find user by email
        users = list(
            self.db.collection(self.users_collection)
            .where("email", "==", email)
            .stream()
        )
        
        if not users:
            raise ValueError("Invalid email or password")
        
        user_doc = users[0]
        user_data = user_doc.to_dict()
        
        # Verify password
        if not PasswordHandler.verify_password(password, user_data.get("password_hash", "")):
            raise ValueError("Invalid email or password")
        
        # Check if user is active
        if not user_data.get("is_active", True):
            raise ValueError("User account is inactive")
        
        logger.info(f"User authenticated: {email}")
        
        # Generate token
        token = JWTHandler.create_token(user_data["user_id"])
        
        return {
            "user_id": user_data["user_id"],
            "access_token": token,
            "token_type": "bearer"
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        doc = self.db.collection(self.users_collection).document(user_id).get()
        
        if not doc.exists:
            return None
        
        user_data = doc.to_dict()
        # Remove sensitive data
        user_data.pop("password_hash", None)
        return user_data
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        users = list(
            self.db.collection(self.users_collection)
            .where("email", "==", email)
            .stream()
        )
        
        if not users:
            return None
        
        user_data = users[0].to_dict()
        # Remove sensitive data
        user_data.pop("password_hash", None)
        return user_data
    
    def update_user(self, user_id: str, **kwargs) -> dict:
        """Update user profile"""
        # Don't allow password updates through this method
        kwargs.pop("password_hash", None)
        kwargs.pop("password", None)
        kwargs["updated_at"] = datetime.utcnow().isoformat()
        
        self.db.collection(self.users_collection).document(user_id).update(kwargs)
        logger.info(f"User updated: {user_id}")
        
        return self.get_user_by_id(user_id)
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        self.db.collection(self.users_collection).document(user_id).delete()
        logger.info(f"User deleted: {user_id}")
        return True
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.get_user_by_id(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        # Get the full user doc with password_hash
        doc = self.db.collection(self.users_collection).document(user_id).get()
        user_data = doc.to_dict()
        
        # Verify old password
        if not PasswordHandler.verify_password(old_password, user_data.get("password_hash", "")):
            raise ValueError("Current password is incorrect")
        
        # Hash new password and update
        new_hash = PasswordHandler.hash_password(new_password)
        self.db.collection(self.users_collection).document(user_id).update({
            "password_hash": new_hash,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        logger.info(f"Password changed: {user_id}")
        return True
