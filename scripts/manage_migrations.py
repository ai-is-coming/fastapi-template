#!/usr/bin/env python3
"""
Migration Management Script for yoyo-migrations

This script provides a command-line interface for managing database migrations.
"""

import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.migrations import (
    check_migration_status,
    run_migrations,
    create_migration,
    create_database_if_not_exists,
    get_migrations_path
)
from app.config.log_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def status_command():
    """Show migration status."""
    logger.info("📊 Checking migration status...")
    
    status = await check_migration_status()
    
    if "error" in status:
        logger.error(f"❌ Error: {status['error']}")
        return False
    
    print(f"\n📊 Migration Status:")
    print(f"  Total migrations: {status['total_migrations']}")
    print(f"  Applied migrations: {status['applied_migrations']}")
    print(f"  Pending migrations: {status['pending_migrations']}")
    
    if status['migration_files']:
        print(f"\n📁 All migration files:")
        for file in status['migration_files']:
            print(f"    {file}")
    
    if status['applied_files']:
        print(f"\n✅ Applied migrations:")
        for file in status['applied_files']:
            print(f"    {file}")
    
    if status['pending_files']:
        print(f"\n⏳ Pending migrations:")
        for file in status['pending_files']:
            print(f"    {file}")
    else:
        print(f"\n✅ All migrations are up to date!")
    
    return True


async def apply_command():
    """Apply pending migrations."""
    logger.info("🔄 Applying migrations...")
    
    success = await run_migrations()
    if success:
        logger.info("✅ Migrations applied successfully!")
        return True
    else:
        logger.error("❌ Failed to apply migrations!")
        return False


def create_command(name: str):
    """Create a new migration file."""
    if not name:
        logger.error("❌ Migration name is required!")
        return False
    
    logger.info(f"📝 Creating migration: {name}")
    
    try:
        migration_file = create_migration(name)
        logger.info(f"✅ Migration created: {migration_file}")
        print(f"\n📝 Created migration file: {migration_file}")
        print(f"Edit the file to add your SQL statements.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create migration: {e}")
        return False


def list_command():
    """List all migration files."""
    migrations_path = get_migrations_path()
    
    if not migrations_path.exists():
        print("📁 No migrations directory found.")
        return True
    
    migration_files = sorted(migrations_path.glob("*.sql"))
    
    if not migration_files:
        print("📁 No migration files found.")
        return True
    
    print(f"\n📁 Migration files in {migrations_path}:")
    for file in migration_files:
        print(f"    {file.name}")
    
    return True


async def create_db_command():
    """Create database if it doesn't exist."""
    logger.info("🗄️  Creating database if needed...")

    success = await create_database_if_not_exists()
    if success:
        logger.info("✅ Database is ready!")
        return True
    else:
        logger.error("❌ Failed to create database!")
        return False


async def rollback_command(revision: Optional[str] = None):
    """Rollback migrations."""
    logger.info("🔄 Rolling back migrations...")

    try:
        # Ensure database exists first
        if not await create_database_if_not_exists():
            logger.error("Failed to ensure database exists")
            return False

        # Use yoyo directly for rollback since we need more control
        import subprocess

        cmd = ["uv", "run", "yoyo", "rollback", "--config", "yoyo.ini", "--batch"]
        if revision:
            cmd.extend(["--revision", revision])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("✅ Rollback completed successfully!")
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error(f"❌ Rollback failed!")
            if result.stderr:
                logger.error(f"Error: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Rollback failed with exception: {e}")
        return False


async def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="Manage database migrations with yoyo-migrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/manage_migrations.py status          # Show migration status
  python scripts/manage_migrations.py apply           # Apply pending migrations
  python scripts/manage_migrations.py create "Add users table"  # Create new migration
  python scripts/manage_migrations.py list            # List all migration files
  python scripts/manage_migrations.py create-db       # Create database if needed
  python scripts/manage_migrations.py rollback        # Rollback last migration
  python scripts/manage_migrations.py rollback -r 2025060623-create_users_table  # Rollback to specific migration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show migration status')
    
    # Apply command
    subparsers.add_parser('apply', help='Apply pending migrations')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('name', help='Migration name')
    
    # List command
    subparsers.add_parser('list', help='List all migration files')

    # Create database command
    subparsers.add_parser('create-db', help='Create database if it doesn\'t exist')

    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback migrations')
    rollback_parser.add_argument('--revision', '-r', help='Rollback to specific revision')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return False
    
    try:
        if args.command == 'status':
            return await status_command()
        elif args.command == 'apply':
            return await apply_command()
        elif args.command == 'create':
            return create_command(args.name)
        elif args.command == 'list':
            return list_command()
        elif args.command == 'create-db':
            return await create_db_command()
        elif args.command == 'rollback':
            revision = getattr(args, 'revision', None)
            return await rollback_command(revision)
        else:
            parser.print_help()
            return False
            
    except Exception as e:
        logger.error(f"❌ Command failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
