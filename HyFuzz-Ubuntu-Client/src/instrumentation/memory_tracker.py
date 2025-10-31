"""Track memory usage via /proc."""
from __future__ import annotations

import os


class MemoryTracker:
    def sample(self) -> float:
        try:
            page_size = os.sysconf("SC_PAGE_SIZE")
            with open("/proc/self/statm", "r", encoding="utf-8") as handle:
                pages = int(handle.readline().split()[0])
            return pages * page_size / (1024 * 1024)
        except (OSError, ValueError, AttributeError):
            return 0.0


if __name__ == "__main__":
    tracker = MemoryTracker()
    print(tracker.sample())
