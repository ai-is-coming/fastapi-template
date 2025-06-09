#!/usr/bin/env python3
"""
Database Creation Script

This script creates the database if it doesn't exist.
"""

import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.migrations import create_database_if_not_exists
from app.config.log_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def main():
    """Create database if it doesn't exist."""
    logger.info("🗄️  Database Creation Script")
    logger.info("=" * 40)
    
    try:
        success = await create_database_if_not_exists()
        
        if success:
            logger.info("✅ Database setup completed successfully!")
            return True
        else:
            logger.error("❌ Failed to create database!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Script failed with exception: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
