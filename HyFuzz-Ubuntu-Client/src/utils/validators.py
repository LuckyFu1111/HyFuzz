"""Common validation helpers."""
from __future__ import annotations

from typing import Iterable

from .exceptions import ProtocolNotSupported


def ensure_supported(protocol: str, supported: Iterable[str]) -> str:
    if protocol not in supported:
        raise ProtocolNotSupported(f"Protocol '{protocol}' is not enabled")
    return protocol


if __name__ == "__main__":
    print(ensure_supported("coap", ["coap", "modbus"]))
