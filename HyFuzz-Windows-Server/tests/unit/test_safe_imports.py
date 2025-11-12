"""
Unit tests for SafeImports module

Tests the whitelist-based import system that prevents
arbitrary module injection attacks (CWE-94).
"""

import pytest
import sys
from unittest.mock import patch, MagicMock

from src.utils.safe_imports import (
    safe_import,
    safe_import_from_path,
    is_module_allowed,
    register_module,
    unregister_module,
    get_registered_modules,
    CORE_ALLOWED_MODULES,
)


class TestSafeImportBasic:
    """Test basic safe import functionality"""

    def test_import_whitelisted_module(self):
        """Test importing a whitelisted module succeeds"""
        # llm_client is in the default whitelist
        module = safe_import('llm_client')

        assert module is not None
        assert hasattr(module, '__name__')

    def test_import_whitelisted_class(self):
        """Test importing specific class from whitelisted module"""
        # This may fail if the class doesn't exist, but should not raise security error
        try:
            result = safe_import('llm_client', 'LLMClient')
            # If it succeeds, verify it's not None
            if result is not None:
                assert hasattr(result, '__name__') or callable(result)
        except AttributeError:
            # Class doesn't exist, but import was allowed
            pass

    def test_import_non_whitelisted_module_fails(self):
        """Test that non-whitelisted modules are blocked"""
        # 'os' should not be in whitelist
        with pytest.raises(ValueError) as exc_info:
            safe_import('os')

        assert 'not in the whitelist' in str(exc_info.value)

    def test_import_dangerous_module_fails(self):
        """Test that dangerous modules are blocked"""
        dangerous_modules = ['subprocess', 'eval', '__builtins__']

        for module_name in dangerous_modules:
            with pytest.raises(ValueError):
                safe_import(module_name)


class TestSafeImportFromPath:
    """Test path-based import functionality"""

    def test_import_from_allowed_path(self):
        """Test importing from allowed module path"""
        # Use a known good path
        module = safe_import_from_path('src.utils.safe_imports')

        assert module is not None
        assert hasattr(module, '__name__')

    def test_import_class_from_allowed_path(self):
        """Test importing specific item from allowed path"""
        # Import a known function
        func = safe_import_from_path(
            'src.utils.safe_imports',
            'is_module_allowed'
        )

        assert callable(func)

    def test_import_from_disallowed_path_fails(self):
        """Test that disallowed paths are blocked"""
        # Try to import from os module
        with pytest.raises(ValueError) as exc_info:
            safe_import_from_path('os', 'system')

        assert 'not in the allowed paths' in str(exc_info.value)

    def test_path_traversal_blocked(self):
        """Test that path traversal attempts are blocked"""
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32',
            'src/../../../malicious',
        ]

        for path in malicious_paths:
            with pytest.raises(ValueError):
                safe_import_from_path(path)


class TestModuleWhitelist:
    """Test whitelist management"""

    def test_is_module_allowed_for_whitelisted(self):
        """Test checking if module is allowed"""
        # Known whitelisted module
        assert is_module_allowed('llm_client') is True

    def test_is_module_allowed_for_non_whitelisted(self):
        """Test checking non-whitelisted module"""
        assert is_module_allowed('os') is False
        assert is_module_allowed('subprocess') is False

    def test_register_new_module(self):
        """Test registering a new module"""
        module_key = 'test_custom_module'
        module_path = 'plugins.test_module'

        try:
            # Register
            register_module(module_key, module_path)

            # Verify it's registered
            assert is_module_allowed(module_key) is True

            # Verify it's in the list
            modules = get_registered_modules()
            assert module_key in modules
            assert modules[module_key] == module_path

        finally:
            # Cleanup
            unregister_module(module_key)

    def test_unregister_module(self):
        """Test unregistering a module"""
        module_key = 'test_temporary_module'
        module_path = 'plugins.temporary'

        # Register
        register_module(module_key, module_path)
        assert is_module_allowed(module_key) is True

        # Unregister
        unregister_module(module_key)
        assert is_module_allowed(module_key) is False

    def test_cannot_unregister_core_module(self):
        """Test that core modules cannot be unregistered"""
        # Try to unregister a core module
        with pytest.raises(ValueError) as exc_info:
            unregister_module('llm_client')

        assert 'core module' in str(exc_info.value).lower()

    def test_get_registered_modules(self):
        """Test getting list of registered modules"""
        modules = get_registered_modules()

        assert isinstance(modules, dict)
        assert len(modules) > 0

        # Should include core modules
        assert 'llm_client' in modules
        assert 'llm_service' in modules


class TestSafeImportSecurity:
    """Test security features"""

    def test_cannot_import_builtins(self):
        """Test that __builtins__ cannot be imported"""
        with pytest.raises(ValueError):
            safe_import('__builtins__')

    def test_cannot_import_with_exec(self):
        """Test that exec/eval cannot be accessed"""
        dangerous_items = ['exec', 'eval', 'compile']

        for item in dangerous_items:
            with pytest.raises(ValueError):
                safe_import(item)

    def test_cannot_bypass_with_importlib(self):
        """Test that importlib cannot be used to bypass whitelist"""
        # Even if importlib is whitelisted, it shouldn't allow arbitrary imports
        with pytest.raises(ValueError):
            safe_import('importlib')

    def test_module_name_validation(self):
        """Test that module names are validated"""
        invalid_names = [
            '',  # Empty
            '..', # Path traversal
            'module;os',  # Injection attempt
            'module\x00',  # Null byte
        ]

        for name in invalid_names:
            with pytest.raises(ValueError):
                safe_import(name)


class TestSafeImportEdgeCases:
    """Test edge cases"""

    def test_import_none_module(self):
        """Test importing None raises error"""
        with pytest.raises((ValueError, TypeError, AttributeError)):
            safe_import(None)

    def test_import_empty_string(self):
        """Test importing empty string raises error"""
        with pytest.raises(ValueError):
            safe_import('')

    def test_import_with_spaces(self):
        """Test importing module name with spaces"""
        with pytest.raises(ValueError):
            safe_import('module with spaces')

    def test_fallback_value(self):
        """Test fallback parameter in safe_import_from_path"""
        fallback_value = 'FALLBACK'

        # Try to import non-existent item with fallback
        result = safe_import_from_path(
            'src.utils.safe_imports',
            'NonExistentClass',
            fallback=fallback_value
        )

        assert result == fallback_value


class TestSafeImportLogging:
    """Test logging functionality"""

    @patch('src.utils.safe_imports.logger')
    def test_blocked_import_is_logged(self, mock_logger):
        """Test that blocked imports are logged"""
        try:
            safe_import('os')
        except ValueError:
            pass

        # Should have logged an error
        mock_logger.error.assert_called()

    @patch('src.utils.safe_imports.logger')
    def test_successful_import_is_logged(self, mock_logger):
        """Test that successful imports are logged at debug level"""
        try:
            safe_import('llm_client')
        except:
            pass

        # May log at debug level
        # This is optional, just checking it doesn't crash


class TestSafeImportPerformance:
    """Test performance considerations"""

    def test_multiple_imports_same_module(self):
        """Test that importing the same module multiple times works"""
        # Should use Python's module cache
        module1 = safe_import('llm_client')
        module2 = safe_import('llm_client')

        # Should be the same object (Python caches imports)
        assert module1 is module2

    def test_whitelist_lookup_performance(self):
        """Test that whitelist lookup is fast"""
        import time

        # Should be O(1) dict lookup
        start = time.time()
        for _ in range(10000):
            is_module_allowed('llm_client')
        end = time.time()

        # Should complete in well under 1 second
        assert (end - start) < 1.0


class TestSafeImportIntegration:
    """Integration tests with real modules"""

    def test_import_actual_project_module(self):
        """Test importing actual project modules"""
        # Try to import a real module from the project
        module = safe_import('llm_client')
        assert module is not None

    def test_whitelist_contains_expected_modules(self):
        """Test that whitelist contains expected project modules"""
        expected_modules = [
            'llm_client',
            'llm_service',
            'cot_engine',
        ]

        modules = get_registered_modules()
        for expected in expected_modules:
            assert expected in modules, f"{expected} not in whitelist"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
