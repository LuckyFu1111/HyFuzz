"""Target manager orchestrates scanning and profiling."""
from __future__ import annotations

from typing import List

from .target_scanner import TargetScanner
from .target_profiler import TargetProfiler
from .target_models import TargetProfile


class TargetManager:
    def __init__(self) -> None:
        self.scanner = TargetScanner()
        self.profiler = TargetProfiler()

    def discover(self) -> List[TargetProfile]:
        targets = self.scanner.scan()
        return [self.profiler.profile(target) for target in targets]


if __name__ == "__main__":
    manager = TargetManager()
    print(manager.discover())
