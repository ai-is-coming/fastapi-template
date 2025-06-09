"""
User API Routes

This module contains FastAPI routes for user-related operations.
These routes act as the View layer in the MVC pattern.
"""

import math
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.dependencies import (
    get_current_active_user,
    get_current_superuser,
    get_pagination_params
)
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException
)
from app.controllers.user_controller import user_controller
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserList
)

# Create router instance
router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        Created user data
        
    Raises:
        HTTPException: If email or username already exists
    """
    try:
        user = await user_controller.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.detail
        )


@router.get("/users", response_model=UserList)
async def get_users(
    db: AsyncSession = Depends(get_db),
    pagination: dict = Depends(get_pagination_params),
    active_only: bool = Query(False, description="Return only active users"),
    current_user: User = Depends(get_current_superuser)
):
    """
    Get list of users with pagination.
    
    Requires superuser permissions.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        active_only: Whether to return only active users
        current_user: Current authenticated superuser
        
    Returns:
        Paginated list of users
    """
    users = await user_controller.get_users(
        db,
        skip=pagination["skip"],
        limit=pagination["limit"],
        active_only=active_only
    )
    
    total = await user_controller.count_users(db, active_only=active_only)
    pages = math.ceil(total / pagination["per_page"])
    
    return UserList(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        page=pagination["page"],
        per_page=pagination["per_page"],
        pages=pages
    )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID.
    
    Users can only access their own data unless they are superusers.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found or access denied
    """
    # Check if user is accessing their own data or is a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        user = await user_controller.get_user_by_id(db, user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user information.
    
    Users can only update their own data unless they are superusers.
    
    Args:
        user_id: User ID
        user_data: User update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found, access denied, or validation error
    """
    # Check if user is updating their own data or is a superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        user = await user_controller.update_user(db, user_id, user_data)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.detail
        )


@router.put("/users/{user_id}/password", response_model=UserResponse)
async def update_user_password(
    user_id: int,
    password_data: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user password.
    
    Users can only update their own password.
    
    Args:
        user_id: User ID
        password_data: Password update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated user data
        
    Raises:
        HTTPException: If user not found, access denied, or invalid credentials
    """
    # Users can only update their own password
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own password"
        )
    
    try:
        user = await user_controller.update_user_password(db, user_id, password_data)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.detail
        )


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete user.
    
    Requires superuser permissions.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated superuser
        
    Returns:
        Deleted user data
        
    Raises:
        HTTPException: If user not found
    """
    try:
        user = await user_controller.delete_user(db, user_id)
        return UserResponse.model_validate(user)
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail
        )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return UserResponse.model_validate(current_user)
