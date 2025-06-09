"""
Custom Exceptions

This module contains custom exception classes for the application
with proper error codes and HTTP status codes.
"""

from typing import Any, Dict, Optional


class CustomException(Exception):
    """
    Base custom exception class.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize custom exception.
        
        Args:
            detail: Error message
            status_code: HTTP status code
            error_code: Application-specific error code
            headers: Optional HTTP headers
        """
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.headers = headers
        super().__init__(detail)


class ValidationException(CustomException):
    """Exception for validation errors"""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=422, error_code="VALIDATION_ERROR")


class AuthenticationException(CustomException):
    """Exception for authentication errors"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationException(CustomException):
    """Exception for authorization errors"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(detail=detail, status_code=403, error_code="AUTHORIZATION_ERROR")


class NotFoundException(CustomException):
    """Exception for resource not found errors"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=404, error_code="NOT_FOUND")


class ConflictException(CustomException):
    """Exception for resource conflict errors"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=409, error_code="CONFLICT")


class BadRequestException(CustomException):
    """Exception for bad request errors"""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail=detail, status_code=400, error_code="BAD_REQUEST")


class InternalServerException(CustomException):
    """Exception for internal server errors"""
    
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail=detail, status_code=500, error_code="INTERNAL_SERVER_ERROR")


class RateLimitException(CustomException):
    """Exception for rate limit errors"""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=429, error_code="RATE_LIMIT_EXCEEDED")


class ServiceUnavailableException(CustomException):
    """Exception for service unavailable errors"""
    
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(detail=detail, status_code=503, error_code="SERVICE_UNAVAILABLE")


# User-specific exceptions
class UserNotFoundException(NotFoundException):
    """Exception for user not found errors"""
    
    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail)


class UserAlreadyExistsException(ConflictException):
    """Exception for user already exists errors"""
    
    def __init__(self, detail: str = "User already exists"):
        super().__init__(detail=detail)


class InvalidCredentialsException(AuthenticationException):
    """Exception for invalid credentials errors"""
    
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail)


class InactiveUserException(AuthenticationException):
    """Exception for inactive user errors"""
    
    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail)
