"""Execution models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ExecutionRequest:
    payload_id: str
    protocol: str
    parameters: Dict[str, str] = field(default_factory=dict)
    session_id: Optional[str] = None
    sequence: int = 0


@dataclass
class ExecutionResult:
    payload_id: str
    success: bool
    output: str
    diagnostics: Optional[Dict[str, str]] = None
    session_id: Optional[str] = None


if __name__ == "__main__":
    req = ExecutionRequest(payload_id="1", protocol="coap")
    res = ExecutionResult(payload_id=req.payload_id, success=True, output="ok")
    print(req, res)
