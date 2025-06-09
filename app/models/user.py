"""
User Model

This module contains the User model definition with all necessary fields
and relationships for user management.
"""

from typing import Optional
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class User(BaseModel):
    """
    User model for authentication and user management.
    
    Attributes:
        id: Primary key
        email: User email address (unique)
        username: Username (unique)
        full_name: User's full name
        hashed_password: Hashed password for authentication
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        bio: User biography/description
        avatar_url: URL to user's avatar image
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User email address"
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
        doc="Username for login"
    )
    
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed password"
    )
    
    # User information
    full_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="User's full name"
    )
    
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User biography"
    )
    
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="URL to user's avatar image"
    )
    
    # Status fields
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )
    
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user has admin privileges"
    )
    
    def __repr__(self) -> str:
        """String representation of the User model"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
