"""Helper fixtures for exercising the LLM judge pipeline."""
from __future__ import annotations

from typing import Dict, Iterable, List, TypedDict


class JudgeRequest(TypedDict):
    """Simplified judge request payload used in unit tests."""

    payload_id: str
    target_id: str
    signals: List[str]
    metadata: Dict[str, str]


class JudgeResponse(TypedDict):
    """Simplified judge response payload used in unit tests."""

    verdict: str
    confidence: float
    rationale: str


_SAMPLE_REQUESTS: List[JudgeRequest] = [
    JudgeRequest(
        payload_id="payload-xss-http",
        target_id="target-http-1",
        signals=["http_status:200", "defense:passive"],
        metadata={"campaign": "demo"},
    ),
    JudgeRequest(
        payload_id="payload-modbus-read",
        target_id="target-coap-1",
        signals=["modbus_exception:0x04"],
        metadata={"campaign": "demo"},
    ),
]

_SAMPLE_RESPONSES: List[JudgeResponse] = [
    JudgeResponse(verdict="escalate", confidence=0.82, rationale="Defense logs indicated suspicious activity."),
    JudgeResponse(verdict="monitor", confidence=0.55, rationale="Limited evidence of exploitability."),
]


def sample_requests() -> List[JudgeRequest]:
    """Return request samples used in tests."""
    return list(_SAMPLE_REQUESTS)


def sample_responses() -> List[JudgeResponse]:
    """Return response samples used in tests."""
    return list(_SAMPLE_RESPONSES)


def verdicts() -> Iterable[str]:
    """Yield example verdict labels."""
    return (response["verdict"] for response in _SAMPLE_RESPONSES)


if __name__ == "__main__":  # pragma: no cover - sanity harness
    for request, response in zip(sample_requests(), sample_responses(), strict=False):
        print(f"{request['payload_id']} => {response['verdict']} ({response['confidence']:.2f})")
