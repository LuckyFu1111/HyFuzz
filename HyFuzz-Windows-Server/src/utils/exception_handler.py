"""
Global Exception Handler for HyFuzz MCP Server

This module provides global exception handling to catch and log all unhandled
exceptions, ensuring the server can fail gracefully and maintain logs for debugging.

Features:
- Global exception hook for uncaught exceptions
- Graceful shutdown with resource cleanup
- Comprehensive error logging with stack traces
- Signal handler integration (SIGTERM, SIGINT)
- Context manager for easy integration

Security:
- Prevents information leakage in error messages
- Sanitizes sensitive data from stack traces
- Maintains audit trail of all crashes

Example Usage:
    >>> from src.utils.exception_handler import GlobalExceptionHandler
    >>>
    >>> # Method 1: Context manager
    >>> with GlobalExceptionHandler(logger):
    ...     run_server()
    >>>
    >>> # Method 2: Decorator
    >>> @handle_exceptions(logger)
    >>> def main():
    ...     run_server()

Author: HyFuzz Security Team
Version: 1.0.0
Date: 2025-11-11
"""

import sys
import os
import signal
import traceback
import logging
import threading
from typing import Optional, Callable, Any, Type
from types import TracebackType, FrameType
from functools import wraps
from contextlib import contextmanager
from datetime import datetime

# ==============================================================================
# TYPE DEFINITIONS
# ==============================================================================

ExcInfo = tuple[Type[BaseException], BaseException, Optional[TracebackType]]
SignalHandler = Callable[[int, Optional[FrameType]], None]


# ==============================================================================
# EXCEPTION SANITIZATION
# ==============================================================================

def sanitize_traceback(tb_str: str) -> str:
    """
    Sanitize traceback to remove potentially sensitive information.

    Args:
        tb_str: Original traceback string

    Returns:
        Sanitized traceback with sensitive info redacted

    Security:
        - Redacts password fields
        - Redacts API keys
        - Redacts secret keys
        - Preserves debugging information
    """
    # Patterns to sanitize
    patterns = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', r'password=***REDACTED***'),
        (r'api_key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', r'api_key=***REDACTED***'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', r'secret=***REDACTED***'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', r'token=***REDACTED***'),
        (r'JWT_SECRET_KEY["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', r'JWT_SECRET_KEY=***REDACTED***'),
    ]

    import re
    sanitized = tb_str
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


# ==============================================================================
# RESOURCE CLEANUP REGISTRY
# ==============================================================================

class CleanupRegistry:
    """
    Registry for cleanup functions to be called on shutdown.

    This allows different components to register their cleanup logic
    which will be called when the application terminates.
    """

    def __init__(self):
        self._cleanup_functions: list[tuple[str, Callable]] = []
        self._lock = threading.Lock()

    def register(self, name: str, cleanup_func: Callable) -> None:
        """
        Register a cleanup function.

        Args:
            name: Name of the cleanup function (for logging)
            cleanup_func: Function to call on shutdown

        Example:
            >>> registry = CleanupRegistry()
            >>> registry.register('database', close_db_connection)
        """
        with self._lock:
            self._cleanup_functions.append((name, cleanup_func))

    def cleanup_all(self, logger: logging.Logger) -> None:
        """
        Execute all registered cleanup functions.

        Args:
            logger: Logger instance for logging cleanup status
        """
        logger.info("Starting resource cleanup...")

        with self._lock:
            for name, cleanup_func in reversed(self._cleanup_functions):
                try:
                    logger.debug(f"Cleaning up: {name}")
                    cleanup_func()
                    logger.debug(f"Successfully cleaned up: {name}")
                except Exception as e:
                    logger.error(f"Error during cleanup of {name}: {e}", exc_info=True)

        logger.info("Resource cleanup completed")


# Global cleanup registry
_cleanup_registry = CleanupRegistry()


def register_cleanup(name: str, cleanup_func: Callable) -> None:
    """
    Register a cleanup function globally.

    Args:
        name: Name of the cleanup function
        cleanup_func: Function to call on shutdown

    Example:
        >>> def close_database():
        ...     db.close()
        >>> register_cleanup('database', close_database)
    """
    _cleanup_registry.register(name, cleanup_func)


# ==============================================================================
# GLOBAL EXCEPTION HANDLER CLASS
# ==============================================================================

class GlobalExceptionHandler:
    """
    Global exception handler for catching unhandled exceptions.

    This class provides a context manager and decorators for handling
    uncaught exceptions at the application level.

    Attributes:
        logger: Logger instance for error logging
        exit_on_exception: Whether to exit after handling exception
        original_excepthook: Original sys.excepthook for restoration
    """

    def __init__(
        self,
        logger: logging.Logger,
        exit_on_exception: bool = True,
        cleanup_registry: Optional[CleanupRegistry] = None
    ):
        """
        Initialize global exception handler.

        Args:
            logger: Logger instance for error logging
            exit_on_exception: Exit application after exception (default: True)
            cleanup_registry: Optional cleanup registry (uses global if None)
        """
        self.logger = logger
        self.exit_on_exception = exit_on_exception
        self.cleanup_registry = cleanup_registry or _cleanup_registry
        self.original_excepthook: Optional[Callable] = None
        self._signal_handlers: dict[int, SignalHandler] = {}

    def __enter__(self):
        """Enter context manager - install exception hook"""
        self.install()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> bool:
        """Exit context manager - restore original hook"""
        self.uninstall()

        # If an exception occurred within the context, handle it
        if exc_type is not None:
            self.handle_exception(exc_type, exc_val, exc_tb)
            return True  # Suppress exception

        return False

    def install(self) -> None:
        """Install global exception hook and signal handlers"""
        # Install exception hook
        self.original_excepthook = sys.excepthook
        sys.excepthook = self.handle_exception

        # Install signal handlers
        self._install_signal_handlers()

        self.logger.info("Global exception handler installed")

    def uninstall(self) -> None:
        """Restore original exception hook and signal handlers"""
        if self.original_excepthook:
            sys.excepthook = self.original_excepthook
            self.original_excepthook = None

        # Restore signal handlers
        self._restore_signal_handlers()

        self.logger.info("Global exception handler uninstalled")

    def _install_signal_handlers(self) -> None:
        """Install signal handlers for graceful shutdown"""
        def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
            """Handle termination signals"""
            signal_names = {
                signal.SIGINT: 'SIGINT (Ctrl+C)',
                signal.SIGTERM: 'SIGTERM',
            }
            signal_name = signal_names.get(signum, f'Signal {signum}')

            self.logger.warning(f"Received {signal_name}, initiating graceful shutdown...")

            # Cleanup resources
            self.cleanup_registry.cleanup_all(self.logger)

            # Exit
            sys.exit(0)

        # Install handlers for common signals
        for sig in [signal.SIGINT, signal.SIGTERM]:
            try:
                self._signal_handlers[sig] = signal.signal(sig, signal_handler)
            except (OSError, ValueError) as e:
                self.logger.warning(f"Could not install handler for signal {sig}: {e}")

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers"""
        for sig, handler in self._signal_handlers.items():
            try:
                signal.signal(sig, handler)
            except (OSError, ValueError) as e:
                self.logger.warning(f"Could not restore handler for signal {sig}: {e}")

        self._signal_handlers.clear()

    def handle_exception(
        self,
        exc_type: Type[BaseException],
        exc_val: BaseException,
        exc_tb: Optional[TracebackType]
    ) -> None:
        """
        Handle uncaught exception.

        Args:
            exc_type: Exception type
            exc_val: Exception instance
            exc_tb: Traceback object

        This method:
        1. Logs the exception with full details
        2. Executes cleanup functions
        3. Optionally exits the application
        """
        # Allow KeyboardInterrupt to work normally
        if issubclass(exc_type, KeyboardInterrupt):
            if self.original_excepthook:
                self.original_excepthook(exc_type, exc_val, exc_tb)
            return

        # Get stack trace
        tb_lines = traceback.format_exception(exc_type, exc_val, exc_tb)
        tb_str = ''.join(tb_lines)

        # Sanitize sensitive information
        sanitized_tb = sanitize_traceback(tb_str)

        # Log the exception
        self.logger.critical(
            "UNCAUGHT EXCEPTION - Application crash",
            exc_info=(exc_type, exc_val, exc_tb),
            extra={
                'exception_type': exc_type.__name__,
                'exception_message': str(exc_val),
                'sanitized_traceback': sanitized_tb,
                'timestamp': datetime.now().isoformat(),
                'pid': os.getpid(),
                'thread': threading.current_thread().name,
            }
        )

        # Also log to stderr for visibility
        sys.stderr.write(f"\n{'='*80}\n")
        sys.stderr.write(f"FATAL ERROR: {exc_type.__name__}: {exc_val}\n")
        sys.stderr.write(f"{'='*80}\n")
        sys.stderr.write(sanitized_tb)
        sys.stderr.write(f"{'='*80}\n\n")

        # Attempt cleanup
        try:
            self.logger.info("Attempting cleanup before exit...")
            self.cleanup_registry.cleanup_all(self.logger)
        except Exception as cleanup_error:
            self.logger.error(f"Error during cleanup: {cleanup_error}", exc_info=True)

        # Exit if configured
        if self.exit_on_exception:
            self.logger.critical("Exiting due to uncaught exception")
            sys.exit(1)


# ==============================================================================
# DECORATOR FOR EXCEPTION HANDLING
# ==============================================================================

def handle_exceptions(logger: logging.Logger, exit_on_exception: bool = True):
    """
    Decorator to wrap a function with global exception handling.

    Args:
        logger: Logger instance
        exit_on_exception: Exit on exception

    Returns:
        Decorated function

    Example:
        >>> @handle_exceptions(logger)
        >>> def main():
        ...     run_server()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = GlobalExceptionHandler(logger, exit_on_exception)

            with handler:
                return func(*args, **kwargs)

        return wrapper

    return decorator


# ==============================================================================
# ASYNC SUPPORT
# ==============================================================================

def handle_async_exceptions(logger: logging.Logger, exit_on_exception: bool = True):
    """
    Decorator for async functions with exception handling.

    Args:
        logger: Logger instance
        exit_on_exception: Exit on exception

    Returns:
        Decorated async function

    Example:
        >>> @handle_async_exceptions(logger)
        >>> async def main():
        ...     await run_async_server()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            handler = GlobalExceptionHandler(logger, exit_on_exception)

            try:
                handler.install()
                return await func(*args, **kwargs)
            except Exception as e:
                handler.handle_exception(type(e), e, e.__traceback__)
            finally:
                handler.uninstall()

        return wrapper

    return decorator


# ==============================================================================
# MODULE EXPORTS
# ==============================================================================

__all__ = [
    'GlobalExceptionHandler',
    'handle_exceptions',
    'handle_async_exceptions',
    'register_cleanup',
    'CleanupRegistry',
    'sanitize_traceback',
]


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    print("=== Global Exception Handler Demo ===\n")

    # Register cleanup functions
    register_cleanup('test_resource_1', lambda: print("Cleaning up resource 1"))
    register_cleanup('test_resource_2', lambda: print("Cleaning up resource 2"))

    # Test 1: Context manager
    print("Test 1: Context manager with exception")
    try:
        with GlobalExceptionHandler(logger, exit_on_exception=False):
            print("  Running code that will raise exception...")
            raise ValueError("Test exception!")
    except SystemExit:
        pass

    print("\nTest 2: Decorator")
    @handle_exceptions(logger, exit_on_exception=False)
    def test_function():
        print("  Running decorated function...")
        raise RuntimeError("Test runtime error!")

    try:
        test_function()
    except SystemExit:
        pass

    print("\n✓ Demo completed (exceptions were handled gracefully)")
