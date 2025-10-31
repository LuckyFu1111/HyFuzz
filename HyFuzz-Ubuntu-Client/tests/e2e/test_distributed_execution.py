from src.scheduling.campaign_manager import CampaignManager
from src.scheduling.scheduling_models import CampaignPlan


def test_distributed_execution_planning():
    manager = CampaignManager()
    plan_names = manager.plan([CampaignPlan(name="campaign", targets=2)])
    assert plan_names == ["campaign"]
