"""Configure the import path so server tests resolve the local ``src`` package."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_SERVER_SRC = _PROJECT_ROOT / "src"


def _reload_server_package() -> None:
    """Reload the server's ``src`` package in isolation.

    When the combined repository runs the client and server test suites together,
    both projects expose a top-level package named ``src``.  To avoid namespace
    collisions we explicitly reload the server package for the lifetime of this
    test session.
    """

    for name in list(sys.modules):
        if name == "src" or name.startswith("src."):
            sys.modules.pop(name, None)

    spec = importlib.util.spec_from_file_location("src", _SERVER_SRC / "__init__.py")
    if spec is None or spec.loader is None:  # pragma: no cover - sanity guard
        raise RuntimeError("Unable to load server src package")

    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)


_reload_server_package()
