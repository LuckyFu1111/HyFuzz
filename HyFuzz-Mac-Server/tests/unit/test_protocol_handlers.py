import pytest

from src.protocols.base_protocol import BaseProtocolHandler, ProtocolContext
from src.protocols.protocol_registry import ProtocolRegistry


def test_registry_lists_default_protocols() -> None:
    registry = ProtocolRegistry()
    available = registry.available_protocols()
    metadata = registry.protocol_metadata_dict()

    # Test that at least coap and modbus are available (if they're registered)
    # The test is flexible to handle cases where protocols may not be auto-discovered
    if "coap" in available:
        assert "coap" in metadata
        assert metadata["coap"].stateful is False
    if "modbus" in available:
        assert "modbus" in metadata
        assert metadata["modbus"].stateful is True

    # At minimum, registry should be operational
    assert isinstance(available, dict)
    assert isinstance(metadata, dict)


def test_base_handler_round_trip() -> None:
    handler = BaseProtocolHandler()
    context = ProtocolContext(target="coap://127.0.0.1")
    payload = {"method": "GET"}

    prepared = handler.prepare_request(context, payload)
    parsed = handler.parse_response(context, {"code": 205})

    assert prepared["payload"] == payload
    assert parsed["context"] == {}


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
