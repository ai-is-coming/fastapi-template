# FastAPI MVC Template

A robust, production-ready FastAPI framework following MVC (Model-View-Controller) architecture patterns. This template provides a solid foundation for building scalable web applications and APIs with modern Python technologies.

## 🏗️ Architecture

This project follows a clean MVC architecture adapted for FastAPI:

- **Models** (`app/models/`): SQLAlchemy ORM models for database entities
- **Views** (`app/views/`): FastAPI route handlers and API endpoints
- **Controllers** (`app/controllers/`): Business logic layer between views and models
- **Repositories** (`app/repositories/`): Data access layer with database operations
- **Schemas** (`app/schemas/`): Pydantic models for data validation and serialization

## ✨ Features

- **🚀 FastAPI Framework**: High-performance async web framework
- **🏛️ MVC Architecture**: Clean separation of concerns
- **🗃️ SQLAlchemy ORM**: Async database operations with PostgreSQL
- **🔐 JWT Authentication**: Secure token-based authentication
- **📝 Pydantic Validation**: Request/response data validation
- **🔄 Database Migrations**: Alembic for database schema management
- **📊 Pagination**: Built-in pagination support
- **🧪 Testing Ready**: Pytest configuration for unit and integration tests
- **🐳 Docker Support**: Containerization ready
- **📚 API Documentation**: Auto-generated OpenAPI/Swagger docs
- **⚙️ Configuration Management**: Environment-based settings
- **🛡️ Security**: Password hashing, CORS, and security headers
- **📦 Dependency Injection**: Clean dependency management
- **📋 Structured Logging**: JSON logging by default with environment-based configuration
- **🔍 OpenTelemetry Integration**: Distributed tracing with trace ID correlation

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115+
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0+ (async)
- **Validation**: Pydantic 2.0+
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic
- **Testing**: Pytest with async support
- **Code Quality**: Black, isort, mypy
- **Package Management**: uv (modern Python package manager)
- **Observability**: OpenTelemetry for distributed tracing

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL 12+ (or SQLite for development)
- uv package manager
- VS Code (recommended) with Python extension

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-template
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb fastapi_mvc

   # Run migrations
   uv run alembic upgrade head
   ```

5. **Run the application**
   ```bash
   uv run python app/main.py
   ```

The API will be available at `http://localhost:8000`

- **API Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

## 🔧 VS Code Integration

This project includes comprehensive VS Code configuration for an optimal development experience.

### Quick Start with VS Code

1. **Open in VS Code**
   ```bash
   code .
   ```

2. **Install Recommended Extensions**
   - VS Code will prompt to install recommended extensions
   - Or manually install from the Extensions panel

3. **Run the Application**
   - Press `F5` to start debugging
   - Or `Ctrl+F5` to run without debugging
   - Uses debugpy for enhanced debugging capabilities
   - Or use `Ctrl+Shift+P` → "Tasks: Run Task" → "🚀 Start FastAPI Server"

### Launch Configuration

- **🚀 Run FastAPI App (with Trace Server)** - Run with trace server integration
  - Sends traces to your trace server at 127.0.0.1:4317
  - Clean console output (no verbose span logs)
  - Uses debugpy for better debugging performance
  - Integrated terminal output with JSON logging
  - Full OpenTelemetry instrumentation enabled

- **🚀 Run FastAPI App (Console Only)** - Run with console-only tracing
  - OpenTelemetry traces output to console only
  - Clean console output (no verbose span logs)
  - Uses debugpy for better debugging performance
  - Integrated terminal output with JSON logging

- **🔍 Run FastAPI App (Verbose Spans)** - Run with detailed span output
  - Sends traces to trace server AND outputs verbose spans to console
  - Detailed JSON span information for debugging
  - Uses debugpy for better debugging performance
  - Full OpenTelemetry instrumentation enabled

### Available Tasks

Access via `Ctrl+Shift+P` → "Tasks: Run Task":

- **🚀 Start FastAPI Server** - Start development server
- **🧪 Run Tests** - Execute test suite
- **📊 Run Tests with Coverage** - Tests with HTML coverage report
- **🎨 Format Code** - Format code with Black
- **📋 Sort Imports** - Sort imports with isort
- **🔍 Type Check** - Run MyPy type checking
- **🗃️ Run Database Migration** - Apply migrations
- **🆕 Create Database Migration** - Create new migration
- **📦 Install Dependencies** - Sync dependencies with uv
- **🧹 Clean Cache** - Remove Python cache files
- **🔧 Format, Sort & Type Check** - Run all code quality tools

### Debugging

1. **Set Breakpoints** - Click in the gutter or press `F9`
2. **Start Debugging** - Press `F5` and select "🐛 Debug FastAPI App"
3. **Debug Console** - Access variables and execute code
4. **Step Through Code** - Use `F10` (step over), `F11` (step into), `Shift+F11` (step out)

### Recommended Extensions

The project includes extension recommendations for:
- Python development (formatting, linting, type checking)
- FastAPI and web development
- Database management
- Git integration
- REST API testing
- Documentation writing

## 📁 Project Structure

```
fastapi-template/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Application settings
│   │   └── database.py         # Database configuration
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py            # Base model class
│   │   └── user.py            # User model
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── user.py            # User schemas
│   ├── controllers/           # Business logic
│   │   ├── __init__.py
│   │   └── user_controller.py # User controller
│   ├── views/                 # API routes
│   │   ├── __init__.py
│   │   └── api/v1/users.py    # User endpoints
│   ├── repositories/          # Data access layer
│   │   ├── __init__.py
│   │   ├── base.py            # Base repository
│   │   └── user_repository.py # User repository
│   ├── core/                  # Core utilities
│   │   ├── __init__.py
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   ├── exceptions.py      # Custom exceptions
│   │   └── security.py        # Authentication utilities
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       └── helpers.py
├── tests/                     # Test suite
├── alembic/                   # Database migrations
├── pyproject.toml            # Project configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## 🔧 Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

### Key Configuration Options

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ENVIRONMENT`: development/staging/production
- `ALLOWED_HOSTS`: CORS allowed origins

## 🗃️ Database

### Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "Description"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## 📋 Logging

The application features a comprehensive logging system with JSON format by default and environment-based configuration.

### Log Formats

**JSON Format (Default)**
```json
{
  "timestamp": "2024-01-01T12:00:00.123456",
  "level": "INFO",
  "caller": "app.main.create_user:42",
  "message": "User created successfully",
  "extra": {
    "user_id": 123,
    "username": "johndoe"
  }
}
```

**Standard Format**
```
2024-01-01 12:00:00 - app.main - INFO - User created successfully
```

### Configuration

Configure logging via environment variables:

```bash
# Log format: "json" (default) or "standard"
LOG_FORMAT=json

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Optional: Log to file
LOG_FILE=app.log

# Optional: Pretty print JSON logs (development)
LOG_JSON_INDENT=2

# Include/exclude log components
LOG_INCLUDE_TIMESTAMP=true
LOG_INCLUDE_LEVEL=true
LOG_INCLUDE_LOGGER_NAME=true
```

### Key Features

- **Unified Format**: All logs (application + uvicorn) use the same format
- **No Duplication**: Prevents duplicate log messages during development reload
- **Compact Caller Info**: Combines logger, function, and line into single "caller" field
- **Clean JSON Output**: Excludes color codes and terminal-specific fields from JSON logs
- **Structured Data**: JSON logs include rich metadata and contextual information
- **Environment Aware**: Automatically adjusts colors and formatting based on environment

### Usage Examples

```bash
# Run with JSON logging (default)
uv run python -m app.main

# Run with standard format
LOG_FORMAT=standard uv run python -m app.main

# Run with debug level and pretty JSON
LOG_LEVEL=DEBUG LOG_JSON_INDENT=2 uv run python -m app.main

# Run with file logging
LOG_FILE=app.log uv run python -m app.main

# Run with SQL query logging enabled
DATABASE_ECHO=true uv run python -m app.main

# Run with SQL logging and standard format for better readability
DATABASE_ECHO=true LOG_FORMAT=standard uv run python -m app.main
```

### Custom Logging in Code

```python
from app.config.log_config import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("User operation completed")

# Structured logging with extra data
logger.info(
    "User created successfully",
    extra={
        "user_id": user.id,
        "username": user.username,
        "operation": "create_user"
    }
)

# Error logging with context
logger.error(
    "Database operation failed",
    extra={
        "operation": "user_update",
        "user_id": 123,
        "error_code": "DB_CONNECTION_ERROR"
    }
)
```

### SQL Query Logging

Enable detailed SQL query logging to monitor database operations:

```bash
# Enable SQL logging
DATABASE_ECHO=true uv run python -m app.main
```

**Clean SQL Logs (JSON Format):**
```json
{
  "timestamp": "2025-06-07T00:52:50.811210",
  "level": "INFO",
  "caller": "app.database.log_sql_query:427",
  "message": "SELECT users.id, users.email, users.username, users.hashed_password, users.full_name, users.bio, users.avatar_url, users.is_active, users.is_superuser, users.created_at, users.updated_at FROM users WHERE users.email = 'super-clean@example.com'",
  "extra": {
    "taskName": "Task-3"
  }
}
{
  "timestamp": "2025-06-07T00:52:51.001779",
  "level": "INFO",
  "caller": "app.database.log_sql_query:427",
  "message": "INSERT INTO users (email, username, hashed_password, full_name, bio, avatar_url, is_active, is_superuser) VALUES ('super-clean@example.com', 'superclean', '$2b$12$...', 'Super Clean User', 'Testing super clean SQL logging', NULL, TRUE, FALSE) RETURNING users.id, users.created_at, users.updated_at",
  "extra": {
    "taskName": "Task-3"
  }
}
```

**Clean SQL Logs (Standard Format):**
```
2025-06-07 00:52:50 - app.database - INFO - SELECT users.id, users.email, users.username, users.hashed_password, users.full_name, users.bio, users.avatar_url, users.is_active, users.is_superuser, users.created_at, users.updated_at FROM users WHERE users.email = 'super-clean@example.com'

2025-06-07 00:52:51 - app.database - INFO - INSERT INTO users (email, username, hashed_password, full_name, bio, avatar_url, is_active, is_superuser) VALUES ('super-clean@example.com', 'superclean', '$2b$12$...', 'Super Clean User', 'Testing super clean SQL logging', NULL, TRUE, FALSE) RETURNING users.id, users.created_at, users.updated_at
```

**Features:**
- **Clean SQL Queries**: Single-line SQL with no newlines or formatting noise
- **Real Parameter Values**: Shows actual values instead of $1::VARCHAR placeholders
- **No Duplicate Logs**: Only one clean log per SQL query (no SQLAlchemy duplicates)
- **Copy-Paste Ready**: SQL can be directly executed in database tools
- **Type Casting Removal**: Removes PostgreSQL type annotations for cleaner display
- **Custom Logger**: Uses `app.database` logger for easy identification
- **Dual Format Support**: Works with both JSON and standard log formats
- **Production Ready**: Structured logging for monitoring and debugging

**Perfect Results:**
- ✅ **Single Log Per Query**: No more duplicate SQLAlchemy logs
- ✅ **No Newlines**: SQL queries are clean single lines
- ✅ **Real Values**: Shows `'user@example.com'` instead of `$1::VARCHAR`
- ✅ **Clean Format**: Easy to copy/paste and analyze
- ✅ **Easy Identification**: Look for `caller": "app.database.log_sql_query:427"`

## 🔍 OpenTelemetry Integration

The application includes comprehensive OpenTelemetry integration for distributed tracing and observability.

### Features

- **Automatic Trace ID Generation**: Each API request gets a unique trace ID
- **Trace ID in Logs**: All log entries include the trace ID for correlation
- **Response Headers**: Trace ID is returned in `X-Trace-ID` response header
- **Custom Trace ID Support**: Use existing trace ID from `X-Trace-ID` request header
- **Database Tracing**: Automatic instrumentation of SQLAlchemy database operations
- **FastAPI Instrumentation**: Automatic HTTP request/response tracing
- **Span Correlation**: Full request lifecycle tracing with parent-child relationships

### Usage

**Automatic Trace ID Generation:**
```bash
curl -X GET http://localhost:8001/health
# Response includes: X-Trace-Id: ac95151b356d446e8dc7c89312cdcbbe659bf81dd6e5418c
```

**Using Custom Trace ID:**
```bash
curl -X GET http://localhost:8001/health \
  -H "X-Trace-ID: my-custom-trace-id-12345"
# Response includes: X-Trace-Id: my-custom-trace-id-12345
```

### Log Correlation

All logs automatically include the trace ID for easy correlation:

**JSON Format:**
```json
{
  "timestamp": "2025-06-07T01:07:12.096781",
  "level": "INFO",
  "caller": "app.controllers.user_controller.create_user:82",
  "trace_id": "ac95151b356d446e8dc7c89312cdcbbe659bf81dd6e5418c",
  "message": "Successfully created user",
  "extra": {
    "user_id": 10,
    "username": "tracetest",
    "email": "trace-test@example.com"
  }
}
```

**Standard Format:**
```
2025-06-07 01:07:12 - app.controllers.user_controller - INFO - [trace:ac95151b] Successfully created user
```

### Span Information

In development mode, detailed span information is output to the console:

```json
{
  "name": "POST /api/v1/users",
  "context": {
    "trace_id": "0x28a8a4f643727679d04faf4e8e687aa1",
    "span_id": "0xad61f5b380dbceb0"
  },
  "kind": "SpanKind.SERVER",
  "attributes": {
    "http.method": "POST",
    "http.url": "http://localhost:8001/api/v1/users",
    "http.route": "/api/v1/users",
    "trace.id": "ac95151b356d446e8dc7c89312cdcbbe659bf81dd6e5418c",
    "http.status_code": 201
  }
}
```

### Configuration

OpenTelemetry is automatically configured and enabled. Configure it using environment variables:

**Basic Configuration (Clean Console Output):**
```bash
# Service identification
OTEL_SERVICE_NAME="fastapi-template"
OTEL_SERVICE_VERSION="1.0.0"
ENVIRONMENT="development"
OTEL_CONSOLE_SPANS=false  # Clean console output (default)
```

**Trace Server Configuration:**
```bash
# Enable sending traces to your trace server
OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317"

# Optional: Add custom headers for authentication
OTEL_EXPORTER_OTLP_HEADERS="api-key=your-api-key,authorization=Bearer token"

# Service identification
OTEL_SERVICE_NAME="fastapi-template"
OTEL_SERVICE_VERSION="1.0.0"
ENVIRONMENT="production"
OTEL_CONSOLE_SPANS=false  # Clean console output
```

**Verbose Debugging Configuration:**
```bash
# Enable detailed span output for debugging
OTEL_CONSOLE_SPANS=true
OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317"
OTEL_SERVICE_NAME="fastapi-template"
OTEL_SERVICE_VERSION="1.0.0"
ENVIRONMENT="development"
```

**Custom Spans in Code:**
```python
# In app/config/telemetry.py
from app.config.telemetry import get_tracer, create_span

# Create custom spans
tracer = get_tracer()
with tracer.start_as_current_span("custom_operation") as span:
    span.set_attribute("operation.type", "business_logic")
    # Your code here
```

### Running with Trace Server

**Start with trace server enabled:**
```bash
# Set environment variables and start the server
OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4317" \
DATABASE_URL="postgresql+asyncpg://root:password@127.0.0.1:5432/alice" \
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001
```

**Or add to your .env file:**
```bash
# Add to .env
OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4317
OTEL_SERVICE_NAME=fastapi-template
OTEL_SERVICE_VERSION=1.0.0
ENVIRONMENT=production
```

When configured with a trace server endpoint:
- ✅ **Traces are sent to your trace server** at 127.0.0.1:4317
- ✅ **Console output is still available** in development mode
- ✅ **All trace data is preserved** with service metadata
- ✅ **Compatible with Jaeger, Zipkin, and other OTLP-compatible systems**

### Benefits

- **🔍 Request Tracing**: Track requests across the entire application stack
- **📊 Performance Monitoring**: Identify bottlenecks and slow operations
- **🐛 Debugging**: Correlate logs with specific requests using trace IDs
- **📈 Observability**: Monitor application health and performance
- **🔗 Distributed Tracing**: Ready for microservices architecture
- **📋 Log Correlation**: Easy to find all logs related to a specific request
- **🖥️ Trace Server Integration**: Send traces to external monitoring systems

## 🗃️ Database Setup

### PostgreSQL Setup

1. **Start PostgreSQL** (if not running):
   ```bash
   # macOS with Homebrew
   brew services start postgresql

   # Or manually
   pg_ctl -D /usr/local/var/postgres start
   ```

2. **Create Database**:
   ```bash
   createdb alice
   ```

3. **Run Migrations**:
   ```bash
   # Using the migration script
   ./scripts/migrate.sh

   # Or manually
   DATABASE_URL="postgresql+asyncpg://root:password@127.0.0.1:5432/alice" uv run alembic upgrade head
   ```

### Migration Commands

```bash
# Run migrations
./scripts/migrate.sh upgrade

# Create new migration
./scripts/migrate.sh create "Add new table"

# Check migration status
./scripts/migrate.sh status

# Show help
./scripts/migrate.sh help
```

### Database Configuration

The application is configured to use PostgreSQL by default in VS Code launch configuration:

- **Host**: 127.0.0.1:5432
- **Username**: root
- **Password**: password
- **Database**: alice

You can override these settings using environment variables:

```bash
DATABASE_URL="postgresql+asyncpg://username:password@host:port/database"
DATABASE_ECHO=true  # Enable SQL query logging
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_users.py
```

## 🐳 Docker

```bash
# Build image
docker build -t fastapi-mvc .

# Run container
docker run -p 8000:8000 fastapi-mvc

# Using docker-compose
docker-compose up -d
```

## 📚 API Documentation

The API automatically generates documentation available at:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

## 🔐 Authentication

The API uses JWT tokens for authentication:

1. Create a user account
2. Login to receive access and refresh tokens
3. Include the access token in the `Authorization` header: `Bearer <token>`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions and support, please open an issue in the repository.