from src.protocols.protocol_factory import available_capabilities


def test_available_capabilities_marks_modbus_stateful() -> None:
    capabilities = available_capabilities()
    assert capabilities["modbus"].stateful is True
    assert capabilities["coap"].stateful is False
