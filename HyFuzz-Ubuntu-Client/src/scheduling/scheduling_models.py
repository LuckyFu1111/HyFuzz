"""Scheduling models."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CampaignPlan:
    name: str
    targets: int


if __name__ == "__main__":
    print(CampaignPlan(name="demo", targets=2))
