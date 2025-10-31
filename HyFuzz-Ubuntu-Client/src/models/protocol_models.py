"""Protocol descriptors."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProtocolDescriptor:
    name: str
    default_port: int
    description: str


if __name__ == "__main__":
    print(ProtocolDescriptor(name="coap", default_port=5683, description="CoAP protocol"))
