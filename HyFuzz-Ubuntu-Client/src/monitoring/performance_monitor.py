"""Performance monitoring."""
from __future__ import annotations

import time


class PerformanceMonitor:
    def measure(self, func) -> float:
        start = time.perf_counter()
        func()
        return time.perf_counter() - start


if __name__ == "__main__":
    monitor = PerformanceMonitor()
    print(monitor.measure(lambda: time.sleep(0.01)))
