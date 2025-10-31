"""Execution helpers."""
from __future__ import annotations

from typing import Iterable

from ..models.execution_models import ExecutionRequest


def build_requests(payload_ids: Iterable[str], protocol: str) -> list[ExecutionRequest]:
    return [ExecutionRequest(payload_id=pid, protocol=protocol) for pid in payload_ids]


if __name__ == "__main__":
    print(build_requests(["1", "2"], "coap"))
