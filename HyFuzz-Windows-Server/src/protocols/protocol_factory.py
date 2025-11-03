"""Factory for instantiating protocol handlers."""

from __future__ import annotations

from typing import Dict

from .base_protocol import ProtocolHandler, ProtocolSpec
from .protocol_registry import ProtocolRegistry


class ProtocolFactory:
    """Factory using the :class:`ProtocolRegistry` for instantiation."""

    def __init__(self, registry: ProtocolRegistry) -> None:
        self.registry = registry

    def create(self, name: str) -> ProtocolHandler:
        handler_cls = self.registry.get(name)
        handler: ProtocolHandler = handler_cls()  # type: ignore[call-arg]
        return handler

    def create_all(self) -> Dict[str, ProtocolHandler]:
        return {name: self.create(name) for name in self.registry.available_protocols().keys()}

    def describe(self, name: str) -> ProtocolSpec:
        return self.registry.describe(name)

    def available_specs(self) -> Dict[str, ProtocolSpec]:
        return self.registry.protocol_specs()


if __name__ == "__main__":
    factory = ProtocolFactory(ProtocolRegistry())
    handlers = factory.create_all()
    print({name: handler.name for name, handler in handlers.items()})
