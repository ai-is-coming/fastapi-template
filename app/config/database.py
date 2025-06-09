"""
Database Configuration and Session Management

This module handles database connection, session management, and provides
the database engine and session factory for the application.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from app.config.settings import settings


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async database engine
# Note: We disable SQLAlchemy's built-in echo to use our custom clean SQL logging
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Always False - we use custom SQL logging in logging.py
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    This function creates all tables defined in the models.
    Should be called during application startup.
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        from app.models import user  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    Should be called during application shutdown.
    """
    await engine.dispose()
