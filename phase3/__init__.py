"""Phase 3 coordination helpers bridging the server and client stacks."""

from .coordinator import (
    CampaignTarget,
    ExecutionDetail,
    Phase3Coordinator,
    Phase3RunSummary,
)

__all__ = [
    "CampaignTarget",
    "ExecutionDetail",
    "Phase3Coordinator",
    "Phase3RunSummary",
]


if __name__ == "__main__":  # pragma: no cover - smoke test
    coordinator = Phase3Coordinator()
    summary = coordinator.run_campaign(
        [
            CampaignTarget(name="demo-coap", protocol="coap", endpoint="coap://localhost"),
            CampaignTarget(name="demo-modbus", protocol="modbus", endpoint="modbus://localhost"),
        ]
    )
    print(summary.to_dict())
