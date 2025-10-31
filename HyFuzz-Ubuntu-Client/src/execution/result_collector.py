"""Collects execution results."""
from __future__ import annotations

from typing import List

from ..models.execution_models import ExecutionResult


class ResultCollector:
    def __init__(self) -> None:
        self._results: List[ExecutionResult] = []

    def store(self, result: ExecutionResult) -> None:
        self._results.append(result)

    def all(self) -> List[ExecutionResult]:
        return list(self._results)


if __name__ == "__main__":
    collector = ResultCollector()
    collector.store(ExecutionResult(payload_id="1", success=True, output="ok"))
    print(collector.all())
