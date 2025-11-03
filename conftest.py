"""
Project-wide pytest configuration for HyFuzz.

This configuration ensures all test modules can access the coordinator,
server, and client components from the repository root.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

_COORDINATOR_SRC = ROOT / "coordinator"
_ROOT_TESTS = ROOT / "tests"

# The coordinator module must be accessible for integration tests that
# orchestrate campaigns across server and client components.
if _COORDINATOR_SRC.exists():
    str_coordinator = str(_COORDINATOR_SRC)
    if str_coordinator not in sys.path:
        sys.path.insert(0, str_coordinator)

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
