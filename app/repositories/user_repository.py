"""
User Repository

This module contains the UserRepository class that handles all database
operations related to user management.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository class for User model with specific user operations.
    
    Extends BaseRepository to provide user-specific database operations
    such as finding users by email or username.
    """
    
    def __init__(self):
        """Initialize UserRepository with User model"""
        super().__init__(User)
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email address
            
        Returns:
            User instance or None if not found
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User instance or None if not found
        """
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_active_users(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """
        Get all active users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active user instances
        """
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_superusers(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> list[User]:
        """
        Get all superusers with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of superuser instances
        """
        result = await db.execute(
            select(User)
            .where(User.is_superuser == True)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def is_email_taken(self, db: AsyncSession, *, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if email is already taken by another user.
        
        Args:
            db: Database session
            email: Email to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if email is taken, False otherwise
        """
        query = select(User).where(User.email == email)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def is_username_taken(self, db: AsyncSession, *, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        Check if username is already taken by another user.
        
        Args:
            db: Database session
            username: Username to check
            exclude_id: User ID to exclude from check (for updates)
            
        Returns:
            True if username is taken, False otherwise
        """
        query = select(User).where(User.username == username)
        if exclude_id:
            query = query.where(User.id != exclude_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None


# Create global repository instance
user_repository = UserRepository()
