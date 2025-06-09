"""
FastAPI MVC Framework - Main Application Entry Point

This module initializes the FastAPI application with all necessary configurations,
middleware, and route handlers following MVC architecture patterns.
"""

import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.config.log_config import setup_logging, get_logger
from app.config.telemetry import setup_telemetry, instrument_fastapi
from app.config.migrations import run_migrations
from app.config.database import close_db
from app.core.exceptions import CustomException
from app.middleware.trace_middleware import TraceIDMiddleware
from app.views.api.v1 import users

# Initialize logging - handle reload scenario
if not hasattr(setup_logging, '_already_setup'):
    setup_logging()
    setup_logging._already_setup = True

# Initialize OpenTelemetry - handle reload scenario
if not hasattr(setup_telemetry, '_already_setup'):
    setup_telemetry()
    setup_telemetry._already_setup = True

logger = get_logger(__name__)

# Create a flag file to prevent duplicate startup logs across processes
startup_flag_file = Path(tempfile.gettempdir()) / f"fastapi_startup_{os.getpid()}.flag"

# Only log startup info once per application startup
should_log_startup = not any(
    Path(tempfile.gettempdir()).glob("fastapi_startup_*.flag")
)

if should_log_startup:
    # Create flag file
    startup_flag_file.touch()
    logger.info(f"Initializing {settings.PROJECT_NAME} v{settings.VERSION}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Application startup")

    # Run database migrations
    logger.info("Running database migrations...")
    migration_success = await run_migrations()
    if not migration_success:
        logger.error("❌ Failed to run migrations. Application may not work correctly.")
    else:
        logger.info("✅ Database migrations completed successfully")

    yield

    # Shutdown
    logger.info("🛑 Application shutdown")
    await close_db()
    logger.info("✅ Database connections closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A robust FastAPI MVC framework for building scalable web applications",
    version=settings.VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)

if should_log_startup:
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log format: {settings.LOG_FORMAT}")

# Add OpenTelemetry instrumentation
if should_log_startup:
    logger.info("Setting up OpenTelemetry instrumentation")
instrument_fastapi(app)

# Add trace ID middleware (should be added early in the middleware stack)
if should_log_startup:
    logger.info("Adding trace ID middleware")
app.add_middleware(TraceIDMiddleware)

# Configure CORS middleware
if should_log_startup:
    logger.info("Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    """Handle custom exceptions globally"""
    logger.error(
        f"Custom exception occurred",
        extra={
            "error_code": exc.error_code,
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }


# Include API routers
if should_log_startup:
    logger.info("Including API routers")
app.include_router(
    users.router,
    prefix="/api/v1",
    tags=["users"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    from app.config.uvicorn_config import get_uvicorn_config

    # Ensure logging is set up for direct execution
    setup_logging()

    logger.info(f"Starting {settings.PROJECT_NAME} server")
    logger.info(f"Server will run on http://{settings.HOST}:{settings.PORT}")
    logger.info(f"Reload enabled: {settings.ENVIRONMENT == 'development'}")

    # Get uvicorn configuration
    uvicorn_config = get_uvicorn_config()

    try:
        uvicorn.run(
            "app.main:app",
            **uvicorn_config
        )
    finally:
        # Clean up flag files on exit
        try:
            for flag_file in Path(tempfile.gettempdir()).glob("fastapi_startup_*.flag"):
                flag_file.unlink()
        except:
            pass
