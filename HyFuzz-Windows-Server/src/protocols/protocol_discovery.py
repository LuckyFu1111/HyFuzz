"""Protocol plugin discovery and loading system."""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

from .base_protocol import BaseProtocolHandler, ProtocolHandler
from .protocol_metadata import ProtocolMetadata

logger = logging.getLogger(__name__)


class ProtocolDiscovery:
    """
    Automatic protocol plugin discovery and loading.

    This class scans directories for protocol implementations and
    automatically registers them.
    """

    def __init__(self):
        self._discovered_protocols: Dict[str, Type[ProtocolHandler]] = {}
        self._discovery_paths: Set[Path] = set()

    def add_discovery_path(self, path: str | Path) -> None:
        """
        Add a directory to scan for protocol plugins.

        Args:
            path: Directory path to scan
        """
        path_obj = Path(path)
        if not path_obj.exists():
            logger.warning(f"Discovery path does not exist: {path}")
            return

        if not path_obj.is_dir():
            logger.warning(f"Discovery path is not a directory: {path}")
            return

        self._discovery_paths.add(path_obj.resolve())
        logger.info(f"Added discovery path: {path_obj}")

    def discover_protocols(self, package_name: Optional[str] = None) -> Dict[str, Type[ProtocolHandler]]:
        """
        Discover all protocol implementations.

        Args:
            package_name: Optional package name to scan (e.g., 'src.protocols')

        Returns:
            Dictionary mapping protocol names to handler classes
        """
        discovered = {}

        # Discover from package
        if package_name:
            discovered.update(self._discover_from_package(package_name))

        # Discover from filesystem paths
        for path in self._discovery_paths:
            discovered.update(self._discover_from_path(path))

        self._discovered_protocols.update(discovered)
        logger.info(f"Discovered {len(discovered)} protocol(s): {', '.join(discovered.keys())}")

        return discovered

    def _discover_from_package(self, package_name: str) -> Dict[str, Type[ProtocolHandler]]:
        """
        Discover protocols from a Python package.

        Args:
            package_name: Fully qualified package name

        Returns:
            Dictionary of discovered protocols
        """
        discovered = {}

        try:
            package = importlib.import_module(package_name)
            package_path = Path(package.__file__).parent

            # Scan for *_protocol.py files
            for module_info in pkgutil.iter_modules([str(package_path)]):
                if module_info.name.endswith("_protocol") and not module_info.name.startswith("base"):
                    try:
                        module = importlib.import_module(f"{package_name}.{module_info.name}")
                        handlers = self._extract_handlers_from_module(module)
                        discovered.update(handlers)
                    except Exception as e:
                        logger.error(f"Failed to load module {module_info.name}: {e}")

        except ImportError as e:
            logger.error(f"Failed to import package {package_name}: {e}")

        return discovered

    def _discover_from_path(self, path: Path) -> Dict[str, Type[ProtocolHandler]]:
        """
        Discover protocols from a filesystem path.

        Args:
            path: Directory path to scan

        Returns:
            Dictionary of discovered protocols
        """
        discovered = {}

        # Scan for *_protocol.py files
        for file_path in path.glob("*_protocol.py"):
            if file_path.stem.startswith("base"):
                continue

            try:
                # Load module from file
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    handlers = self._extract_handlers_from_module(module)
                    discovered.update(handlers)

            except Exception as e:
                logger.error(f"Failed to load protocol from {file_path}: {e}")

        return discovered

    def _extract_handlers_from_module(self, module) -> Dict[str, Type[ProtocolHandler]]:
        """
        Extract protocol handler classes from a module.

        Args:
            module: Python module to inspect

        Returns:
            Dictionary of protocol handlers
        """
        handlers = {}

        for name, obj in inspect.getmembers(module):
            # Skip imports and non-classes
            if not inspect.isclass(obj):
                continue

            # Skip if not defined in this module
            if obj.__module__ != module.__name__:
                continue

            # Check if it's a protocol handler
            if self._is_protocol_handler(obj):
                protocol_name = getattr(obj, "name", None)
                if protocol_name:
                    handlers[protocol_name] = obj
                    logger.debug(f"Found protocol handler: {protocol_name} ({obj.__name__})")

        return handlers

    def _is_protocol_handler(self, cls: type) -> bool:
        """
        Check if a class is a valid protocol handler.

        Args:
            cls: Class to check

        Returns:
            True if it's a protocol handler
        """
        # Must be a subclass of BaseProtocolHandler or implement ProtocolHandler
        if hasattr(cls, "__mro__"):
            for base in cls.__mro__:
                if base.__name__ == "BaseProtocolHandler":
                    # Skip the base class itself
                    return cls.__name__ != "BaseProtocolHandler"

        # Check if it implements the ProtocolHandler protocol
        required_methods = {"prepare_request", "parse_response", "validate"}
        has_all_methods = all(hasattr(cls, method) for method in required_methods)

        # Must have a name attribute
        has_name = hasattr(cls, "name") and isinstance(getattr(cls, "name"), str)

        return has_all_methods and has_name

    def get_discovered_protocols(self) -> Dict[str, Type[ProtocolHandler]]:
        """
        Get all discovered protocols.

        Returns:
            Dictionary of protocol handlers
        """
        return dict(self._discovered_protocols)

    def get_protocol(self, name: str) -> Optional[Type[ProtocolHandler]]:
        """
        Get a specific discovered protocol.

        Args:
            name: Protocol name

        Returns:
            Protocol handler class or None
        """
        return self._discovered_protocols.get(name)

    def validate_protocol(self, handler_cls: Type[ProtocolHandler]) -> List[str]:
        """
        Validate a protocol handler implementation.

        Args:
            handler_cls: Protocol handler class to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required attributes
        if not hasattr(handler_cls, "name"):
            errors.append("Missing 'name' attribute")
        elif not isinstance(handler_cls.name, str):
            errors.append("'name' attribute must be a string")

        # Check required methods
        required_methods = {
            "prepare_request": ["context", "payload"],
            "parse_response": ["context", "response"],
            "validate": ["payload"],
        }

        for method_name, expected_params in required_methods.items():
            if not hasattr(handler_cls, method_name):
                errors.append(f"Missing required method: {method_name}")
            else:
                method = getattr(handler_cls, method_name)
                if not callable(method):
                    errors.append(f"'{method_name}' is not callable")

        # Check if it has metadata
        if hasattr(handler_cls, "get_spec"):
            try:
                # Try to instantiate and get spec
                instance = handler_cls()
                spec = instance.get_spec()
                if not isinstance(spec, ProtocolMetadata):
                    errors.append("get_spec() must return ProtocolMetadata")
            except Exception as e:
                errors.append(f"Failed to get protocol metadata: {e}")
        else:
            errors.append("Missing 'get_spec()' method or 'SPEC' attribute")

        return errors


# Global discovery instance
_discovery = ProtocolDiscovery()


def get_discovery() -> ProtocolDiscovery:
    """Get the global protocol discovery instance."""
    return _discovery


def discover_protocols(package_name: Optional[str] = None) -> Dict[str, Type[ProtocolHandler]]:
    """
    Convenience function for protocol discovery.

    Args:
        package_name: Optional package name to scan

    Returns:
        Dictionary of discovered protocols
    """
    return _discovery.discover_protocols(package_name)


def add_discovery_path(path: str | Path) -> None:
    """
    Convenience function to add a discovery path.

    Args:
        path: Directory path to scan
    """
    _discovery.add_discovery_path(path)


if __name__ == "__main__":
    # Test protocol discovery
    logging.basicConfig(level=logging.INFO)

    print("Testing protocol discovery...")

    # Discover from current package
    protocols = discover_protocols("src.protocols")

    print(f"\nDiscovered {len(protocols)} protocol(s):")
    for name, handler_cls in protocols.items():
        print(f"\n{name}:")
        print(f"  Class: {handler_cls.__name__}")
        print(f"  Module: {handler_cls.__module__}")

        # Validate
        errors = _discovery.validate_protocol(handler_cls)
        if errors:
            print(f"  Validation errors: {', '.join(errors)}")
        else:
            print(f"  Status: ✓ Valid")

            # Get metadata
            try:
                instance = handler_cls()
                spec = instance.get_spec()
                print(f"  Version: {spec.version}")
                print(f"  Description: {spec.description}")
            except Exception as e:
                print(f"  Failed to get metadata: {e}")
