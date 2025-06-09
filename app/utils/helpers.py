"""
Utility Helper Functions

This module contains various utility functions and helpers used throughout
the application, including logging utilities and common operations.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from app.config.log_config import get_logger

logger = get_logger(__name__)


def log_execution_time(func_name: Optional[str] = None):
    """
    Decorator to log function execution time.
    
    Args:
        func_name: Optional custom function name for logging
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            logger.debug(f"Starting execution of {name}")
            
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Completed execution of {name}",
                    extra={
                        "function": name,
                        "execution_time_seconds": round(execution_time, 4),
                        "status": "success"
                    }
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Failed execution of {name}",
                    extra={
                        "function": name,
                        "execution_time_seconds": round(execution_time, 4),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            logger.debug(f"Starting execution of {name}")
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    f"Completed execution of {name}",
                    extra={
                        "function": name,
                        "execution_time_seconds": round(execution_time, 4),
                        "status": "success"
                    }
                )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Failed execution of {name}",
                    extra={
                        "function": name,
                        "execution_time_seconds": round(execution_time, 4),
                        "status": "error",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_api_request(request_data: Dict[str, Any], endpoint: str) -> None:
    """
    Log API request information.
    
    Args:
        request_data: Request data to log
        endpoint: API endpoint being called
    """
    logger.info(
        f"API request to {endpoint}",
        extra={
            "endpoint": endpoint,
            "request_data": request_data,
            "request_type": "api_request"
        }
    )


def log_api_response(response_data: Dict[str, Any], endpoint: str, status_code: int) -> None:
    """
    Log API response information.
    
    Args:
        response_data: Response data to log
        endpoint: API endpoint that was called
        status_code: HTTP status code
    """
    logger.info(
        f"API response from {endpoint}",
        extra={
            "endpoint": endpoint,
            "status_code": status_code,
            "response_data": response_data,
            "request_type": "api_response"
        }
    )


def log_database_operation(operation: str, table: str, record_id: Optional[Any] = None) -> None:
    """
    Log database operation.
    
    Args:
        operation: Type of operation (CREATE, READ, UPDATE, DELETE)
        table: Database table name
        record_id: Optional record ID
    """
    extra_data = {
        "operation": operation,
        "table": table,
        "operation_type": "database"
    }
    
    if record_id is not None:
        extra_data["record_id"] = record_id
    
    logger.debug(
        f"Database {operation} operation on {table}",
        extra=extra_data
    )


def sanitize_log_data(data: Dict[str, Any], sensitive_fields: Optional[list] = None) -> Dict[str, Any]:
    """
    Sanitize sensitive data from log entries.
    
    Args:
        data: Data dictionary to sanitize
        sensitive_fields: List of field names to sanitize
        
    Returns:
        Sanitized data dictionary
    """
    if sensitive_fields is None:
        sensitive_fields = [
            'password', 'hashed_password', 'token', 'secret', 'key',
            'authorization', 'auth', 'credential', 'private'
        ]
    
    sanitized = data.copy()
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"
    
    return sanitized


def format_user_info(user) -> Dict[str, Any]:
    """
    Format user information for logging (without sensitive data).
    
    Args:
        user: User object
        
    Returns:
        Formatted user info dictionary
    """
    return {
        "user_id": getattr(user, 'id', None),
        "username": getattr(user, 'username', None),
        "email": getattr(user, 'email', None),
        "is_active": getattr(user, 'is_active', None),
        "is_superuser": getattr(user, 'is_superuser', None)
    }
