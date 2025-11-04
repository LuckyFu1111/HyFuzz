"""Unified protocol metadata system (client-side copy)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# Note: This is a copy of the server-side protocol_metadata.py
# In production, consider using a shared package or synchronizing these files


@dataclass(frozen=True)
class ProtocolMetadata:
    """
    Unified protocol metadata for both server and client.

    This replaces the ProtocolCapabilities class with the unified ProtocolMetadata.
    """

    # Basic information
    name: str
    version: str = "1.0.0"
    description: str = ""

    # Behavioral flags
    stateful: bool = False
    default_parameters: Dict[str, str] = field(default_factory=dict)

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
    description="Constrained Application Protocol handler",
    stateful=False,
    default_parameters={"method": "GET", "path": "/", "confirmable": "true"},
    supports_fragmentation=True,
    supports_encryption=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    tags=["iot", "udp"],
)

MODBUS_METADATA = ProtocolMetadata(
    name="modbus",
    version="1.0.0",
    description="Modbus protocol handler for ICS",
    stateful=True,
    default_parameters={"function_code": "3", "unit_id": "1", "timeout": "5"},
    supports_fragmentation=False,
    supports_encryption=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    tags=["ics", "scada"],
)

MQTT_METADATA = ProtocolMetadata(
    name="mqtt",
    version="1.0.0",
    description="MQTT protocol handler for IoT",
    stateful=True,
    default_parameters={"topic": "test", "qos": "0", "retain": "false"},
    supports_fragmentation=False,
    supports_encryption=True,
    supports_authentication=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    tags=["iot", "messaging"],
)

HTTP_METADATA = ProtocolMetadata(
    name="http",
    version="1.0.0",
    description="HTTP protocol handler for web services",
    stateful=False,
    default_parameters={"method": "GET", "path": "/", "follow_redirects": "true"},
    supports_fragmentation=True,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    tags=["web", "http"],
)

GRPC_METADATA = ProtocolMetadata(
    name="grpc",
    version="1.0.0",
    description="gRPC protocol handler",
    stateful=True,
    default_parameters={"method": "Unary", "timeout": "30"},
    supports_fragmentation=True,
    supports_encryption=True,
    supports_authentication=True,
    supports_compression=True,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="HyFuzz Team",
    tags=["rpc", "http2"],
)


# Registry of all built-in protocol metadata
BUILTIN_PROTOCOLS: Dict[str, ProtocolMetadata] = {
    "coap": COAP_METADATA,
    "modbus": MODBUS_METADATA,
    "mqtt": MQTT_METADATA,
    "http": HTTP_METADATA,
    "grpc": GRPC_METADATA,
}
