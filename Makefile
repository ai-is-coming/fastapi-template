# FastAPI Project Makefile
# ======================

.PHONY: help install dev run test clean migrate-up migrate-down migrate-status migrate-create migrate-rollback db-create db-reset lint format check

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Help target
help: ## Show this help message
	@echo "$(BLUE)FastAPI Project Commands$(RESET)"
	@echo "========================"
	@echo ""
	@echo "$(GREEN)Development:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(install|dev|run|test|clean|lint|format|check)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Database & Migrations:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(migrate|db)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Examples:$(RESET)"
	@echo "  make migrate-up                    # Apply pending migrations"
	@echo "  make migrate-down                  # Rollback last migration"
	@echo "  make migrate-create MSG=\"Add users table\"  # Create new migration"
	@echo "  make db-reset                      # Reset database and apply all migrations"

# Development Commands
# ===================

install: ## Install dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	uv sync

dev: install ## Install dependencies and setup development environment
	@echo "$(GREEN)Development environment ready!$(RESET)"

run: ## Run the FastAPI development server
	@echo "$(BLUE)Starting FastAPI development server...$(RESET)"
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests
	@echo "$(BLUE)Running tests...$(RESET)"
	uv run pytest

clean: ## Clean up cache files and temporary files
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Code Quality Commands
# ====================

lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(RESET)"
	uv run ruff check .

format: ## Format code
	@echo "$(BLUE)Formatting code...$(RESET)"
	uv run ruff format .

check: lint ## Run all code quality checks
	@echo "$(GREEN)Code quality checks completed!$(RESET)"

# Database Commands
# ================

db-create: ## Create database if it doesn't exist
	@echo "$(BLUE)Creating database...$(RESET)"
	uv run python scripts/create_database.py

db-reset: ## Reset database (drop and recreate with all migrations)
	@echo "$(YELLOW)Resetting database...$(RESET)"
	@echo "$(RED)WARNING: This will destroy all data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	uv run python -c "import asyncio; from sqlalchemy.ext.asyncio import create_async_engine; from sqlalchemy import text; from app.config.settings import settings; from urllib.parse import urlparse; \
	async def drop_db(): \
		parsed = urlparse(settings.DATABASE_URL); \
		db_name = parsed.path.lstrip('/'); \
		postgres_url = settings.DATABASE_URL.replace(f'/{db_name}', '/postgres'); \
		engine = create_async_engine(postgres_url); \
		try: \
			async with engine.execution_options(isolation_level='AUTOCOMMIT').connect() as conn: \
				await conn.execute(text(f'DROP DATABASE IF EXISTS \"{db_name}\"')); \
				print(f'Dropped database {db_name}'); \
		finally: \
			await engine.dispose(); \
	asyncio.run(drop_db())"
	@$(MAKE) db-create
	@$(MAKE) migrate-up

# Migration Commands
# =================

migrate-up: ## Apply pending migrations (migrate up)
	@echo "$(BLUE)Applying migrations...$(RESET)"
	uv run python scripts/manage_migrations.py apply

migrate-down: ## Rollback last migration (migrate down)
	@echo "$(YELLOW)Rolling back last migration...$(RESET)"
	uv run python scripts/manage_migrations.py rollback

migrate-status: ## Show migration status
	@echo "$(BLUE)Migration status:$(RESET)"
	uv run python scripts/manage_migrations.py status

migrate-create: ## Create new migration (use: make migrate-create MSG="Your migration message")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: MSG is required$(RESET)"; \
		echo "Usage: make migrate-create MSG=\"Your migration message\""; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating migration: $(MSG)$(RESET)"
	uv run python scripts/manage_migrations.py create "$(MSG)"

migrate-rollback: migrate-down ## Alias for migrate-down

# Alternative migration commands using shell scripts
# =================================================

migrate-up-shell: ## Apply migrations using shell script
	@echo "$(BLUE)Applying migrations (shell script)...$(RESET)"
	bash scripts/migrate.sh upgrade

migrate-down-shell: ## Rollback migrations using shell script
	@echo "$(YELLOW)Rolling back migrations (shell script)...$(RESET)"
	bash scripts/migrate.sh rollback

migrate-status-shell: ## Show migration status using shell script
	@echo "$(BLUE)Migration status (shell script):$(RESET)"
	bash scripts/migrate.sh status

migrate-create-shell: ## Create migration using shell script (use: make migrate-create-shell MSG="Your message")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)Error: MSG is required$(RESET)"; \
		echo "Usage: make migrate-create-shell MSG=\"Your migration message\""; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating migration: $(MSG)$(RESET)"
	bash scripts/migrate.sh create "$(MSG)"

# Direct yoyo commands
# ===================

yoyo-up: ## Apply migrations using yoyo directly
	@echo "$(BLUE)Applying migrations (yoyo)...$(RESET)"
	uv run yoyo apply --config yoyo.ini --batch

yoyo-down: ## Rollback migrations using yoyo directly
	@echo "$(YELLOW)Rolling back migrations (yoyo)...$(RESET)"
	uv run yoyo rollback --config yoyo.ini --batch

yoyo-status: ## Show migration status using yoyo directly
	@echo "$(BLUE)Migration status (yoyo):$(RESET)"
	uv run yoyo list --config yoyo.ini

# Utility Commands
# ===============

logs: ## Show application logs (if running in background)
	@echo "$(BLUE)Showing logs...$(RESET)"
	tail -f logs/*.log 2>/dev/null || echo "No log files found"

ps: ## Show running processes related to the app
	@echo "$(BLUE)FastAPI processes:$(RESET)"
	ps aux | grep -E "(uvicorn|fastapi)" | grep -v grep || echo "No FastAPI processes found"

# Docker commands (if using Docker)
# =================================

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t fastapi-app .

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	docker run -p 8000:8000 fastapi-app

# Development Workflow Commands
# ============================

setup: install db-create migrate-up ## Complete project setup (install + database + migrations)
	@echo "$(GREEN)Project setup completed!$(RESET)"
	@echo "Run 'make run' to start the development server"

reset-dev: clean db-reset ## Reset development environment
	@echo "$(GREEN)Development environment reset!$(RESET)"

fresh-start: clean install db-reset ## Fresh start (clean + install + reset database)
	@echo "$(GREEN)Fresh start completed!$(RESET)"

# Quick shortcuts
# ==============

up: migrate-up ## Quick alias for migrate-up
down: migrate-down ## Quick alias for migrate-down
status: migrate-status ## Quick alias for migrate-status
create: migrate-create ## Quick alias for migrate-create
