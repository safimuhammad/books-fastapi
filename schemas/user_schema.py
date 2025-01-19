from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com", description="The user's email address")


class UserCreate(UserBase):
    password: str = Field(..., example="strongpassword", description="The user's password")


class UserOut(UserBase):
    id: int = Field(..., example=1, description="The user's unique identifier")
    is_active: bool = Field(..., example=True, description="Whether the user is active")
    created_at: datetime = Field(..., example="2024-01-01 10:00:00", description="The date and time the user was created")

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[EmailStr] = None
