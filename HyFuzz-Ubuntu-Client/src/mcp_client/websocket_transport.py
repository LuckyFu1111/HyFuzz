"""WebSocket transport mock."""
from __future__ import annotations

from typing import Dict


def send(message: bytes, endpoint: str) -> Dict[str, str]:
    return {"websocket": endpoint, "body": message.decode("utf-8")}


if __name__ == "__main__":
    print(send(b"hello", "ws://localhost"))
