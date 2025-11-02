"""Project-wide pytest configuration."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_PHASE3_SRC = ROOT / "phase3"
_ROOT_TESTS = ROOT / "tests"

# Only the shared phase3 tests run from the repository root.  They require
# access to the coordinating package as well as the client fixtures directory
# for illustrative imports in documentation-driven examples.
if _PHASE3_SRC.exists():
    str_phase3 = str(_PHASE3_SRC)
    if str_phase3 not in sys.path:
        sys.path.insert(0, str_phase3)

if _ROOT_TESTS.exists():
    str_root_tests = str(_ROOT_TESTS)
    if str_root_tests not in sys.path:
        sys.path.insert(0, str_root_tests)

# Ensure the client test package remains importable for shared fixtures that
# documentation examples rely on when executed from the repository root.
_CLIENT_TESTS = ROOT / "HyFuzz-Ubuntu-Client" / "tests"
if _CLIENT_TESTS.exists():
    str_client_tests = str(_CLIENT_TESTS)
    if str_client_tests not in sys.path:
        sys.path.insert(0, str_client_tests)
