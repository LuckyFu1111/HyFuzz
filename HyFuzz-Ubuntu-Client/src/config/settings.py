"""Configuration helpers for the HyFuzz Ubuntu client."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

import yaml

CONFIG_ROOT = Path(__file__).resolve().parent


@dataclass
class Settings:
    """Application settings loaded from multiple YAML files."""

    client: Dict[str, Any] = field(default_factory=dict)
    protocols: Dict[str, Any] = field(default_factory=dict)
    execution: Dict[str, Any] = field(default_factory=dict)
    sandbox: Dict[str, Any] = field(default_factory=dict)
    instrumentation: Dict[str, Any] = field(default_factory=dict)
    analysis: Dict[str, Any] = field(default_factory=dict)
    monitoring: Dict[str, Any] = field(default_factory=dict)
    notifications: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path | None = None) -> "Settings":
        base = root or CONFIG_ROOT
        data: Dict[str, Dict[str, Any]] = {}
        for name in (
            "client_config.yaml",
            "protocol_config.yaml",
            "execution_config.yaml",
            "sandbox_config.yaml",
            "instrumentation_config.yaml",
            "analysis_config.yaml",
            "monitoring_config.yaml",
            "notification_config.yaml",
        ):
            path = base / name
            if path.exists():
                with path.open("r", encoding="utf-8") as handle:
                    data[name.split("_")[0]] = yaml.safe_load(handle) or {}
        return cls(
            client=data.get("client", {}),
            protocols=data.get("protocol", {}),
            execution=data.get("execution", {}),
            sandbox=data.get("sandbox", {}),
            instrumentation=data.get("instrumentation", {}),
            analysis=data.get("analysis", {}),
            monitoring=data.get("monitoring", {}),
            notifications=data.get("notification", {}),
        )


if __name__ == "__main__":
    settings = Settings.load(CONFIG_ROOT.parent.parent / "config")
    print(f"Loaded configuration keys: {sorted(k for k in settings.__dict__ if getattr(settings, k))}")
