"""Factory for protocol handlers."""
from __future__ import annotations

from typing import Dict, Type

from .base_handler import BaseProtocolHandler
from .coap_handler import CoAPHandler
from .modbus_handler import ModbusHandler
from .mqtt_handler import MQTTHandler
from .http_handler import HTTPHandler
from .grpc_handler import GRPCHandler

_HANDLERS: Dict[str, Type[BaseProtocolHandler]] = {
    handler.name: handler
    for handler in (CoAPHandler, ModbusHandler, MQTTHandler, HTTPHandler, GRPCHandler)
}
_CAPABILITIES = {
    name: handler().get_capabilities() for name, handler in _HANDLERS.items()
}


def get_handler(protocol: str) -> BaseProtocolHandler:
    handler_cls = _HANDLERS.get(protocol)
    if handler_cls is None:
        raise ValueError(f"Unsupported protocol: {protocol}")
    return handler_cls()


def get_capabilities(protocol: str):
    if protocol not in _CAPABILITIES:
        raise ValueError(f"Unsupported protocol: {protocol}")
    return _CAPABILITIES[protocol]


def available_capabilities():
    return dict(_CAPABILITIES)


if __name__ == "__main__":
    print(get_handler("coap").name)
