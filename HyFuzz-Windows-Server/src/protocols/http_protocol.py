"""
HTTP Protocol Handler for HyFuzz

This module implements the HTTP/HTTPS protocol handler for fuzzing web
applications, REST APIs, and HTTP services. Supports HTTP/1.1, HTTP/2,
and common web vulnerability testing.

Key Features:
- HTTP/1.1 and HTTP/2 support
- All HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
- Header manipulation and injection
- Cookie handling
- Query parameter fuzzing
- Request body fuzzing (JSON, XML, form data)
- Authentication testing (Basic, Bearer, OAuth)
- Content-Type negotiation

Protocol Overview:
    HTTP is a stateless request-response protocol:
    - Transport: TCP (port 80), TLS (port 443)
    - Methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, etc.
    - Headers: Request/response metadata
    - Status Codes: 1xx (info), 2xx (success), 3xx (redirect), 4xx (client error), 5xx (server error)
    - Content Types: JSON, XML, HTML, form-urlencoded, multipart/form-data

Fuzzing Targets:
- Web applications
- REST APIs
- GraphQL endpoints
- SOAP services
- WebSocket upgrade endpoints
- HTTP proxies and gateways
- API gateways
- Microservices

Common Vulnerabilities:
- CWE-79: Cross-Site Scripting (XSS)
- CWE-89: SQL Injection
- CWE-78: OS Command Injection
- CWE-22: Path Traversal
- CWE-352: Cross-Site Request Forgery (CSRF)
- CWE-798: Hard-coded credentials
- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-611: XML External Entity (XXE)
- CWE-502: Deserialization vulnerabilities
- CWE-287: Authentication bypass

HTTP Methods:
    - GET: Retrieve resource (idempotent, safe)
    - POST: Create resource (non-idempotent)
    - PUT: Update/replace resource (idempotent)
    - PATCH: Partial update (non-idempotent)
    - DELETE: Remove resource (idempotent)
    - HEAD: Get headers only
    - OPTIONS: Get supported methods
    - TRACE: Echo request (often disabled)

Security Headers:
    - Content-Security-Policy (CSP)
    - X-Frame-Options
    - X-Content-Type-Options
    - Strict-Transport-Security (HSTS)
    - X-XSS-Protection (deprecated)

Example Usage:
    >>> handler = HTTPProtocolHandler()
    >>> context = ProtocolContext(target="https://api.example.com")
    >>>
    >>> # GET request
    >>> payload = {
    ...     "method": "GET",
    ...     "path": "/api/users/123",
    ...     "headers": {"Authorization": "Bearer token123"}
    ... }
    >>> request = handler.prepare_request(context, payload)
    >>>
    >>> # POST request with JSON body
    >>> payload = {
    ...     "method": "POST",
    ...     "path": "/api/users",
    ...     "headers": {
    ...         "Content-Type": "application/json",
    ...         "Authorization": "Bearer token123"
    ...     },
    ...     "payload": {"name": "John", "email": "john@example.com"}
    ... }
    >>> request = handler.prepare_request(context, payload)
    >>>
    >>> # File upload with multipart/form-data
    >>> payload = {
    ...     "method": "POST",
    ...     "path": "/upload",
    ...     "headers": {"Content-Type": "multipart/form-data"},
    ...     "files": {"file": ("test.txt", b"content")}
    ... }
    >>> request = handler.prepare_request(context, payload)

Content Types:
    - application/json: JSON data
    - application/xml: XML data
    - application/x-www-form-urlencoded: Form data
    - multipart/form-data: File uploads
    - text/html: HTML content
    - text/plain: Plain text

Attack Vectors:
    - Header injection (CRLF injection)
    - HTTP parameter pollution
    - HTTP request smuggling
    - Host header injection
    - Cookie injection and manipulation
    - Authorization header bypass
    - Method override (X-HTTP-Method-Override)

Author: HyFuzz Team
Version: 1.0.0
Protocol: HTTP/1.1, HTTP/2
"""

from __future__ import annotations

from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext


class HTTPProtocolHandler(BaseProtocolHandler):
    """
    HTTP Protocol Handler for web application and API fuzzing.

    This handler implements HTTP/HTTPS request construction and validation
    for fuzzing web applications, REST APIs, and HTTP services. Supports
    all standard HTTP methods, headers, and content types.

    Attributes:
        name: Protocol identifier ("http")

    Protocol Details:
        - Transport: TCP (port 80) or TLS (port 443)
        - Methods: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE
        - Versions: HTTP/1.0, HTTP/1.1, HTTP/2
        - Content-Types: JSON, XML, form-urlencoded, multipart/form-data

    Common Attack Surfaces:
        - URL parameters and query strings
        - Request headers (especially Host, User-Agent, Referer)
        - Request body (JSON, XML, form data)
        - Cookies and session tokens
        - Authentication headers
        - File upload endpoints
    """

    name = "http"

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare an HTTP request from the given payload.

        Constructs an HTTP request with method, path, headers, and body.
        Handles various content types and authentication schemes.

        Args:
            context: Protocol context with target URL
            payload: Payload dictionary containing:
                - method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
                - path (str): URL path (e.g., "/api/users")
                - headers (Dict): HTTP headers
                - query (Dict): URL query parameters
                - payload (Any): Request body
                - cookies (Dict): HTTP cookies
                - auth (tuple): (username, password) for Basic Auth
                - files (Dict): Files for multipart upload

        Returns:
            Dict containing the prepared HTTP request:
                - method: HTTP method
                - path: URL path
                - headers: HTTP headers dictionary
                - Additional fields from base handler

        Example:
            >>> handler = HTTPProtocolHandler()
            >>> ctx = ProtocolContext(target="https://api.example.com")
            >>>
            >>> # Simple GET request
            >>> req = handler.prepare_request(ctx, {
            ...     "method": "GET",
            ...     "path": "/users",
            ...     "query": {"page": 1, "limit": 10}
            ... })
            >>>
            >>> # POST with JSON body
            >>> req = handler.prepare_request(ctx, {
            ...     "method": "POST",
            ...     "path": "/users",
            ...     "headers": {"Content-Type": "application/json"},
            ...     "payload": {"name": "Alice", "age": 30}
            ... })
            >>>
            >>> # Authenticated request
            >>> req = handler.prepare_request(ctx, {
            ...     "method": "GET",
            ...     "path": "/private",
            ...     "headers": {"Authorization": "Bearer abc123"}
            ... })
        """
        # Get base request from parent handler
        request = super().prepare_request(context, payload)

        # Set HTTP method (default to GET)
        request.setdefault("method", payload.get("method", "GET"))

        # Set path (required for HTTP)
        request.setdefault("path", payload.get("path", "/"))

        # Set headers (default to empty dict)
        request.setdefault("headers", payload.get("headers", {}))

        # Add optional HTTP-specific fields
        if "query" in payload:
            request["query"] = payload["query"]

        if "cookies" in payload:
            request["cookies"] = payload["cookies"]

        if "auth" in payload:
            request["auth"] = payload["auth"]

        if "files" in payload:
            request["files"] = payload["files"]

        return request

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate an HTTP payload.

        Ensures the payload contains the minimum required fields for a
        valid HTTP request (method and path).

        Args:
            payload: Payload dictionary to validate

        Returns:
            True if payload is valid, False otherwise

        Validation Rules:
            - Must contain "method" field
            - Must contain "path" field
            - Method should be a valid HTTP method (checked at runtime)
            - Path should be a valid URL path (checked at runtime)

        Example:
            >>> handler = HTTPProtocolHandler()
            >>> handler.validate({"method": "GET", "path": "/"})
            True
            >>> handler.validate({"method": "GET"})  # Missing path
            False
            >>> handler.validate({"path": "/"})  # Missing method
            False
        """
        return "method" in payload and "path" in payload


if __name__ == "__main__":
    handler = HTTPProtocolHandler()
    ctx = ProtocolContext(target="http://example.com")
    print(handler.prepare_request(ctx, {"method": "POST", "path": "/api"}))
    print("Valid:", handler.validate({"method": "GET", "path": "/"}))
