"""Enhanced registry with version management and plugin support."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Type


from .base_protocol import ProtocolHandler
from .protocol_metadata import ProtocolMetadata
from .protocol_discovery import discover_protocols, ProtocolDiscovery

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProtocolRegistration:
    """Container for registered protocol handlers with metadata."""

    handler_cls: Type[ProtocolHandler]
    metadata: ProtocolMetadata
    source: str = "builtin"  # builtin, plugin, external


class ProtocolRegistry:
    """
    Enhanced protocol registry with version management and plugin support.

    Features:
    - Automatic protocol discovery
    - Version compatibility checking
    - Plugin loading from external paths
    - Protocol validation
    - Conflict resolution
    """

    def __init__(self, auto_discover: bool = True) -> None:
        """
        Initialize the registry.

        Args:
            auto_discover: Whether to automatically discover built-in protocols
        """
        self._registry: Dict[str, ProtocolRegistration] = {}
        self._discovery = ProtocolDiscovery()

        if auto_discover:
            self._discover_builtin_protocols()

    def _discover_builtin_protocols(self) -> None:
        """Discover and register built-in protocol handlers."""
        # Try multiple package names for compatibility
        package_names = [
            "hyfuzz_server.protocols",
            "HyFuzz_Windows_Server.src.protocols",
            "src.protocols",
            __package__,  # Try current package
        ]

        discovered_count = 0
        for package_name in package_names:
            if not package_name:
                continue

            try:
                protocols = discover_protocols(package_name)
                for name, handler_cls in protocols.items():
                    try:
                        self.register(name, handler_cls, source="builtin")
                        discovered_count += 1
                    except Exception as e:
                        logger.debug(f"Failed to register protocol '{name}': {e}")

                if discovered_count > 0:
                    logger.info(f"Discovered {discovered_count} protocols from {package_name}")
                    return  # Success, no need to try other packages

            except Exception as e:
                logger.debug(f"Failed to discover from {package_name}: {e}")
                continue

        # If no protocols discovered, fall back to manual registration
        logger.info("Falling back to manual protocol registration")
        self._register_defaults_manual()

    def _register_defaults_manual(self) -> None:
        """Manual fallback registration of built-in protocols."""
        # List of protocol handlers to try importing
        protocol_imports = [
            ("coap", ".coap_protocol", "CoAPProtocolHandler"),
            ("modbus", ".modbus_protocol", "ModbusProtocolHandler"),
            ("mqtt", ".mqtt_protocol", "MQTTProtocolHandler"),
            ("http", ".http_protocol", "HTTPProtocolHandler"),
            ("grpc", ".grpc_protocol", "GRPCProtocolHandler"),
            ("jsonrpc", ".jsonrpc_protocol", "JSONRPCProtocolHandler"),
        ]

        registered_count = 0
        for protocol_name, module_name, class_name in protocol_imports:
            try:
                # Try to import the protocol handler
                module = importlib.import_module(module_name, package=__package__)
                handler_cls = getattr(module, class_name)

                # Register the handler
                self.register(protocol_name, handler_cls, source="builtin")
                registered_count += 1
                logger.debug(f"Manually registered protocol: {protocol_name}")

            except ImportError as e:
                logger.debug(f"Failed to import {protocol_name} protocol: {e}")
            except AttributeError as e:
                logger.debug(f"Failed to find {class_name} in module: {e}")
            except Exception as e:
                logger.debug(f"Failed to register {protocol_name}: {e}")

        if registered_count > 0:
            logger.info(f"Manually registered {registered_count} built-in protocol(s)")
        else:
            logger.warning("No built-in protocols could be registered")

    def register(
        self,
        name: str,
        handler_cls: Type[ProtocolHandler],
        metadata: Optional[ProtocolMetadata] = None,
        source: str = "external",
        allow_override: bool = False,
    ) -> None:
        """
        Register a protocol handler.

        Args:
            name: Protocol identifier
            handler_cls: Protocol handler class
            metadata: Optional protocol metadata (will be extracted if not provided)
            source: Source of the protocol (builtin, plugin, external)
            allow_override: Whether to allow overriding existing protocols

        Raises:
            ValueError: If protocol is already registered and override not allowed
            TypeError: If handler class is invalid
        """
        # Check if already registered
        if name in self._registry and not allow_override:
            existing = self._registry[name]
            raise ValueError(
                f"Protocol '{name}' is already registered "
                f"(source: {existing.source}, version: {existing.metadata.version}). "
                f"Use allow_override=True to replace it."
            )

        # Extract metadata if not provided
        if metadata is None:
            try:
                instance = handler_cls()
                spec = instance.get_spec()

                # Handle both ProtocolMetadata and legacy ProtocolSpec
                if isinstance(spec, ProtocolMetadata):
                    metadata = spec
                else:
                    # Convert legacy ProtocolSpec to ProtocolMetadata
                    metadata = ProtocolMetadata(
                        name=getattr(spec, 'name', name),
                        version="1.0.0",
                        description=getattr(spec, 'description', ''),
                        stateful=getattr(spec, 'stateful', False),
                        default_parameters=getattr(spec, 'default_parameters', {}),
                    )
            except Exception as e:
                raise TypeError(f"Failed to extract metadata from handler: {e}")

        # Validate the handler (but don't fail for backward compatibility)
        validation_errors = self._discovery.validate_protocol(handler_cls)
        if validation_errors:
            logger.debug(f"Protocol handler validation warnings for '{name}': {'; '.join(validation_errors)}")

        # Register the protocol
        registration = ProtocolRegistration(
            handler_cls=handler_cls, metadata=metadata, source=source
        )
        self._registry[name] = registration

        logger.info(
            f"Registered protocol '{name}' (version: {metadata.version}, source: {source})"
        )

    def unregister(self, name: str) -> bool:
        """
        Unregister a protocol.

        Args:
            name: Protocol identifier

        Returns:
            True if protocol was unregistered, False if not found
        """
        if name in self._registry:
            registration = self._registry[name]
            del self._registry[name]
            logger.info(f"Unregistered protocol '{name}' (source: {registration.source})")
            return True
        return False

    def get(self, name: str) -> Type[ProtocolHandler]:
        """
        Get a protocol handler class.

        Args:
            name: Protocol identifier

        Returns:
            Protocol handler class

        Raises:
            KeyError: If protocol is not registered
        """
        if name not in self._registry:
            raise KeyError(
                f"Protocol '{name}' is not registered. "
                f"Available: {', '.join(self.list_protocols())}"
            )
        return self._registry[name].handler_cls

    def get_metadata(self, name: str) -> ProtocolMetadata:
        """
        Get protocol metadata.

        Args:
            name: Protocol identifier

        Returns:
            Protocol metadata

        Raises:
            KeyError: If protocol is not registered
        """
        if name not in self._registry:
            raise KeyError(f"Protocol '{name}' is not registered")
        return self._registry[name].metadata

    def get_registration(self, name: str) -> ProtocolRegistration:
        """
        Get complete registration information.

        Args:
            name: Protocol identifier

        Returns:
            Protocol registration

        Raises:
            KeyError: If protocol is not registered
        """
        if name not in self._registry:
            raise KeyError(f"Protocol '{name}' is not registered")
        return self._registry[name]

    def is_registered(self, name: str) -> bool:
        """
        Check if a protocol is registered.

        Args:
            name: Protocol identifier

        Returns:
            True if registered
        """
        return name in self._registry

    def list_protocols(self) -> List[str]:
        """
        List all registered protocol names.

        Returns:
            List of protocol identifiers
        """
        return sorted(self._registry.keys())

    def list_by_source(self, source: str) -> List[str]:
        """
        List protocols by source.

        Args:
            source: Source filter (builtin, plugin, external)

        Returns:
            List of protocol identifiers
        """
        return sorted(name for name, reg in self._registry.items() if reg.source == source)

    def available_protocols(self) -> Dict[str, Type[ProtocolHandler]]:
        """
        Get all available protocol handlers.

        Returns:
            Dictionary mapping protocol names to handler classes
        """
        return {name: reg.handler_cls for name, reg in self._registry.items()}

    def protocol_metadata_dict(self) -> Dict[str, ProtocolMetadata]:
        """
        Get all protocol metadata.

        Returns:
            Dictionary mapping protocol names to metadata
        """
        return {name: reg.metadata for name, reg in self._registry.items()}

    def check_version_compatibility(
        self, protocol_name: str, server_version: str, client_version: str
    ) -> tuple[bool, List[str]]:
        """
        Check version compatibility for a protocol.

        Args:
            protocol_name: Protocol identifier
            server_version: Server version
            client_version: Client version

        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        if protocol_name not in self._registry:
            return False, [f"Protocol '{protocol_name}' not registered"]

        metadata = self._registry[protocol_name].metadata
        issues = []

        if not metadata.is_compatible_with_server(server_version):
            issues.append(
                f"Server version {server_version} is below minimum "
                f"required {metadata.min_server_version}"
            )

        if not metadata.is_compatible_with_client(client_version):
            issues.append(
                f"Client version {client_version} is below minimum "
                f"required {metadata.min_client_version}"
            )

        return len(issues) == 0, issues

    def load_plugins_from_path(self, path: str, source: str = "plugin") -> Dict[str, bool]:
        """
        Load protocol plugins from a directory.

        Args:
            path: Directory path to scan
            source: Source identifier for loaded protocols

        Returns:
            Dictionary mapping protocol names to success status
        """
        self._discovery.add_discovery_path(path)
        discovered = self._discovery.discover_protocols()

        results = {}
        for name, handler_cls in discovered.items():
            try:
                self.register(name, handler_cls, source=source, allow_override=False)
                results[name] = True
            except Exception as e:
                logger.error(f"Failed to register plugin protocol '{name}': {e}")
                results[name] = False

        return results

    def get_info(self) -> Dict[str, any]:
        """
        Get registry information.

        Returns:
            Dictionary with registry statistics
        """
        by_source = {}
        for registration in self._registry.values():
            source = registration.source
            by_source[source] = by_source.get(source, 0) + 1

        return {
            "total_protocols": len(self._registry),
            "by_source": by_source,
            "protocols": {
                name: {
                    "version": reg.metadata.version,
                    "source": reg.source,
                    "stateful": reg.metadata.stateful,
                }
                for name, reg in self._registry.items()
            },
        }


if __name__ == "__main__":
    registry = ProtocolRegistry()
    print("Registered protocols:", registry.list_protocols())
    print("Registry info:", registry.get_info())
