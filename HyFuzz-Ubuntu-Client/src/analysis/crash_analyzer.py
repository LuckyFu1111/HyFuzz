"""Crash analysis logic."""
from __future__ import annotations

from .analysis_models import CrashAnalysis
from .backtrace_parser import BacktraceParser
from .exploitability_checker import ExploitabilityChecker


class CrashAnalyzer:
    def __init__(self) -> None:
        self.backtrace = BacktraceParser()
        self.exploitability = ExploitabilityChecker()

    def analyse(self, payload_id: str, trace: str) -> CrashAnalysis:
        frames = self.backtrace.parse(trace)
        exploitable = self.exploitability.check(frames)
        return CrashAnalysis(payload_id=payload_id, stack_trace=frames, exploitable=exploitable)


if __name__ == "__main__":
    analyzer = CrashAnalyzer()
    print(analyzer.analyse("1", "main->foo->bar"))
