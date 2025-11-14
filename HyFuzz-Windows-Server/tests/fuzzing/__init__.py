"""
Fuzzing Tests Package

This package contains comprehensive fuzzing tests for the HyFuzz system,
including tests for MCP protocol, database operations, and transport layers.

Test Modules:
- test_mcp_fuzzing: MCP protocol message fuzzing
- test_database_fuzzing: Database and SQL injection fuzzing
- test_mcp_transport_fuzzing: Transport layer (stdio, HTTP, WebSocket) fuzzing
"""

__version__ = "1.0.0"
__all__ = [
    "test_mcp_fuzzing",
    "test_database_fuzzing",
    "test_mcp_transport_fuzzing",
]
