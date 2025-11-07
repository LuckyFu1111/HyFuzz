"""
Campaign coordination module for HyFuzz.

This module provides coordination helpers that bridge the server control plane
and client execution agents, enabling distributed fuzzing campaigns across
multiple targets and protocols.
"""

from .coordinator import (
    CampaignTarget,
    ExecutionDetail,
    FuzzingCoordinator,
    CampaignRunSummary,
)

__all__ = [
    "CampaignTarget",
    "ExecutionDetail",
    "FuzzingCoordinator",
    "CampaignRunSummary",
]


if __name__ == "__main__":  # pragma: no cover - smoke test
    coordinator = FuzzingCoordinator()
    summary = coordinator.run_campaign(
        [
            CampaignTarget(name="demo-coap", protocol="coap", endpoint="coap://localhost"),
            CampaignTarget(name="demo-modbus", protocol="modbus", endpoint="modbus://localhost"),
        ]
    )
    print(summary.to_dict())
