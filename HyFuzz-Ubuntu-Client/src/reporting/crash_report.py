"""Crash report builder."""
from __future__ import annotations

from typing import Dict


class CrashReport:
    def build(self, crash: Dict[str, str]) -> str:
        return f"Crash {crash.get('payload_id')} -> {crash.get('reason')}"


if __name__ == "__main__":
    report = CrashReport()
    print(report.build({"payload_id": "1", "reason": "segfault"}))
