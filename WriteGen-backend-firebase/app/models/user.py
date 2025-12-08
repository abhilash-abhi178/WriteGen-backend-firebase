# app/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[str]
    uid: str
    email: Optional[EmailStr]
    name: Optional[str]
    created_at: Optional[str]
