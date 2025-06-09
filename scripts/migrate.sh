#!/bin/bash

# Database Migration Script
# This script helps run database migrations with proper environment setup

set -e  # Exit on any error

echo "🚀 FastAPI Database Migration Script"
echo "======================================"

# Set default database URL if not provided
if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql+asyncpg://root:password@127.0.0.1:5432/alice"
    echo "Using default DATABASE_URL: $DATABASE_URL"
else
    echo "Using DATABASE_URL: $DATABASE_URL"
fi

# Function to check if PostgreSQL is running
check_postgres() {
    echo "🔍 Checking PostgreSQL connection..."
    if uv run python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    try:
        engine = create_async_engine('$DATABASE_URL')
        async with engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        await engine.dispose()
        print('✅ PostgreSQL is running and accessible')
        return True
    except Exception as e:
        print(f'❌ PostgreSQL connection failed: {e}')
        return False

import sys
sys.exit(0 if asyncio.run(test()) else 1)
"; then
        return 0
    else
        return 1
    fi
}

# Function to create database if needed
create_database() {
    echo "🗄️  Ensuring database exists..."
    uv run python scripts/create_database.py
    if [ $? -eq 0 ]; then
        echo "✅ Database ready!"
    else
        echo "❌ Failed to create database!"
        exit 1
    fi
}

# Function to run migrations
run_migrations() {
    echo "📦 Running database migrations..."
    # First ensure database exists
    create_database

    # Then run migrations
    uv run yoyo apply --config yoyo.ini
    if [ $? -eq 0 ]; then
        echo "✅ Migrations completed successfully!"
    else
        echo "❌ Migration failed!"
        exit 1
    fi
}

# Function to create new migration
create_migration() {
    if [ -z "$1" ]; then
        echo "❌ Please provide a migration message"
        echo "Usage: $0 create 'Your migration message'"
        exit 1
    fi

    echo "📝 Creating new migration: $1"
    # Generate timestamp in yyyymmddhh format
    timestamp=$(date +"%Y%m%d%H")
    # Sanitize migration name
    sanitized_name=$(echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')
    filename="${timestamp}-${sanitized_name}.sql"
    rollback_filename="${timestamp}-${sanitized_name}.rollback.sql"

    # Create migration file
    cat > "migrations/${filename}" << EOF
-- $1
-- depends:

-- Add your SQL here
-- Example:
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(255) NOT NULL
-- );

-- CREATE INDEX idx_example_name ON example (name);
EOF

    # Create rollback file
    cat > "migrations/${rollback_filename}" << EOF
-- Rollback for $1

-- Add your rollback SQL here
-- Example:
-- DROP INDEX IF EXISTS idx_example_name;
-- DROP TABLE IF EXISTS example;
EOF

    if [ $? -eq 0 ]; then
        echo "✅ Migration created successfully:"
        echo "  Forward:  migrations/${filename}"
        echo "  Rollback: migrations/${rollback_filename}"
    else
        echo "❌ Failed to create migration!"
        exit 1
    fi
}

# Function to show migration status
show_status() {
    echo "📊 Current migration status:"
    uv run yoyo list --config yoyo.ini
}

# Main script logic
case "$1" in
    "upgrade"|"")
        if check_postgres; then
            run_migrations
        else
            echo ""
            echo "💡 To start PostgreSQL:"
            echo "   brew services start postgresql"
            echo "   # or"
            echo "   pg_ctl -D /usr/local/var/postgres start"
            echo ""
            echo "💡 To create the database:"
            echo "   createdb alice"
            echo ""
            exit 1
        fi
        ;;
    "create")
        if check_postgres; then
            create_migration "$2"
        else
            echo "❌ PostgreSQL must be running to create migrations"
            exit 1
        fi
        ;;
    "status")
        if check_postgres; then
            show_status
        else
            echo "❌ PostgreSQL must be running to check status"
            exit 1
        fi
        ;;
    "create-db")
        if check_postgres; then
            create_database
        else
            echo "❌ PostgreSQL must be running to create database"
            exit 1
        fi
        ;;
    "rollback")
        if check_postgres; then
            echo "🔄 Rolling back migrations..."
            uv run yoyo rollback --config yoyo.ini --batch
            if [ $? -eq 0 ]; then
                echo "✅ Rollback completed successfully!"
            else
                echo "❌ Rollback failed!"
                exit 1
            fi
        else
            echo "❌ PostgreSQL must be running to rollback migrations"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  upgrade (default)  Run pending migrations"
        echo "  create <message>   Create new migration"
        echo "  status            Show migration status"
        echo "  create-db         Create database if it doesn't exist"
        echo "  rollback          Rollback last migration"
        echo "  help              Show this help"
        echo ""
        echo "Environment Variables:"
        echo "  DATABASE_URL      PostgreSQL connection URL"
        echo "                    Default: postgresql+asyncpg://root:password@127.0.0.1:5432/alice"
        echo ""
        echo "Examples:"
        echo "  $0                           # Run migrations"
        echo "  $0 upgrade                   # Run migrations"
        echo "  $0 create 'Add user table'   # Create new migration"
        echo "  $0 status                    # Show migration status"
        echo "  $0 create-db                 # Create database if needed"
        echo "  $0 rollback                  # Rollback last migration"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac
