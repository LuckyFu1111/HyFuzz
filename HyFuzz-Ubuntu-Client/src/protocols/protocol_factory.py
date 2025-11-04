"""Enhanced protocol factory with plugin support."""
from __future__ import annotations

import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base_handler import BaseProtocolHandler
from .protocol_metadata import ProtocolMetadata

logger = logging.getLogger(__name__)


class ProtocolFactory:
    """
    Enhanced protocol factory with automatic discovery and plugin support.

    Features:
    - Automatic protocol discovery
    - Plugin loading from external paths
    - Protocol validation
    - Metadata management
    """

    def __init__(self, auto_discover: bool = True):
        """
        Initialize the factory.

        Args:
            auto_discover: Whether to automatically discover built-in handlers
        """
        self._handlers: Dict[str, Type[BaseProtocolHandler]] = {}
        self._metadata: Dict[str, ProtocolMetadata] = {}

        if auto_discover:
            self._discover_builtin_handlers()

    def _discover_builtin_handlers(self) -> None:
        """Discover and register built-in protocol handlers."""
        try:
            # Try to import built-in handlers
            from .coap_handler import CoAPHandler
            from .modbus_handler import ModbusHandler
            from .mqtt_handler import MQTTHandler
            from .http_handler import HTTPHandler
            from .grpc_handler import GRPCHandler

            for handler_cls in [CoAPHandler, ModbusHandler, MQTTHandler, HTTPHandler, GRPCHandler]:
                try:
                    self.register_handler(handler_cls)
                except Exception as e:
                    logger.error(f"Failed to register handler {handler_cls.__name__}: {e}")

        except ImportError as e:
            logger.error(f"Failed to import built-in handlers: {e}")

    def register_handler(
        self,
        handler_cls: Type[BaseProtocolHandler],
        allow_override: bool = False
    ) -> None:
        """
        Register a protocol handler.

        Args:
            handler_cls: Protocol handler class
            allow_override: Whether to allow overriding existing handlers

        Raises:
            ValueError: If handler is invalid or already registered
        """
        # Validate handler
        validation_errors = self._validate_handler(handler_cls)
        if validation_errors:
            raise ValueError(f"Invalid handler: {'; '.join(validation_errors)}")

        # Get handler name
        name = handler_cls.name

        # Check if already registered
        if name in self._handlers and not allow_override:
            raise ValueError(
                f"Handler for protocol '{name}' is already registered. "
                f"Use allow_override=True to replace it."
            )

        # Extract metadata
        try:
            instance = handler_cls()
            metadata = instance.get_capabilities()
        except Exception as e:
            raise ValueError(f"Failed to extract metadata from handler: {e}")

        # Register the handler
        self._handlers[name] = handler_cls
        self._metadata[name] = metadata

        logger.info(f"Registered protocol handler: {name} (version: {metadata.version})")

    def unregister_handler(self, protocol: str) -> bool:
        """
        Unregister a protocol handler.

        Args:
            protocol: Protocol identifier

        Returns:
            True if handler was unregistered, False if not found
        """
        if protocol in self._handlers:
            del self._handlers[protocol]
            del self._metadata[protocol]
            logger.info(f"Unregistered protocol handler: {protocol}")
            return True
        return False

    def get_handler(self, protocol: str) -> BaseProtocolHandler:
        """
        Get a protocol handler instance.

        Args:
            protocol: Protocol identifier

        Returns:
            Protocol handler instance

        Raises:
            ValueError: If protocol is not registered
        """
        handler_cls = self._handlers.get(protocol)
        if handler_cls is None:
            raise ValueError(
                f"Unsupported protocol: {protocol}. "
                f"Available: {', '.join(self.list_protocols())}"
            )
        return handler_cls()

    def get_metadata(self, protocol: str) -> ProtocolMetadata:
        """
        Get protocol metadata.

        Args:
            protocol: Protocol identifier

        Returns:
            Protocol metadata

        Raises:
            ValueError: If protocol is not registered
        """
        if protocol not in self._metadata:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return self._metadata[protocol]

    def is_registered(self, protocol: str) -> bool:
        """
        Check if a protocol is registered.

        Args:
            protocol: Protocol identifier

        Returns:
            True if registered
        """
        return protocol in self._handlers

    def list_protocols(self) -> List[str]:
        """
        List all registered protocol names.

        Returns:
            List of protocol identifiers
        """
        return sorted(self._handlers.keys())

    def available_handlers(self) -> Dict[str, Type[BaseProtocolHandler]]:
        """
        Get all available protocol handlers.

        Returns:
            Dictionary mapping protocol names to handler classes
        """
        return dict(self._handlers)

    def available_metadata(self) -> Dict[str, ProtocolMetadata]:
        """
        Get all protocol metadata.

        Returns:
            Dictionary mapping protocol names to metadata
        """
        return dict(self._metadata)

    def load_plugins_from_path(self, path: str) -> Dict[str, bool]:
        """
        Load protocol plugins from a directory.

        Args:
            path: Directory path to scan

        Returns:
            Dictionary mapping protocol names to success status
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning(f"Plugin path does not exist: {path}")
            return {}

        results = {}

        # Scan for *_handler.py files
        for file_path in path_obj.glob("*_handler.py"):
            if file_path.stem.startswith("base"):
                continue

            try:
                # Load module from file
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Find handler classes
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, BaseProtocolHandler)
                            and obj is not BaseProtocolHandler
                            and obj.__module__ == module.__name__
                        ):
                            try:
                                self.register_handler(obj, allow_override=False)
                                results[obj.name] = True
                            except Exception as e:
                                logger.error(f"Failed to register handler from {file_path}: {e}")
                                results[obj.name] = False

            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")

        return results

    def _validate_handler(self, handler_cls: Type[BaseProtocolHandler]) -> List[str]:
        """
        Validate a protocol handler.

        Args:
            handler_cls: Handler class to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check if it's a class
        if not inspect.isclass(handler_cls):
            errors.append("Must be a class")
            return errors

        # Check required attributes
        if not hasattr(handler_cls, "name"):
            errors.append("Missing 'name' attribute")
        elif not isinstance(handler_cls.name, str):
            errors.append("'name' attribute must be a string")

        # Check required methods
        if not hasattr(handler_cls, "execute"):
            errors.append("Missing 'execute()' method")
        elif not callable(getattr(handler_cls, "execute")):
            errors.append("'execute' is not callable")

        if not hasattr(handler_cls, "get_capabilities"):
            errors.append("Missing 'get_capabilities()' method")

        # Try to instantiate
        try:
            instance = handler_cls()
        except Exception as e:
            errors.append(f"Failed to instantiate: {e}")
            return errors

        # Check if get_capabilities works
        try:
            metadata = instance.get_capabilities()
            if not isinstance(metadata, ProtocolMetadata):
                errors.append("get_capabilities() must return ProtocolMetadata")
        except Exception as e:
            errors.append(f"Failed to get capabilities: {e}")

        return errors

    def get_info(self) -> Dict[str, any]:
        """
        Get factory information.

        Returns:
            Dictionary with factory statistics
        """
        return {
            "total_protocols": len(self._handlers),
            "protocols": {
                name: {
                    "version": metadata.version,
                    "stateful": metadata.stateful,
                    "description": metadata.description,
                }
                for name, metadata in self._metadata.items()
            },
        }


# Global factory instance
_factory = ProtocolFactory()


def get_handler(protocol: str) -> BaseProtocolHandler:
    """
    Get a protocol handler instance.

    Args:
        protocol: Protocol identifier

    Returns:
        Protocol handler instance
    """
    return _factory.get_handler(protocol)


def get_metadata(protocol: str) -> ProtocolMetadata:
    """
    Get protocol metadata (renamed from get_capabilities).

    Args:
        protocol: Protocol identifier

    Returns:
        Protocol metadata
    """
    return _factory.get_metadata(protocol)


def get_capabilities(protocol: str) -> ProtocolMetadata:
    """
    Legacy function for backward compatibility.

    Args:
        protocol: Protocol identifier

    Returns:
        Protocol metadata
    """
    return get_metadata(protocol)


def available_capabilities() -> Dict[str, ProtocolMetadata]:
    """Legacy function for backward compatibility."""
    return _factory.available_metadata()


def register_handler(handler_cls: Type[BaseProtocolHandler], allow_override: bool = False) -> None:
    """
    Register a protocol handler.

    Args:
        handler_cls: Protocol handler class
        allow_override: Whether to allow overriding existing handlers
    """
    _factory.register_handler(handler_cls, allow_override)


def load_plugins_from_path(path: str) -> Dict[str, bool]:
    """
    Load protocol plugins from a directory.

    Args:
        path: Directory path to scan

    Returns:
        Dictionary mapping protocol names to success status
    """
    return _factory.load_plugins_from_path(path)


def get_factory() -> ProtocolFactory:
    """Get the global factory instance."""
    return _factory


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Registered protocols:")
    for protocol in _factory.list_protocols():
        metadata = _factory.get_metadata(protocol)
        print(f"  {protocol}: {metadata.description} (v{metadata.version})")

    # Test getting a handler
    handler = get_handler("coap")
    print(f"\nCoAP handler: {handler.name}")
