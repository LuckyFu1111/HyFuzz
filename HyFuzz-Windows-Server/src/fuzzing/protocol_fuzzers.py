"""
Protocol-Specific Fuzzers for IoT and Industrial Protocols

This module provides specialized fuzzing implementations for:
- CoAP (Constrained Application Protocol) - IoT messaging
- Modbus - Industrial control systems
- MQTT - IoT publish/subscribe messaging
- HTTP/2 - Modern web protocol
- WebSocket - Real-time communication

Each fuzzer implements protocol-aware mutations that maintain syntactic
validity while exploring edge cases and boundary conditions.

Author: HyFuzz Team
Version: 1.0.0
"""

import struct
import random
import logging
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


# ============================================================================
# CoAP Protocol Fuzzer
# ============================================================================

class CoAPType(Enum):
    """CoAP message types"""
    CONFIRMABLE = 0
    NON_CONFIRMABLE = 1
    ACKNOWLEDGEMENT = 2
    RESET = 3


class CoAPCode(Enum):
    """CoAP method and response codes"""
    # Methods (0.XX)
    EMPTY = 0x00
    GET = 0x01
    POST = 0x02
    PUT = 0x03
    DELETE = 0x04

    # Success (2.XX)
    CREATED = 0x41
    DELETED = 0x42
    VALID = 0x43
    CHANGED = 0x44
    CONTENT = 0x45

    # Client Error (4.XX)
    BAD_REQUEST = 0x80
    UNAUTHORIZED = 0x81
    BAD_OPTION = 0x82
    FORBIDDEN = 0x83
    NOT_FOUND = 0x84

    # Server Error (5.XX)
    INTERNAL_ERROR = 0xA0
    NOT_IMPLEMENTED = 0xA1
    BAD_GATEWAY = 0xA2
    SERVICE_UNAVAILABLE = 0xA3


@dataclass
class CoAPMessage:
    """CoAP message structure"""
    version: int = 1
    msg_type: CoAPType = CoAPType.CONFIRMABLE
    token_length: int = 0
    code: CoAPCode = CoAPCode.GET
    message_id: int = 0
    token: bytes = b''
    options: List[Tuple[int, bytes]] = None
    payload: bytes = b''

    def __post_init__(self):
        if self.options is None:
            self.options = []


class CoAPFuzzer:
    """
    CoAP (Constrained Application Protocol) Fuzzer

    RFC 7252 compliant fuzzer for IoT devices using CoAP.
    Targets vulnerabilities in:
    - Option parsing
    - Payload handling
    - Token validation
    - Message ID handling
    - Block transfer
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Common CoAP option numbers
        self.OPTION_URI_HOST = 3
        self.OPTION_URI_PORT = 7
        self.OPTION_URI_PATH = 11
        self.OPTION_URI_QUERY = 15
        self.OPTION_CONTENT_FORMAT = 12
        self.OPTION_BLOCK2 = 23
        self.OPTION_SIZE2 = 28

    def encode_message(self, msg: CoAPMessage) -> bytes:
        """Encode CoAP message to bytes"""
        # First byte: version (2 bits) | type (2 bits) | token length (4 bits)
        first_byte = (msg.version << 6) | (msg.msg_type.value << 4) | msg.token_length

        # Second byte: code (class.detail)
        code_byte = msg.code.value

        # Third and fourth bytes: message ID (big-endian)
        msg_id_bytes = struct.pack('>H', msg.message_id)

        # Build header
        header = bytes([first_byte, code_byte]) + msg_id_bytes

        # Add token
        packet = header + msg.token

        # Add options (delta-encoded)
        if msg.options:
            packet += self._encode_options(msg.options)

        # Add payload marker and payload if present
        if msg.payload:
            packet += b'\xFF' + msg.payload

        return packet

    def _encode_options(self, options: List[Tuple[int, bytes]]) -> bytes:
        """Encode CoAP options with delta encoding"""
        encoded = b''
        prev_option = 0

        for option_num, option_value in sorted(options):
            delta = option_num - prev_option
            length = len(option_value)

            # Simple encoding (no extended delta/length)
            if delta < 13 and length < 13:
                encoded += bytes([(delta << 4) | length])
                encoded += option_value
            else:
                # Extended encoding (simplified)
                encoded += bytes([0xDD])  # Placeholder
                encoded += option_value

            prev_option = option_num

        return encoded

    def decode_message(self, data: bytes) -> Optional[CoAPMessage]:
        """Decode bytes to CoAP message (best effort)"""
        if len(data) < 4:
            return None

        try:
            first_byte = data[0]
            version = (first_byte >> 6) & 0x03
            msg_type = CoAPType((first_byte >> 4) & 0x03)
            token_length = first_byte & 0x0F

            code = CoAPCode(data[1])
            message_id = struct.unpack('>H', data[2:4])[0]

            offset = 4
            token = data[offset:offset + token_length] if token_length > 0 else b''
            offset += token_length

            # Parse options and payload (simplified)
            payload = b''
            if b'\xFF' in data[offset:]:
                payload_start = data.index(b'\xFF', offset) + 1
                payload = data[payload_start:]

            return CoAPMessage(
                version=version,
                msg_type=msg_type,
                token_length=token_length,
                code=code,
                message_id=message_id,
                token=token,
                payload=payload
            )
        except Exception as e:
            self.logger.debug(f"Failed to decode CoAP message: {e}")
            return None

    def fuzz_message(self, base_msg: Optional[CoAPMessage] = None) -> bytes:
        """Generate fuzzed CoAP message"""
        if base_msg is None:
            base_msg = self._create_default_message()

        # Select fuzzing strategy
        strategy = random.choice([
            'fuzz_version',
            'fuzz_type',
            'fuzz_token',
            'fuzz_message_id',
            'fuzz_options',
            'fuzz_payload',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_version':
            base_msg.version = random.randint(0, 15)

        elif strategy == 'fuzz_type':
            base_msg.msg_type = CoAPType(random.randint(0, 3))

        elif strategy == 'fuzz_token':
            # Invalid token lengths or content
            base_msg.token_length = random.choice([0, 8, 15, 16, 255])
            base_msg.token = bytes([random.randint(0, 255) for _ in range(base_msg.token_length)])

        elif strategy == 'fuzz_message_id':
            base_msg.message_id = random.choice([0, 0xFFFF, random.randint(0, 0xFFFF)])

        elif strategy == 'fuzz_options':
            base_msg.options = self._fuzz_options()

        elif strategy == 'fuzz_payload':
            base_msg.payload = self._fuzz_payload()

        elif strategy == 'fuzz_malformed':
            # Completely malformed message
            return bytes([random.randint(0, 255) for _ in range(random.randint(1, 100))])

        return self.encode_message(base_msg)

    def _create_default_message(self) -> CoAPMessage:
        """Create default CoAP GET request"""
        return CoAPMessage(
            version=1,
            msg_type=CoAPType.CONFIRMABLE,
            token_length=4,
            code=CoAPCode.GET,
            message_id=random.randint(0, 0xFFFF),
            token=bytes([random.randint(0, 255) for _ in range(4)]),
            options=[
                (self.OPTION_URI_PATH, b'test'),
            ],
            payload=b''
        )

    def _fuzz_options(self) -> List[Tuple[int, bytes]]:
        """Generate fuzzed CoAP options"""
        options = []

        fuzz_patterns = [
            # Normal options
            (self.OPTION_URI_PATH, b'/..' * 10),  # Path traversal
            (self.OPTION_URI_PATH, b'A' * 1000),  # Long path
            (self.OPTION_URI_QUERY, b'x' * 500),  # Long query
            (self.OPTION_CONTENT_FORMAT, b'\xFF\xFF'),  # Invalid format

            # Invalid option numbers
            (255, b'invalid'),
            (1000, b'very_invalid'),

            # Duplicate options
            (self.OPTION_URI_PATH, b'dup1'),
            (self.OPTION_URI_PATH, b'dup2'),
        ]

        # Select random subset
        return random.sample(fuzz_patterns, k=random.randint(1, 4))

    def _fuzz_payload(self) -> bytes:
        """Generate fuzzed payload"""
        patterns = [
            b'',  # Empty
            b'A' * 10000,  # Very long
            bytes([0xFF] * 100),  # All 0xFF
            bytes([0x00] * 100),  # All nulls
            bytes([random.randint(0, 255) for _ in range(1024)]),  # Random
        ]
        return random.choice(patterns)


# ============================================================================
# Modbus Protocol Fuzzer
# ============================================================================

class ModbusFunction(Enum):
    """Modbus function codes"""
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10
    READ_FILE_RECORD = 0x14
    WRITE_FILE_RECORD = 0x15
    DIAGNOSTICS = 0x08


@dataclass
class ModbusRequest:
    """Modbus TCP/RTU request structure"""
    # TCP header (for Modbus TCP)
    transaction_id: int = 0
    protocol_id: int = 0  # Always 0 for Modbus
    length: int = 0  # Remaining bytes
    unit_id: int = 1  # Slave address

    # PDU (Protocol Data Unit)
    function_code: ModbusFunction = ModbusFunction.READ_HOLDING_REGISTERS
    data: bytes = b''


class ModbusFuzzer:
    """
    Modbus Protocol Fuzzer

    Targets industrial control systems using Modbus TCP/RTU.
    Focuses on:
    - Function code validation
    - Register address boundaries
    - Data length validation
    - Exception handling
    - Illegal operations
    """

    def __init__(self, protocol: str = 'tcp'):
        """
        Initialize Modbus fuzzer

        Args:
            protocol: 'tcp' or 'rtu'
        """
        self.protocol = protocol
        self.logger = logging.getLogger(__name__)

    def encode_tcp_request(self, req: ModbusRequest) -> bytes:
        """Encode Modbus TCP request"""
        # MBAP Header (7 bytes)
        header = struct.pack(
            '>HHHB',
            req.transaction_id,
            req.protocol_id,
            req.length,
            req.unit_id
        )

        # PDU
        pdu = bytes([req.function_code.value]) + req.data

        return header + pdu

    def encode_rtu_request(self, req: ModbusRequest) -> bytes:
        """Encode Modbus RTU request"""
        # RTU: slave_id + function_code + data + CRC
        frame = bytes([req.unit_id, req.function_code.value]) + req.data

        # Calculate CRC16 (simplified - real impl should use proper CRC)
        crc = self._calculate_crc16(frame)

        return frame + struct.pack('<H', crc)

    def _calculate_crc16(self, data: bytes) -> int:
        """Calculate Modbus RTU CRC16 (simplified)"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def fuzz_request(self, base_req: Optional[ModbusRequest] = None) -> bytes:
        """Generate fuzzed Modbus request"""
        if base_req is None:
            base_req = self._create_default_request()

        # Select fuzzing strategy
        strategy = random.choice([
            'fuzz_function_code',
            'fuzz_address',
            'fuzz_quantity',
            'fuzz_data_values',
            'fuzz_length_mismatch',
            'fuzz_invalid_crc',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_function_code':
            # Invalid or reserved function codes
            base_req.function_code = ModbusFunction(random.choice([
                0x01, 0x03, 0x06, 0x10,  # Valid
                0x00, 0x80, 0xFF, 0x7F,  # Invalid
            ]))

        elif strategy == 'fuzz_address':
            # Read holding registers with boundary addresses
            base_req.function_code = ModbusFunction.READ_HOLDING_REGISTERS
            start_addr = random.choice([
                0x0000,  # Start
                0xFFFF,  # Max
                0x9C40,  # Common max (40000)
                0xFFFFFFFF,  # Overflow
            ])
            quantity = random.randint(1, 125)
            base_req.data = struct.pack('>HH', start_addr & 0xFFFF, quantity)

        elif strategy == 'fuzz_quantity':
            # Invalid quantity values
            base_req.function_code = ModbusFunction.READ_HOLDING_REGISTERS
            quantity = random.choice([
                0,  # Zero
                1,  # Min valid
                125,  # Max valid
                126,  # Just over max
                0xFFFF,  # Way over max
            ])
            base_req.data = struct.pack('>HH', 0, quantity)

        elif strategy == 'fuzz_data_values':
            # Write operations with edge-case values
            base_req.function_code = ModbusFunction.WRITE_MULTIPLE_REGISTERS
            start_addr = random.randint(0, 100)
            values = [
                0x0000,
                0xFFFF,
                0x8000,
                0x7FFF,
                random.randint(0, 0xFFFF)
            ]
            quantity = len(values)
            byte_count = quantity * 2

            data = struct.pack('>HHB', start_addr, quantity, byte_count)
            for value in values:
                data += struct.pack('>H', value)
            base_req.data = data

        elif strategy == 'fuzz_length_mismatch':
            # TCP length field doesn't match actual data
            base_req.length = random.choice([0, 255, 1, 0xFFFF])
            base_req.data = bytes([random.randint(0, 255) for _ in range(10)])

        elif strategy == 'fuzz_invalid_crc':
            if self.protocol == 'rtu':
                # Generate request with wrong CRC
                req_bytes = self.encode_rtu_request(base_req)
                # Corrupt last 2 bytes (CRC)
                return req_bytes[:-2] + bytes([0xFF, 0xFF])

        elif strategy == 'fuzz_malformed':
            # Completely malformed packet
            return bytes([random.randint(0, 255) for _ in range(random.randint(1, 256))])

        # Encode based on protocol
        if self.protocol == 'tcp':
            return self.encode_tcp_request(base_req)
        else:
            return self.encode_rtu_request(base_req)

    def _create_default_request(self) -> ModbusRequest:
        """Create default Modbus read request"""
        return ModbusRequest(
            transaction_id=random.randint(0, 0xFFFF),
            protocol_id=0,
            length=6,  # Unit ID (1) + Function Code (1) + Data (4)
            unit_id=1,
            function_code=ModbusFunction.READ_HOLDING_REGISTERS,
            data=struct.pack('>HH', 0, 10)  # Start addr 0, read 10 registers
        )


# ============================================================================
# MQTT Protocol Fuzzer
# ============================================================================

class MQTTPacketType(Enum):
    """MQTT packet types"""
    CONNECT = 1
    CONNACK = 2
    PUBLISH = 3
    PUBACK = 4
    SUBSCRIBE = 8
    SUBACK = 9
    UNSUBSCRIBE = 10
    UNSUBACK = 11
    PINGREQ = 12
    PINGRESP = 13
    DISCONNECT = 14


class MQTTFuzzer:
    """
    MQTT Protocol Fuzzer

    Targets IoT messaging brokers using MQTT.
    Focuses on:
    - Packet type validation
    - Topic name parsing
    - QoS level handling
    - Payload size limits
    - Will message handling
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def encode_connect(self, client_id: str = "fuzzer", clean_session: bool = True) -> bytes:
        """Encode MQTT CONNECT packet"""
        # Fixed header
        packet_type = MQTTPacketType.CONNECT.value << 4

        # Variable header
        protocol_name = b'\x00\x04MQTT'  # Protocol name length + name
        protocol_level = 4  # MQTT 3.1.1
        connect_flags = 0x02 if clean_session else 0x00
        keep_alive = 60

        var_header = protocol_name + bytes([protocol_level, connect_flags]) + struct.pack('>H', keep_alive)

        # Payload
        client_id_bytes = len(client_id).to_bytes(2, 'big') + client_id.encode()

        # Remaining length
        remaining = len(var_header) + len(client_id_bytes)

        return bytes([packet_type, remaining]) + var_header + client_id_bytes

    def encode_publish(self, topic: str, payload: bytes, qos: int = 0) -> bytes:
        """Encode MQTT PUBLISH packet"""
        # Fixed header
        packet_type = (MQTTPacketType.PUBLISH.value << 4) | (qos << 1)

        # Variable header
        topic_bytes = len(topic).to_bytes(2, 'big') + topic.encode()

        # Packet ID (only for QoS > 0)
        packet_id = struct.pack('>H', random.randint(1, 0xFFFF)) if qos > 0 else b''

        # Remaining length
        remaining = len(topic_bytes) + len(packet_id) + len(payload)

        return bytes([packet_type, remaining]) + topic_bytes + packet_id + payload

    def fuzz_mqtt(self) -> bytes:
        """Generate fuzzed MQTT packet"""
        strategy = random.choice([
            'fuzz_connect',
            'fuzz_publish',
            'fuzz_subscribe',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_connect':
            client_id = random.choice([
                'normal_client',
                '',  # Empty client ID
                'A' * 1000,  # Very long
                '../../../etc/passwd',  # Path traversal
                '\x00' * 10,  # Null bytes
            ])
            return self.encode_connect(client_id)

        elif strategy == 'fuzz_publish':
            topic = random.choice([
                'test/topic',
                '',  # Empty topic
                '//' * 50,  # Many slashes
                'A' * 1000,  # Long topic
                '$SYS/broker/config',  # System topic
            ])
            payload = bytes([random.randint(0, 255) for _ in range(random.randint(0, 1000))])
            qos = random.choice([0, 1, 2, 3])  # 3 is invalid
            return self.encode_publish(topic, payload, qos)

        elif strategy == 'fuzz_subscribe':
            # Simplified subscribe packet
            packet_type = MQTTPacketType.SUBSCRIBE.value << 4 | 0x02
            topic = b'\x00\x04test'
            qos = bytes([random.choice([0, 1, 2, 3])])
            remaining = len(topic) + len(qos) + 2  # +2 for packet ID
            packet_id = struct.pack('>H', random.randint(1, 0xFFFF))
            return bytes([packet_type, remaining]) + packet_id + topic + qos

        else:  # fuzz_malformed
            return bytes([random.randint(0, 255) for _ in range(random.randint(1, 256))])


# ============================================================================
# HTTP/2 Protocol Fuzzer
# ============================================================================

class HTTP2FrameType(Enum):
    """HTTP/2 frame types"""
    DATA = 0x0
    HEADERS = 0x1
    PRIORITY = 0x2
    RST_STREAM = 0x3
    SETTINGS = 0x4
    PUSH_PROMISE = 0x5
    PING = 0x6
    GOAWAY = 0x7
    WINDOW_UPDATE = 0x8
    CONTINUATION = 0x9


@dataclass
class HTTP2Frame:
    """HTTP/2 frame structure"""
    length: int = 0
    frame_type: HTTP2FrameType = HTTP2FrameType.HEADERS
    flags: int = 0
    stream_id: int = 1
    payload: bytes = b''


class HTTP2Fuzzer:
    """
    HTTP/2 Protocol Fuzzer

    Targets HTTP/2 implementations with focus on:
    - Frame header parsing
    - HPACK header compression
    - Stream multiplexing
    - Flow control
    - Settings frame validation
    """

    CONNECTION_PREFACE = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def encode_frame(self, frame: HTTP2Frame) -> bytes:
        """Encode HTTP/2 frame"""
        # 3 bytes length + 1 byte type + 1 byte flags + 4 bytes stream ID
        header = struct.pack(
            '>HBB',
            (frame.length >> 8) & 0xFFFF,
            frame.length & 0xFF,
            frame.frame_type.value
        )
        header += bytes([frame.flags])
        header += struct.pack('>I', frame.stream_id & 0x7FFFFFFF)

        return header + frame.payload

    def fuzz_frame(self, base_frame: Optional[HTTP2Frame] = None) -> bytes:
        """Generate fuzzed HTTP/2 frame"""
        if base_frame is None:
            base_frame = HTTP2Frame()

        strategy = random.choice([
            'fuzz_length',
            'fuzz_type',
            'fuzz_stream_id',
            'fuzz_settings',
            'fuzz_headers',
            'fuzz_priority',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_length':
            # Length field mismatch
            base_frame.payload = bytes([random.randint(0, 255) for _ in range(100)])
            base_frame.length = random.choice([0, 1, 0xFFFFFF, len(base_frame.payload) * 2])

        elif strategy == 'fuzz_type':
            # Invalid frame type
            base_frame.frame_type = HTTP2FrameType(random.randint(0, 15))

        elif strategy == 'fuzz_stream_id':
            # Invalid stream IDs
            base_frame.stream_id = random.choice([
                0,  # Reserved
                1,  # Client-initiated
                2,  # Server-initiated (invalid from client)
                0x7FFFFFFF,  # Max
                0x80000000,  # Reserved bit set
            ])

        elif strategy == 'fuzz_settings':
            # Malformed SETTINGS frame
            base_frame.frame_type = HTTP2FrameType.SETTINGS
            base_frame.stream_id = 0  # Must be 0

            # Invalid settings: ID (2 bytes) + Value (4 bytes)
            num_settings = random.randint(0, 10)
            payload = b''
            for _ in range(num_settings):
                setting_id = random.choice([0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0xFF, 0xFFFF])
                value = random.choice([0, 1, 0x7FFFFFFF, 0xFFFFFFFF])
                payload += struct.pack('>HI', setting_id, value)

            base_frame.payload = payload
            base_frame.length = len(payload)

        elif strategy == 'fuzz_headers':
            # Malformed HEADERS frame
            base_frame.frame_type = HTTP2FrameType.HEADERS
            base_frame.flags = random.choice([0x0, 0x1, 0x4, 0x5, 0x20, 0xFF])
            base_frame.payload = bytes([random.randint(0, 255) for _ in range(random.randint(0, 500))])
            base_frame.length = len(base_frame.payload)

        elif strategy == 'fuzz_priority':
            # PRIORITY frame with invalid values
            base_frame.frame_type = HTTP2FrameType.PRIORITY
            exclusive = random.choice([0, 1])
            dependency = random.randint(0, 0x7FFFFFFF)
            weight = random.randint(0, 255)
            base_frame.payload = struct.pack('>IB', (exclusive << 31) | dependency, weight)
            base_frame.length = 5

        else:  # fuzz_malformed
            return bytes([random.randint(0, 255) for _ in range(random.randint(9, 100))])

        return self.encode_frame(base_frame)

    def fuzz_connection_preface(self) -> bytes:
        """Fuzz HTTP/2 connection preface"""
        return random.choice([
            self.CONNECTION_PREFACE,  # Valid
            b'PRI * HTTP/1.1\r\n\r\n',  # Wrong version
            b'GET / HTTP/2.0\r\n\r\n',  # Wrong method
            b'',  # Empty
            b'A' * 24,  # Same length, wrong content
            self.CONNECTION_PREFACE[:10],  # Truncated
        ])


# ============================================================================
# WebSocket Protocol Fuzzer
# ============================================================================

class WebSocketOpcode(Enum):
    """WebSocket opcodes"""
    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA


@dataclass
class WebSocketFrame:
    """WebSocket frame structure"""
    fin: bool = True
    rsv1: bool = False
    rsv2: bool = False
    rsv3: bool = False
    opcode: WebSocketOpcode = WebSocketOpcode.TEXT
    masked: bool = True
    payload_length: int = 0
    masking_key: bytes = b'\x00\x00\x00\x00'
    payload: bytes = b''


class WebSocketFuzzer:
    """
    WebSocket Protocol Fuzzer

    Targets WebSocket implementations with focus on:
    - Frame header parsing
    - Masking/unmasking
    - Fragmentation
    - Control frame handling
    - Extension negotiation
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def encode_frame(self, frame: WebSocketFrame) -> bytes:
        """Encode WebSocket frame"""
        # First byte: FIN + RSV + Opcode
        first_byte = (
            (1 if frame.fin else 0) << 7 |
            (1 if frame.rsv1 else 0) << 6 |
            (1 if frame.rsv2 else 0) << 5 |
            (1 if frame.rsv3 else 0) << 4 |
            frame.opcode.value
        )

        # Second byte: Mask + Payload length
        payload_len = len(frame.payload)
        masked_bit = 1 if frame.masked else 0

        if payload_len < 126:
            second_byte = (masked_bit << 7) | payload_len
            length_bytes = b''
        elif payload_len < 65536:
            second_byte = (masked_bit << 7) | 126
            length_bytes = struct.pack('>H', payload_len)
        else:
            second_byte = (masked_bit << 7) | 127
            length_bytes = struct.pack('>Q', payload_len)

        packet = bytes([first_byte, second_byte]) + length_bytes

        # Add masking key and masked payload
        if frame.masked:
            packet += frame.masking_key
            masked_payload = bytes([
                frame.payload[i] ^ frame.masking_key[i % 4]
                for i in range(len(frame.payload))
            ])
            packet += masked_payload
        else:
            packet += frame.payload

        return packet

    def fuzz_frame(self, base_frame: Optional[WebSocketFrame] = None) -> bytes:
        """Generate fuzzed WebSocket frame"""
        if base_frame is None:
            base_frame = WebSocketFrame(payload=b'Hello, WebSocket!')

        strategy = random.choice([
            'fuzz_opcode',
            'fuzz_rsv_bits',
            'fuzz_masking',
            'fuzz_length',
            'fuzz_fragmentation',
            'fuzz_control_frame',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_opcode':
            # Invalid opcodes
            base_frame.opcode = WebSocketOpcode(random.choice([0x0, 0x1, 0x2, 0x3, 0x8, 0x9, 0xA, 0xF]))

        elif strategy == 'fuzz_rsv_bits':
            # RSV bits should be 0 unless extension negotiated
            base_frame.rsv1 = random.choice([True, False])
            base_frame.rsv2 = random.choice([True, False])
            base_frame.rsv3 = random.choice([True, False])

        elif strategy == 'fuzz_masking':
            # Client frames must be masked, server frames must not
            base_frame.masked = random.choice([True, False])
            if base_frame.masked:
                base_frame.masking_key = bytes([random.randint(0, 255) for _ in range(4)])

        elif strategy == 'fuzz_length':
            # Length field mismatch
            base_frame.payload = bytes([random.randint(0, 255) for _ in range(random.randint(0, 1000))])

        elif strategy == 'fuzz_fragmentation':
            # Invalid fragmentation
            base_frame.fin = random.choice([True, False])
            base_frame.opcode = random.choice([
                WebSocketOpcode.CONTINUATION,
                WebSocketOpcode.TEXT,
                WebSocketOpcode.BINARY
            ])

        elif strategy == 'fuzz_control_frame':
            # Control frames with invalid properties
            base_frame.opcode = random.choice([
                WebSocketOpcode.CLOSE,
                WebSocketOpcode.PING,
                WebSocketOpcode.PONG
            ])
            base_frame.fin = random.choice([True, False])  # Control frames must have FIN=1
            base_frame.payload = bytes([random.randint(0, 255) for _ in range(random.randint(0, 200))])  # Max 125

        else:  # fuzz_malformed
            return bytes([random.randint(0, 255) for _ in range(random.randint(2, 100))])

        return self.encode_frame(base_frame)


# ============================================================================
# DNS Protocol Fuzzer
# ============================================================================

class DNSFuzzer:
    """
    DNS Protocol Fuzzer

    Targets DNS implementations with focus on:
    - Query/response parsing
    - Name compression
    - Resource record handling
    - DNSSEC validation
    - Buffer overflow in name parsing
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def encode_dns_query(self, domain: str, qtype: int = 1, qclass: int = 1) -> bytes:
        """Encode DNS query packet"""
        # Header: ID (2) + Flags (2) + QDCOUNT (2) + ANCOUNT (2) + NSCOUNT (2) + ARCOUNT (2)
        transaction_id = random.randint(0, 0xFFFF)
        flags = 0x0100  # Standard query, recursion desired

        header = struct.pack(
            '>HHHHHH',
            transaction_id,
            flags,
            1,  # QDCOUNT: 1 question
            0,  # ANCOUNT: 0 answers
            0,  # NSCOUNT: 0 authority records
            0   # ARCOUNT: 0 additional records
        )

        # Question section: QNAME + QTYPE + QCLASS
        qname = self._encode_domain_name(domain)
        question = qname + struct.pack('>HH', qtype, qclass)

        return header + question

    def _encode_domain_name(self, domain: str) -> bytes:
        """Encode domain name in DNS format"""
        encoded = b''
        for label in domain.split('.'):
            label_bytes = label.encode('utf-8')
            encoded += bytes([len(label_bytes)]) + label_bytes
        encoded += b'\x00'  # Root label
        return encoded

    def fuzz_dns_query(self) -> bytes:
        """Generate fuzzed DNS query"""
        strategy = random.choice([
            'fuzz_domain_name',
            'fuzz_query_type',
            'fuzz_header_flags',
            'fuzz_compression',
            'fuzz_malformed',
        ])

        if strategy == 'fuzz_domain_name':
            # Various malformed domain names
            domain = random.choice([
                'example.com',  # Normal
                '.' * 255,  # Max length
                'A' * 63 + '.com',  # Max label length
                'A' * 64 + '.com',  # Over max label length
                '../../../etc/passwd',  # Path traversal
                '',  # Empty
                'test..com',  # Empty label
                '\x00\x00\x00',  # Null bytes
            ])
            return self.encode_dns_query(domain)

        elif strategy == 'fuzz_query_type':
            # Invalid or uncommon query types
            qtype = random.choice([
                1,    # A
                28,   # AAAA
                255,  # ANY
                0,    # Invalid
                65535,  # Max
            ])
            return self.encode_dns_query('example.com', qtype=qtype)

        elif strategy == 'fuzz_header_flags':
            # Malformed header
            packet = self.encode_dns_query('example.com')
            # Corrupt flags field
            packet = packet[:2] + bytes([random.randint(0, 255), random.randint(0, 255)]) + packet[4:]
            return packet

        elif strategy == 'fuzz_compression':
            # DNS name compression pointer abuse
            packet = self.encode_dns_query('example.com')
            # Add compression pointer pointing to itself or invalid offset
            packet += bytes([0xC0, random.choice([0x00, 0x0C, 0xFF])])
            return packet

        else:  # fuzz_malformed
            return bytes([random.randint(0, 255) for _ in range(random.randint(12, 512))])


# ============================================================================
# Protocol Fuzzer Factory
# ============================================================================

class ProtocolFuzzerFactory:
    """Factory for creating protocol-specific fuzzers"""

    @staticmethod
    def create_fuzzer(protocol: str) -> Any:
        """
        Create fuzzer for specified protocol

        Args:
            protocol: Protocol name ('coap', 'modbus_tcp', 'modbus_rtu', 'mqtt',
                                    'http2', 'websocket', 'dns')

        Returns:
            Protocol-specific fuzzer instance
        """
        fuzzers = {
            'coap': CoAPFuzzer,
            'modbus_tcp': lambda: ModbusFuzzer('tcp'),
            'modbus_rtu': lambda: ModbusFuzzer('rtu'),
            'mqtt': MQTTFuzzer,
            'http2': HTTP2Fuzzer,
            'websocket': WebSocketFuzzer,
            'dns': DNSFuzzer,
        }

        fuzzer_class = fuzzers.get(protocol.lower())
        if fuzzer_class is None:
            raise ValueError(f"Unknown protocol: {protocol}")

        return fuzzer_class() if callable(fuzzer_class) else fuzzer_class

    @staticmethod
    def list_protocols() -> List[str]:
        """List all supported protocols"""
        return ['coap', 'modbus_tcp', 'modbus_rtu', 'mqtt', 'http2', 'websocket', 'dns']


# ============================================================================
# Testing
# ============================================================================

def test_protocol_fuzzers():
    """Test protocol fuzzers"""
    print("="*70)
    print("PROTOCOL FUZZER TESTS")
    print("="*70)

    # Test CoAP
    print("\n[CoAP Fuzzer]")
    coap = CoAPFuzzer()
    for i in range(5):
        fuzzed = coap.fuzz_message()
        print(f"  Fuzzed message {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test Modbus TCP
    print("\n[Modbus TCP Fuzzer]")
    modbus_tcp = ModbusFuzzer('tcp')
    for i in range(5):
        fuzzed = modbus_tcp.fuzz_request()
        print(f"  Fuzzed request {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test Modbus RTU
    print("\n[Modbus RTU Fuzzer]")
    modbus_rtu = ModbusFuzzer('rtu')
    for i in range(5):
        fuzzed = modbus_rtu.fuzz_request()
        print(f"  Fuzzed request {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test MQTT
    print("\n[MQTT Fuzzer]")
    mqtt = MQTTFuzzer()
    for i in range(5):
        fuzzed = mqtt.fuzz_mqtt()
        print(f"  Fuzzed packet {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test HTTP/2
    print("\n[HTTP/2 Fuzzer]")
    http2 = HTTP2Fuzzer()
    for i in range(5):
        fuzzed = http2.fuzz_frame()
        print(f"  Fuzzed frame {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test WebSocket
    print("\n[WebSocket Fuzzer]")
    websocket = WebSocketFuzzer()
    for i in range(5):
        fuzzed = websocket.fuzz_frame()
        print(f"  Fuzzed frame {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test DNS
    print("\n[DNS Fuzzer]")
    dns = DNSFuzzer()
    for i in range(5):
        fuzzed = dns.fuzz_dns_query()
        print(f"  Fuzzed query {i+1}: {len(fuzzed)} bytes - {fuzzed[:20].hex()}...")

    # Test Factory
    print("\n[Protocol Factory]")
    print(f"  Supported protocols: {', '.join(ProtocolFuzzerFactory.list_protocols())}")
    for protocol in ['coap', 'mqtt', 'http2']:
        fuzzer = ProtocolFuzzerFactory.create_fuzzer(protocol)
        print(f"  Created {protocol} fuzzer: {type(fuzzer).__name__}")

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)


if __name__ == "__main__":
    test_protocol_fuzzers()
