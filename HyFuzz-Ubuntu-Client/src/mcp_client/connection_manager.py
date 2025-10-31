"""Simplified connection manager."""
from __future__ import annotations

from typing import Dict


class ConnectionManager:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self._connected = False

    def connect(self) -> None:
        self._connected = True

    def send(self, message: bytes) -> Dict[str, str]:
        if not self._connected:
            raise RuntimeError("Not connected")
        return {"endpoint": self.endpoint, "ack": message.decode("utf-8")}


if __name__ == "__main__":
    manager = ConnectionManager("http://localhost")
    manager.connect()
    print(manager.send(b"hello"))
