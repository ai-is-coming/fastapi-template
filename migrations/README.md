# Database Migrations with yoyo-migrations

This project uses [yoyo-migrations](https://pypi.org/project/yoyo-migrations/) for database schema management with raw SQL files.

## Features

- ✅ Raw SQL migration files
- ✅ Automatic migration execution on app startup
- ✅ Automatic database creation if it doesn't exist
- ✅ Skip already applied migrations
- ✅ PostgreSQL support (no SQLite)
- ✅ Naming convention: `yyyymmddhh-description.sql`
- ✅ Rollback support

## Migration File Format

Migration files follow this naming convention: `yyyymmddhh-description.sql`

Example: `2025060623-create_users_table.sql`

### File Structure

```sql
-- Description of the migration
-- depends:

CREATE TABLE example (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE INDEX idx_example_name ON example (name);
```

Each SQL statement is executed in order. Yoyo automatically handles transaction management and tracks applied migrations.

### Rollback Files

For each migration file, you should create a corresponding rollback file:

- Migration: `2025060623-create_users_table.sql`
- Rollback: `2025060623-create_users_table.rollback.sql`

The rollback file contains SQL statements to undo the migration:

```sql
-- Rollback for create users table migration

DROP INDEX IF EXISTS ix_users_id;
DROP INDEX IF EXISTS ix_users_username;
DROP INDEX IF EXISTS ix_users_email;
DROP TABLE IF EXISTS users;
```

## Configuration

The migration system is configured in `yoyo.ini`:

```ini
[DEFAULT]
sources = migrations
database = postgresql://root:password@127.0.0.1:5432/alice
verbosity = 1
batch_mode = on
```

## Usage

### Automatic Migrations

Migrations run automatically when the FastAPI application starts. The system will:

1. **Check if the database exists** - if not, it creates it automatically
2. **Run pending migrations** - applies any new migration files
3. **Skip already applied migrations** - only runs what's needed

No manual intervention required for normal operation.

### Using Makefile Commands (Recommended)

The project includes a comprehensive Makefile with migration commands:

```bash
# Show all available commands
make help

# Migration commands (quick aliases)
make up                    # Apply pending migrations
make down                  # Rollback last migration
make status                # Show migration status
make create MSG="Add new table"  # Create new migration

# Full migration commands
make migrate-up            # Apply pending migrations
make migrate-down          # Rollback last migration
make migrate-status        # Show migration status
make migrate-create MSG="Your message"  # Create new migration

# Database commands
make db-create             # Create database if needed
make db-reset              # Reset database (WARNING: destroys data)

# Direct yoyo commands
make yoyo-up               # Apply migrations using yoyo directly
make yoyo-down             # Rollback using yoyo directly
make yoyo-status           # Show status using yoyo directly
```

### Manual Migration Management

The project provides multiple ways to manage migrations:

1. **Makefile commands** (recommended for development)
2. **Python management script** (programmatic access)
3. **Shell script** (bash-based commands)
4. **Direct yoyo commands** (low-level access)

#### Using the management script:

```bash
# Check migration status
python scripts/manage_migrations.py status

# Apply pending migrations
python scripts/manage_migrations.py apply

# Create a new migration
python scripts/manage_migrations.py create "Add new table"

# List all migration files
python scripts/manage_migrations.py list

# Create database if it doesn't exist
python scripts/manage_migrations.py create-db

# Rollback migrations
python scripts/manage_migrations.py rollback

# Rollback to specific migration
python scripts/manage_migrations.py rollback --revision 2025060623-create_users_table
```

#### Using the shell script:

```bash
# Run migrations
bash scripts/migrate.sh upgrade

# Check status
bash scripts/migrate.sh status

# Create new migration
bash scripts/migrate.sh create "Add new table"

# Create database if needed
bash scripts/migrate.sh create-db

# Rollback last migration
bash scripts/migrate.sh rollback
```

#### Using yoyo directly:

```bash
# List migrations
uv run yoyo list --config yoyo.ini

# Apply migrations
uv run yoyo apply --config yoyo.ini

# Rollback last migration
uv run yoyo rollback --config yoyo.ini --batch

# Rollback to specific migration
uv run yoyo rollback --config yoyo.ini --batch --revision 2025060623-create_users_table
```

## Database Requirements

- PostgreSQL 12+ running on localhost:5432
- User: `root` with password `password`
- Database: `alice` (will be created automatically if it doesn't exist)

## Migration Best Practices

1. **Always test migrations** on a copy of production data
2. **Write rollback statements** for every migration
3. **Use descriptive names** for migration files
4. **Keep migrations small** and focused on single changes
5. **Never modify existing migrations** once they're applied in production

## Troubleshooting

### Connection Issues

If you get connection errors:

1. Ensure PostgreSQL is running:
   ```bash
   brew services start postgresql
   ```

2. The database will be created automatically when you run migrations

3. If you need to create it manually:
   ```bash
   createdb alice
   ```

4. Check connection settings in your `.env` file

### Migration Errors

- Check the migration SQL syntax
- Ensure dependencies are correctly specified
- Review the yoyo logs for detailed error messages
