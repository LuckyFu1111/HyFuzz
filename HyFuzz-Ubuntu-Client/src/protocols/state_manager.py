"""Simple protocol session state manager for stateful fuzzing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class ProtocolSessionState:
    """Track protocol-specific state for a single session."""

    session_id: str
    attributes: Dict[str, object] = field(default_factory=dict)


class ProtocolStateManager:
    """Store per-protocol session state for the client orchestrator."""

    def __init__(self) -> None:
        self._sessions: Dict[Tuple[str, str], ProtocolSessionState] = {}

    def get(self, protocol: str, session_id: str) -> ProtocolSessionState:
        key = (protocol, session_id)
        if key not in self._sessions:
            self._sessions[key] = ProtocolSessionState(session_id=session_id)
        return self._sessions[key]

    def snapshot(self) -> Dict[str, Dict[str, object]]:
        return {
            f"{protocol}:{session_id}": dict(state.attributes)
            for (protocol, session_id), state in self._sessions.items()
        }


_STATE_MANAGER = ProtocolStateManager()


def get_state_manager() -> ProtocolStateManager:
    return _STATE_MANAGER


if __name__ == "__main__":
    manager = get_state_manager()
    session = manager.get("modbus", "demo-session")
    session.attributes["count"] = session.attributes.get("count", 0) + 1
    print(manager.snapshot())
