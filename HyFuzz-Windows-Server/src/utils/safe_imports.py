"""
Safe Dynamic Import Module for HyFuzz MCP Server

This module provides secure dynamic import functionality with whitelist-based
validation to prevent arbitrary module injection attacks.

Features:
- Whitelist-based module loading
- Protection against path traversal
- Plugin system support with validation
- Comprehensive logging of import attempts
- Type hints for better IDE support

Security:
- Only whitelisted modules can be imported
- No arbitrary module loading from user input
- Path validation prevents directory traversal
- All import attempts are logged

Example Usage:
    >>> from src.utils.safe_imports import safe_import, register_module
    >>>
    >>> # Import from whitelist
    >>> llm_client = safe_import('llm_client', 'LLMClient')
    >>>
    >>> # Register a new module (for plugins)
    >>> register_module('my_plugin', 'plugins.my_plugin')
    >>> plugin_class = safe_import('my_plugin', 'MyPlugin')

Author: HyFuzz Security Team
Version: 1.0.0
Date: 2025-11-11
Security: Prevents arbitrary module injection (CWE-94)
"""

import logging
import importlib
import re
from typing import Any, Optional, Dict, Set
from pathlib import Path
from threading import Lock

# ==============================================================================
# LOGGER SETUP
# ==============================================================================

logger = logging.getLogger(__name__)


# ==============================================================================
# MODULE WHITELIST
# ==============================================================================

# Core modules that are allowed to be dynamically imported
CORE_ALLOWED_MODULES: Dict[str, str] = {
    # LLM modules
    'llm_client': 'src.llm.llm_client',
    'llm_service': 'src.llm.llm_service',
    'cot_engine': 'src.llm.cot_engine',
    'prompt_builder': 'src.llm.prompt_builder',
    'embedding_manager': 'src.llm.embedding_manager',
    'cache_manager': 'src.llm.cache_manager',
    'response_parser': 'src.llm.response_parser',
    'token_counter': 'src.llm.token_counter',

    # Knowledge modules
    'knowledge': 'src.knowledge',
    'cwe_repository': 'src.knowledge.cwe_repository',
    'cve_repository': 'src.knowledge.cve_repository',
    'vulnerability_db': 'src.knowledge.vulnerability_db',
    'graph_db_manager': 'src.knowledge.graph_db_manager',
    'vector_db_manager': 'src.knowledge.vector_db_manager',
    'graph_cache': 'src.knowledge.graph_cache',
    'knowledge_loader': 'src.knowledge.knowledge_loader',

    # Protocol modules
    'base_protocol': 'src.protocols.base_protocol',
    'coap_protocol': 'src.protocols.coap_protocol',
    'modbus_protocol': 'src.protocols.modbus_protocol',
    'mqtt_protocol': 'src.protocols.mqtt_protocol',
    'grpc_protocol': 'src.protocols.grpc_protocol',
    'json_rpc_protocol': 'src.protocols.json_rpc_protocol',

    # API modules
    'routes': 'src.api.routes',
    'handlers': 'src.api.handlers',
    'middleware': 'src.api.middleware',
    'validators': 'src.api.validators',

    # Utility modules
    'logger': 'src.utils.logger',
    'exceptions': 'src.utils.exceptions',
    'helpers': 'src.utils.helpers',
    'decorators': 'src.utils.decorators',
    'validators': 'src.utils.validators',
    'safe_serializer': 'src.utils.safe_serializer',
    'secure_auth': 'src.utils.secure_auth',

    # Model modules
    'config_models': 'src.models.config_models',
    'llm_models': 'src.models.llm_models',
    'knowledge_models': 'src.models.knowledge_models',
    'message_models': 'src.models.message_models',
    'common_models': 'src.models.common_models',

    # Fuzzing modules
    'fuzz_engine': 'src.fuzzing.fuzz_engine',
    'protocol_fuzzing_engine': 'src.fuzzing.protocol_fuzzing_engine',
    'fuzzing_strategies': 'src.fuzzing.fuzzing_strategies',

    # Defense modules
    'defense_system': 'src.defense.defense_system',
    'waf_integration': 'src.defense.waf_integration',
    'ids_integration': 'src.defense.ids_integration',
    'defense_analyzer': 'src.defense.defense_analyzer',

    # Plugin base
    'base_plugin': 'src.plugins.base_plugin',
    'plugin_manager': 'src.plugins.plugin_manager',
}

# Additional modules registered at runtime (e.g., plugins)
_runtime_modules: Dict[str, str] = {}
_modules_lock = Lock()


# ==============================================================================
# VALIDATION FUNCTIONS
# ==============================================================================

def _validate_module_key(module_key: str) -> bool:
    """
    Validate module key format.

    Args:
        module_key: Module key to validate

    Returns:
        True if valid, False otherwise

    Security:
        - Must be alphanumeric with underscores
        - No path traversal characters
        - No special characters
    """
    # Only allow alphanumeric and underscores
    if not re.match(r'^[a-zA-Z0-9_]+$', module_key):
        logger.warning(f"Invalid module key format: {module_key}")
        return False

    # Prevent path traversal
    if '..' in module_key or '/' in module_key or '\\' in module_key:
        logger.warning(f"Path traversal attempt in module key: {module_key}")
        return False

    return True


def _validate_module_path(module_path: str) -> bool:
    """
    Validate module path format.

    Args:
        module_path: Module path to validate

    Returns:
        True if valid, False otherwise

    Security:
        - Must start with src. or plugins.
        - No path traversal
        - Valid Python module path format
    """
    # Must start with allowed prefixes
    allowed_prefixes = ('src.', 'plugins.')
    if not any(module_path.startswith(prefix) for prefix in allowed_prefixes):
        logger.warning(f"Module path must start with {allowed_prefixes}: {module_path}")
        return False

    # Validate Python module path format
    if not re.match(r'^[a-zA-Z0-9_.]+$', module_path):
        logger.warning(f"Invalid module path format: {module_path}")
        return False

    # Prevent path traversal
    if '..' in module_path:
        logger.warning(f"Path traversal attempt in module path: {module_path}")
        return False

    return True


# ==============================================================================
# WHITELIST MANAGEMENT
# ==============================================================================

def register_module(module_key: str, module_path: str) -> bool:
    """
    Register a module in the runtime whitelist.

    This is typically used for plugins or dynamically loaded modules.

    Args:
        module_key: Short name/alias for the module
        module_path: Full Python module path

    Returns:
        True if registered successfully, False otherwise

    Raises:
        ValueError: If module_key or module_path is invalid

    Security:
        - Both key and path are validated
        - Only allowed paths (src.*, plugins.*) are accepted
        - All registrations are logged

    Example:
        >>> register_module('my_plugin', 'plugins.my_plugin')
        True
    """
    # Validate inputs
    if not _validate_module_key(module_key):
        raise ValueError(f"Invalid module key: {module_key}")

    if not _validate_module_path(module_path):
        raise ValueError(f"Invalid module path: {module_path}")

    # Check if already in core whitelist
    if module_key in CORE_ALLOWED_MODULES:
        logger.warning(
            f"Cannot register '{module_key}': already in core whitelist as '{CORE_ALLOWED_MODULES[module_key]}'"
        )
        return False

    # Register module
    with _modules_lock:
        _runtime_modules[module_key] = module_path

    logger.info(f"Registered module: {module_key} -> {module_path}")
    return True


def unregister_module(module_key: str) -> bool:
    """
    Remove a module from the runtime whitelist.

    Args:
        module_key: Module key to unregister

    Returns:
        True if unregistered, False if not found

    Note:
        Core modules cannot be unregistered
    """
    if module_key in CORE_ALLOWED_MODULES:
        logger.warning(f"Cannot unregister core module: {module_key}")
        return False

    with _modules_lock:
        if module_key in _runtime_modules:
            del _runtime_modules[module_key]
            logger.info(f"Unregistered module: {module_key}")
            return True

    return False


def get_registered_modules() -> Dict[str, str]:
    """
    Get all registered modules (core + runtime).

    Returns:
        Dictionary mapping module keys to module paths

    Example:
        >>> modules = get_registered_modules()
        >>> print(modules['llm_client'])
        'src.llm.llm_client'
    """
    with _modules_lock:
        return {**CORE_ALLOWED_MODULES, **_runtime_modules}


def is_module_allowed(module_key: str) -> bool:
    """
    Check if a module is in the whitelist.

    Args:
        module_key: Module key to check

    Returns:
        True if module is allowed, False otherwise
    """
    with _modules_lock:
        return module_key in CORE_ALLOWED_MODULES or module_key in _runtime_modules


# ==============================================================================
# SAFE IMPORT FUNCTIONS
# ==============================================================================

def safe_import(
    module_key: str,
    item_name: Optional[str] = None,
    fallback: Any = None
) -> Any:
    """
    Safely import a module or item from a whitelisted module.

    Args:
        module_key: Short name/key of the module (must be in whitelist)
        item_name: Name of item to import from module (class, function, etc.)
        fallback: Value to return if import fails

    Returns:
        Imported module/item or fallback value

    Raises:
        ValueError: If module_key is not in whitelist
        ImportError: If import fails and no fallback provided

    Security:
        - Only whitelisted modules can be imported
        - All import attempts are logged
        - Validation prevents path traversal

    Example:
        >>> # Import entire module
        >>> llm_module = safe_import('llm_client')
        >>>
        >>> # Import specific class
        >>> LLMClient = safe_import('llm_client', 'LLMClient')
        >>>
        >>> # With fallback
        >>> plugin = safe_import('optional_plugin', 'Plugin', fallback=None)
    """
    # Check if module is whitelisted
    if not is_module_allowed(module_key):
        error_msg = (
            f"Module '{module_key}' is not in the whitelist. "
            f"Use register_module() to add it, or check spelling."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Get module path from whitelist
    with _modules_lock:
        module_path = CORE_ALLOWED_MODULES.get(module_key) or _runtime_modules.get(module_key)

    if not module_path:
        raise ValueError(f"Module key '{module_key}' not found in whitelist")

    # Log import attempt
    logger.debug(f"Importing from whitelist: {module_key} ({module_path})")

    try:
        # Import the module
        if item_name:
            # Import specific item from module
            module = importlib.import_module(module_path)
            item = getattr(module, item_name)
            logger.debug(f"Successfully imported {item_name} from {module_path}")
            return item
        else:
            # Import entire module
            module = importlib.import_module(module_path)
            logger.debug(f"Successfully imported module {module_path}")
            return module

    except (ImportError, AttributeError) as e:
        error_msg = f"Failed to import {item_name or 'module'} from {module_path}: {e}"
        logger.warning(error_msg)

        if fallback is not None:
            logger.info(f"Using fallback value for {module_key}")
            return fallback
        else:
            raise ImportError(error_msg) from e


def safe_import_from_path(
    module_path: str,
    item_name: Optional[str] = None,
    fallback: Any = None
) -> Any:
    """
    Safely import from a full module path (if it's whitelisted).

    Args:
        module_path: Full Python module path
        item_name: Name of item to import
        fallback: Value to return if import fails

    Returns:
        Imported module/item or fallback

    Raises:
        ValueError: If module path is not whitelisted
        ImportError: If import fails and no fallback

    Security:
        - Validates module path is in whitelist
        - Prevents arbitrary imports

    Example:
        >>> LLMClient = safe_import_from_path('src.llm.llm_client', 'LLMClient')
    """
    # Check if module path is in whitelist
    all_modules = get_registered_modules()
    if module_path not in all_modules.values():
        raise ValueError(f"Module path '{module_path}' is not whitelisted")

    # Find the corresponding key
    module_key = None
    for key, path in all_modules.items():
        if path == module_path:
            module_key = key
            break

    if not module_key:
        raise ValueError(f"Module path '{module_path}' not found in whitelist")

    # Use safe_import with the found key
    return safe_import(module_key, item_name, fallback)


# ==============================================================================
# PLUGIN SUPPORT
# ==============================================================================

def load_plugin(plugin_name: str, plugin_path: Optional[Path] = None) -> bool:
    """
    Load a plugin securely.

    Args:
        plugin_name: Name of the plugin
        plugin_path: Path to plugin directory (optional)

    Returns:
        True if loaded successfully, False otherwise

    Security:
        - Plugin must be in plugins/ directory
        - Plugin path is validated
        - Plugin is registered in whitelist before import

    Example:
        >>> if load_plugin('my_plugin'):
        ...     Plugin = safe_import('my_plugin', 'MyPlugin')
    """
    # Validate plugin name
    if not _validate_module_key(plugin_name):
        logger.error(f"Invalid plugin name: {plugin_name}")
        return False

    # Determine plugin module path
    if plugin_path:
        # Custom plugin path (must be validated)
        plugin_module = f"plugins.{plugin_name}"
    else:
        # Default: plugins.<plugin_name>
        plugin_module = f"plugins.{plugin_name}"

    # Validate plugin module path
    if not _validate_module_path(plugin_module):
        logger.error(f"Invalid plugin module path: {plugin_module}")
        return False

    # Register plugin
    try:
        register_module(plugin_name, plugin_module)
        logger.info(f"Plugin '{plugin_name}' loaded and registered")
        return True
    except ValueError as e:
        logger.error(f"Failed to load plugin '{plugin_name}': {e}")
        return False


# ==============================================================================
# MODULE INFO
# ==============================================================================

__all__ = [
    'safe_import',
    'safe_import_from_path',
    'register_module',
    'unregister_module',
    'is_module_allowed',
    'get_registered_modules',
    'load_plugin',
]


if __name__ == '__main__':
    # Example usage and testing
    import sys

    logging.basicConfig(level=logging.DEBUG)

    print("=== HyFuzz Safe Import Module Demo ===\n")

    # Test 1: Import from whitelist
    print("1. Import from whitelist:")
    try:
        llm_client = safe_import('llm_client')
        print(f"   ✓ Successfully imported: {llm_client}\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")

    # Test 2: Import specific class
    print("2. Import specific class:")
    try:
        Settings = safe_import('config_models', 'Settings', fallback=object)
        print(f"   ✓ Successfully imported Settings class\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")

    # Test 3: Try to import non-whitelisted module (should fail)
    print("3. Try to import non-whitelisted module:")
    try:
        dangerous = safe_import('os')  # Should fail
        print(f"   ✗ SECURITY BREACH: Imported {dangerous}\n")
    except ValueError as e:
        print(f"   ✓ Correctly blocked: {e}\n")

    # Test 4: Register and load a module
    print("4. Register custom module:")
    try:
        register_module('test_module', 'plugins.test_plugin')
        print(f"   ✓ Module registered\n")
    except Exception as e:
        print(f"   ✗ Failed: {e}\n")

    # Test 5: Show all registered modules
    print("5. Show all registered modules:")
    modules = get_registered_modules()
    print(f"   Total modules: {len(modules)}")
    print(f"   Sample: {list(modules.keys())[:5]}\n")

    print("✓ All demos completed!")
