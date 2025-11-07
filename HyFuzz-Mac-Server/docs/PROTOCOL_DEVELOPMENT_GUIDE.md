# Protocol Development Guide

## Overview

This guide explains how to develop custom protocol handlers for the HyFuzz platform. HyFuzz provides a flexible, plugin-based architecture that allows you to easily add support for new protocols.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Protocol Interface Specification](#protocol-interface-specification)
- [Creating a New Protocol](#creating-a-new-protocol)
- [Server-Side Protocol Handler](#server-side-protocol-handler)
- [Client-Side Protocol Handler](#client-side-protocol-handler)
- [Protocol Registration](#protocol-registration)
- [Testing Your Protocol](#testing-your-protocol)
- [Best Practices](#best-practices)
- [Example: DNS Protocol](#example-dns-protocol)

## Architecture Overview

HyFuzz uses a distributed architecture with two main components:

1. **Server (Windows)**: Generates payloads and coordinates campaigns
2. **Client (Ubuntu)**: Executes payloads and reports results

Each component requires its own protocol handler:

```
┌─────────────────────────────────────────────────────────┐
│                    Server Component                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Protocol Handler (extends BaseProtocolHandler)     │ │
│  │  - prepare_request()   : Generate request payload  │ │
│  │  - parse_response()    : Parse execution results   │ │
│  │  - validate()          : Validate payload          │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            ↓
                    Network Transport
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    Client Component                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Protocol Handler (extends BaseProtocolHandler)     │ │
│  │  - execute()           : Send payload to target    │ │
│  │  - execute_stateful()  : Handle stateful sessions  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Protocol Interface Specification

### Unified Protocol Metadata

Both server and client use a unified metadata structure:

```python
@dataclass(frozen=True)
class ProtocolMetadata:
    """Unified protocol metadata for both server and client."""

    name: str                              # Protocol identifier (e.g., "dns", "coap")
    version: str = "1.0.0"                 # Protocol handler version
    description: str = ""                  # Human-readable description
    stateful: bool = False                 # Whether protocol maintains state
    default_parameters: Dict[str, Any] = field(default_factory=dict)

    # Capability flags
    supports_fragmentation: bool = False
    supports_encryption: bool = False
    supports_authentication: bool = False

    # Version compatibility
    min_server_version: str = "1.0.0"
    min_client_version: str = "1.0.0"
```

### Server-Side Interface

Server-side handlers must implement:

```python
class ProtocolHandler(Protocol):
    """Protocol handler interface for server component."""

    name: str

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare a request to be sent to the client.

        Args:
            context: Target and session information
            payload: Generated payload data

        Returns:
            Request dictionary containing all necessary fields
        """
        ...

    def parse_response(
        self,
        context: ProtocolContext,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse the response from client execution.

        Args:
            context: Original request context
            response: Execution results from client

        Returns:
            Parsed response with extracted metrics
        """
        ...

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate a payload before sending.

        Args:
            payload: Payload to validate

        Returns:
            True if payload is valid, False otherwise
        """
        ...

    def get_spec(self) -> ProtocolMetadata:
        """Return protocol metadata."""
        ...
```

### Client-Side Interface

Client-side handlers must implement:

```python
class BaseProtocolHandler(ABC):
    """Base class for client-side protocol handlers."""

    name: str

    @abstractmethod
    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        """
        Execute a payload against the target.

        Args:
            request: Execution request with payload and parameters

        Returns:
            Execution result with status and metrics
        """
        ...

    def execute_stateful(
        self,
        request: ExecutionRequest,
        session: ProtocolSessionState
    ) -> Dict[str, str]:
        """
        Execute a stateful request (optional).

        Args:
            request: Execution request
            session: Current session state

        Returns:
            Execution result
        """
        return self.execute(request)

    def get_capabilities(self) -> ProtocolMetadata:
        """Return protocol metadata."""
        ...
```

## Creating a New Protocol

### Step 1: Define Protocol Metadata

Create a shared metadata definition:

```python
from dataclasses import dataclass, field
from typing import Dict, Any

DNS_PROTOCOL_METADATA = ProtocolMetadata(
    name="dns",
    version="1.0.0",
    description="Domain Name System protocol fuzzer",
    stateful=False,
    default_parameters={
        "query_type": "A",
        "recursive": True,
        "timeout": 5
    },
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0"
)
```

### Step 2: Implement Server-Side Handler

Create `HyFuzz-Windows-Server/src/protocols/dns_protocol.py`:

```python
"""DNS protocol handler for server."""

from __future__ import annotations
from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext, ProtocolMetadata
from .protocol_metadata import DNS_PROTOCOL_METADATA


class DNSProtocolHandler(BaseProtocolHandler):
    """DNS protocol handler for payload generation and result parsing."""

    name = "dns"
    SPEC = DNS_PROTOCOL_METADATA

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare DNS query request."""
        request = super().prepare_request(context, payload)

        # Extract DNS-specific parameters
        request["query_name"] = payload.get("query_name", "example.com")
        request["query_type"] = payload.get("query_type", "A")
        request["recursive"] = payload.get("recursive", True)
        request["timeout"] = payload.get("timeout", 5)

        return request

    def parse_response(
        self,
        context: ProtocolContext,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse DNS query response."""
        parsed = super().parse_response(context, response)

        # Extract DNS-specific metrics
        parsed["response_code"] = response.get("response_code", "UNKNOWN")
        parsed["answer_count"] = response.get("answer_count", 0)
        parsed["authority_count"] = response.get("authority_count", 0)
        parsed["additional_count"] = response.get("additional_count", 0)
        parsed["query_time_ms"] = response.get("query_time_ms", 0)

        return parsed

    def validate(self, payload: Dict[str, Any]) -> bool:
        """Validate DNS payload."""
        # Must have a query name
        if "query_name" not in payload:
            return False

        # Query type must be valid
        valid_types = ["A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "TXT"]
        query_type = payload.get("query_type", "A")
        if query_type not in valid_types:
            return False

        return True

    def get_spec(self) -> ProtocolMetadata:
        """Return DNS protocol metadata."""
        return self.SPEC


if __name__ == "__main__":
    # Test the handler
    handler = DNSProtocolHandler()
    context = ProtocolContext(target="dns://8.8.8.8:53")

    # Test prepare_request
    payload = {
        "query_name": "example.com",
        "query_type": "A",
        "recursive": True
    }
    request = handler.prepare_request(context, payload)
    print(f"Request: {request}")

    # Test validate
    print(f"Valid: {handler.validate(payload)}")
    print(f"Invalid: {handler.validate({})}")

    # Test parse_response
    response = {
        "status": "ok",
        "response_code": "NOERROR",
        "answer_count": 1,
        "query_time_ms": 15
    }
    parsed = handler.parse_response(context, response)
    print(f"Parsed: {parsed}")
```

### Step 3: Implement Client-Side Handler

Create `HyFuzz-Ubuntu-Client/src/protocols/dns_handler.py`:

```python
"""DNS protocol handler for client."""

from __future__ import annotations
from typing import Dict
import socket
import time

from .base_handler import BaseProtocolHandler, ProtocolMetadata
from ..models.execution_models import ExecutionRequest
from .protocol_metadata import DNS_PROTOCOL_METADATA


class DNSHandler(BaseProtocolHandler):
    """DNS protocol handler for payload execution."""

    name = "dns"
    capabilities = DNS_PROTOCOL_METADATA

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        """Execute DNS query against target."""
        # Extract parameters
        query_name = request.parameters.get("query_name", "example.com")
        query_type = request.parameters.get("query_type", "A")
        timeout = int(request.parameters.get("timeout", 5))

        # Parse target URL (dns://host:port)
        target_parts = request.target.replace("dns://", "").split(":")
        host = target_parts[0]
        port = int(target_parts[1]) if len(target_parts) > 1 else 53

        start_time = time.time()

        try:
            # Create DNS query packet (simplified)
            query_id = 1234
            query_packet = self._build_dns_query(
                query_id,
                query_name,
                query_type
            )

            # Send query
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(query_packet, (host, port))

            # Receive response
            response_data, _ = sock.recvfrom(512)
            sock.close()

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Parse response (simplified)
            response_code, answer_count = self._parse_dns_response(response_data)

            return {
                "status": "ok",
                "message": f"DNS query for {query_name} completed",
                "response_code": response_code,
                "answer_count": str(answer_count),
                "query_time_ms": str(elapsed_ms)
            }

        except socket.timeout:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "status": "timeout",
                "message": f"DNS query for {query_name} timed out",
                "query_time_ms": str(elapsed_ms)
            }

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {
                "status": "error",
                "message": f"DNS query failed: {str(e)}",
                "query_time_ms": str(elapsed_ms)
            }

    def _build_dns_query(
        self,
        query_id: int,
        query_name: str,
        query_type: str
    ) -> bytes:
        """Build DNS query packet."""
        # Simplified DNS query construction
        # In production, use dnspython or similar library
        packet = bytearray()

        # Header
        packet.extend(query_id.to_bytes(2, 'big'))  # ID
        packet.extend(b'\x01\x00')  # Flags: standard query
        packet.extend(b'\x00\x01')  # Questions: 1
        packet.extend(b'\x00\x00')  # Answers: 0
        packet.extend(b'\x00\x00')  # Authority: 0
        packet.extend(b'\x00\x00')  # Additional: 0

        # Question section
        for label in query_name.split('.'):
            packet.append(len(label))
            packet.extend(label.encode())
        packet.append(0)  # End of name

        # Query type and class
        type_map = {"A": 1, "NS": 2, "CNAME": 5, "MX": 15, "TXT": 16, "AAAA": 28}
        packet.extend(type_map.get(query_type, 1).to_bytes(2, 'big'))
        packet.extend(b'\x00\x01')  # Class: IN

        return bytes(packet)

    def _parse_dns_response(self, response_data: bytes) -> tuple[str, int]:
        """Parse DNS response packet."""
        # Simplified DNS response parsing
        if len(response_data) < 12:
            return "FORMERR", 0

        # Extract response code from flags
        flags = int.from_bytes(response_data[2:4], 'big')
        rcode = flags & 0x000F
        rcode_map = {0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL", 3: "NXDOMAIN"}
        response_code = rcode_map.get(rcode, "UNKNOWN")

        # Extract answer count
        answer_count = int.from_bytes(response_data[6:8], 'big')

        return response_code, answer_count

    def get_capabilities(self) -> ProtocolMetadata:
        """Return DNS protocol metadata."""
        return self.capabilities


if __name__ == "__main__":
    # Test the handler
    handler = DNSHandler()
    request = ExecutionRequest(
        payload_id="test-1",
        protocol="dns",
        target="dns://8.8.8.8:53",
        parameters={
            "query_name": "example.com",
            "query_type": "A",
            "timeout": "5"
        }
    )
    result = handler.execute(request)
    print(f"Result: {result}")
```

### Step 4: Create Shared Metadata File

Create `protocol_metadata.py` in both locations with shared definitions:

**HyFuzz-Windows-Server/src/protocols/protocol_metadata.py**:
```python
"""Shared protocol metadata definitions."""

from dataclasses import dataclass, field
from typing import Dict, Any

from .base_protocol import ProtocolMetadata

# DNS Protocol
DNS_PROTOCOL_METADATA = ProtocolMetadata(
    name="dns",
    version="1.0.0",
    description="Domain Name System protocol fuzzer",
    stateful=False,
    default_parameters={
        "query_type": "A",
        "recursive": True,
        "timeout": 5
    },
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0"
)

# Add more protocol metadata as needed
```

## Protocol Registration

### Automatic Registration (Recommended)

Use the plugin discovery system for automatic registration:

1. Place your protocol handler in the appropriate `protocols/` directory
2. Ensure it follows the naming convention: `{protocol_name}_protocol.py` (server) or `{protocol_name}_handler.py` (client)
3. The protocol will be automatically discovered and registered

### Manual Registration

If you need manual control, use the registry directly:

**Server-side**:
```python
from src.protocols.protocol_registry import ProtocolRegistry
from src.protocols.dns_protocol import DNSProtocolHandler

registry = ProtocolRegistry()
registry.register("dns", DNSProtocolHandler)
```

**Client-side**:
```python
from src.protocols.protocol_factory import register_handler
from src.protocols.dns_handler import DNSHandler

register_handler("dns", DNSHandler)
```

## Testing Your Protocol

### Unit Tests

Create comprehensive unit tests for both handlers:

**tests/protocols/test_dns_protocol.py**:
```python
"""Tests for DNS protocol handlers."""

import pytest
from src.protocols.dns_protocol import DNSProtocolHandler
from src.protocols.base_protocol import ProtocolContext


class TestDNSProtocolHandler:
    """Test DNS server-side protocol handler."""

    def test_prepare_request(self):
        """Test request preparation."""
        handler = DNSProtocolHandler()
        context = ProtocolContext(target="dns://8.8.8.8:53")
        payload = {
            "query_name": "example.com",
            "query_type": "A"
        }

        request = handler.prepare_request(context, payload)

        assert request["query_name"] == "example.com"
        assert request["query_type"] == "A"
        assert request["target"] == "dns://8.8.8.8:53"

    def test_validate_valid_payload(self):
        """Test validation of valid payload."""
        handler = DNSProtocolHandler()
        payload = {"query_name": "example.com", "query_type": "A"}

        assert handler.validate(payload) is True

    def test_validate_invalid_payload(self):
        """Test validation of invalid payload."""
        handler = DNSProtocolHandler()

        # Missing query_name
        assert handler.validate({"query_type": "A"}) is False

        # Invalid query_type
        assert handler.validate({"query_name": "example.com", "query_type": "INVALID"}) is False

    def test_parse_response(self):
        """Test response parsing."""
        handler = DNSProtocolHandler()
        context = ProtocolContext(target="dns://8.8.8.8:53")
        response = {
            "status": "ok",
            "response_code": "NOERROR",
            "answer_count": 1
        }

        parsed = handler.parse_response(context, response)

        assert parsed["response_code"] == "NOERROR"
        assert parsed["answer_count"] == 1
```

### Integration Tests

Test the complete workflow:

```python
"""Integration test for DNS protocol."""

import pytest
from coordinator import FuzzingCoordinator, CampaignTarget


@pytest.mark.integration
def test_dns_fuzzing_campaign():
    """Test complete DNS fuzzing campaign."""
    coordinator = FuzzingCoordinator(model_name="test")

    target = CampaignTarget(
        name="google-dns",
        protocol="dns",
        endpoint="dns://8.8.8.8:53"
    )

    summary = coordinator.run_campaign([target], payload_count=10)

    assert len(summary.executions) == 10
    assert summary.average_judgment_score() >= 0
```

### Manual Testing

Use the provided test scripts:

```bash
# Test server-side handler
python -m src.protocols.dns_protocol

# Test client-side handler
python -m src.protocols.dns_handler

# Run fuzzing campaign
python scripts/test_protocol.py --protocol dns --target dns://8.8.8.8:53
```

## Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
def execute(self, request: ExecutionRequest) -> Dict[str, str]:
    try:
        # Your execution logic
        result = self._execute_internal(request)
        return {"status": "ok", "message": "Success", **result}
    except TimeoutError as e:
        return {"status": "timeout", "message": str(e)}
    except ConnectionError as e:
        return {"status": "error", "message": f"Connection failed: {e}"}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {e}"}
```

### 2. Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

class DNSHandler(BaseProtocolHandler):
    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        logger.info(f"Executing DNS query", extra={
            "target": request.target,
            "query_name": request.parameters.get("query_name")
        })
        # ...
```

### 3. Timeout Management

Always implement timeouts:

```python
timeout = int(request.parameters.get("timeout", 5))
sock.settimeout(timeout)
```

### 4. Resource Cleanup

Use context managers for resource cleanup:

```python
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.settimeout(timeout)
    sock.sendto(data, (host, port))
    response, _ = sock.recvfrom(4096)
```

### 5. Protocol Versioning

Include version information:

```python
SPEC = ProtocolMetadata(
    name="dns",
    version="1.0.0",  # Semantic versioning
    min_server_version="1.0.0",
    min_client_version="1.0.0"
)
```

### 6. Documentation

Document all public methods:

```python
def prepare_request(self, context: ProtocolContext, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare DNS query request.

    Args:
        context: Target and session information
        payload: Dictionary containing:
            - query_name (str): Domain name to query
            - query_type (str): DNS record type (A, AAAA, MX, etc.)
            - recursive (bool): Whether to request recursive query
            - timeout (int): Query timeout in seconds

    Returns:
        Request dictionary with prepared DNS query parameters

    Raises:
        ValueError: If required parameters are missing
    """
    # Implementation
```

### 7. Testing Coverage

Aim for high test coverage:

- Unit tests for all public methods
- Edge cases and error conditions
- Integration tests with real targets
- Performance benchmarks

### 8. Security Considerations

- Validate all inputs
- Sanitize payload data
- Implement rate limiting
- Use secure connections when available
- Never execute untrusted code

## Example: Complete WebSocket Protocol

See `examples/protocols/websocket_example/` for a complete, production-ready protocol implementation including:

- Server and client handlers
- Comprehensive tests
- Documentation
- Example campaigns
- Performance benchmarks

## Next Steps

1. Review existing protocol implementations in `src/protocols/`
2. Study the protocol metadata system
3. Implement your protocol following this guide
4. Write comprehensive tests
5. Submit a pull request

## Support

For questions or issues:

- Check the [FAQ](../FAQ.md)
- Review [API documentation](../API.md)
- Open an issue on GitHub
- Join community discussions

## Related Documentation

- [Architecture Overview](../ARCHITECTURE.md)
- [API Reference](../API.md)
- [Testing Guide](../TESTING.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
