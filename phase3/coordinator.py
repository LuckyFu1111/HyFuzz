"""High level coordinator that stitches the server and client flows together."""

from __future__ import annotations

import json
import logging
import sys
import types
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Sequence
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Namespace bootstrapping
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_SERVER_SRC = _ROOT / "HyFuzz-Windows-Server" / "src"
_CLIENT_SRC = _ROOT / "HyFuzz-Ubuntu-Client" / "src"


def _ensure_namespace(name: str, path: Path) -> None:
    module = sys.modules.get(name)
    if module is None:
        module = types.ModuleType(name)
        module.__path__ = [str(path)]  # type: ignore[attr-defined]
        sys.modules[name] = module
    else:
        path_str = str(path)
        existing = list(getattr(module, "__path__", []))  # type: ignore[attr-defined]
        if path_str not in existing:
            existing.append(path_str)
            module.__path__ = existing  # type: ignore[attr-defined]


_ensure_namespace("hyfuzz_server", _SERVER_SRC)
_ensure_namespace("hyfuzz_client", _CLIENT_SRC)

# ---------------------------------------------------------------------------
# Imports from the namespaced packages
# ---------------------------------------------------------------------------
from hyfuzz_server.defense.defense_integrator import BaseDefenseModule, DefenseIntegrator
from hyfuzz_server.defense.defense_models import (
    DefenseAction,
    DefenseEvent,
    DefenseResult,
    DefenseSignal,
)
from hyfuzz_server.learning.feedback_loop import FeedbackLoop
from hyfuzz_server.llm.llm_judge import Judgment, LLMJudge
from hyfuzz_server.llm.payload_generator import PayloadGenerationRequest, PayloadGenerator
from hyfuzz_server.protocols.base_protocol import ProtocolContext, ProtocolSession, ProtocolSpec
from hyfuzz_server.protocols.protocol_factory import ProtocolFactory
from hyfuzz_server.protocols.protocol_registry import ProtocolRegistry

from hyfuzz_client.execution.orchestrator import Orchestrator
from hyfuzz_client.models.execution_models import ExecutionRequest, ExecutionResult


@dataclass(frozen=True)
class CampaignTarget:
    """Target metadata describing what to fuzz."""

    name: str
    protocol: str
    endpoint: str


@dataclass
class ExecutionDetail:
    """Detailed record of a single campaign execution."""

    target: CampaignTarget
    payload: str
    request_id: str
    request_parameters: Dict[str, str]
    execution: ExecutionResult
    defense: Optional[DefenseResult]
    judgment: Judgment
    spec: ProtocolSpec
    session_id: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        verdict = self.defense.verdict if self.defense else "none"
        risk = self.defense.risk_score if self.defense else 0.0
        return {
            "target": {
                "name": self.target.name,
                "protocol": self.target.protocol,
                "endpoint": self.target.endpoint,
            },
            "request_id": self.request_id,
            "session_id": self.session_id,
            "payload": self.payload,
            "parameters": dict(self.request_parameters),
            "execution": {
                "payload_id": self.execution.payload_id,
                "success": self.execution.success,
                "output": self.execution.output,
                "diagnostics": self.execution.diagnostics or {},
            },
            "defense": {
                "verdict": verdict,
                "risk_score": risk,
                "summary": self.defense.to_dict() if self.defense else {},
            },
            "judgment": {
                "score": self.judgment.score,
                "reasoning": self.judgment.reasoning,
            },
            "spec": {
                "name": self.spec.name,
                "description": self.spec.description,
                "stateful": self.spec.stateful,
            },
        }


@dataclass
class Phase3RunSummary:
    """Aggregated summary for a full campaign run."""

    executions: List[ExecutionDetail] = field(default_factory=list)
    feedback_history: List[str] = field(default_factory=list)

    def verdict_breakdown(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for detail in self.executions:
            verdict = detail.defense.verdict if detail.defense else "none"
            counts[verdict] = counts.get(verdict, 0) + 1
        return counts

    def average_judgment_score(self) -> float:
        if not self.executions:
            return 0.0
        return mean(detail.judgment.score for detail in self.executions)

    def to_dict(self) -> Dict[str, object]:
        return {
            "executions": [detail.to_dict() for detail in self.executions],
            "feedback": list(self.feedback_history),
            "verdict_breakdown": self.verdict_breakdown(),
            "average_judgment": round(self.average_judgment_score(), 4),
        }


class _BaselineDefenseModule(BaseDefenseModule):
    """Simplistic defense module producing deterministic verdicts for testing."""

    def handle_signal(self, signal: DefenseSignal) -> Optional[DefenseResult]:
        success = signal.event.payload.get("success", False)
        verdict = "monitor" if success else "escalate"
        risk = 0.2 if success else 0.8
        action = DefenseAction(name="log", description="Baseline defense action")
        rationale = "Execution succeeded" if success else "Execution reported failure"
        return DefenseResult(
            signal=signal,
            actions=[action],
            verdict=verdict,
            rationale=rationale,
            risk_score=risk,
            context={"success": success},
        )


class Phase3Coordinator:
    """Coordinate the server payload generation and client execution flows."""

    def __init__(self, *, model_name: str = "mistral") -> None:
        self.logger = logging.getLogger(__name__)
        self.payload_generator = PayloadGenerator(model_name=model_name)
        self.protocol_factory = ProtocolFactory(ProtocolRegistry())
        self.defense_integrator = DefenseIntegrator()
        self.defense_integrator.register_integrator("baseline", _BaselineDefenseModule())
        self.judge = LLMJudge(model_name=model_name)
        self.feedback_loop = FeedbackLoop(history=[])
        self.orchestrator = Orchestrator()

    @staticmethod
    def _normalise_parameters(params: Dict[str, object]) -> Dict[str, str]:
        normalised: Dict[str, str] = {}
        for key, value in params.items():
            if isinstance(value, (dict, list)):
                normalised[key] = json.dumps(value, sort_keys=True)
            elif value is None:
                normalised[key] = ""
            else:
                normalised[key] = str(value)
        return normalised

    def _payload_defaults(
        self, target: CampaignTarget, spec: ProtocolSpec, raw_payload: str
    ) -> Dict[str, object]:
        base: Dict[str, object] = {"raw": raw_payload, "target": target.endpoint}
        base.update(spec.default_parameters)
        protocol = target.protocol.lower()
        if protocol == "coap":
            parsed = urlparse(target.endpoint)
            base.setdefault("path", parsed.path or "/")
        elif protocol == "mqtt":
            base.setdefault("topic", "hyfuzz/demo")
            base.setdefault("qos", 1)
        elif protocol == "http":
            parsed = urlparse(target.endpoint)
            base.setdefault("method", "POST")
            base.setdefault("path", parsed.path or "/")
        else:
            base.setdefault("notes", "Using generic payload defaults")
        return base

    def _plan_requests(self, targets: Sequence[CampaignTarget]) -> List[ExecutionDetail]:
        plans: List[ExecutionDetail] = []
        for index, target in enumerate(targets):
            handler = self.protocol_factory.create(target.protocol)
            spec = handler.get_spec()
            prompt = f"{target.protocol}:{target.endpoint}"
            payload = self.payload_generator.generate(
                PayloadGenerationRequest(prompt=prompt)
            )
            payload_template = self._payload_defaults(target, spec, payload)
            if not handler.validate(payload_template):
                self.logger.debug(
                    "Payload template failed validation for protocol %s, applying fallback",
                    target.protocol,
                )
                payload_template.setdefault("auto_generated", True)
            context = ProtocolContext(target=target.endpoint)
            session_id = None
            if spec.stateful:
                context = handler.start_session(context)
                session = context.session or ProtocolSession(session_id=f"{spec.name}-session")
                default_session = f"{spec.name}-session"
                if session.session_id == default_session:
                    session = ProtocolSession(
                        session_id=f"{spec.name}-{target.name}-{index}",
                        attributes=session.attributes,
                    )
                context = context.with_session(session)
                session_id = session.session_id
            protocol_request = handler.prepare_request(context, payload_template)
            protocol_request.setdefault("payload_template", payload_template)
            params = self._normalise_parameters(protocol_request)
            request_id = f"{target.name}-{index}"
            execution = ExecutionResult(
                payload_id=request_id, success=False, output="", diagnostics={}
            )
            if session_id is None and spec.stateful:
                session_id = protocol_request.get("session_id")
            if session_id is not None:
                params.setdefault("session_id", session_id)
            plans.append(
                ExecutionDetail(
                    target=target,
                    payload=payload,
                    request_id=request_id,
                    request_parameters=params,
                    execution=execution,
                    defense=None,
                    judgment=Judgment(score=0.0, reasoning=""),
                    spec=spec,
                    session_id=session_id,
                )
            )
        return plans

    def run_campaign(self, targets: Sequence[CampaignTarget]) -> Phase3RunSummary:
        details = self._plan_requests(targets)
        requests: List[ExecutionRequest] = []
        for detail in details:
            request = ExecutionRequest(
                payload_id=detail.request_id,
                protocol=detail.target.protocol,
                parameters=detail.request_parameters,
                session_id=detail.session_id,
                sequence=len(requests),
            )
            requests.append(request)

        self.orchestrator.queue_requests(requests)
        execution_results = self.orchestrator.run()

        by_identifier = {result.payload_id: result for result in execution_results}

        for detail in details:
            execution = by_identifier.get(detail.request_id)
            if execution is None:
                self.logger.warning(
                    "No execution result returned for payload %s", detail.request_id
                )
                continue

            detail.execution = execution
            event = DefenseEvent(
                source="client-execution",
                payload={
                    "success": execution.success,
                    "protocol": detail.target.protocol,
                    "payload_id": execution.payload_id,
                    "parameters": detail.request_parameters,
                    "session_id": detail.session_id,
                },
            )
            severity = "low" if execution.success else "high"
            signal = DefenseSignal(
                event=event,
                severity=severity,
                confidence=0.75 if execution.success else 0.95,
            )
            detail.defense = self.defense_integrator.process_signal(signal)
            detail.judgment = self.judge.judge(detail.payload)
            feedback_entry = (
                f"{detail.target.protocol}:{detail.judgment.score:.2f}"
                f":{detail.defense.verdict if detail.defense else 'none'}"
            )
            self.feedback_loop.add_feedback(feedback_entry)

        summary = Phase3RunSummary(
            executions=details,
            feedback_history=list(self.feedback_loop.history),
        )
        return summary


if __name__ == "__main__":  # pragma: no cover - example usage
    coordinator = Phase3Coordinator()
    run_summary = coordinator.run_campaign(
        [
            CampaignTarget(name="coap-demo", protocol="coap", endpoint="coap://127.0.0.1"),
            CampaignTarget(name="modbus-demo", protocol="modbus", endpoint="modbus://127.0.0.1"),
        ]
    )
    import json

    print(json.dumps(run_summary.to_dict(), indent=2))
