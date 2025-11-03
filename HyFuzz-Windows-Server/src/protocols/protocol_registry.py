"""Registry that keeps track of supported protocol handlers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Type

from .base_protocol import ProtocolHandler, ProtocolSpec
from .coap_protocol import CoAPProtocolHandler
from .modbus_protocol import ModbusProtocolHandler
from .mqtt_protocol import MQTTProtocolHandler
from .http_protocol import HTTPProtocolHandler
from .grpc_protocol import GRPCProtocolHandler
from .jsonrpc_protocol import JSONRPCProtocolHandler


@dataclass(frozen=True)
class ProtocolRegistration:
    """Container for registered protocol handlers."""

    handler_cls: Type[ProtocolHandler]
    spec: ProtocolSpec


class ProtocolRegistry:
    """Registry mapping protocol identifiers to handlers."""

    def __init__(self) -> None:
        self._registry: Dict[str, ProtocolRegistration] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("coap", CoAPProtocolHandler)
        self.register("modbus", ModbusProtocolHandler)
        self.register("mqtt", MQTTProtocolHandler)
        self.register("http", HTTPProtocolHandler)
        self.register("grpc", GRPCProtocolHandler)
        self.register("jsonrpc", JSONRPCProtocolHandler)

    def register(
        self, name: str, handler_cls: Type[ProtocolHandler], spec: ProtocolSpec | None = None
    ) -> None:
        handler_spec = spec or handler_cls().get_spec()
        self._registry[name] = ProtocolRegistration(handler_cls=handler_cls, spec=handler_spec)

    def get(self, name: str) -> Type[ProtocolHandler]:
        if name not in self._registry:
            raise KeyError(f"Protocol '{name}' is not registered")
        return self._registry[name].handler_cls

    def describe(self, name: str) -> ProtocolSpec:
        if name not in self._registry:
            raise KeyError(f"Protocol '{name}' is not registered")
        return self._registry[name].spec

    def available_protocols(self) -> Dict[str, Type[ProtocolHandler]]:
        return {name: registration.handler_cls for name, registration in self._registry.items()}

    def protocol_specs(self) -> Dict[str, ProtocolSpec]:
        return {name: registration.spec for name, registration in self._registry.items()}


if __name__ == "__main__":
    registry = ProtocolRegistry()
    print(sorted(registry.protocol_specs()))
