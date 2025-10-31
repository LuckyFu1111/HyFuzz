"""Execution models."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ExecutionRequest:
    payload_id: str
    protocol: str
    parameters: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    payload_id: str
    success: bool
    output: str
    diagnostics: Optional[Dict[str, str]] = None


if __name__ == "__main__":
    req = ExecutionRequest(payload_id="1", protocol="coap")
    res = ExecutionResult(payload_id=req.payload_id, success=True, output="ok")
    print(req, res)
