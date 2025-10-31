"""Coverage report builder."""
from __future__ import annotations

from typing import Dict


class CoverageReport:
    def build(self, coverage: Dict[str, float]) -> str:
        return "\n".join(f"{k}: {v}" for k, v in coverage.items())


if __name__ == "__main__":
    report = CoverageReport()
    print(report.build({"blocks": 10.0}))
