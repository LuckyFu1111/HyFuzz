"""Simple scheduler."""
from __future__ import annotations

from typing import Iterable

from .scheduling_models import CampaignPlan


class Scheduler:
    def schedule(self, plans: Iterable[CampaignPlan]) -> list[str]:
        return [plan.name for plan in plans]


if __name__ == "__main__":
    scheduler = Scheduler()
    print(scheduler.schedule([CampaignPlan(name="demo", targets=1)]))
