"""Adaptive tuner."""
from __future__ import annotations


class AdaptiveTuner:
    def tune(self, score: float) -> str:
        return "aggressive" if score < 0.5 else "balanced"


if __name__ == "__main__":
    tuner = AdaptiveTuner()
    print(tuner.tune(0.3))
