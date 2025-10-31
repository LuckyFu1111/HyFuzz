"""Validates protocol payloads."""
from __future__ import annotations

from ..utils.validators import ensure_supported


def validate(protocol: str, supported: list[str]) -> str:
    return ensure_supported(protocol, supported)


if __name__ == "__main__":
    print(validate("coap", ["coap", "modbus"]))
