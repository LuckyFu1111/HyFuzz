"""STDIO transport mock."""
from __future__ import annotations

from typing import Dict


def send(message: bytes) -> Dict[str, str]:
    return {"stdio": message.decode("utf-8")}


if __name__ == "__main__":
    print(send(b"hello"))
