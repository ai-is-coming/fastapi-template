"""
Uvicorn Configuration

This module provides custom uvicorn configuration to integrate with our
logging system and prevent duplicate log messages.
"""

from typing import Dict, Any

from app.config.settings import settings


def get_uvicorn_log_config() -> Dict[str, Any]:
    """
    Get uvicorn logging configuration that integrates with our logging system.
    
    Returns:
        Dictionary with uvicorn logging configuration
    """
    # Determine if we should use JSON format
    use_json = settings.LOG_FORMAT.lower() == "json"
    
    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "app.config.log_config.JSONFormatter" if use_json else "app.config.log_config.StandardFormatter",
                "include_timestamp": settings.LOG_INCLUDE_TIMESTAMP,
                "include_level": settings.LOG_INCLUDE_LEVEL,
                "include_logger_name": settings.LOG_INCLUDE_LOGGER_NAME,
                "json_indent": settings.LOG_JSON_INDENT,
            } if use_json else {
                "()": "app.config.log_config.StandardFormatter",
                "use_colors": settings.ENVIRONMENT == "development",
            },
            "access": {
                "()": "app.config.log_config.JSONFormatter" if use_json else "app.config.log_config.StandardFormatter",
                "include_timestamp": settings.LOG_INCLUDE_TIMESTAMP,
                "include_level": settings.LOG_INCLUDE_LEVEL,
                "include_logger_name": settings.LOG_INCLUDE_LOGGER_NAME,
                "json_indent": settings.LOG_JSON_INDENT,
            } if use_json else {
                "()": "app.config.log_config.StandardFormatter",
                "use_colors": settings.ENVIRONMENT == "development",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL.upper(),
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "WARNING",  # Reduce access log noise
                "propagate": False,
            },
        },
    }
    
    return config


def get_uvicorn_config() -> Dict[str, Any]:
    """
    Get complete uvicorn configuration.
    
    Returns:
        Dictionary with uvicorn configuration
    """
    return {
        "host": settings.HOST,
        "port": settings.PORT,
        "reload": settings.ENVIRONMENT == "development",
        "log_config": get_uvicorn_log_config(),
        "log_level": settings.LOG_LEVEL.lower(),
        "access_log": False,  # Disable default access logging to avoid duplication
    }
