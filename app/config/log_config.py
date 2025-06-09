"""
Logging Configuration

This module provides comprehensive logging configuration with support for
JSON and standard formats, configurable via environment variables.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from app.config.settings import settings


class SQLFormatter(logging.Formatter):
    """
    Custom formatter for SQL queries to make them more readable.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_sql_query = None
        self._last_sql_params = None

    def format(self, record: logging.LogRecord) -> str:
        """
        Format SQL log records with better readability.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        # Check if this is a SQL query log
        if hasattr(record, 'name') and 'sqlalchemy.engine' in record.name:
            msg = record.getMessage()

            # Check if this is a SQL query
            if msg.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER')):
                # Clean up the SQL query
                formatted_sql = self._format_sql(msg)
                self._last_sql_query = formatted_sql
                record.msg = f"SQL Query: {formatted_sql}"

            # Check if this is parameter binding
            elif '[generated in' in msg and '(' in msg and ')' in msg:
                # Extract parameters from the message
                params_start = msg.find('(')
                params_end = msg.rfind(')')
                if params_start != -1 and params_end != -1:
                    params_str = msg[params_start:params_end+1]
                    self._last_sql_params = params_str

                    # If we have both query and params, combine them
                    if self._last_sql_query and self._last_sql_params:
                        combined_sql = self._combine_sql_with_params(self._last_sql_query, self._last_sql_params)
                        record.msg = f"SQL Executed: {combined_sql}"
                        # Reset for next query
                        self._last_sql_query = None
                        self._last_sql_params = None
                    else:
                        record.msg = f"SQL Parameters: {params_str}"

        return super().format(record)

    def _format_sql(self, sql: str) -> str:
        """
        Format SQL query for better readability.

        Args:
            sql: Raw SQL query string

        Returns:
            Formatted SQL query
        """
        # Remove newlines and extra spaces
        sql = ' '.join(sql.split())

        # Remove PostgreSQL type casting for cleaner display
        import re
        sql = re.sub(r'\$\d+::\w+', lambda m: m.group(0).split('::')[0], sql)

        return sql.strip()

    def _combine_sql_with_params(self, sql: str, params_str: str) -> str:
        """
        Combine SQL query with actual parameter values.

        Args:
            sql: SQL query string
            params_str: Parameter values string like "('value1', 'value2')"

        Returns:
            SQL query with parameters substituted
        """
        try:
            # Extract parameter values from the string
            import ast

            # Clean up the params string and evaluate it
            params_clean = params_str.strip()
            if params_clean.startswith('(') and params_clean.endswith(')'):
                # Handle single parameter case
                if params_clean.count(',') == 0 and not params_clean.endswith(',)'):
                    # Single parameter: ('value',) or ('value')
                    param_value = params_clean[1:-1]
                    if param_value.startswith("'") and param_value.endswith("'"):
                        param_value = param_value[1:-1]
                    params = [param_value]
                else:
                    # Multiple parameters
                    try:
                        params = list(ast.literal_eval(params_clean))
                    except:
                        # Fallback: manual parsing
                        inner = params_clean[1:-1]
                        params = [p.strip().strip("'\"") for p in inner.split(',') if p.strip()]
            else:
                return f"{sql} -- Parameters: {params_str}"

            # Replace $1, $2, etc. with actual values
            result_sql = sql
            for i, param in enumerate(params, 1):
                placeholder = f'${i}'
                if isinstance(param, str):
                    # Escape single quotes in string values
                    escaped_param = param.replace("'", "''")
                    replacement = f"'{escaped_param}'"
                elif param is None:
                    replacement = 'NULL'
                elif isinstance(param, bool):
                    replacement = 'TRUE' if param else 'FALSE'
                else:
                    replacement = str(param)

                result_sql = result_sql.replace(placeholder, replacement)

            return result_sql

        except Exception:
            # If anything goes wrong, return original SQL with parameters
            return f"{sql} -- Parameters: {params_str}"


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    Formats log records as JSON with configurable fields and pretty printing.
    """
    
    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_logger_name: bool = True,
        json_indent: Optional[int] = None
    ):
        """
        Initialize JSON formatter.
        
        Args:
            include_timestamp: Whether to include timestamp
            include_level: Whether to include log level
            include_logger_name: Whether to include logger name
            json_indent: JSON indentation for pretty printing
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_logger_name = include_logger_name
        self.json_indent = json_indent
        self._last_sql_query = None
        self._last_sql_params = None
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {}
        
        # Add timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.fromtimestamp(record.created).isoformat()
        
        # Add log level
        if self.include_level:
            log_data["level"] = record.levelname
        
        # Add caller info (combines logger, function, and line)
        if self.include_logger_name:
            log_data["caller"] = f"{record.name}:{record.funcName}:{record.lineno}"

        # Add trace ID and span ID if available
        trace_id = self._get_trace_id()
        span_id = self._get_span_id()
        if trace_id:
            log_data["trace_id"] = trace_id
        if span_id:
            log_data["span_id"] = span_id

        # Process SQL queries for better formatting
        message = record.getMessage()
        if hasattr(record, 'name') and 'sqlalchemy.engine' in record.name:
            message = self._process_sql_message(message)

        # Add message
        log_data["message"] = message
        
        # Add extra fields from record (exclude color_message for JSON logs)
        extra_fields = {
            key: value for key, value in record.__dict__.items()
            if key not in {
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info', 'color_message', 'trace_id', 'span_id'
            }
        }
        
        if extra_fields:
            log_data["extra"] = extra_fields
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add stack info if present
        if record.stack_info:
            log_data["stack_info"] = record.stack_info
        
        return json.dumps(log_data, indent=self.json_indent, default=str)

    def _get_trace_id(self) -> Optional[str]:
        """
        Get the current trace ID from context.

        Returns:
            Current trace ID or None if not available
        """
        try:
            # First try to get trace ID from OpenTelemetry (now synchronized with middleware)
            from app.config.telemetry import get_current_trace_id
            otel_trace_id = get_current_trace_id()
            if otel_trace_id:
                return otel_trace_id
        except ImportError:
            pass
        
        try:
            # Fallback to middleware context
            from app.middleware.trace_middleware import get_current_trace_id
            return get_current_trace_id()
        except ImportError:
            return None

    def _get_span_id(self) -> Optional[str]:
        """
        Get the current span ID from context.

        Returns:
            Current span ID or None if not available
        """
        try:
            # Get span ID from OpenTelemetry
            from app.config.telemetry import get_current_span_id
            return get_current_span_id()
        except ImportError:
            return None

    def _process_sql_message(self, message: str) -> str:
        """
        Process SQL messages for better formatting.

        Args:
            message: Original SQL message

        Returns:
            Processed SQL message
        """
        # The SQL filter already processes the messages, so we just need to clean up the format
        if message.startswith('SQL: '):
            # This is already a processed SQL query from our filter
            return message[5:]  # Remove 'SQL: ' prefix

        return message


class StandardFormatter(logging.Formatter):
    """
    Enhanced standard formatter with color support for development.
    """
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def __init__(self, use_colors: bool = True):
        """
        Initialize standard formatter.

        Args:
            use_colors: Whether to use colors in output
        """
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.use_colors = use_colors and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with optional colors.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        # Add trace ID and span ID to the record if available
        trace_id = self._get_trace_id()
        span_id = self._get_span_id()
        if trace_id or span_id:
            # Add trace/span info to the message
            original_msg = record.getMessage()
            trace_info = []
            if trace_id:
                trace_info.append(f"trace:{trace_id}")
            if span_id:
                trace_info.append(f"span:{span_id}")
            trace_prefix = "[" + ",".join(trace_info) + "]"
            record.msg = f"{trace_prefix} {original_msg}"

        if self.use_colors:
            # Add color to level name
            level_color = self.COLORS.get(record.levelname, '')
            if level_color:
                record.levelname = f"{level_color}{record.levelname}{self.RESET}"
        
        record.name = f"{record.filename}:{record.lineno}"

        return super().format(record)

    def _get_trace_id(self) -> Optional[str]:
        """
        Get the current trace ID from context.

        Returns:
            Current trace ID or None if not available
        """
        try:
            # First try to get trace ID from OpenTelemetry (now synchronized with middleware)
            from app.config.telemetry import get_current_trace_id
            otel_trace_id = get_current_trace_id()
            if otel_trace_id:
                return otel_trace_id
        except ImportError:
            pass
        
        try:
            # Fallback to middleware context
            from app.middleware.trace_middleware import get_current_trace_id
            return get_current_trace_id()
        except ImportError:
            return None

    def _get_span_id(self) -> Optional[str]:
        """
        Get the current span ID from context.

        Returns:
            Current span ID or None if not available
        """
        try:
            # Get span ID from OpenTelemetry
            from app.config.telemetry import get_current_span_id
            return get_current_span_id()
        except ImportError:
            return None


def setup_logging() -> None:
    """
    Set up logging configuration based on settings.

    Configures formatters, handlers, and loggers according to
    environment variables and application settings.
    """
    # Check if logging is already configured to avoid duplicate setup
    root_logger = logging.getLogger()
    if root_logger.handlers and any(getattr(h, '_app_configured', False) for h in root_logger.handlers):
        return
    # Determine formatter based on settings
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter(
            include_timestamp=settings.LOG_INCLUDE_TIMESTAMP,
            include_level=settings.LOG_INCLUDE_LEVEL,
            include_logger_name=settings.LOG_INCLUDE_LOGGER_NAME,
            json_indent=settings.LOG_JSON_INDENT
        )
    else:
        formatter = StandardFormatter(
            use_colors=settings.ENVIRONMENT == "development"
        )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    # Mark handler as configured by our app
    setattr(console_handler, '_app_configured', True)
    
    # Create file handler if log file is specified
    handlers = [console_handler]
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        setattr(file_handler, '_app_configured', True)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        handlers=handlers,
        force=True  # Override any existing configuration
    )
    
    # Configure specific loggers
    configure_loggers()


def configure_loggers() -> None:
    """
    Configure specific loggers for different components.

    Sets appropriate log levels for third-party libraries
    and application components.
    """
    # Configure uvicorn loggers to use our formatter
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_main = logging.getLogger("uvicorn")

    # Remove existing handlers to avoid duplication
    for logger in [uvicorn_access, uvicorn_error, uvicorn_main]:
        logger.handlers.clear()
        logger.propagate = True  # Let root logger handle it

    # Set appropriate levels
    uvicorn_access.setLevel(logging.WARNING)
    uvicorn_error.setLevel(logging.INFO)
    uvicorn_main.setLevel(logging.INFO)

    # Configure watchfiles logger
    watchfiles_logger = logging.getLogger("watchfiles")
    watchfiles_logger.handlers.clear()
    watchfiles_logger.propagate = True
    watchfiles_logger.setLevel(logging.WARNING)

    # SQLAlchemy logging
    if settings.DATABASE_ECHO:
        # Completely disable ALL SQLAlchemy logging to avoid duplicates
        logging.getLogger("sqlalchemy").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.dialects").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.orm").setLevel(logging.CRITICAL)

        # Set up custom SQL logging using SQLAlchemy events
        from sqlalchemy import event
        from sqlalchemy.engine import Engine

        # Get the main logger for SQL queries
        sql_logger = logging.getLogger("app.database")
        sql_logger.setLevel(logging.INFO)

        @event.listens_for(Engine, "before_cursor_execute")
        def log_sql_query(_conn, _cursor, statement, parameters, _context, _executemany):
            """Log clean SQL queries with real parameter values."""
            # Skip connection setup queries
            if any(x in statement.lower() for x in [
                'select pg_catalog.version', 'select current_schema',
                'show standard_conforming'
            ]):
                return

            # Skip if not a main SQL query
            if not statement.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE')):
                return

            try:
                # Clean up the SQL
                clean_sql = ' '.join(statement.split())

                # Remove PostgreSQL type casting
                import re
                clean_sql = re.sub(r'\$\d+::\w+', lambda m: m.group(0).split('::')[0], clean_sql)

                # Substitute parameters
                if parameters:
                    final_sql = _substitute_sql_parameters(clean_sql, parameters)
                else:
                    final_sql = clean_sql

                # Log the final SQL
                sql_logger.info(final_sql)

            except Exception as e:
                # Fallback logging
                sql_logger.info(f"{statement} -- Parameters: {parameters} (Error: {e})")
    else:
        # Completely disable SQLAlchemy logging when DATABASE_ECHO is False
        logging.getLogger("sqlalchemy").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
        logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.CRITICAL)

    # HTTP client logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Application loggers
    logging.getLogger("app").setLevel(getattr(logging, settings.LOG_LEVEL.upper()))


def _substitute_sql_parameters(sql: str, parameters) -> str:
    """
    Substitute parameters in SQL query.

    Args:
        sql: SQL query string with placeholders
        parameters: Parameter values

    Returns:
        SQL query with parameters substituted
    """
    try:
        if not parameters:
            return sql

        # Handle different parameter formats
        if isinstance(parameters, (list, tuple)):
            params = parameters
        elif isinstance(parameters, dict):
            # For named parameters, we'd need different logic
            return f"{sql} -- Parameters: {parameters}"
        else:
            return f"{sql} -- Parameters: {parameters}"

        # Replace $1, $2, etc. with actual values
        result_sql = sql
        for i, param in enumerate(params, 1):
            placeholder = f'${i}'
            if isinstance(param, str):
                # Escape single quotes and wrap in quotes
                escaped_param = param.replace("'", "''")
                replacement = f"'{escaped_param}'"
            elif param is None:
                replacement = 'NULL'
            elif isinstance(param, bool):
                replacement = 'TRUE' if param else 'FALSE'
            elif isinstance(param, (int, float)):
                replacement = str(param)
            else:
                # For other types, convert to string and quote
                replacement = f"'{str(param)}'"

            result_sql = result_sql.replace(placeholder, replacement)

        return result_sql

    except Exception:
        return f"{sql} -- Parameters: {parameters}"


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
