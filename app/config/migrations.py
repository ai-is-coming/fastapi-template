"""
Database Migration Management with yoyo-migrations

This module handles automatic database migrations using yoyo-migrations.
Migrations are applied automatically when the application starts.
"""

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse
import asyncio
from yoyo import get_backend, read_migrations
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config.settings import settings
from app.config.log_config import get_logger

logger = get_logger(__name__)


def get_migrations_path() -> Path:
    """
    Get the path to the migrations directory.
    
    Returns:
        Path: Path to migrations directory
    """
    # Get the project root (where yoyo.ini is located)
    project_root = Path(__file__).parent.parent.parent
    migrations_path = project_root / "migrations"
    
    if not migrations_path.exists():
        logger.warning(f"Migrations directory not found: {migrations_path}")
        migrations_path.mkdir(exist_ok=True)
        logger.info(f"Created migrations directory: {migrations_path}")
    
    return migrations_path


async def ensure_database_exists() -> bool:
    """
    Ensure the target database exists, create it if it doesn't.

    Returns:
        bool: True if database exists or was created successfully, False otherwise
    """
    try:
        # Parse the database URL to extract components
        parsed = urlparse(settings.DATABASE_URL)
        db_name = parsed.path.lstrip('/')

        if not db_name:
            logger.error("No database name found in DATABASE_URL")
            return False

        # Create connection URL to postgres database (default database)
        postgres_url = settings.DATABASE_URL.replace(f"/{db_name}", "/postgres")

        logger.info(f"Checking if database '{db_name}' exists...")

        # Create engine to connect to postgres database
        engine = create_async_engine(postgres_url)

        try:
            # First check if database exists
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name}
                )
                exists = result.fetchone() is not None

            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating it...")

                # Create database using autocommit mode (no transaction)
                async with engine.execution_options(isolation_level="AUTOCOMMIT").connect() as conn:
                    await conn.execute(text(f'CREATE DATABASE "{db_name}"'))

                logger.info(f"✅ Database '{db_name}' created successfully!")
            else:
                logger.info(f"✅ Database '{db_name}' already exists.")

        finally:
            await engine.dispose()

        return True

    except Exception as e:
        logger.error(f"❌ Failed to ensure database exists: {e}", exc_info=True)
        return False


async def create_database_if_not_exists() -> bool:
    """
    Create the database if it doesn't exist.
    This is a convenience function that can be called independently.

    Returns:
        bool: True if database exists or was created successfully, False otherwise
    """
    return await ensure_database_exists()


def get_database_backend():
    """
    Get yoyo database backend from settings.

    Returns:
        Backend: yoyo database backend
    """
    try:
        # Convert SQLAlchemy URL format to yoyo format
        # SQLAlchemy: postgresql+asyncpg://user:pass@host:port/db
        # yoyo: postgresql://user:pass@host:port/db
        db_url = settings.DATABASE_URL
        if "+asyncpg" in db_url:
            db_url = db_url.replace("+asyncpg", "")
        elif "+aiosqlite" in db_url:
            # Convert SQLite async to sync for yoyo
            db_url = db_url.replace("sqlite+aiosqlite", "sqlite")

        backend = get_backend(db_url)
        return backend
    except Exception as e:
        logger.error(f"Failed to create database backend: {e}")
        raise


async def run_migrations() -> bool:
    """
    Run pending database migrations.

    Returns:
        bool: True if migrations ran successfully, False otherwise
    """
    try:
        logger.info("Starting database migrations...")

        # Ensure database exists first
        if not await ensure_database_exists():
            logger.error("Failed to ensure database exists")
            return False

        # Get migrations path and backend
        migrations_path = get_migrations_path()
        backend = get_database_backend()
        
        # Read migrations from directory
        migrations = read_migrations(str(migrations_path))
        
        if not migrations:
            logger.info("No migrations found")
            return True
        
        # Get pending migrations
        with backend.lock():
            pending_migrations = backend.to_apply(migrations)
            
            if not pending_migrations:
                logger.info("No pending migrations")
                return True
            
            logger.info(f"Found {len(pending_migrations)} pending migration(s)")
            
            # Apply pending migrations
            for migration in pending_migrations:
                logger.info(f"Applying migration: {migration.id}")
                backend.apply_one(migration)
                logger.info(f"✅ Applied migration: {migration.id}")
        
        logger.info("✅ All migrations applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        return False


async def check_migration_status() -> dict:
    """
    Check the status of migrations.

    Returns:
        dict: Migration status information
    """
    try:
        # Ensure database exists first
        if not await ensure_database_exists():
            return {
                "error": "Failed to ensure database exists",
                "total_migrations": 0,
                "applied_migrations": 0,
                "pending_migrations": 0,
            }

        migrations_path = get_migrations_path()
        backend = get_database_backend()
        
        # Read all migrations
        migrations = read_migrations(str(migrations_path))
        
        with backend.lock():
            applied_migrations = backend.to_rollback(migrations)
            pending_migrations = backend.to_apply(migrations)
        
        return {
            "total_migrations": len(migrations),
            "applied_migrations": len(applied_migrations),
            "pending_migrations": len(pending_migrations),
            "migration_files": [m.id for m in migrations],
            "applied_files": [m.id for m in applied_migrations],
            "pending_files": [m.id for m in pending_migrations],
        }
        
    except Exception as e:
        logger.error(f"Failed to check migration status: {e}")
        return {
            "error": str(e),
            "total_migrations": 0,
            "applied_migrations": 0,
            "pending_migrations": 0,
        }


def create_migration(name: str, content: Optional[str] = None, rollback_content: Optional[str] = None) -> Path:
    """
    Create a new migration file with the proper naming convention.

    Args:
        name: Migration name (will be sanitized)
        content: Optional SQL content for the migration
        rollback_content: Optional SQL content for the rollback

    Returns:
        Path: Path to the created migration file
    """
    from datetime import datetime

    # Generate timestamp in yyyymmddhh format
    timestamp = datetime.now().strftime("%Y%m%d%H")

    # Sanitize name (replace spaces and special chars with underscores)
    sanitized_name = "".join(c if c.isalnum() else "_" for c in name.lower())

    # Create filename - use .sql extension for SQL migrations
    filename = f"{timestamp}-{sanitized_name}.sql"
    rollback_filename = f"{timestamp}-{sanitized_name}.rollback.sql"

    migrations_path = get_migrations_path()
    migration_file = migrations_path / filename
    rollback_file = migrations_path / rollback_filename

    # Default content if none provided
    if content is None:
        content = f"""-- {name}
-- depends:

-- Add your SQL here
-- Example:
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL
-- );

-- CREATE INDEX idx_example_name ON example (name);
"""

    # Default rollback content if none provided
    if rollback_content is None:
        rollback_content = f"""-- Rollback for {name}

-- Add your rollback SQL here
-- Example:
-- DROP INDEX IF EXISTS idx_example_name;
-- DROP TABLE IF EXISTS example;
"""

    # Write migration file
    migration_file.write_text(content)
    logger.info(f"Created migration file: {migration_file}")

    # Write rollback file
    rollback_file.write_text(rollback_content)
    logger.info(f"Created rollback file: {rollback_file}")

    return migration_file
