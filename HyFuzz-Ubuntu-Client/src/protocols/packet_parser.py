"""Parses binary packets."""
from __future__ import annotations

from typing import Dict


def parse(packet: bytes) -> Dict[str, int]:
    return {"length": len(packet), "first_byte": packet[0] if packet else -1}


if __name__ == "__main__":
    print(parse(b"abc"))
