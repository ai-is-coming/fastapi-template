#!/usr/bin/env python3
"""
Database Setup Script

This script helps set up the database connection and run migrations.
Run this after starting your PostgreSQL server.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine
from app.config.settings import settings
from app.config.log_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def test_database_connection():
    """Test the database connection."""
    try:
        logger.info(f"Testing connection to: {settings.DATABASE_URL}")
        engine = create_async_engine(settings.DATABASE_URL)
        
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            logger.info(f"✅ Database connection successful! Test query result: {row}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def check_database_exists():
    """Check if the database exists and create it if not."""
    try:
        # Extract database name from URL
        db_name = settings.DATABASE_URL.split('/')[-1]
        base_url = settings.DATABASE_URL.rsplit('/', 1)[0]
        
        logger.info(f"Checking if database '{db_name}' exists...")
        
        # Connect to postgres database to check if target database exists
        postgres_url = f"{base_url}/postgres"
        engine = create_async_engine(postgres_url)
        
        async with engine.connect() as conn:
            # Check if database exists
            result = await conn.execute(
                f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"
            )
            exists = result.fetchone() is not None
            
            if not exists:
                logger.info(f"Database '{db_name}' does not exist. Creating it...")
                # Note: CREATE DATABASE cannot be run in a transaction
                await conn.execute("COMMIT")
                await conn.execute(f"CREATE DATABASE {db_name}")
                logger.info(f"✅ Database '{db_name}' created successfully!")
            else:
                logger.info(f"✅ Database '{db_name}' already exists.")
                
        await engine.dispose()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to check/create database: {e}")
        return False


def run_migrations():
    """Run yoyo migrations."""
    import subprocess

    try:
        logger.info("Running database migrations...")

        # Run yoyo apply
        result = subprocess.run(
            ["uv", "run", "yoyo", "apply", "--config", "yoyo.ini"],
            capture_output=True,
            text=True,
            cwd=project_root
        )

        if result.returncode == 0:
            logger.info("✅ Migrations completed successfully!")
            logger.info(f"Migration output:\n{result.stdout}")
            return True
        else:
            logger.error(f"❌ Migration failed with return code {result.returncode}")
            logger.error(f"Error output:\n{result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to run migrations: {e}")
        return False


async def main():
    """Main setup function."""
    logger.info("🚀 Starting database setup...")
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    
    # Step 1: Check/create database
    if not await check_database_exists():
        logger.error("Failed to setup database. Exiting.")
        return False
    
    # Step 2: Test connection
    if not await test_database_connection():
        logger.error("Database connection test failed. Exiting.")
        return False
    
    # Step 3: Run migrations
    if not run_migrations():
        logger.error("Migration failed. Exiting.")
        return False
    
    logger.info("🎉 Database setup completed successfully!")
    logger.info("You can now start your FastAPI application.")
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
