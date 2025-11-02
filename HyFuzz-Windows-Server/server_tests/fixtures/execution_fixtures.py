"""Execution result fixtures used across integration server_tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class ExecutionSample:
    """Minimal representation of an execution run used by smoke server_tests."""

    id: str
    payload_id: str
    target_id: str
    verdict: str
    metrics: Dict[str, float]

    def is_success(self) -> bool:
        """Return True when the verdict marks the execution as successful."""
        return self.verdict == "success"


SAMPLES: List[ExecutionSample] = [
    ExecutionSample(
        id="exec-001",
        payload_id="payload-xss-http",
        target_id="target-http-1",
        verdict="success",
        metrics={"latency_ms": 120.5, "coverage": 0.34},
    ),
    ExecutionSample(
        id="exec-002",
        payload_id="payload-modbus-read",
        target_id="target-coap-1",
        verdict="monitor",
        metrics={"latency_ms": 89.2, "coverage": 0.12},
    ),
]


def all_samples() -> List[ExecutionSample]:
    """Return all execution samples."""
    return list(SAMPLES)


def successful_ids() -> Iterable[str]:
    """Yield identifiers of successful executions."""
    return (sample.id for sample in SAMPLES if sample.is_success())


if __name__ == "__main__":  # pragma: no cover - convenience harness
    for sample in all_samples():
        status = "✅" if sample.is_success() else "⚠️"
        print(f"{status} {sample.id} -> {sample.verdict} ({sample.metrics})")
