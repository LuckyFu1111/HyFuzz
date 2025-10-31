"""Metric helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Metric:
    name: str
    value: float
    unit: str = ""


class MetricStore:
    def __init__(self) -> None:
        self._metrics: List[Metric] = []

    def add(self, metric: Metric) -> None:
        self._metrics.append(metric)

    def as_dict(self) -> Dict[str, float]:
        return {metric.name: metric.value for metric in self._metrics}


if __name__ == "__main__":
    store = MetricStore()
    store.add(Metric("cpu", 0.5, "%"))
    print(store.as_dict())
