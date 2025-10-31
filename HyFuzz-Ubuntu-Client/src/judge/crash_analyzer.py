"""Judge crash analyzer wrapper."""
from __future__ import annotations

from ..analysis.crash_analyzer import CrashAnalyzer as CoreCrashAnalyzer


class CrashAnalyzer:
    def __init__(self) -> None:
        self.analyzer = CoreCrashAnalyzer()

    def analyse(self, payload_id: str, trace: str) -> str:
        analysis = self.analyzer.analyse(payload_id, trace)
        return f"frames={len(analysis.stack_trace)}, exploitable={analysis.exploitable}"


if __name__ == "__main__":
    analyzer = CrashAnalyzer()
    print(analyzer.analyse("1", "main"))
