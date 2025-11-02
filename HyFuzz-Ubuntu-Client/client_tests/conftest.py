"""Pytest fixtures and namespace configuration for the client suite."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CLIENT_SRC = _PROJECT_ROOT / "src"


def _reload_client_package() -> None:
    """Reload the client ``src`` package, isolating it from the server copy."""

    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            sys.modules.pop(name, None)

    spec = importlib.util.spec_from_file_location("src", _CLIENT_SRC / "__init__.py")
    if spec is None or spec.loader is None:  # pragma: no cover - sanity guard
        raise RuntimeError("Unable to load client src package")

    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)


_reload_client_package()


from src.targets.target_manager import TargetManager  # noqa: E402  (after bootstrap)


@pytest.fixture(scope="session")
def target_manager() -> TargetManager:
    return TargetManager()
