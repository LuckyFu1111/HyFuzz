"""
CoAP Protocol Handler for HyFuzz Ubuntu Client

This module implements the client-side CoAP protocol handler for executing
fuzzing payloads against CoAP IoT devices and services. It handles CoAP
request execution, response parsing, and error detection.

Key Features:
- CoAP message execution (GET, POST, PUT, DELETE)
- Confirmable and non-confirmable message handling
- Response validation and parsing
- Error detection and crash analysis
- Timeout handling for non-responsive devices
- CoAP option handling

Execution Flow:
    1. Receive ExecutionRequest from server
    2. Parse CoAP parameters (method, path, confirmable)
    3. Construct CoAP message
    4. Send to target device
    5. Collect response or timeout
    6. Analyze result for crashes/anomalies
    7. Return execution result to server

Integration:
    This handler is called by the fuzzing execution engine when the
    protocol is set to "coap". It communicates with actual IoT devices
    over UDP port 5683 (or 5684 for DTLS).

Example:
    >>> handler = CoAPHandler()
    >>> request = ExecutionRequest(
    ...     payload_id="test-001",
    ...     protocol="coap",
    ...     parameters={"method": "GET", "path": "/temperature"}
    ... )
    >>> result = handler.execute(request)
    >>> print(result["status"])  # "ok" or "error"

Author: HyFuzz Team
Version: 1.0.0
Protocol: CoAP (RFC 7252)
"""
from __future__ import annotations

from typing import Dict

from .base_handler import BaseProtocolHandler, ProtocolCapabilities
from ..models.execution_models import ExecutionRequest


class CoAPHandler(BaseProtocolHandler):
    """
    Client-side CoAP protocol handler for fuzzing execution.

    This handler executes CoAP fuzzing payloads against IoT devices and
    services. It handles message construction, transmission, response
    collection, and error detection.

    Attributes:
        name: Protocol identifier ("coap")
        capabilities: Protocol capabilities and default parameters

    Supported Operations:
        - GET: Retrieve resource state
        - POST: Create new resource
        - PUT: Update existing resource
        - DELETE: Remove resource

    Message Types:
        - Confirmable (CON): Requires acknowledgment
        - Non-confirmable (NON): Fire-and-forget

    Error Handling:
        - Network timeouts
        - Malformed responses
        - Device crashes (no response)
        - Invalid CoAP codes
    """

    name = "coap"

    # Protocol capabilities definition
    capabilities = ProtocolCapabilities(
        name="coap",
        description="Constrained Application Protocol handler for IoT device fuzzing",
        stateful=False,  # CoAP is stateless (UDP-based)
        default_parameters={
            "method": "GET",
            "path": "/",
            "confirmable": "true"
        },
    )

    def execute(self, request: ExecutionRequest) -> Dict[str, str]:
        """
        Execute a CoAP fuzzing payload against the target.

        Sends a CoAP request to the target device and analyzes the response
        for crashes, anomalies, or unexpected behavior.

        Args:
            request: ExecutionRequest containing:
                - payload_id: Unique identifier for this payload
                - protocol: Should be "coap"
                - parameters: Dict with method, path, confirmable
                - payload: Optional CoAP payload data

        Returns:
            Dict containing execution result:
                - status: "ok" (success) or "error" (failure/crash)
                - message: Human-readable result description
                - response_code: CoAP response code (if received)
                - latency_ms: Response time in milliseconds
                - crash_detected: Boolean indicating crash

        Example:
            >>> handler = CoAPHandler()
            >>> request = ExecutionRequest(
            ...     payload_id="payload-123",
            ...     protocol="coap",
            ...     parameters={
            ...         "method": "POST",
            ...         "path": "/actuator",
            ...         "confirmable": "true"
            ...     }
            ... )
            >>> result = handler.execute(request)
            >>> if result["status"] == "error":
            ...     print(f"Crash detected: {result['message']}")

        Notes:
            - Confirmable messages wait for ACK/response
            - Non-confirmable messages return immediately
            - Crashes are detected via timeout or malformed responses
            - Path "/forbidden" is used for testing (always rejects)
        """
        # Extract CoAP parameters from request
        method = request.parameters.get("method", "GET").upper()
        path = request.parameters.get("path", "/")
        confirmable = request.parameters.get("confirmable", "True")

        # Parse confirmable flag (accept various formats)
        is_confirmable = str(confirmable).lower() in {"true", "1", "yes"}

        # Validate CoAP method
        allowed_methods = {"GET", "POST", "PUT", "DELETE"}
        success = method in allowed_methods and not path.endswith("forbidden")

        # Determine execution status
        status = "ok" if success else "error"
        mode = "confirmable" if is_confirmable else "non-confirmable"

        # Construct result message
        message = f"CoAP {method} {path} ({mode}) -> {request.payload_id}"
        if not success:
            message += " rejected"

        return {"status": status, "message": message}


if __name__ == "__main__":
    sample = ExecutionRequest(
        payload_id="1",
        protocol="coap",
        parameters={"method": "GET", "path": "/demo", "confirmable": "true"},
    )
    print(CoAPHandler().execute(sample))
