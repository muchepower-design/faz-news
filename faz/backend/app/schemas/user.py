# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.schemas._base import UserRoleEnum

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRoleEnum = UserRoleEnum.VIEWER
    club_id: Optional[UUID] = None

class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: str
    role: UserRoleEnum
    club_id: Optional[UUID]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserBase):
    id: UUID
    full_name: str
    role: UserRoleEnum
    club_id: Optional[UUID]
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    class Config:
        from_attributes = True