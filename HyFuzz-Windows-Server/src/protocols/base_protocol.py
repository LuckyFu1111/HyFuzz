"""Base protocol handler definitions with stateful support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@dataclass(frozen=True)
class ProtocolSpec:
    """Describe protocol metadata used by registries and coordinators."""

    name: str
    description: str = ""
    stateful: bool = False
    default_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolSession:
    """Representation of an active protocol session."""

    session_id: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolContext:
    """Context describing the target under test."""

    target: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    session: Optional[ProtocolSession] = None

    def with_metadata(self, **kwargs: Any) -> "ProtocolContext":
        merged = {**self.metadata, **kwargs}
        return ProtocolContext(target=self.target, metadata=merged, session=self.session)

    def with_session(self, session: ProtocolSession) -> "ProtocolContext":
        return ProtocolContext(target=self.target, metadata=self.metadata, session=session)


@runtime_checkable
class ProtocolHandler(Protocol):
    """Protocol for protocol handlers."""

    name: str

    def prepare_request(self, context: ProtocolContext, payload: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def parse_response(self, context: ProtocolContext, response: Dict[str, Any]) -> Dict[str, Any]:
        ...

    def validate(self, payload: Dict[str, Any]) -> bool:
        ...


class BaseProtocolHandler:
    """Concrete base class implementing default behaviors."""

    name: str = "base"
    SPEC: ProtocolSpec = ProtocolSpec(name="base", description="Base protocol handler")

    def prepare_request(self, context: ProtocolContext, payload: Dict[str, Any]) -> Dict[str, Any]:
        request = {"target": context.target, "payload": payload}
        if context.session is not None:
            request["session_id"] = context.session.session_id
        return request

    def parse_response(self, context: ProtocolContext, response: Dict[str, Any]) -> Dict[str, Any]:
        return {"context": context.metadata, "response": response}

    def validate(self, payload: Dict[str, Any]) -> bool:
        return bool(payload)

    # ------------------------------------------------------------------
    # Capability helpers
    # ------------------------------------------------------------------

    def get_spec(self) -> ProtocolSpec:
        """Return the protocol specification for the handler."""

        spec = getattr(self, "SPEC", None)
        if spec is None or spec.name == "base":
            return ProtocolSpec(name=getattr(self, "name", "base"))
        return spec

    def start_session(self, context: ProtocolContext) -> ProtocolContext:
        """Return a context bound to a newly created session if supported."""

        spec = self.get_spec()
        if not spec.stateful:
            return context
        session = ProtocolSession(session_id=f"{spec.name}-session", attributes={})
        return context.with_session(session)

    def end_session(self, context: ProtocolContext) -> ProtocolContext:
        """Allow handlers to clean up session resources."""

        return context


if __name__ == "__main__":
    context = ProtocolContext(target="demo")
    handler = BaseProtocolHandler()
    prepared = handler.prepare_request(context, {"ping": True})
    print(prepared)
    print(handler.parse_response(context, {"pong": True}))
    print("Valid:", handler.validate({"ping": True}))
