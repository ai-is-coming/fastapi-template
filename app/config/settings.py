"""
Application Configuration Settings

This module contains all configuration settings for the FastAPI MVC application.
Uses Pydantic Settings for environment variable management and validation.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    PROJECT_NAME: str = Field(default="FastAPI MVC Template", description="Project name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=True, description="Debug mode")
    
    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Allowed CORS origins")
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://root:password@127.0.0.1:5432/alice",
        description="Database connection URL"
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis Settings (Optional)
    REDIS_URL: Optional[str] = Field(default=None, description="Redis connection URL")
    
    # Security Settings
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration time")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration time")
    
    # Email Settings (Optional)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    SMTP_PORT: Optional[int] = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    SMTP_TLS: bool = Field(default=True, description="Use TLS for SMTP")
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes (10MB)")
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    
    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format: 'json' or 'standard'")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path (optional)")
    LOG_JSON_INDENT: Optional[int] = Field(default=None, description="JSON log indentation (for pretty printing)")
    LOG_INCLUDE_TIMESTAMP: bool = Field(default=True, description="Include timestamp in logs")
    LOG_INCLUDE_LEVEL: bool = Field(default=True, description="Include log level in logs")
    LOG_INCLUDE_LOGGER_NAME: bool = Field(default=True, description="Include logger name in logs")

    # OpenTelemetry Settings
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(default="", description="OTLP exporter endpoint (e.g., http://127.0.0.1:4317)")
    OTEL_EXPORTER_OTLP_HEADERS: str = Field(default="", description="OTLP exporter headers (comma-separated key=value pairs)")
    OTEL_SERVICE_NAME: str = Field(default="fastapi-template", description="OpenTelemetry service name")
    OTEL_SERVICE_VERSION: str = Field(default="1.0.0", description="OpenTelemetry service version")
    OTEL_CONSOLE_SPANS: bool = Field(default=False, description="Enable console span output (verbose)")

    # API Settings
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")
    ITEMS_PER_PAGE: int = Field(default=20, description="Default pagination size")
    MAX_ITEMS_PER_PAGE: int = Field(default=100, description="Maximum pagination size")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()
