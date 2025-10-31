"""LLM-inspired judgement pipeline."""
from __future__ import annotations

from typing import Dict

from .metrics_calculator import MetricsCalculator
from .feedback_generator import FeedbackGenerator
from .adaptive_tuner import AdaptiveTuner
from .coverage_analyzer import CoverageAnalyzer
from .crash_analyzer import CrashAnalyzer


class Judge:
    def __init__(self) -> None:
        self.metrics = MetricsCalculator()
        self.feedback = FeedbackGenerator()
        self.tuner = AdaptiveTuner()
        self.coverage = CoverageAnalyzer()
        self.crashes = CrashAnalyzer()

    def evaluate(self, result: Dict[str, str]) -> Dict[str, str]:
        score = self.metrics.calculate(result)
        feedback = self.feedback.generate(score)
        coverage = self.coverage.analyse(result.get("coverage", ""))
        crash = self.crashes.analyse(result.get("payload_id", ""), result.get("trace", ""))
        tuning = self.tuner.tune(score)
        return {
            "score": str(score),
            "feedback": feedback,
            "coverage": str(coverage),
            "crash": crash,
            "tuning": tuning,
        }


if __name__ == "__main__":
    judge = Judge()
    print(judge.evaluate({"payload_id": "1", "trace": "main", "coverage": "block"}))
