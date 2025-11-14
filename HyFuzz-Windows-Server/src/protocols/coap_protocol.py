"""
CoAP (Constrained Application Protocol) Handler for HyFuzz

This module implements the CoAP protocol handler for fuzzing IoT devices and
constrained environments. CoAP is a specialized web transfer protocol designed
for use with constrained nodes and networks in the Internet of Things.

Key Features:
- CoAP request/response message construction
- Support for confirmable and non-confirmable messages
- Method handling (GET, POST, PUT, DELETE)
- URI path and query parameter fuzzing
- Option header manipulation
- Block-wise transfer support

Protocol Overview:
    CoAP (RFC 7252) is a lightweight HTTP-like protocol designed for IoT:
    - Uses UDP for transport (default port 5683)
    - Binary message format for efficiency
    - Request/Response interaction model
    - Observe pattern for publish/subscribe
    - Resource discovery via /.well-known/core

Fuzzing Targets:
- IoT devices and sensors
- Smart home systems
- Industrial control systems (ICS)
- Embedded systems with constrained resources
- CoAP-to-HTTP proxies

Common Vulnerabilities:
- CWE-400: Resource exhaustion via observe requests
- CWE-20: Improper input validation in URI paths
- CWE-770: Block transfer DoS attacks
- CWE-306: Missing authentication
- CWE-319: Cleartext transmission (no DTLS)

Example Usage:
    >>> handler = CoAPProtocolHandler()
    >>> context = ProtocolContext(target="coap://192.168.1.100")
    >>> payload = {
    ...     "method": "GET",
    ...     "path": "/temperature",
    ...     "confirmable": True
    ... }
    >>> request = handler.prepare_request(context, payload)
    >>> is_valid = handler.validate(payload)

Author: HyFuzz Team
Version: 1.0.0
Protocol: CoAP (RFC 7252)
"""

from __future__ import annotations

from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext, ProtocolSpec


class CoAPProtocolHandler(BaseProtocolHandler):
    """
    CoAP (Constrained Application Protocol) handler for fuzzing IoT devices.

    This handler implements CoAP message construction and validation for
    fuzzing constrained devices in IoT environments. It supports standard
    CoAP methods, confirmable/non-confirmable messages, and option headers.

    Attributes:
        name: Protocol identifier ("coap")
        SPEC: Protocol specification with default parameters

    Protocol Details:
        - Transport: UDP (default port 5683, DTLS on 5684)
        - Message Types: CON, NON, ACK, RST
        - Methods: GET, POST, PUT, DELETE
        - Options: Uri-Path, Uri-Query, Content-Format, etc.

    Security Considerations:
        - CoAP often lacks authentication in IoT deployments
        - DTLS is optional and frequently disabled
        - Resource discovery can leak sensitive information
        - Block-wise transfers can cause memory exhaustion
    """

    name = "coap"

    SPEC = ProtocolSpec(
        name="coap",
        description="Constrained Application Protocol (RFC 7252) - Lightweight HTTP for IoT",
        stateful=False,
        default_parameters={
            "method": "GET",
            "path": "/",
            "confirmable": True
        },
    )

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare a CoAP request from the given payload.

        This method constructs a CoAP request message by combining the base
        request from the parent class with CoAP-specific parameters like
        method, path, and message type.

        Args:
            context: Protocol context with target information
            payload: Payload dictionary containing:
                - method (str): CoAP method (GET, POST, PUT, DELETE)
                - path (str): URI path (e.g., "/temperature")
                - payload (Any): Request payload/body
                - confirmable (bool): Whether to use confirmable message
                - options (Dict): Additional CoAP options

        Returns:
            Dict containing the prepared CoAP request with:
                - method: CoAP method
                - path: URI path
                - payload: Request payload
                - confirmable: Message type
                - Additional fields from base handler

        Example:
            >>> handler = CoAPProtocolHandler()
            >>> ctx = ProtocolContext(target="coap://device.local")
            >>> req = handler.prepare_request(ctx, {
            ...     "method": "POST",
            ...     "path": "/actuator",
            ...     "payload": {"state": "on"}
            ... })
        """
        # Get base request from parent handler
        request = super().prepare_request(context, payload)

        # Add CoAP-specific fields
        request["payload"] = payload.get("payload", request["payload"])
        request["method"] = payload.get("method", "GET")
        request["path"] = payload.get("path", "/")

        # Add optional CoAP-specific parameters
        if "confirmable" in payload:
            request["confirmable"] = payload["confirmable"]
        if "options" in payload:
            request["options"] = payload["options"]

        return request

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate a CoAP payload.

        Performs basic validation to ensure the payload contains required
        fields for a valid CoAP request. At minimum, a path must be specified.

        Args:
            payload: Payload dictionary to validate

        Returns:
            True if payload is valid, False otherwise

        Validation Rules:
            - Must contain a "path" field
            - Path should be a string (checked implicitly)
            - Method is optional (defaults to GET)
            - Additional validation performed at execution time

        Example:
            >>> handler = CoAPProtocolHandler()
            >>> handler.validate({"path": "/sensor"})
            True
            >>> handler.validate({"method": "GET"})
            False
        """
        return "path" in payload


if __name__ == "__main__":
    handler = CoAPProtocolHandler()
    ctx = ProtocolContext(target="coap://demo")
    print(handler.prepare_request(ctx, {"path": "/ping"}))
    print("Valid:", handler.validate({"path": "/ping"}))
