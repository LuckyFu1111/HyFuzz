"""Metric models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MetricSample:
    name: str
    value: float


if __name__ == "__main__":
    print(MetricSample(name="cpu", value=0.5))
