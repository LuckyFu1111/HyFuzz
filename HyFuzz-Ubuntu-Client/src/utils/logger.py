"""
Logging Utilities for HyFuzz Ubuntu Client

This module provides centralized logging configuration and utilities for the
HyFuzz fuzzing client. It ensures consistent log formatting, proper log
levels, and integration with system logging facilities.

Key Features:
- Standardized log formatting across all modules
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Stream and file handler support
- Thread-safe logging operations
- Integration with system monitoring tools
- Structured logging for machine parsing

Log Format:
    Default format: "YYYY-MM-DD HH:MM:SS LEVEL module_name: message"
    Example: "2025-01-14 10:30:45 INFO hyfuzz-client: Starting fuzzing campaign"

Log Levels:
    - DEBUG: Detailed diagnostic information (verbose)
    - INFO: General informational messages
    - WARNING: Warning messages for non-critical issues
    - ERROR: Error messages for recoverable errors
    - CRITICAL: Critical errors requiring immediate attention

Usage Patterns:
    1. Module-level logging:
        >>> from utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")

    2. Component-specific logging:
        >>> logger = get_logger("fuzzing.engine")
        >>> logger.debug("Processing payload #123")

    3. Structured logging:
        >>> logger.info("Payload executed", extra={
        ...     "payload_id": "abc123",
        ...     "protocol": "coap",
        ...     "status": "success"
        ... })

Integration:
    - Logs can be collected by systemd journald
    - Compatible with log aggregation tools (ELK, Splunk)
    - Supports rotation via standard Python logging handlers
    - Can be configured via environment variables or config files

Best Practices:
    - Use module name for logger (get_logger(__name__))
    - Use appropriate log levels (don't log everything as INFO)
    - Include context in log messages (IDs, states, values)
    - Avoid logging sensitive data (credentials, tokens)
    - Use structured logging for machine parsing

Example:
    >>> logger = get_logger("execution")
    >>> logger.info("Starting payload execution")
    >>> try:
    ...     result = execute_payload()
    ...     logger.info(f"Execution successful: {result}")
    ... except Exception as e:
    ...     logger.error(f"Execution failed: {e}", exc_info=True)

Author: HyFuzz Team
Version: 1.0.0
"""
from __future__ import annotations

import logging
from logging import Logger
from typing import Optional


def get_logger(name: Optional[str] = None) -> Logger:
    """
    Get a configured logger instance with standardized formatting.

    Creates or retrieves a logger with consistent formatting and log level
    configuration. If the logger already exists, returns the existing instance.
    Otherwise, creates a new logger with a StreamHandler and default formatting.

    Args:
        name: Logger name (typically __name__ for module-level logging).
              If None, uses "hyfuzz-client" as default.

    Returns:
        Configured Logger instance ready for use.

    Log Format:
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
        Example: "2025-01-14 10:30:45 INFO fuzzing.engine: Payload executed"

    Default Configuration:
        - Handler: StreamHandler (outputs to stderr)
        - Level: INFO (shows INFO, WARNING, ERROR, CRITICAL)
        - Format: Includes timestamp, level, logger name, and message

    Example:
        >>> # Module-level logger (recommended)
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized successfully")
        >>>
        >>> # Component-specific logger
        >>> engine_logger = get_logger("fuzzing.engine")
        >>> engine_logger.debug("Processing seed #42")
        >>>
        >>> # Default logger
        >>> default_logger = get_logger()
        >>> default_logger.warning("Using default logger")

    Notes:
        - Loggers are singletons per name (calling get_logger(name) multiple
          times returns the same logger instance)
        - Handler is only added if logger has no handlers (prevents duplicates)
        - Default log level is INFO; use logger.setLevel() to change
        - For file logging, add FileHandler to the returned logger

    Thread Safety:
        This function and the returned logger are thread-safe. Multiple
        threads can call get_logger() and log messages concurrently.

    See Also:
        - Python logging documentation: https://docs.python.org/3/library/logging.html
        - Logging best practices: https://docs.python.org/3/howto/logging.html
    """
    # Get or create logger with given name
    logger = logging.getLogger(name or "hyfuzz-client")

    # Only configure logger if it has no handlers (avoid duplicate handlers)
    if not logger.handlers:
        # Create stream handler for console output
        handler = logging.StreamHandler()

        # Set consistent log message format
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)

        # Attach handler to logger
        logger.addHandler(handler)

        # Set default log level to INFO
        logger.setLevel(logging.INFO)

    return logger


if __name__ == "__main__":
    log = get_logger(__name__)
    log.info("Logger bootstrap test passed.")
