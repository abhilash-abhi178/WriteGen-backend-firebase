from pydantic import BaseModel, EmailStr
from typing import Optional

class UserDTO(BaseModel):
    uid: str
    email: Optional[EmailStr]
    name: Optional[str] = None
