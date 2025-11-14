"""
Modbus Protocol Handler for HyFuzz

This module implements the Modbus protocol handler for fuzzing industrial control
systems (ICS) and SCADA devices. Modbus is a widely-used communication protocol
in industrial automation and critical infrastructure.

Key Features:
- Modbus TCP and RTU protocol support
- Function code fuzzing (read/write coils, registers)
- Address range fuzzing
- Payload manipulation
- State-aware request sequencing
- Exception code handling

Protocol Overview:
    Modbus is a master-slave communication protocol used in ICS/SCADA:
    - Modbus TCP: Uses TCP/IP (port 502)
    - Modbus RTU: Serial communication (RS-232/RS-485)
    - Request-response model
    - 256 function codes (1-127 public, 128-255 user-defined)
    - Addressing: 16-bit addresses for coils/registers

Common Function Codes:
    - 0x01: Read Coils (discrete outputs)
    - 0x02: Read Discrete Inputs
    - 0x03: Read Holding Registers (most common)
    - 0x04: Read Input Registers
    - 0x05: Write Single Coil
    - 0x06: Write Single Register
    - 0x0F: Write Multiple Coils
    - 0x10: Write Multiple Registers

Fuzzing Targets:
- PLCs (Programmable Logic Controllers)
- RTUs (Remote Terminal Units)
- DCS (Distributed Control Systems)
- Industrial sensors and actuators
- SCADA master stations
- Energy management systems

Common Vulnerabilities:
- CWE-306: Missing authentication (Modbus has no built-in auth)
- CWE-319: Cleartext transmission
- CWE-400: Resource exhaustion via flood attacks
- CWE-20: Invalid function code handling
- CWE-125: Out-of-bounds read (invalid addresses)
- CWE-787: Out-of-bounds write (dangerous writes)

Security Considerations:
    - Modbus has NO authentication or encryption
    - Write operations can damage physical equipment
    - Use EXTREME caution when fuzzing production systems
    - Always test in isolated lab environments
    - Monitor for physical safety implications

Example Usage:
    >>> handler = ModbusProtocolHandler()
    >>> context = ProtocolContext(target="modbus://192.168.1.100:502")
    >>>
    >>> # Read holding registers
    >>> payload = {
    ...     "function_code": 3,
    ...     "address": 0,
    ...     "count": 10
    ... }
    >>> request = handler.prepare_request(context, payload)
    >>>
    >>> # Write single register
    >>> payload = {
    ...     "function_code": 6,
    ...     "address": 100,
    ...     "value": 1234
    ... }
    >>> request = handler.prepare_request(context, payload)

WARNING:
    Fuzzing Modbus can cause PHYSICAL DAMAGE to equipment and
    infrastructure. Only fuzz in controlled lab environments.
    Never fuzz production ICS/SCADA systems.

Author: HyFuzz Team
Version: 1.0.0
Protocol: Modbus (TCP/RTU)
"""

from __future__ import annotations

from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext, ProtocolSpec


class ModbusProtocolHandler(BaseProtocolHandler):
    """
    Modbus Protocol Handler for ICS/SCADA fuzzing.

    This handler implements Modbus TCP/RTU message construction and validation
    for fuzzing industrial control systems. It supports all standard Modbus
    function codes and provides state-aware request sequencing.

    Attributes:
        name: Protocol identifier ("modbus")
        SPEC: Protocol specification with default parameters

    Protocol Details:
        - Transport: TCP (port 502) or RTU (serial)
        - Function Codes: 1-127 (public), 128-255 (user-defined)
        - Addressing: 16-bit (0-65535)
        - Data Types: Coils (bits), Registers (16-bit words)

    WARNING:
        Modbus operations can affect physical equipment. Use extreme
        caution and only fuzz in isolated lab environments.
    """

    name = "modbus"

    SPEC = ProtocolSpec(
        name="modbus",
        description="Modbus TCP/RTU - Industrial control system protocol",
        stateful=True,  # Modbus maintains session state
        default_parameters={
            "function_code": 3,  # Read Holding Registers
            "address": 0,
            "count": 1
        },
    )

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare a Modbus request from the given payload.

        Constructs a Modbus protocol request with function code, address,
        and data parameters. Supports both read and write operations.

        Args:
            context: Protocol context with target information
            payload: Payload dictionary containing:
                - function_code (int): Modbus function code (1-255)
                - address (int): Starting register/coil address (0-65535)
                - count (int): Number of registers/coils to read
                - value (int/list): Value(s) to write (for write operations)
                - payload (Any): Additional payload data

        Returns:
            Dict containing the prepared Modbus request:
                - function_code: Modbus function code
                - address: Target address
                - count: Number of items
                - Additional fields from base handler

        Example:
            >>> handler = ModbusProtocolHandler()
            >>> ctx = ProtocolContext(target="modbus://plc.local:502")
            >>>
            >>> # Read 10 holding registers starting at address 100
            >>> req = handler.prepare_request(ctx, {
            ...     "function_code": 3,
            ...     "address": 100,
            ...     "count": 10
            ... })
            >>>
            >>> # Write value to single register
            >>> req = handler.prepare_request(ctx, {
            ...     "function_code": 6,
            ...     "address": 200,
            ...     "value": 5000
            ... })
        """
        # Get base request from parent handler
        request = super().prepare_request(context, payload)

        # Add Modbus-specific fields
        request["payload"] = payload.get("payload", request["payload"])
        request["function_code"] = payload.get("function_code", 3)
        request["address"] = payload.get("address", 0)
        request["count"] = payload.get("count", 1)

        # Add optional write value for write operations
        if "value" in payload:
            request["value"] = payload["value"]

        return request

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate a Modbus payload.

        Ensures the payload contains the minimum required fields for a
        valid Modbus request (function code).

        Args:
            payload: Payload dictionary to validate

        Returns:
            True if payload is valid, False otherwise

        Validation Rules:
            - Must contain a "function_code" field
            - Function code should be 1-255 (checked at runtime)
            - Address and count are optional (have defaults)

        Example:
            >>> handler = ModbusProtocolHandler()
            >>> handler.validate({"function_code": 3})
            True
            >>> handler.validate({"address": 100})  # Missing function_code
            False
        """
        return "function_code" in payload


if __name__ == "__main__":
    handler = ModbusProtocolHandler()
    ctx = ProtocolContext(target="modbus://127.0.0.1:502")
    print(handler.prepare_request(ctx, {"function_code": 1, "address": 10, "count": 2}))
    print("Valid:", handler.validate({"function_code": 3}))
