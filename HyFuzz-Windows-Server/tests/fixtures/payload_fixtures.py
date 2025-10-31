"""Reusable payload fixtures for HyFuzz server tests."""
from __future__ import annotations

from typing import Iterable, List

from . import TestPayload, get_sample_payloads


def all_payloads() -> List[TestPayload]:
    """Return all sample payloads defined for the test-suite."""
    return list(get_sample_payloads())


def filter_by_protocol(protocol: str) -> List[TestPayload]:
    """Return payloads that target the provided protocol."""
    normalized = protocol.lower().strip()
    return [payload for payload in get_sample_payloads() if payload.protocol == normalized]


def ids() -> Iterable[str]:
    """Yield identifiers of all payload samples."""
    for payload in get_sample_payloads():
        yield payload.id


if __name__ == "__main__":  # pragma: no cover - developer smoke test
    print("Payload identifiers:", ", ".join(ids()))
    for proto in {p.protocol for p in all_payloads()}:
        print(f"Protocol {proto}: {len(filter_by_protocol(proto))} payload(s)")
