"""
User and authentication schemas for the application.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from pydantic import ConfigDict


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str
    email: EmailStr
    full_name: Optional[str] = None
    # Remove is_active and is_superuser from creation payload
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserUpdate(BaseModel):
    """Schema for user updates."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDBBase(UserBase):
    """Base schema for users in DB, including id."""
    id: UUID
    
    class Config:
        from_attributes = True


class UserPublic(UserInDBBase):
    """Schema for public user data."""
    pass


class UserInDB(UserInDBBase):
    """Schema for user in DB, including hashed password."""
    hashed_password: str


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str
    expires_in: int
    scope: str


class TokenData(BaseModel):
    """Schema for token data."""
    sub: Optional[str] = None
    scopes: List[str] = []
