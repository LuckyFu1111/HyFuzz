"""Unified protocol metadata system with version management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from packaging import version


@dataclass(frozen=True)
class ProtocolMetadata:
    """
    Unified protocol metadata for both server and client.

    This replaces the separate ProtocolSpec (server) and ProtocolCapabilities (client)
    with a single, unified metadata structure.
    """

    # Basic information
    name: str
    version: str = "1.0.0"
    description: str = ""

    # Behavioral flags
    stateful: bool = False
    default_parameters: Dict[str, Any] = field(default_factory=dict)

    # Capability flags
    supports_fragmentation: bool = False
    supports_encryption: bool = False
    supports_authentication: bool = False
    supports_compression: bool = False

    # Version compatibility
    min_server_version: str = "1.0.0"
    min_client_version: str = "1.0.0"

    # Optional metadata
    author: str = ""
    license: str = "MIT"
    documentation_url: str = ""
    tags: List[str] = field(default_factory=list)

    def is_compatible_with_server(self, server_version: str) -> bool:
        """Check if protocol is compatible with server version."""
        try:
            return version.parse(server_version) >= version.parse(self.min_server_version)
        except Exception:
            return False

    def is_compatible_with_client(self, client_version: str) -> bool:
        """Check if protocol is compatible with client version."""
        try:
            return version.parse(client_version) >= version.parse(self.min_client_version)
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "stateful": self.stateful,
            "default_parameters": self.default_parameters,
            "capabilities": {
                "fragmentation": self.supports_fragmentation,
                "encryption": self.supports_encryption,
                "authentication": self.supports_authentication,
                "compression": self.supports_compression,
            },
            "version_requirements": {
                "min_server_version": self.min_server_version,
                "min_client_version": self.min_client_version,
            },
            "metadata": {
                "author": self.author,
                "license": self.license,
                "documentation_url": self.documentation_url,
                "tags": self.tags,
            },
        }


# ============================================================================
# Built-in Protocol Metadata Definitions
# ============================================================================

COAP_METADATA = ProtocolMetadata(
    name="coap",
    version="1.0.0",
    description="Constrained Application Protocol for IoT devices",
    stateful=False,
    default_parameters={"method": "GET", "path": "/", "confirmable": True},
    supports_fragmentation=True,
    supports_encryption=True,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["iot", "udp", "rfc7252"],
)

MODBUS_METADATA = ProtocolMetadata(
    name="modbus",
    version="1.0.0",
    description="Modbus protocol for industrial control systems",
    stateful=True,
    default_parameters={"function_code": 3, "unit_id": 1, "timeout": 5},
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["ics", "scada", "tcp"],
)

MQTT_METADATA = ProtocolMetadata(
    name="mqtt",
    version="1.0.0",
    description="Message Queue Telemetry Transport for IoT messaging",
    stateful=True,
    default_parameters={"topic": "test", "qos": 0, "retain": False},
    supports_fragmentation=False,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["iot", "messaging", "pub-sub"],
)

HTTP_METADATA = ProtocolMetadata(
    name="http",
    version="1.0.0",
    description="Hypertext Transfer Protocol for web services",
    stateful=False,
    default_parameters={"method": "GET", "path": "/", "follow_redirects": True},
    supports_fragmentation=True,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["web", "http", "api"],
)

GRPC_METADATA = ProtocolMetadata(
    name="grpc",
    version="1.0.0",
    description="gRPC remote procedure call framework",
    stateful=True,
    default_parameters={"method": "Unary", "timeout": 30},
    supports_fragmentation=True,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["rpc", "http2", "protobuf"],
)

JSONRPC_METADATA = ProtocolMetadata(
    name="jsonrpc",
    version="1.0.0",
    description="JSON-RPC 2.0 remote procedure call protocol",
    stateful=False,
    default_parameters={"method": "echo", "version": "2.0"},
    supports_fragmentation=False,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    license="MIT",
    tags=["rpc", "json", "web"],
)


# Registry of all built-in protocol metadata
BUILTIN_PROTOCOLS: Dict[str, ProtocolMetadata] = {
    "coap": COAP_METADATA,
    "modbus": MODBUS_METADATA,
    "mqtt": MQTT_METADATA,
    "http": HTTP_METADATA,
    "grpc": GRPC_METADATA,
    "jsonrpc": JSONRPC_METADATA,
}


def get_protocol_metadata(name: str) -> Optional[ProtocolMetadata]:
    """Get metadata for a built-in protocol."""
    return BUILTIN_PROTOCOLS.get(name)


def list_protocols() -> Dict[str, ProtocolMetadata]:
    """List all built-in protocol metadata."""
    return dict(BUILTIN_PROTOCOLS)


if __name__ == "__main__":
    # Test metadata system
    print("Built-in protocols:")
    for name, metadata in list_protocols().items():
        print(f"\n{name}:")
        print(f"  Version: {metadata.version}")
        print(f"  Description: {metadata.description}")
        print(f"  Stateful: {metadata.stateful}")
        print(f"  Tags: {', '.join(metadata.tags)}")

    # Test version compatibility
    print("\n\nVersion compatibility:")
    coap = get_protocol_metadata("coap")
    print(f"CoAP compatible with server 1.0.0: {coap.is_compatible_with_server('1.0.0')}")
    print(f"CoAP compatible with server 0.9.0: {coap.is_compatible_with_server('0.9.0')}")
