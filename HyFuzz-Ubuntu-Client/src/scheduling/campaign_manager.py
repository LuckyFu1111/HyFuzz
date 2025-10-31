"""Campaign manager orchestrates schedules."""
from __future__ import annotations

from typing import Iterable

from .scheduler import Scheduler
from .scheduling_models import CampaignPlan


class CampaignManager:
    def __init__(self) -> None:
        self.scheduler = Scheduler()

    def plan(self, plans: Iterable[CampaignPlan]) -> list[str]:
        return self.scheduler.schedule(plans)


if __name__ == "__main__":
    manager = CampaignManager()
    print(manager.plan([CampaignPlan(name="demo", targets=1)]))
