"""Models for targets."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TargetProfile:
    host: str
    port: int
    protocol: str
    service: str


if __name__ == "__main__":
    print(TargetProfile("localhost", 5683, "coap", "CoAP"))
