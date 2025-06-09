"""
User Schemas

This module contains Pydantic schemas for user data validation,
serialization, and API request/response models.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields"""
    
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")


class UserCreate(UserBase):
    """Schema for creating a new user"""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "password": "securepassword123",
                "bio": "Software developer passionate about Python",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    bio: Optional[str] = Field(None, max_length=1000, description="User biography")
    avatar_url: Optional[str] = Field(None, description="URL to user's avatar image")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Smith",
                "bio": "Updated biography",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }
    )


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 characters)"
    )


class UserResponse(UserBase):
    """Schema for user response data"""
    
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has admin privileges")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "bio": "Software developer passionate about Python",
                "avatar_url": "https://example.com/avatar.jpg",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:00:00Z"
            }
        }
    )


class UserList(BaseModel):
    """Schema for paginated user list response"""
    
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "users": [],
                "total": 100,
                "page": 1,
                "per_page": 20,
                "pages": 5
            }
        }
    )
