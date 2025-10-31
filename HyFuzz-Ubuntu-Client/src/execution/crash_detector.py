"""Detects crashes from execution results."""
from __future__ import annotations

from ..models.execution_models import ExecutionResult
from ..storage.crash_storage import CrashStorage


class CrashDetector:
    def __init__(self) -> None:
        self.storage = CrashStorage()

    def inspect(self, result: ExecutionResult) -> None:
        if not result.success:
            self.storage.save(result.payload_id, result.output)


if __name__ == "__main__":
    detector = CrashDetector()
    detector.inspect(ExecutionResult(payload_id="1", success=False, output="boom"))
    print(detector.storage.list_crashes())
