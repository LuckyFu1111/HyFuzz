"""Feedback models for adaptive fuzzing."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeedbackSignal:
    payload_id: str
    score: float
    notes: str


if __name__ == "__main__":
    print(FeedbackSignal(payload_id="1", score=0.9, notes="High impact"))
