# Makefile Quick Reference

This document provides a quick reference for all available Makefile commands in the FastAPI project.

## 🚀 Quick Start

```bash
# Complete project setup (first time)
make setup

# Daily development workflow
make up                    # Apply any new migrations
make run                   # Start development server
make down                  # Rollback if needed
```

## 📦 Development Commands

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make dev` | Install dependencies and setup development environment |
| `make run` | Run the FastAPI development server |
| `make test` | Run tests |
| `make clean` | Clean up cache files and temporary files |
| `make setup` | Complete project setup (install + database + migrations) |
| `make reset-dev` | Reset development environment |
| `make fresh-start` | Fresh start (clean + install + reset database) |

## 🗄️ Database & Migration Commands

### Quick Aliases (Recommended)
| Command | Description |
|---------|-------------|
| `make up` | Apply pending migrations |
| `make down` | Rollback last migration |
| `make status` | Show migration status |
| `make create MSG="Your message"` | Create new migration |

### Full Migration Commands
| Command | Description |
|---------|-------------|
| `make migrate-up` | Apply pending migrations (migrate up) |
| `make migrate-down` | Rollback last migration (migrate down) |
| `make migrate-status` | Show migration status |
| `make migrate-create MSG="message"` | Create new migration |
| `make migrate-rollback` | Alias for migrate-down |

### Database Management
| Command | Description |
|---------|-------------|
| `make db-create` | Create database if it doesn't exist |
| `make db-reset` | Reset database (⚠️ destroys all data) |

### Shell Script Variants
| Command | Description |
|---------|-------------|
| `make migrate-up-shell` | Apply migrations using shell script |
| `make migrate-down-shell` | Rollback migrations using shell script |
| `make migrate-status-shell` | Show migration status using shell script |
| `make migrate-create-shell MSG="message"` | Create migration using shell script |

### Direct Yoyo Commands
| Command | Description |
|---------|-------------|
| `make yoyo-up` | Apply migrations using yoyo directly |
| `make yoyo-down` | Rollback migrations using yoyo directly |
| `make yoyo-status` | Show migration status using yoyo directly |

## 🔧 Code Quality Commands

| Command | Description |
|---------|-------------|
| `make lint` | Run linting checks |
| `make format` | Format code |
| `make check` | Run all code quality checks |

## 🐳 Docker Commands

| Command | Description |
|---------|-------------|
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |

## 🔍 Utility Commands

| Command | Description |
|---------|-------------|
| `make logs` | Show application logs |
| `make ps` | Show running FastAPI processes |
| `make help` | Show all available commands |

## 📝 Common Workflows

### New Developer Setup
```bash
make fresh-start    # Clean setup from scratch
make run           # Start development server
```

### Daily Development
```bash
make status        # Check migration status
make up           # Apply any new migrations
make run          # Start development server
```

### Creating New Features
```bash
make create MSG="Add user profiles table"
# Edit the generated migration files
make up           # Apply the migration
make test         # Run tests
```

### Rollback Workflow
```bash
make status       # Check current status
make down         # Rollback last migration
make status       # Verify rollback
make up           # Re-apply if needed
```

### Database Reset (Development)
```bash
make db-reset     # ⚠️ Destroys all data and reapplies migrations
```

## ⚠️ Important Notes

- **`make db-reset`** will destroy all data! Only use in development.
- Always check `make status` before and after migrations.
- Use `MSG="Your message"` when creating migrations.
- The `make setup` command is perfect for new developers.
- Quick aliases (`up`, `down`, `status`, `create`) are recommended for daily use.

## 🆘 Help

Run `make help` to see all available commands with descriptions.

For migration-specific help, see `migrations/README.md`.
