"""
OpenTelemetry Configuration

This module configures OpenTelemetry for distributed tracing in the FastAPI application.
It sets up trace providers, instrumentations, and trace ID handling.
"""

import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# OTLP exporters
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from app.config.settings import settings

# Global tracer instance
tracer: Optional[trace.Tracer] = None


def _parse_headers(headers_str: str) -> dict:
    """
    Parse headers string into dictionary.

    Args:
        headers_str: Comma-separated key=value pairs

    Returns:
        Dictionary of headers
    """
    headers = {}
    if headers_str:
        for header in headers_str.split(','):
            if '=' in header:
                key, value = header.strip().split('=', 1)
                headers[key.strip()] = value.strip()
    return headers


def setup_telemetry() -> None:
    """
    Set up OpenTelemetry tracing configuration.

    Configures the tracer provider, span processors, and instrumentations
    for FastAPI and SQLAlchemy.
    """
    global tracer

    # Create resource with service information
    resource = Resource.create({
        "service.name": settings.OTEL_SERVICE_NAME,
        "service.version": settings.OTEL_SERVICE_VERSION,
        "deployment.environment": settings.ENVIRONMENT,
    })

    # Set up tracer provider with resource
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # Configure exporters based on settings
    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        # Set up OTLP exporter for trace server
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            headers=_parse_headers(settings.OTEL_EXPORTER_OTLP_HEADERS) if settings.OTEL_EXPORTER_OTLP_HEADERS else None,
        )
        otlp_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(otlp_processor)

    # Add console exporter only if explicitly enabled
    if settings.OTEL_CONSOLE_SPANS and settings.ENVIRONMENT == "development":
        console_exporter = ConsoleSpanExporter()
        console_processor = BatchSpanProcessor(console_exporter)
        tracer_provider.add_span_processor(console_processor)

    # Get tracer instance
    tracer = trace.get_tracer(__name__)

    # Set up SQLAlchemy instrumentation
    SQLAlchemyInstrumentor().instrument()


def instrument_fastapi(app) -> None:
    """
    Instrument FastAPI application with OpenTelemetry.
    
    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(app)


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.

    Returns:
        OpenTelemetry tracer instance
    """
    global tracer
    if tracer is None:
        setup_telemetry()
    # tracer should be set after setup_telemetry()
    assert tracer is not None, "Tracer should be initialized after setup_telemetry()"
    return tracer


def get_current_trace_id() -> Optional[str]:
    """
    Get the current trace ID from the active span context.
    
    Returns:
        Trace ID as hex string, or None if no active trace
    """
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            trace_id = current_span.get_span_context().trace_id
            return format(trace_id, '032x')  # Convert to 32-character hex string
        return None
    except Exception:
        return None


def get_current_span_id() -> Optional[str]:
    """
    Get the current span ID from the active span context.
    
    Returns:
        Span ID as hex string, or None if no active span
    """
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.get_span_context().is_valid:
            span_id = current_span.get_span_context().span_id
            return format(span_id, '016x')  # Convert to 16-character hex string
        return None
    except Exception:
        return None


def create_span(name: str, **attributes) -> trace.Span:
    """
    Create a new span with the given name and attributes.
    
    Args:
        name: Span name
        **attributes: Additional span attributes
        
    Returns:
        New span instance
    """
    tracer = get_tracer()
    span = tracer.start_span(name)
    
    # Add attributes to span
    for key, value in attributes.items():
        span.set_attribute(key, value)
    
    return span
