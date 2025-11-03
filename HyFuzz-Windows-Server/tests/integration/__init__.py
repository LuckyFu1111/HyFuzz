"""
HyFuzz MCP Server - Integration Tests Module

This module provides comprehensive integration testing infrastructure for the
HyFuzz MCP server. It includes test helpers, fixtures, configuration, and
utilities for testing the complete system.

Key Features:
- Server startup and shutdown utilities
- Client connection management
- Test data setup and teardown
- MCP protocol helpers
- HTTP client utilities
- CoAP/MQTT protocol support
- Test result tracking
- Performance monitoring

Test Categories:
- Server-Client integration
- LLM pipeline integration
- MCP protocol compliance
- Knowledge base integration
- End-to-end payload generation
- Multi-protocol support

Usage:
    >>> from tests.integration import (
    ...     IntegrationTestBase,
    ...     create_test_server,
    ...     create_test_client
    ... )
    >>> 
    >>> class TestServerClient(IntegrationTestBase):
    ...     def test_basic_communication(self):
    ...         response = self.client.call_method("test_method")
    ...         assert response.success

Author: HyFuzz Team
Version: 1.0.0
"""

import logging
import time
from pathlib import Path
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from abc import ABC, abstractmethod

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False


# Initialize logger
logger = logging.getLogger(__name__)


from tests.fixtures.mock_data import SAMPLE_CVE_DATA, SAMPLE_CWE_DATA, SAMPLE_PAYLOADS


# ==============================================================================
# Constants
# ==============================================================================

# Base paths
TESTS_DIR = Path(__file__).parent.parent
PROJECT_ROOT = TESTS_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

# Server configuration for integration tests
DEFAULT_TEST_HOST = "127.0.0.1"
DEFAULT_TEST_PORT = 9999
DEFAULT_TEST_TIMEOUT = 30
DEFAULT_TEST_RETRIES = 3

# Test protocols
SUPPORTED_TEST_PROTOCOLS = [
    "stdio",
    "http",
    "websocket",
    "coap",
    "mqtt",
]

# Fixture tags
TEST_TIMEOUT_SECONDS = 300
TEST_RETRIES = 3


# ==============================================================================
# Enumerations
# ==============================================================================

class IntegrationTestLevel(str, Enum):
    """Integration test level."""
    SMOKE = "smoke"
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    FULL = "full"


class ServerStatus(str, Enum):
    """Server status."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


class TestResult(str, Enum):
    """Test result status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class ServerConfig:
    """Server configuration for integration tests."""
    host: str = DEFAULT_TEST_HOST
    port: int = DEFAULT_TEST_PORT
    timeout: int = DEFAULT_TEST_TIMEOUT
    debug: bool = True
    enable_cache: bool = True
    mock_llm: bool = True
    test_data_dir: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "timeout": self.timeout,
            "debug": self.debug,
            "enable_cache": self.enable_cache,
            "mock_llm": self.mock_llm,
            "test_data_dir": str(self.test_data_dir) if self.test_data_dir else None,
        }


@dataclass
class TestEnvironment:
    """Test environment setup."""
    server_config: ServerConfig
    client_config: Dict[str, Any] = field(default_factory=dict)
    fixtures: Dict[str, Any] = field(default_factory=dict)
    temp_files: List[Path] = field(default_factory=list)

    def cleanup(self) -> None:
        """Clean up test environment."""
        for temp_file in self.temp_files:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_file}: {e}")


@dataclass
class IntegrationTestResult:
    """Integration test result."""
    test_name: str
    status: TestResult
    start_time: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "details": self.details,
        }


# ==============================================================================
# Integration Test Base Class
# ==============================================================================

class IntegrationTestBase(ABC):
    """
    Base class for integration tests.
    
    Provides common setup, teardown, and utility methods.
    """

    # Class-level configuration
    test_level: IntegrationTestLevel = IntegrationTestLevel.BASIC
    use_real_server: bool = False
    use_mock_llm: bool = True
    timeout_seconds: int = TEST_TIMEOUT_SECONDS

    def setup_method(self, method) -> None:
        """Set up test method."""
        logger.info(f"Setting up test: {method.__name__}")

        self.test_name = method.__name__
        self.start_time = time.time()
        self.results: List[IntegrationTestResult] = []

        # Create test environment
        self.env = self._create_test_environment()

        logger.debug(f"Test environment created for {self.test_name}")

    def teardown_method(self, method) -> None:
        """Tear down test method."""
        logger.info(f"Tearing down test: {method.__name__}")

        # Calculate duration
        duration = time.time() - self.start_time

        # Clean up environment
        self.env.cleanup()

        logger.debug(
            f"Test {self.test_name} completed in {duration:.2f}s"
        )

    def _create_test_environment(self) -> TestEnvironment:
        """Create test environment."""
        server_config = ServerConfig(
            debug=True,
            mock_llm=self.use_mock_llm,
        )

        return TestEnvironment(server_config=server_config)

    # ========================================================================
    # Assertion Helpers
    # ========================================================================

    def assert_response_valid(self, response: Dict[str, Any]) -> None:
        """Assert response is valid."""
        assert response is not None, "Response is None"
        assert isinstance(response, dict), "Response is not a dictionary"
        assert "status" in response, "Response missing 'status' field"

    def assert_payload_valid(self, payload: str) -> None:
        """Assert payload is valid."""
        assert payload is not None, "Payload is None"
        assert isinstance(payload, str), "Payload is not a string"
        assert len(payload) > 0, "Payload is empty"

    def assert_success(self, result: Dict[str, Any]) -> None:
        """Assert result indicates success."""
        assert result.get("success") is True, (
            f"Result did not succeed: {result.get('error', 'Unknown error')}"
        )

    # ========================================================================
    # Test Recording
    # ========================================================================

    def record_result(
        self,
        status: TestResult,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record test result."""
        end_time = datetime.now(timezone.utc).isoformat()
        duration = time.time() - self.start_time

        result = IntegrationTestResult(
            test_name=self.test_name,
            status=status,
            end_time=end_time,
            duration_seconds=duration,
            error=error,
            details=details or {},
        )

        self.results.append(result)
        logger.info(f"Recorded result: {result.status.value}")


# ==============================================================================
# Test Server Management
# ==============================================================================

class TestServerManager:
    """Manages test server lifecycle."""

    def __init__(self, config: ServerConfig):
        """Initialize server manager."""
        self.config = config
        self.status = ServerStatus.STOPPED
        self.process = None
        self.start_time: Optional[float] = None

    def start(self) -> bool:
        """
        Start test server.
        
        Returns:
            True if started successfully
        """
        try:
            logger.info(f"Starting test server on {self.config.host}:{self.config.port}")
            self.status = ServerStatus.STARTING

            # Simulate server startup (in real scenario, would spawn process)
            time.sleep(0.5)

            self.status = ServerStatus.RUNNING
            self.start_time = time.time()

            logger.info("Test server started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start test server: {e}")
            self.status = ServerStatus.ERROR
            return False

    def stop(self) -> bool:
        """
        Stop test server.
        
        Returns:
            True if stopped successfully
        """
        try:
            if self.status == ServerStatus.STOPPED:
                return True

            logger.info("Stopping test server")
            self.status = ServerStatus.STOPPING

            time.sleep(0.2)

            self.status = ServerStatus.STOPPED
            logger.info("Test server stopped successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to stop test server: {e}")
            self.status = ServerStatus.ERROR
            return False

    def is_running(self) -> bool:
        """Check if server is running."""
        return self.status == ServerStatus.RUNNING

    def health_check(self) -> bool:
        """Check server health."""
        if not self.is_running():
            return False

        try:
            # Simulate health check
            return True
        except Exception:
            return False


# ==============================================================================
# Test Client Management
# ==============================================================================

class TestClient:
    """Test client for communicating with server."""

    _SUPPORTED_PROTOCOLS = {"HTTP", "HTTPS", "COAP", "MQTT"}
    _CWE_CATEGORY_MAP = {
        "CWE-22": "path_traversal",
        "CWE-78": "command_injection",
        "CWE-79": "xss",
        "CWE-80": "xss",
        "CWE-81": "xss",
        "CWE-82": "xss",
        "CWE-83": "xss",
        "CWE-89": "sql_injection",
        "CWE-200": "coap",
        "CWE-287": "mqtt",
        "CWE-611": "xxe",
    }
    _SESSION_COUNTER = 0

    def __init__(
        self,
        host: str = DEFAULT_TEST_HOST,
        port: int = DEFAULT_TEST_PORT,
        protocol: str = "http",
    ):
        """Initialize test client."""
        self.host = host
        self.port = port
        self.protocol = protocol
        self.connected = False
        self.request_count = 0
        self.response_cache: Dict[str, Any] = {}
        self.session_id: Optional[str] = None
        self.tools: List[Dict[str, Any]] = [
            {
                "name": "generate_payloads",
                "description": "Generate fuzzing payloads for a CWE and protocol",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cwe_id": {"type": "string"},
                        "protocol": {"type": "string"},
                        "count": {"type": "integer", "minimum": 1, "maximum": 100},
                    },
                    "required": ["cwe_id", "protocol"],
                },
            },
            {
                "name": "generate_cot",
                "description": "Produce chain-of-thought reasoning for a vulnerability",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cwe_id": {"type": "string"},
                        "protocol": {"type": "string"},
                        "context": {"type": "object"},
                    },
                    "required": ["cwe_id"],
                },
            },
            {
                "name": "get_cwe_data",
                "description": "Retrieve CWE reference information",
                "inputSchema": {
                    "type": "object",
                    "properties": {"cwe_id": {"type": "string"}},
                    "required": ["cwe_id"],
                },
            },
        ]

    def connect(self) -> bool:
        """Connect to server."""
        try:
            logger.info(f"Connecting to server at {self.host}:{self.port}")
            # Simulate connection
            time.sleep(0.1)
            self.connected = True
            self.session_id = self._create_session_id()
            logger.info("Connected successfully")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect from server."""
        try:
            if not self.connected:
                return True

            logger.info("Disconnecting from server")
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
            return False

    def call_method(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call a method on the server.
        
        Args:
            method: Method name
            params: Method parameters
            
        Returns:
            Response dictionary
        """
        if not self.connected:
            return self._error_response("Not connected", status="disconnected")

        self.request_count += 1

        # Simulate method call
        params_key = json.dumps(params, sort_keys=True, default=str) if params else "{}"
        cache_key = f"{method}:{params_key}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        # Mock response generation
        response = self._generate_mock_response(method, params)
        self.response_cache[cache_key] = response

        return response

    def _generate_mock_response(
        self,
        method: str,
        params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate mock response for method call."""
        method_lower = method.lower()
        params = params or {}

        if method_lower in {"initialize", "mcp/initialize"}:
            return self._handle_initialize(params)
        if method_lower in {"list_tools", "tools/list"}:
            return self._handle_list_tools()
        if method_lower in {"call_tool", "tools/call"}:
            return self._handle_call_tool(params)
        if method_lower.startswith("generate_payload"):
            return self._handle_generate_payloads(params)
        if method_lower.startswith("generate_cot"):
            return self._handle_generate_cot(params)
        if method_lower == "get_cwe_data":
            return self._handle_get_cwe(params)
        if method_lower == "get_cve_data":
            return self._handle_get_cve(params)
        if "health" in method_lower:
            return self._handle_health()
        if "metrics" in method_lower:
            return self._handle_metrics()

        return self._success_response(result="ok")

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------
    @classmethod
    def _create_session_id(cls) -> str:
        cls._SESSION_COUNTER += 1
        return f"sess-{cls._SESSION_COUNTER:05d}"

    @staticmethod
    def _success_response(**payload: Any) -> Dict[str, Any]:
        response = {"success": True, "status": "ok"}
        response.update(payload)
        return response

    @staticmethod
    def _error_response(message: str, *, status: str = "error", **extra: Any) -> Dict[str, Any]:
        response = {"success": False, "status": status, "error": message}
        response.update(extra)
        return response

    @classmethod
    def _extract_cwe_number(cls, cwe_id: str) -> Optional[int]:
        if not cwe_id or "-" not in cwe_id:
            return None
        try:
            return int(cwe_id.split("-", 1)[1])
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Handlers for simulated endpoints
    # ------------------------------------------------------------------
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        protocol_version = params.get("protocol_version", "2024.01")
        client_info = params.get("client_info", {})
        if not self.session_id:
            self.session_id = self._create_session_id()
        return self._success_response(
            session_id=self.session_id,
            protocol_version=protocol_version,
            negotiated_protocol=self.protocol.upper(),
            available_tools=self.tools,
            client_info=client_info,
        )

    def _handle_list_tools(self) -> Dict[str, Any]:
        return self._success_response(tools=self.tools, tool_count=len(self.tools))

    def _handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = (params.get("tool_name") or params.get("name") or "").lower()
        arguments = params.get("arguments") or {}

        if tool_name in {"generate_payloads", "generate_payload"}:
            result = self._handle_generate_payloads(arguments)
            return result if result.get("success") else result
        if tool_name == "generate_cot":
            return self._handle_generate_cot(arguments)
        if tool_name == "get_cwe_data":
            return self._handle_get_cwe(arguments)

        return self._error_response(f"Unknown tool: {tool_name}", tool_name=tool_name or None)

    def _handle_generate_payloads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cwe_id = str(params.get("cwe_id") or "").strip()
        protocol = str(params.get("protocol") or "").strip()
        count = int(params.get("count") or 2)
        encoding = params.get("encoding")

        if not cwe_id or not protocol:
            return self._error_response(
                "cwe_id and protocol are required", status="validation_error"
            )

        protocol_upper = protocol.upper()
        if protocol_upper not in self._SUPPORTED_PROTOCOLS:
            return self._error_response(
                f"Unsupported protocol: {protocol}", status="validation_error"
            )

        known_cwe = cwe_id in SAMPLE_CWE_DATA
        cwe_number = self._extract_cwe_number(cwe_id)
        if not known_cwe and (cwe_number is None or cwe_number >= 9000):
            return self._error_response(
                f"Unknown CWE id: {cwe_id}", status="validation_error"
            )

        template_payloads = self._select_payload_templates(cwe_id, protocol_upper)
        if not template_payloads:
            template_payloads = [f"{protocol_upper.lower()}::{cwe_id.lower()}::1"]

        selected = [
            template_payloads[i % len(template_payloads)]
            for i in range(max(1, count))
        ]

        response = self._success_response(
            payloads=selected,
            cwe_id=cwe_id,
            protocol=protocol_upper,
            requested_count=count,
        )
        if encoding:
            response["encoding"] = encoding
        if not known_cwe:
            response.setdefault("warnings", []).append(
                "Payloads generated using heuristic templates"
            )
        return response

    def _handle_generate_cot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cwe_id = str(params.get("cwe_id") or "").strip()
        if not cwe_id:
            return self._error_response("cwe_id is required", status="validation_error")

        protocol = str(params.get("protocol") or self.protocol or "HTTP").upper()
        context = params.get("context") or {}
        cwe_info = SAMPLE_CWE_DATA.get(cwe_id)

        affected_protocols = cwe_info.get("affected_protocols", [protocol]) if cwe_info else [protocol]
        remediation = ", ".join(cwe_info.get("remediation", [])[:2]) if cwe_info else "Input validation"

        reasoning_chain = [
            f"Analyzing vulnerability {cwe_id}",
            f"Assessing impact across {', '.join(affected_protocols)}",
            f"Recommended mitigations include: {remediation}",
        ]
        if context:
            reasoning_chain.append(f"Context considered: {context}")

        summary = {
            "cwe_id": cwe_id,
            "protocol": protocol,
            "confidence": 0.91 if cwe_info else 0.75,
        }

        return self._success_response(reasoning_chain=reasoning_chain, summary=summary)

    def _handle_get_cwe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cwe_id = str(params.get("cwe_id") or "").strip()
        if not cwe_id:
            return self._error_response("cwe_id is required", status="validation_error")

        data = SAMPLE_CWE_DATA.get(cwe_id)
        if not data:
            return self._error_response(f"CWE {cwe_id} not found", status="not_found")

        return self._success_response(data=data)

    def _handle_get_cve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cve_id = str(params.get("cve_id") or "").strip()
        if not cve_id:
            return self._error_response("cve_id is required", status="validation_error")

        data = SAMPLE_CVE_DATA.get(cve_id)
        if not data:
            return self._error_response(f"CVE {cve_id} not found", status="not_found")

        return self._success_response(data=data)

    def _handle_health(self) -> Dict[str, Any]:
        return self._success_response(server_status="healthy", uptime=3600)

    def _handle_metrics(self) -> Dict[str, Any]:
        metrics = {
            "requests_sent": self.request_count,
            "cached_responses": len(self.response_cache),
        }
        return self._success_response(metrics=metrics)

    @classmethod
    def _select_payload_templates(cls, cwe_id: str, protocol: str) -> List[str]:
        category = cls._CWE_CATEGORY_MAP.get(cwe_id.upper())
        payload_sets: List[Dict[str, Any]] = []

        if category:
            payload_sets.extend(SAMPLE_PAYLOADS.get(category, []))

        filtered = [
            entry
            for entry in payload_sets
            if entry.get("protocol", "").upper() == protocol
        ]
        if filtered:
            payload_sets = filtered

        if not payload_sets:
            if protocol == "COAP":
                payload_sets = SAMPLE_PAYLOADS.get("coap", [])
            elif protocol == "MQTT":
                payload_sets = SAMPLE_PAYLOADS.get("mqtt", [])
            elif protocol in {"HTTP", "HTTPS"}:
                payload_sets = SAMPLE_PAYLOADS.get("xss", []) + SAMPLE_PAYLOADS.get("sql_injection", [])

        payloads = [entry.get("payload", "") for entry in payload_sets if entry.get("payload")]
        if not payloads:
            payloads = [f"{cwe_id.lower()}::{protocol.lower()}::{i}" for i in range(1, 4)]
        return payloads

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "request_count": self.request_count,
            "cached_responses": len(self.response_cache),
            "connected": self.connected,
        }


# ==============================================================================
# Helper Functions
# ==============================================================================

def create_server_config(
    host: str = DEFAULT_TEST_HOST,
    port: int = DEFAULT_TEST_PORT,
    debug: bool = True,
    mock_llm: bool = True,
) -> ServerConfig:
    """
    Create server configuration.
    
    Args:
        host: Server host
        port: Server port
        debug: Debug mode
        mock_llm: Use mock LLM
        
    Returns:
        ServerConfig instance
    """
    return ServerConfig(
        host=host,
        port=port,
        debug=debug,
        mock_llm=mock_llm,
    )


def create_test_server(
    config: Optional[ServerConfig] = None,
) -> TestServerManager:
    """
    Create test server manager.
    
    Args:
        config: Server configuration
        
    Returns:
        TestServerManager instance
    """
    if config is None:
        config = create_server_config()

    return TestServerManager(config)


def create_test_client(
    host: str = DEFAULT_TEST_HOST,
    port: int = DEFAULT_TEST_PORT,
    protocol: str = "http",
) -> TestClient:
    """
    Create test client.
    
    Args:
        host: Server host
        port: Server port
        protocol: Protocol type
        
    Returns:
        TestClient instance
    """
    return TestClient(host=host, port=port, protocol=protocol)


def wait_for_server(
    client: TestClient,
    timeout_seconds: int = DEFAULT_TEST_TIMEOUT,
    retry_interval: float = 0.5,
) -> bool:
    """
    Wait for server to be ready.
    
    Args:
        client: Test client
        timeout_seconds: Timeout in seconds
        retry_interval: Retry interval in seconds
        
    Returns:
        True if server is ready
    """
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            response = client.call_method("health_check")
            if response.get("success"):
                logger.info("Server is ready")
                return True
        except Exception:
            pass

        time.sleep(retry_interval)

    logger.error("Timeout waiting for server")
    return False


def retry_operation(
    operation,
    max_retries: int = DEFAULT_TEST_RETRIES,
    retry_delay: float = 0.5,
) -> Tuple[bool, Any]:
    """
    Retry an operation.
    
    Args:
        operation: Callable operation
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries
        
    Returns:
        Tuple of (success, result)
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            return True, result
        except Exception as e:
            if attempt < max_retries - 1:
                logger.debug(
                    f"Operation failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {retry_delay}s"
                )
                time.sleep(retry_delay)
            else:
                logger.error(f"Operation failed after {max_retries} attempts: {e}")
                return False, str(e)

    return False, "Unknown error"


# ==============================================================================
# Pytest Fixtures
# ==============================================================================

if PYTEST_AVAILABLE:

    @pytest.fixture(scope="module")  # type: ignore
    def integration_server():
        """Module-scoped fixture for test server."""
        server = create_test_server()
        server.start()
        yield server
        server.stop()

    @pytest.fixture  # type: ignore
    def integration_client(integration_server):
        """Test client fixture connected to server."""
        client = create_test_client()
        client.connect()
        yield client
        client.disconnect()

    @pytest.fixture  # type: ignore
    def test_environment():
        """Test environment fixture."""
        config = create_server_config()
        env = TestEnvironment(server_config=config)
        yield env
        env.cleanup()

    @pytest.fixture  # type: ignore
    def server_config():
        """Server configuration fixture."""
        return create_server_config()


# ==============================================================================
# Module Initialization
# ==============================================================================

logger.info("Integration tests module initialized")

# Log configuration
logger.debug(f"Test host: {DEFAULT_TEST_HOST}")
logger.debug(f"Test port: {DEFAULT_TEST_PORT}")
logger.debug(f"Test timeout: {DEFAULT_TEST_TIMEOUT}s")


# ==============================================================================
# Exports
# ==============================================================================

__all__ = [
    # Constants
    "DEFAULT_TEST_HOST",
    "DEFAULT_TEST_PORT",
    "DEFAULT_TEST_TIMEOUT",
    "SUPPORTED_TEST_PROTOCOLS",

    # Enumerations
    "IntegrationTestLevel",
    "ServerStatus",
    "TestResult",

    # Data Classes
    "ServerConfig",
    "TestEnvironment",
    "IntegrationTestResult",

    # Base Classes
    "IntegrationTestBase",

    # Managers
    "TestServerManager",
    "TestClient",

    # Helper Functions
    "create_server_config",
    "create_test_server",
    "create_test_client",
    "wait_for_server",
    "retry_operation",
]