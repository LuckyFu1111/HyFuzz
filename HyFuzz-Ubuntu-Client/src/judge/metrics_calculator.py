"""Calculate judgement metrics."""
from __future__ import annotations

from typing import Dict


class MetricsCalculator:
    def calculate(self, result: Dict[str, str]) -> float:
        return 1.0 if result.get("status", "ok") == "ok" else 0.0


if __name__ == "__main__":
    calculator = MetricsCalculator()
    print(calculator.calculate({"status": "ok"}))
