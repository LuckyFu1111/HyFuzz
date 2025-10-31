"""Runtime monitoring stub."""
from __future__ import annotations

from ..utils.logger import get_logger


class RuntimeMonitor:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self._active = False

    def start(self) -> None:
        self._active = True
        self.logger.info("Runtime monitor started")

    def stop(self) -> None:
        if self._active:
            self.logger.info("Runtime monitor stopped")
        self._active = False


if __name__ == "__main__":
    monitor = RuntimeMonitor()
    monitor.start()
    monitor.stop()
