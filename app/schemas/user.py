from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    profile_pic: Optional[str] = None
    provider: str = "google"
    provider_id: Optional[str] = None


class UserResponse(UserBase):
    id: int
    profile_pic: Optional[str]
    created_at: datetime
    updated_at: datetime
    provider: str

    class Config:
        from_attributes = True


class EmailVerificationResponse(BaseModel):
    exists: bool
