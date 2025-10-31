"""Payload related models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class Payload:
    protocol: str
    content: bytes
    metadata: Dict[str, str]


if __name__ == "__main__":
    payload = Payload(protocol="coap", content=b"ping", metadata={"id": "demo"})
    print(payload)
