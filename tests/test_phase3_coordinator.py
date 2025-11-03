"""Integration-style tests for the Phase 3 coordinator."""

from __future__ import annotations

import json

from phase3 import CampaignTarget, Phase3Coordinator


def test_phase3_coordinator_generates_feedback() -> None:
    coordinator = Phase3Coordinator(model_name="mistral-test")
    summary = coordinator.run_campaign(
        [
            CampaignTarget(name="target-coap", protocol="coap", endpoint="coap://demo"),
            CampaignTarget(name="target-modbus", protocol="modbus", endpoint="modbus://demo"),
        ]
    )

    assert len(summary.executions) == 2
    assert summary.feedback_history
    breakdown = summary.verdict_breakdown()
    assert sum(breakdown.values()) == len(summary.executions)
    assert summary.average_judgment_score() >= 0.0

    for detail in summary.executions:
        assert detail.payload.startswith("mistral-test")
        assert detail.execution.payload_id == detail.request_id
        assert detail.execution.output
        assert detail.judgment.score >= 0.0
        assert detail.defense is not None
        verdict = detail.defense.verdict
        assert verdict in {"monitor", "investigate", "block", "escalate"}

        template = json.loads(detail.request_parameters["payload_template"])
        assert template["target"] == detail.target.endpoint
        if detail.target.protocol == "coap":
            assert template["method"] == "GET"
            assert template["path"].startswith("/")
        if detail.target.protocol == "modbus":
            assert int(template["function_code"]) == 3
            assert int(template["count"]) == 1


if __name__ == "__main__":  # pragma: no cover - smoke run
    import pytest

    pytest.main([__file__])
