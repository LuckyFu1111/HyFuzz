"""Statistical reporting."""
from __future__ import annotations

from typing import Dict


class StatisticsReporter:
    def summarise(self, metrics: Dict[str, float]) -> Dict[str, float]:
        return metrics


if __name__ == "__main__":
    reporter = StatisticsReporter()
    print(reporter.summarise({"coverage": 0.8}))
