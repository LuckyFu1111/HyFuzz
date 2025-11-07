#!/usr/bin/env python3
"""
Protocol template generator for HyFuzz.

This tool generates boilerplate code for new protocol implementations,
including server-side handler, client-side handler, tests, and documentation.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def to_class_name(protocol_name: str) -> str:
    """Convert protocol name to CamelCase class name."""
    parts = protocol_name.replace("-", "_").split("_")
    return "".join(word.capitalize() for word in parts)


def generate_server_protocol(protocol_name: str, description: str, stateful: bool) -> str:
    """Generate server-side protocol handler code."""
    class_name = to_class_name(protocol_name)

    return f'''"""
{protocol_name.upper()} protocol handler for server.

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from __future__ import annotations
from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext
from .protocol_metadata import ProtocolMetadata


# Protocol metadata
{protocol_name.upper()}_METADATA = ProtocolMetadata(
    name="{protocol_name}",
    version="1.0.0",
    description="{description}",
    stateful={stateful},
    default_parameters={{
        # Add your default parameters here
        # Example: "timeout": 5, "method": "GET"
    }},
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="Your Name",
    license="MIT",
    tags=["{protocol_name}"],
)


class {class_name}ProtocolHandler(BaseProtocolHandler):
    """
    {protocol_name.upper()} protocol handler for server-side payload generation.

    This handler is responsible for:
    - Preparing requests to be sent to the client
    - Parsing responses from the client
    - Validating payloads before sending
    """

    name = "{protocol_name}"
    SPEC = {protocol_name.upper()}_METADATA

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare a {protocol_name.upper()} request.

        Args:
            context: Target and session information
            payload: Generated payload data

        Returns:
            Request dictionary with all necessary fields
        """
        # Start with base request
        request = super().prepare_request(context, payload)

        # Extract protocol-specific parameters
        # Example:
        # request["method"] = payload.get("method", "GET")
        # request["path"] = payload.get("path", "/")

        # TODO: Add your protocol-specific request preparation logic here

        return request

    def parse_response(
        self,
        context: ProtocolContext,
        response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse {protocol_name.upper()} response from client.

        Args:
            context: Original request context
            response: Execution results from client

        Returns:
            Parsed response with extracted metrics
        """
        # Start with base parsing
        parsed = super().parse_response(context, response)

        # Extract protocol-specific metrics
        # Example:
        # parsed["status_code"] = response.get("status_code", 0)
        # parsed["response_time_ms"] = response.get("response_time_ms", 0)

        # TODO: Add your protocol-specific response parsing logic here

        return parsed

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate a {protocol_name.upper()} payload.

        Args:
            payload: Payload to validate

        Returns:
            True if payload is valid, False otherwise
        """
        # TODO: Add your validation logic here
        # Example:
        # if "required_field" not in payload:
        #     return False
        # if payload.get("some_value") not in ["valid1", "valid2"]:
        #     return False

        return super().validate(payload)

    def get_spec(self) -> ProtocolMetadata:
        """Return {protocol_name.upper()} protocol metadata."""
        return self.SPEC


if __name__ == "__main__":
    # Test the handler
    handler = {class_name}ProtocolHandler()
    context = ProtocolContext(target="{protocol_name}://example.com")

    # Test prepare_request
    payload = {{"test": "data"}}
    request = handler.prepare_request(context, payload)
    print(f"Request: {{request}}")

    # Test validate
    print(f"Valid: {{handler.validate(payload)}}")

    # Test parse_response
    response = {{"status": "ok"}}
    parsed = handler.parse_response(context, response)
    print(f"Parsed: {{parsed}}")

    # Display metadata
    spec = handler.get_spec()
    print(f"\\nMetadata:")
    print(f"  Name: {{spec.name}}")
    print(f"  Version: {{spec.version}}")
    print(f"  Description: {{spec.description}}")
    print(f"  Stateful: {{spec.stateful}}")
'''


def generate_client_handler(protocol_name: str, description: str, stateful: bool) -> str:
    """Generate client-side protocol handler code."""
    class_name = to_class_name(protocol_name)

    return f'''"""
{protocol_name.upper()} protocol handler for client.

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from __future__ import annotations
from typing import Dict
import time

from .base_handler import BaseProtocolHandler
from .protocol_metadata import ProtocolMetadata
from ..models.execution_models import ExecutionRequest


# Import the same metadata definition
{protocol_name.upper()}_METADATA = ProtocolMetadata(
    name="{protocol_name}",
    version="1.0.0",
    description="{description}",
    stateful={stateful},
    default_parameters={{
        # Add your default parameters here
        # Example: "timeout": "5", "method": "GET"
    }},
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False,
    min_server_version="1.0.0",
    min_client_version="1.0.0",
    author="Your Name",
    tags=["{protocol_name}"],
)


class {class_name}Handler(BaseProtocolHandler):
    """
    {protocol_name.upper()} protocol handler for client-side execution.

    This handler is responsible for:
    - Executing payloads against the target
    - Collecting execution results and metrics
    - Handling errors and timeouts
    """

    name = "{protocol_name}"
    capabilities = {protocol_name.upper()}_METADATA

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        """
        Execute {protocol_name.upper()} payload against target.

        Args:
            request: Execution request with payload and parameters

        Returns:
            Execution result with status and metrics
        """
        # Extract parameters
        # Example:
        # timeout = int(request.parameters.get("timeout", 5))
        # method = request.parameters.get("method", "GET")

        # Parse target URL
        # Example: {protocol_name}://host:port/path
        target_url = request.target
        # TODO: Parse target URL appropriately

        start_time = time.time()

        try:
            # TODO: Implement your protocol execution logic here
            # This is where you send the payload to the target

            # Example structure:
            # 1. Connect to target
            # 2. Send payload
            # 3. Receive response
            # 4. Parse response
            # 5. Return results

            elapsed_ms = int((time.time() - start_time) * 1000)

            return {{
                "status": "ok",
                "message": f"{protocol_name.upper()} execution completed",
                "elapsed_ms": str(elapsed_ms),
                # Add more metrics as needed
            }}

        except TimeoutError as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {{
                "status": "timeout",
                "message": f"{protocol_name.upper()} execution timed out: {{e}}",
                "elapsed_ms": str(elapsed_ms),
            }}

        except ConnectionError as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {{
                "status": "error",
                "message": f"{protocol_name.upper()} connection failed: {{e}}",
                "elapsed_ms": str(elapsed_ms),
            }}

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return {{
                "status": "error",
                "message": f"{protocol_name.upper()} execution failed: {{e}}",
                "elapsed_ms": str(elapsed_ms),
            }}

    def execute_stateful(
        self,
        request: ExecutionRequest,
        session: "ProtocolSessionState"
    ) -> Dict[str, str]:
        """
        Execute stateful {protocol_name.upper()} request.

        Args:
            request: Execution request
            session: Current session state

        Returns:
            Execution result
        """
        # Only implement this if your protocol is stateful
        {"if stateful:" if stateful else "# If protocol becomes stateful, implement this method"}
        {"# TODO: Implement stateful execution logic" if stateful else ""}
        return self.execute(request)

    def get_capabilities(self) -> ProtocolMetadata:
        """Return {protocol_name.upper()} protocol metadata."""
        return self.capabilities


if __name__ == "__main__":
    # Test the handler
    handler = {class_name}Handler()
    request = ExecutionRequest(
        payload_id="test-1",
        protocol="{protocol_name}",
        target="{protocol_name}://localhost:12345",
        parameters={{
            # Add test parameters here
        }}
    )

    result = handler.execute(request)
    print(f"Result: {{result}}")

    # Display metadata
    caps = handler.get_capabilities()
    print(f"\\nMetadata:")
    print(f"  Name: {{caps.name}}")
    print(f"  Version: {{caps.version}}")
    print(f"  Description: {{caps.description}}")
    print(f"  Stateful: {{caps.stateful}}")
'''


def generate_test_file(protocol_name: str) -> str:
    """Generate test file for the protocol."""
    class_name = to_class_name(protocol_name)

    return f'''"""
Tests for {protocol_name.upper()} protocol handlers.

Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import pytest
from unittest.mock import Mock, patch


class Test{class_name}ProtocolHandler:
    """Test {protocol_name.upper()} server-side protocol handler."""

    def test_prepare_request(self):
        """Test request preparation."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler
        from HyFuzz_Windows_Server.src.protocols.base_protocol import ProtocolContext

        handler = {class_name}ProtocolHandler()
        context = ProtocolContext(target="{protocol_name}://example.com")
        payload = {{"test": "data"}}

        request = handler.prepare_request(context, payload)

        assert request["target"] == "{protocol_name}://example.com"
        assert "payload" in request
        # Add more specific assertions

    def test_validate_valid_payload(self):
        """Test validation of valid payload."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler

        handler = {class_name}ProtocolHandler()
        payload = {{"test": "data"}}  # Replace with valid payload

        assert handler.validate(payload) is True

    def test_validate_invalid_payload(self):
        """Test validation of invalid payload."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler

        handler = {class_name}ProtocolHandler()
        payload = {{}}  # Replace with invalid payload

        # Adjust based on your validation logic
        # assert handler.validate(payload) is False

    def test_parse_response(self):
        """Test response parsing."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler
        from HyFuzz_Windows_Server.src.protocols.base_protocol import ProtocolContext

        handler = {class_name}ProtocolHandler()
        context = ProtocolContext(target="{protocol_name}://example.com")
        response = {{"status": "ok", "data": "test"}}

        parsed = handler.parse_response(context, response)

        assert "response" in parsed
        # Add more specific assertions

    def test_get_spec(self):
        """Test metadata retrieval."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler

        handler = {class_name}ProtocolHandler()
        spec = handler.get_spec()

        assert spec.name == "{protocol_name}"
        assert spec.version == "1.0.0"
        assert spec.description != ""


class Test{class_name}Handler:
    """Test {protocol_name.upper()} client-side protocol handler."""

    def test_execute_success(self):
        """Test successful execution."""
        from HyFuzz_Ubuntu_Client.src.protocols.{protocol_name}_handler import {class_name}Handler
        from HyFuzz_Ubuntu_Client.src.models.execution_models import ExecutionRequest

        handler = {class_name}Handler()
        request = ExecutionRequest(
            payload_id="test-1",
            protocol="{protocol_name}",
            target="{protocol_name}://localhost:12345",
            parameters={{}}
        )

        # Mock the actual execution if needed
        result = handler.execute(request)

        assert "status" in result
        assert "message" in result
        # Add more specific assertions

    def test_execute_timeout(self):
        """Test timeout handling."""
        from HyFuzz_Ubuntu_Client.src.protocols.{protocol_name}_handler import {class_name}Handler
        from HyFuzz_Ubuntu_Client.src.models.execution_models import ExecutionRequest

        handler = {class_name}Handler()
        request = ExecutionRequest(
            payload_id="test-1",
            protocol="{protocol_name}",
            target="{protocol_name}://localhost:99999",  # Invalid port
            parameters={{"timeout": "1"}}
        )

        result = handler.execute(request)

        # Adjust based on your error handling
        # assert result["status"] in ["timeout", "error"]

    def test_get_capabilities(self):
        """Test metadata retrieval."""
        from HyFuzz_Ubuntu_Client.src.protocols.{protocol_name}_handler import {class_name}Handler

        handler = {class_name}Handler()
        caps = handler.get_capabilities()

        assert caps.name == "{protocol_name}"
        assert caps.version == "1.0.0"
        assert caps.description != ""


@pytest.mark.integration
class Test{class_name}Integration:
    """Integration tests for {protocol_name.upper()} protocol."""

    def test_end_to_end(self):
        """Test complete workflow from server to client."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler
        from HyFuzz_Windows_Server.src.protocols.base_protocol import ProtocolContext
        from HyFuzz_Ubuntu_Client.src.protocols.{protocol_name}_handler import {class_name}Handler
        from HyFuzz_Ubuntu_Client.src.models.execution_models import ExecutionRequest

        # Server side: prepare request
        server_handler = {class_name}ProtocolHandler()
        context = ProtocolContext(target="{protocol_name}://localhost:12345")
        payload = {{"test": "data"}}

        request_data = server_handler.prepare_request(context, payload)
        assert server_handler.validate(payload)

        # Client side: execute request
        client_handler = {class_name}Handler()
        execution_request = ExecutionRequest(
            payload_id="test-1",
            protocol="{protocol_name}",
            target=request_data["target"],
            parameters={{}}
        )

        result = client_handler.execute(execution_request)

        # Server side: parse response
        parsed = server_handler.parse_response(context, result)

        assert "status" in result
        # Add more assertions

    def test_protocol_compatibility(self):
        """Test that server and client metadata match."""
        from HyFuzz_Windows_Server.src.protocols.{protocol_name}_protocol import {class_name}ProtocolHandler
        from HyFuzz_Ubuntu_Client.src.protocols.{protocol_name}_handler import {class_name}Handler

        server_handler = {class_name}ProtocolHandler()
        client_handler = {class_name}Handler()

        server_spec = server_handler.get_spec()
        client_caps = client_handler.get_capabilities()

        assert server_spec.name == client_caps.name
        assert server_spec.version == client_caps.version
        assert server_spec.stateful == client_caps.stateful


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


def generate_readme(protocol_name: str, description: str) -> str:
    """Generate README for the protocol."""
    class_name = to_class_name(protocol_name)

    return f'''# {protocol_name.upper()} Protocol Implementation

{description}

## Overview

This protocol implementation provides support for fuzzing {protocol_name.upper()} targets in HyFuzz.

Generated on {datetime.now().strftime("%Y-%m-%d")}

## Files

- `{protocol_name}_protocol.py` - Server-side protocol handler
- `{protocol_name}_handler.py` - Client-side protocol handler
- `test_{protocol_name}.py` - Test suite
- `README.md` - This file

## Installation

### 1. Copy to Protocol Directories

```bash
# Server-side handler
cp {protocol_name}_protocol.py ../../HyFuzz-Windows-Server/src/protocols/

# Client-side handler
cp {protocol_name}_handler.py ../../HyFuzz-Ubuntu-Client/src/protocols/
```

### 2. Verify Installation

```bash
# Validate the protocol implementations
python ../../scripts/validate_protocol.py \\
    ../../HyFuzz-Windows-Server/src/protocols/{protocol_name}_protocol.py \\
    --type server

python ../../scripts/validate_protocol.py \\
    ../../HyFuzz-Ubuntu-Client/src/protocols/{protocol_name}_handler.py \\
    --type client

# Check compatibility
python ../../scripts/validate_protocol.py \\
    ../../HyFuzz-Windows-Server/src/protocols/{protocol_name}_protocol.py \\
    ../../HyFuzz-Ubuntu-Client/src/protocols/{protocol_name}_handler.py \\
    --check-compatibility
```

### 3. Run Tests

```bash
pytest test_{protocol_name}.py -v
```

## Usage

### Using the Coordinator

```python
from coordinator import FuzzingCoordinator, CampaignTarget

coordinator = FuzzingCoordinator(model_name="mistral")

target = CampaignTarget(
    name="{protocol_name}-target",
    protocol="{protocol_name}",
    endpoint="{protocol_name}://target-host:port"
)

summary = coordinator.run_campaign([target], payload_count=100)
print(f"Results: {{summary.verdict_breakdown()}}")
```

### Using the API

```python
import requests

response = requests.post('http://localhost:8080/api/v1/campaigns',
    headers={{'X-API-Key': 'your-api-key'}},
    json={{
        'name': '{protocol_name}-fuzzing',
        'protocol': '{protocol_name}',
        'target': '{protocol_name}://target-host:port',
        'model': 'mistral',
        'config': {{'payload_count': 100}}
    }}
)
```

## Protocol Metadata

```python
{protocol_name.upper()}_METADATA = ProtocolMetadata(
    name="{protocol_name}",
    version="1.0.0",
    description="{description}",
    stateful=False,  # Adjust if needed
    default_parameters={{
        # Add default parameters
    }},
)
```

## Development

### TODOs

The generated code includes TODO comments for areas that need implementation:

1. **Server Handler ({protocol_name}_protocol.py)**:
   - [ ] Implement request preparation logic in `prepare_request()`
   - [ ] Implement response parsing logic in `parse_response()`
   - [ ] Implement payload validation in `validate()`
   - [ ] Define default parameters in metadata

2. **Client Handler ({protocol_name}_handler.py)**:
   - [ ] Implement protocol execution logic in `execute()`
   - [ ] Add proper error handling
   - [ ] Implement stateful execution if needed
   - [ ] Add metrics collection

3. **Tests (test_{protocol_name}.py)**:
   - [ ] Add comprehensive unit tests
   - [ ] Add integration tests with real targets
   - [ ] Add edge case and error handling tests

### Extension Points

To extend the protocol:

1. **Add Features**: Modify handler methods to support additional protocol features
2. **Add Parameters**: Update metadata's `default_parameters`
3. **Add Validation**: Enhance `validate()` method
4. **Add Metrics**: Collect and return additional metrics in response

## Testing

Run the test suite:

```bash
# Unit tests only
pytest test_{protocol_name}.py -v

# Include integration tests
pytest test_{protocol_name}.py -v -m integration

# With coverage
pytest test_{protocol_name}.py --cov=. --cov-report=html
```

## Documentation

See also:

- [Protocol Development Guide](../../docs/PROTOCOL_DEVELOPMENT_GUIDE.md)
- [API Documentation](../../API.md)
- [Architecture Overview](../../ARCHITECTURE.md)

## License

MIT

## Contributing

Contributions are welcome! Please:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Run validation before submitting

---

Generated by HyFuzz Protocol Generator
'''


def create_protocol(
    protocol_name: str,
    description: str,
    output_dir: Path,
    stateful: bool = False
) -> None:
    """
    Create a complete protocol implementation.

    Args:
        protocol_name: Name of the protocol (e.g., 'dns', 'custom-protocol')
        description: Brief description of the protocol
        output_dir: Directory to create the protocol files in
        stateful: Whether the protocol maintains state
    """
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating {protocol_name.upper()} protocol in {output_dir}")
    print(f"Description: {description}")
    print(f"Stateful: {stateful}")
    print()

    # Generate files
    files = {
        f"{protocol_name}_protocol.py": generate_server_protocol(
            protocol_name, description, stateful
        ),
        f"{protocol_name}_handler.py": generate_client_handler(
            protocol_name, description, stateful
        ),
        f"test_{protocol_name}.py": generate_test_file(protocol_name),
        "README.md": generate_readme(protocol_name, description),
    }

    # Write files
    for filename, content in files.items():
        file_path = output_dir / filename
        file_path.write_text(content)
        print(f"✅ Created: {file_path}")

    print()
    print("Protocol generation complete!")
    print()
    print("Next steps:")
    print(f"1. cd {output_dir}")
    print("2. Review and implement the TODOs in the generated files")
    print("3. Run tests: pytest test_{protocol_name}.py -v")
    print("4. Validate: python ../../scripts/validate_protocol.py {protocol_name}_protocol.py")
    print("5. Copy to protocol directories (see README.md)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new HyFuzz protocol implementation"
    )
    parser.add_argument(
        "protocol_name",
        help="Protocol name (e.g., 'dns', 'custom-protocol')"
    )
    parser.add_argument(
        "--description",
        "-d",
        required=True,
        help="Brief description of the protocol"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        help="Output directory (default: examples/protocols/<protocol_name>)"
    )
    parser.add_argument(
        "--stateful",
        action="store_true",
        help="Mark protocol as stateful"
    )

    args = parser.parse_args()

    # Normalize protocol name
    protocol_name = args.protocol_name.lower().replace("_", "-")

    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = Path(__file__).parent.parent / "examples" / "protocols" / f"{protocol_name}_example"

    try:
        create_protocol(
            protocol_name=protocol_name,
            description=args.description,
            output_dir=output_dir,
            stateful=args.stateful
        )
        return 0
    except Exception as e:
        print(f"❌ Error creating protocol: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
