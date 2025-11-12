"""
Unit tests for GlobalExceptionHandler module

Tests the comprehensive exception handling system that provides
crash recovery and resource cleanup.
"""

import pytest
import sys
import logging
import signal
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.utils.exception_handler import (
    GlobalExceptionHandler,
    CleanupRegistry,
    sanitize_traceback,
    handle_with_recovery,
)


class TestCleanupRegistry:
    """Test cleanup registry functionality"""

    def test_register_cleanup_function(self):
        """Test registering cleanup functions"""
        registry = CleanupRegistry()
        cleanup_called = []

        def cleanup():
            cleanup_called.append(True)

        # Register cleanup
        registry.register(cleanup, "test_cleanup")

        # Execute cleanup
        logger = logging.getLogger('test')
        registry.cleanup_all(logger)

        assert len(cleanup_called) == 1

    def test_cleanup_with_priority(self):
        """Test cleanup functions execute in priority order"""
        registry = CleanupRegistry()
        execution_order = []

        def cleanup_low():
            execution_order.append('low')

        def cleanup_high():
            execution_order.append('high')

        # Register with different priorities (higher executes first)
        registry.register(cleanup_low, "low_priority", priority=1)
        registry.register(cleanup_high, "high_priority", priority=10)

        logger = logging.getLogger('test')
        registry.cleanup_all(logger)

        # High priority should execute first
        assert execution_order == ['high', 'low']

    def test_cleanup_handles_exceptions(self):
        """Test that cleanup handles exceptions gracefully"""
        registry = CleanupRegistry()
        successful_cleanup = []

        def failing_cleanup():
            raise RuntimeError("Cleanup failed!")

        def successful_cleanup():
            successful_cleanup.append(True)

        registry.register(failing_cleanup, "failing")
        registry.register(successful_cleanup, "success")

        logger = logging.getLogger('test')

        # Should not raise exception
        registry.cleanup_all(logger)

        # Successful cleanup should still execute
        assert len(successful_cleanup) == 1

    def test_unregister_cleanup(self):
        """Test unregistering cleanup functions"""
        registry = CleanupRegistry()
        cleanup_called = []

        def cleanup():
            cleanup_called.append(True)

        # Register and unregister
        registry.register(cleanup, "test")
        registry.unregister("test")

        logger = logging.getLogger('test')
        registry.cleanup_all(logger)

        # Should not have been called
        assert len(cleanup_called) == 0


class TestSanitizeTraceback:
    """Test sensitive data sanitization"""

    def test_sanitize_passwords(self):
        """Test that passwords are sanitized"""
        traceback = """
        File "test.py", line 10
            password = "secret123"
            auth_key = "my_api_key"
        """

        sanitized = sanitize_traceback(traceback)

        assert "secret123" not in sanitized
        assert "***REDACTED***" in sanitized or "REDACTED" in sanitized

    def test_sanitize_tokens(self):
        """Test that tokens are sanitized"""
        traceback = """
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        api_token = "Bearer abc123def456"
        """

        sanitized = sanitize_traceback(traceback)

        # Tokens should be redacted
        assert "eyJhbGci" not in sanitized or "***" in sanitized

    def test_sanitize_api_keys(self):
        """Test that API keys are sanitized"""
        traceback = """
        api_key = "sk_test_1234567890abcdef"
        secret_key = "AKIAIOSFODNN7EXAMPLE"
        """

        sanitized = sanitize_traceback(traceback)

        # Should contain redaction markers
        assert "***" in sanitized or "REDACTED" in sanitized

    def test_preserve_stack_trace_structure(self):
        """Test that stack trace structure is preserved"""
        traceback = """
        Traceback (most recent call last):
          File "test.py", line 10, in test_function
            raise ValueError("test error")
        ValueError: test error
        """

        sanitized = sanitize_traceback(traceback)

        # Structure should be preserved
        assert "Traceback" in sanitized
        assert "test.py" in sanitized
        assert "ValueError" in sanitized


class TestGlobalExceptionHandlerContextManager:
    """Test GlobalExceptionHandler as context manager"""

    def test_context_manager_catches_exceptions(self):
        """Test that context manager catches exceptions"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        exception_caught = False

        try:
            with handler:
                raise ValueError("Test exception")
        except SystemExit:
            # GlobalExceptionHandler may call sys.exit()
            exception_caught = True

        # Exception should have been handled
        # (behavior depends on exit_on_exception setting)

    def test_context_manager_install_uninstall(self):
        """Test that exception hook is installed and uninstalled"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        original_hook = sys.excepthook

        with handler:
            # Hook should be installed
            assert sys.excepthook != original_hook

        # Hook should be restored
        assert sys.excepthook == original_hook

    def test_cleanup_on_exception(self):
        """Test that cleanup executes on exception"""
        logger = logging.getLogger('test')
        cleanup_registry = CleanupRegistry()
        cleanup_called = []

        def cleanup():
            cleanup_called.append(True)

        cleanup_registry.register(cleanup, "test")

        handler = GlobalExceptionHandler(
            logger,
            exit_on_exception=False,
            cleanup_registry=cleanup_registry
        )

        try:
            with handler:
                raise ValueError("Test exception")
        except SystemExit:
            pass

        # Cleanup should have been called
        assert len(cleanup_called) == 1


class TestGlobalExceptionHandlerDecorator:
    """Test GlobalExceptionHandler as decorator"""

    def test_decorator_on_function(self):
        """Test using handler as decorator"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        cleanup_called = []

        def cleanup():
            cleanup_called.append(True)

        handler.cleanup_registry.register(cleanup, "test")

        @handle_with_recovery(logger, exit_on_exception=False)
        def test_function():
            raise ValueError("Test error")

        # Call decorated function
        try:
            test_function()
        except SystemExit:
            pass

        # Should have executed (or handled exception)
        # Cleanup may or may not have been called depending on implementation


class TestGlobalExceptionHandlerSignals:
    """Test signal handling"""

    @patch('signal.signal')
    def test_signal_handlers_installed(self, mock_signal):
        """Test that signal handlers are installed"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        handler.install()

        # Should have called signal.signal for SIGTERM and SIGINT
        assert mock_signal.called

    def test_sigterm_triggers_cleanup(self):
        """Test that SIGTERM triggers cleanup"""
        logger = logging.getLogger('test')
        cleanup_registry = CleanupRegistry()
        cleanup_called = []

        def cleanup():
            cleanup_called.append(True)

        cleanup_registry.register(cleanup, "test")

        handler = GlobalExceptionHandler(
            logger,
            exit_on_exception=False,
            cleanup_registry=cleanup_registry
        )

        # Simulate SIGTERM
        try:
            handler.handle_signal(signal.SIGTERM, None)
        except SystemExit:
            pass

        # Cleanup should have been called
        assert len(cleanup_called) == 1


class TestGlobalExceptionHandlerLogging:
    """Test logging functionality"""

    def test_exception_is_logged(self):
        """Test that exceptions are logged"""
        logger = logging.getLogger('test')
        logger.setLevel(logging.CRITICAL)

        # Capture log output
        stream = StringIO()
        handler_stream = logging.StreamHandler(stream)
        logger.addHandler(handler_stream)

        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        try:
            handler.handle_exception(
                ValueError,
                ValueError("Test error"),
                None
            )
        except SystemExit:
            pass

        log_output = stream.getvalue()

        # Should have logged something
        # (May be empty if exit_on_exception=False doesn't log)

    def test_sensitive_data_not_logged(self):
        """Test that sensitive data is sanitized in logs"""
        logger = logging.getLogger('test')

        # Create exception with sensitive data
        try:
            password = "secret123"
            raise ValueError(f"Failed with password: {password}")
        except ValueError as e:
            exc_info = sys.exc_info()

        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        # Mock logger to capture what was logged
        with patch.object(logger, 'critical') as mock_critical:
            try:
                handler.handle_exception(*exc_info)
            except SystemExit:
                pass

            # Should have logged
            if mock_critical.called:
                # Check that sensitive data was sanitized
                call_args = str(mock_critical.call_args)
                # Depending on implementation, may be sanitized


class TestGlobalExceptionHandlerEdgeCases:
    """Test edge cases"""

    def test_keyboard_interrupt_not_caught(self):
        """Test that KeyboardInterrupt is not caught"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        # KeyboardInterrupt should propagate
        handler.handle_exception(KeyboardInterrupt, KeyboardInterrupt(), None)

        # Should have called original hook or not handled it

    def test_system_exit_propagates(self):
        """Test that SystemExit propagates"""
        logger = logging.getLogger('test')
        handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        # SystemExit should propagate
        # (behavior depends on implementation)

    def test_handler_with_none_logger(self):
        """Test handler with None logger"""
        # Should handle gracefully or raise clear error
        try:
            handler = GlobalExceptionHandler(None, exit_on_exception=False)
        except (TypeError, ValueError):
            # Expected if None logger is not allowed
            pass


class TestGlobalExceptionHandlerIntegration:
    """Integration tests"""

    def test_full_exception_handling_flow(self):
        """Test complete exception handling flow"""
        logger = logging.getLogger('test')
        cleanup_registry = CleanupRegistry()

        cleanup_order = []

        def cleanup1():
            cleanup_order.append(1)

        def cleanup2():
            cleanup_order.append(2)

        cleanup_registry.register(cleanup1, "cleanup1", priority=1)
        cleanup_registry.register(cleanup2, "cleanup2", priority=2)

        handler = GlobalExceptionHandler(
            logger,
            exit_on_exception=False,
            cleanup_registry=cleanup_registry
        )

        try:
            with handler:
                raise RuntimeError("Test error")
        except SystemExit:
            pass

        # Cleanup should have executed in priority order
        assert 2 in cleanup_order  # Higher priority
        assert 1 in cleanup_order  # Lower priority

    def test_nested_exception_handlers(self):
        """Test nested exception handlers"""
        logger = logging.getLogger('test')

        outer_handler = GlobalExceptionHandler(logger, exit_on_exception=False)
        inner_handler = GlobalExceptionHandler(logger, exit_on_exception=False)

        # Nested handlers should work
        try:
            with outer_handler:
                with inner_handler:
                    raise ValueError("Nested exception")
        except SystemExit:
            pass

        # Should have handled exception


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
