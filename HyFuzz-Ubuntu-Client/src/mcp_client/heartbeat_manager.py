"""Heartbeat tracking."""
from __future__ import annotations

import time


class HeartbeatManager:
    def __init__(self, ttl: float = 5.0) -> None:
        self.ttl = ttl
        self._last = 0.0

    def record(self) -> None:
        self._last = time.monotonic()

    def is_alive(self) -> bool:
        return (time.monotonic() - self._last) < self.ttl


if __name__ == "__main__":
    hb = HeartbeatManager()
    hb.record()
    print("alive:", hb.is_alive())
