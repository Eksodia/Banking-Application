from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from uuid import UUID
from src.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole

class UserOut(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None