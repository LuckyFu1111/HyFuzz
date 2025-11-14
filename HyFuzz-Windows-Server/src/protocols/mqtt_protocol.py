"""
MQTT Protocol Handler for HyFuzz

This module implements the MQTT protocol handler for fuzzing IoT messaging
systems. MQTT is a lightweight publish-subscribe messaging protocol widely
used in IoT, mobile applications, and real-time systems.

Key Features:
- MQTT 3.1.1 and 5.0 support
- Publish/subscribe message fuzzing
- Topic hierarchy manipulation
- QoS level testing (0, 1, 2)
- Retained message handling
- Will message fuzzing
- Authentication payload testing

Protocol Overview:
    MQTT is a pub-sub messaging protocol for IoT:
    - Transport: TCP (default port 1883, TLS on 8883)
    - Message Types: CONNECT, PUBLISH, SUBSCRIBE, etc.
    - QoS Levels: 0 (at most once), 1 (at least once), 2 (exactly once)
    - Topic Hierarchy: slash-separated (e.g., "home/sensors/temp")
    - Retained Messages: Last message cached by broker
    - Will Messages: Sent when client disconnects unexpectedly

Fuzzing Targets:
- MQTT brokers (Mosquitto, HiveMQ, EMQ X)
- IoT device MQTT clients
- Mobile app MQTT implementations
- Smart home systems
- Industrial IoT platforms
- Real-time messaging systems

Common Vulnerabilities:
- CWE-306: Missing or weak authentication
- CWE-862: Missing authorization (topic ACLs)
- CWE-400: Resource exhaustion (topic bomb, message flood)
- CWE-770: Retained message DoS
- CWE-119: Buffer overflow in topic/payload parsing
- CWE-20: Invalid UTF-8 in topics
- CWE-319: Cleartext transmission (no TLS)

QoS Levels:
    - QoS 0: Fire and forget (no acknowledgment)
    - QoS 1: Acknowledged delivery (may duplicate)
    - QoS 2: Exactly once delivery (4-way handshake)

Topic Wildcards:
    - '+': Single-level wildcard (e.g., "sensor/+/temp")
    - '#': Multi-level wildcard (e.g., "sensor/#")

Example Usage:
    >>> handler = MQTTProtocolHandler()
    >>> context = ProtocolContext(target="mqtt://broker.local:1883")
    >>>
    >>> # Publish message to topic
    >>> payload = {
    ...     "topic": "home/livingroom/temperature",
    ...     "qos": 1,
    ...     "retain": False,
    ...     "payload": {"temp": 22.5}
    ... }
    >>> request = handler.prepare_request(context, payload)
    >>>
    >>> # Subscribe to topic pattern
    >>> payload = {
    ...     "topic": "home/+/temperature",
    ...     "qos": 2
    ... }
    >>> request = handler.prepare_request(context, payload)

Security Considerations:
    - Many MQTT deployments lack authentication
    - Topic-based access control often misconfigured
    - Wildcard subscriptions can leak sensitive data
    - Retained messages persist on broker
    - Will messages can be abused for DoS

Author: HyFuzz Team
Version: 1.0.0
Protocol: MQTT 3.1.1 / 5.0
"""

from __future__ import annotations

from typing import Any, Dict

from .base_protocol import BaseProtocolHandler, ProtocolContext


class MQTTProtocolHandler(BaseProtocolHandler):
    """
    MQTT Protocol Handler for IoT messaging fuzzing.

    This handler implements MQTT message construction and validation for
    fuzzing IoT messaging systems and brokers. Supports publish/subscribe
    operations with multiple QoS levels.

    Attributes:
        name: Protocol identifier ("mqtt")

    Protocol Details:
        - Transport: TCP (port 1883) or TLS (port 8883)
        - Message Types: CONNECT, PUBLISH, SUBSCRIBE, UNSUBSCRIBE, PING
        - QoS: 0 (at most once), 1 (at least once), 2 (exactly once)
        - Topics: UTF-8 strings with '/' hierarchy
        - Wildcards: '+' (single level), '#' (multi-level)

    Common Attack Vectors:
        - Topic injection with wildcards
        - Oversized payloads
        - Invalid UTF-8 sequences
        - QoS exhaustion attacks
        - Retained message bombs
    """

    name = "mqtt"

    def prepare_request(
        self,
        context: ProtocolContext,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare an MQTT request from the given payload.

        Constructs an MQTT PUBLISH or SUBSCRIBE message with topic,
        QoS level, and optional flags.

        Args:
            context: Protocol context with broker information
            payload: Payload dictionary containing:
                - topic (str): MQTT topic (e.g., "home/temp")
                - qos (int): Quality of Service (0, 1, or 2)
                - retain (bool): Retain flag for PUBLISH
                - payload (Any): Message payload
                - dup (bool): Duplicate flag

        Returns:
            Dict containing the prepared MQTT request:
                - topic: MQTT topic string
                - qos: Quality of Service level
                - Additional fields from base handler

        Example:
            >>> handler = MQTTProtocolHandler()
            >>> ctx = ProtocolContext(target="mqtt://broker.local")
            >>>
            >>> # Publish temperature reading
            >>> req = handler.prepare_request(ctx, {
            ...     "topic": "sensors/temperature",
            ...     "qos": 1,
            ...     "retain": True,
            ...     "payload": {"value": 25.5, "unit": "C"}
            ... })
            >>>
            >>> # Subscribe with wildcard
            >>> req = handler.prepare_request(ctx, {
            ...     "topic": "sensors/+/alert",
            ...     "qos": 2
            ... })
        """
        # Get base request from parent handler
        request = super().prepare_request(context, payload)

        # Add MQTT-specific fields
        request["topic"] = payload.get("topic", "test/topic")
        request["qos"] = payload.get("qos", 0)

        # Add optional MQTT flags
        if "retain" in payload:
            request["retain"] = payload["retain"]
        if "dup" in payload:
            request["dup"] = payload["dup"]

        return request

    def validate(self, payload: Dict[str, Any]) -> bool:
        """
        Validate an MQTT payload.

        Ensures the payload contains the minimum required fields for a
        valid MQTT message (topic).

        Args:
            payload: Payload dictionary to validate

        Returns:
            True if payload is valid, False otherwise

        Validation Rules:
            - Must contain a "topic" field
            - Topic should be valid UTF-8 string
            - QoS is optional (defaults to 0)
            - Additional validation performed at execution time

        Example:
            >>> handler = MQTTProtocolHandler()
            >>> handler.validate({"topic": "sensors/temp"})
            True
            >>> handler.validate({"qos": 1})  # Missing topic
            False
        """
        return "topic" in payload


if __name__ == "__main__":
    handler = MQTTProtocolHandler()
    ctx = ProtocolContext(target="mqtt://broker")
    print(handler.prepare_request(ctx, {"topic": "alerts"}))
    print("Valid:", handler.validate({"topic": "alerts"}))
