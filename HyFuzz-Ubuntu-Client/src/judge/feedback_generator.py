"""Generate textual feedback."""
from __future__ import annotations


class FeedbackGenerator:
    def generate(self, score: float) -> str:
        return "Great job" if score > 0.5 else "Needs improvement"


if __name__ == "__main__":
    generator = FeedbackGenerator()
    print(generator.generate(1.0))
