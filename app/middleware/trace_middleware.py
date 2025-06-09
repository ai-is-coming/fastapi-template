"""
Trace ID Middleware

This middleware handles trace ID extraction from request headers and generation
of new trace IDs. It also adds trace IDs to response headers and logging context.
"""

from typing import Callable
from contextvars import ContextVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
from opentelemetry.trace import set_span_in_context, SpanKind, SpanContext, TraceFlags
from opentelemetry.context import attach, detach
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator

from app.config.telemetry import get_tracer
from app.config.log_config import get_logger

logger = get_logger(__name__)

# Context variable to store trace ID for logging
trace_id_context: ContextVar[str] = ContextVar('trace_id', default='')


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle trace ID extraction and generation.
    
    This middleware:
    1. Checks for existing X-Trace-ID header in request
    2. If present, uses that trace ID
    3. If not present, generates a new trace ID
    4. Adds trace ID to response headers
    5. Makes trace ID available to logging system
    6. Creates OpenTelemetry spans with the same trace ID
    """
    
    def __init__(self, app, header_name: str = "X-Trace-ID"):
        super().__init__(app)
        self.header_name = header_name
        self.tracer = get_tracer()
        self.id_generator = RandomIdGenerator()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and response with trace ID handling.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response with trace ID header
        """
        # Check for existing trace ID in request headers
        existing_trace_id = request.headers.get(self.header_name)
        
        if existing_trace_id:
            # Use existing trace ID from request
            trace_id_str = existing_trace_id
            logger.debug(f"Using existing trace ID from request: {trace_id_str}")
            # Convert hex string to integer for OpenTelemetry
            try:
                trace_id_int = int(trace_id_str, 16)
            except ValueError:
                # If invalid hex, generate new trace ID
                trace_id_int = self.id_generator.generate_trace_id()
                trace_id_str = format(trace_id_int, '032x')
                logger.debug(f"Invalid trace ID format, generated new: {trace_id_str}")
        else:
            # Generate new trace ID
            trace_id_int = self.id_generator.generate_trace_id()
            trace_id_str = format(trace_id_int, '032x')
            logger.debug(f"Generated new trace ID: {trace_id_str}")
        
        # Set trace ID in context for logging
        trace_id_token = trace_id_context.set(trace_id_str)
        
        try:
            # Generate a span ID for this request
            span_id = self.id_generator.generate_span_id()
            
            # Create a custom span context with our trace ID
            span_context = SpanContext(
                trace_id=trace_id_int,
                span_id=span_id,
                is_remote=False,
                trace_flags=TraceFlags(TraceFlags.SAMPLED),
            )
            
            # Create a span with the custom context
            span = self.tracer.start_span(
                name=f"{request.method} {request.url.path}",
                context=trace.set_span_in_context(
                    trace.NonRecordingSpan(span_context)
                ),
                kind=SpanKind.SERVER,
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.route": request.url.path,
                    "http.user_agent": request.headers.get("user-agent", ""),
                    "trace.id": trace_id_str,
                }
            )
            
            # Set the span as current
            context_token = trace.set_span_in_context(span)
            context_token = attach(context_token)
            
            try:
                # Add trace ID as span attribute
                span.set_attribute("trace.id", trace_id_str)
                
                # Process request
                response = await call_next(request)
                
                # Add trace ID to response headers
                response.headers[self.header_name] = trace_id_str
                
                # Add response status to span
                span.set_attribute("http.status_code", response.status_code)
                
                logger.info(
                    f"Request processed",
                    extra={
                        "trace_id": trace_id_str,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                    }
                )
                
                return response
                
            finally:
                # End the span and detach context
                span.end()
                detach(context_token)
                
        except Exception as e:
            logger.error(
                f"Error processing request: {str(e)}",
                extra={
                    "trace_id": trace_id_str,
                    "method": request.method,
                    "path": request.url.path,
                },
                exc_info=True
            )
            raise
        finally:
            # Reset trace ID context
            trace_id_context.reset(trace_id_token)
    
    def _generate_trace_id(self) -> str:
        """
        Generate a new trace ID using OpenTelemetry SDK.
        
        Returns:
            New trace ID as 32-character hex string
        """
        # Use OpenTelemetry's RandomIdGenerator to create a proper 128-bit trace ID
        trace_id = self.id_generator.generate_trace_id()
        # Convert to 32-character hex string (128 bits = 16 bytes = 32 hex chars)
        return format(trace_id, '032x')


def get_current_trace_id() -> str:
    """
    Get the current trace ID from context.
    
    Returns:
        Current trace ID or empty string if not set
    """
    return trace_id_context.get('')
