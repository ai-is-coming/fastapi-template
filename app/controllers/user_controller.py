"""
User Controller

This module contains the UserController class that handles business logic
for user-related operations following the MVC pattern.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.log_config import get_logger
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    ValidationException
)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPasswordUpdate
from app.repositories.user_repository import user_repository

logger = get_logger(__name__)


class UserController:
    """
    Controller class for user business logic.
    
    This class contains all business logic related to user operations,
    acting as an intermediary between the API routes and the repository layer.
    """
    
    def __init__(self):
        """Initialize UserController with repository"""
        self.repository = user_repository
    
    async def create_user(self, db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            UserAlreadyExistsException: If email or username already exists
        """
        logger.info(f"Creating new user with email: {user_data.email}")

        # Check if email already exists
        if await self.repository.is_email_taken(db, email=user_data.email):
            logger.warning(f"Attempt to create user with existing email: {user_data.email}")
            raise UserAlreadyExistsException("Email already registered")

        # Check if username already exists
        if await self.repository.is_username_taken(db, username=user_data.username):
            logger.warning(f"Attempt to create user with existing username: {user_data.username}")
            raise UserAlreadyExistsException("Username already taken")
        
        # Hash password and create user
        logger.debug("Hashing password for new user")
        hashed_password = get_password_hash(user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        # Create user object for repository
        class UserCreateWithHash:
            def __init__(self, data):
                self.__dict__.update(data)

            def model_dump(self):
                return self.__dict__

        user_create = UserCreateWithHash(user_dict)
        created_user = await self.repository.create(db, obj_in=user_create)

        logger.info(
            f"Successfully created user",
            extra={
                "user_id": created_user.id,
                "username": created_user.username,
                "email": created_user.email
            }
        )

        return created_user
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User instance
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.repository.get(db, id=user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return user
    
    async def get_user_by_email(self, db: AsyncSession, email: str) -> User:
        """
        Get user by email.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User instance
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.repository.get_by_email(db, email=email)
        if not user:
            raise UserNotFoundException(f"User with email {email} not found")
        return user
    
    async def get_user_by_username(self, db: AsyncSession, username: str) -> User:
        """
        Get user by username.
        
        Args:
            db: Database session
            username: Username
            
        Returns:
            User instance
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.repository.get_by_username(db, username=username)
        if not user:
            raise UserNotFoundException(f"User with username {username} not found")
        return user
    
    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user instance
            
        Raises:
            UserNotFoundException: If user not found
            UserAlreadyExistsException: If email or username already exists
        """
        # Get existing user
        user = await self.get_user_by_id(db, user_id)
        
        # Check if email is being updated and already exists
        if user_data.email and user_data.email != user.email:
            if await self.repository.is_email_taken(db, email=user_data.email, exclude_id=user_id):
                raise UserAlreadyExistsException("Email already registered")
        
        # Check if username is being updated and already exists
        if user_data.username and user_data.username != user.username:
            if await self.repository.is_username_taken(db, username=user_data.username, exclude_id=user_id):
                raise UserAlreadyExistsException("Username already taken")
        
        return await self.repository.update(db, db_obj=user, obj_in=user_data)
    
    async def update_user_password(
        self,
        db: AsyncSession,
        user_id: int,
        password_data: UserPasswordUpdate
    ) -> User:
        """
        Update user password.
        
        Args:
            db: Database session
            user_id: User ID
            password_data: Password update data
            
        Returns:
            Updated user instance
            
        Raises:
            UserNotFoundException: If user not found
            InvalidCredentialsException: If current password is incorrect
        """
        # Get existing user
        user = await self.get_user_by_id(db, user_id)
        
        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise InvalidCredentialsException("Current password is incorrect")
        
        # Hash new password and update
        hashed_password = get_password_hash(password_data.new_password)
        update_data = {"hashed_password": hashed_password}
        
        return await self.repository.update(db, db_obj=user, obj_in=update_data)
    
    async def delete_user(self, db: AsyncSession, user_id: int) -> User:
        """
        Delete user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Deleted user instance
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.repository.remove(db, id=user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return user
    
    async def get_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> list[User]:
        """
        Get list of users with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Whether to return only active users
            
        Returns:
            List of user instances
        """
        if active_only:
            return await self.repository.get_active_users(db, skip=skip, limit=limit)
        else:
            return await self.repository.get_multi(db, skip=skip, limit=limit)
    
    async def count_users(self, db: AsyncSession, active_only: bool = False) -> int:
        """
        Count total number of users.
        
        Args:
            db: Database session
            active_only: Whether to count only active users
            
        Returns:
            Number of users
        """
        filters = {"is_active": True} if active_only else None
        return await self.repository.count(db, filters=filters)


# Create global controller instance
user_controller = UserController()
