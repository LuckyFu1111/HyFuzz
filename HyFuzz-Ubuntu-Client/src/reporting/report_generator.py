"""Generate structured reports."""
from __future__ import annotations

from typing import Iterable, List


class ReportGenerator:
    def build_summary(self, results: Iterable[dict[str, str]]) -> List[dict[str, str]]:
        return [dict(result) for result in results]


if __name__ == "__main__":
    generator = ReportGenerator()
    print(generator.build_summary([{ "payload_id": "1", "status": "ok" }]))
