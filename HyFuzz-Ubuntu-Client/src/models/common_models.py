"""Common shared models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Target:
    host: str
    port: int
    protocol: str


if __name__ == "__main__":
    print(Target(host="127.0.0.1", port=5683, protocol="coap"))
