"""
Dependency Injection

This module contains FastAPI dependency functions for authentication,
database sessions, and other common dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationException, InactiveUserException
from app.models.user import User
from app.repositories.user_repository import user_repository

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        db: Database session
        credentials: HTTP Bearer credentials
        
    Returns:
        Current user instance
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            raise AuthenticationException("Invalid token")
        
        # Get user from database
        user = await user_repository.get(db, id=int(user_id))
        if user is None:
            raise AuthenticationException("User not found")
        
        return user
        
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user instance
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current superuser.
    
    Args:
        current_user: Current active user
        
    Returns:
        Current superuser instance
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    This dependency is useful for endpoints that work for both
    authenticated and anonymous users.
    
    Args:
        db: Database session
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Current user instance or None
    """
    if credentials is None:
        return None
    
    try:
        # Verify token and get user ID
        token = credentials.credentials
        user_id = verify_token(token)
        
        if user_id is None:
            return None
        
        # Get user from database
        user = await user_repository.get(db, id=int(user_id))
        return user
        
    except (AuthenticationException, ValueError):
        return None


def get_pagination_params(
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> dict:
    """
    Get pagination parameters with validation.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        max_per_page: Maximum items per page
        
    Returns:
        Dictionary with skip and limit values
        
    Raises:
        HTTPException: If parameters are invalid
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be greater than 0"
        )
    
    if per_page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Items per page must be greater than 0"
        )
    
    if per_page > max_per_page:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Items per page cannot exceed {max_per_page}"
        )
    
    skip = (page - 1) * per_page
    return {"skip": skip, "limit": per_page, "page": page, "per_page": per_page}
