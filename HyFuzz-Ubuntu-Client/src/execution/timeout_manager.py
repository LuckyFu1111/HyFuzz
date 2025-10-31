"""Timeout manager."""
from __future__ import annotations

import threading
from typing import Callable


class TimeoutManager:
    def __init__(self, timeout: float) -> None:
        self.timeout = timeout

    def run_with_timeout(self, func: Callable[[], None]) -> bool:
        thread = threading.Thread(target=func, daemon=True)
        thread.start()
        thread.join(self.timeout)
        return not thread.is_alive()


if __name__ == "__main__":
    def slow() -> None:
        import time

        time.sleep(0.1)

    manager = TimeoutManager(0.2)
    print("completed:", manager.run_with_timeout(slow))
