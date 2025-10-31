"""Pytest fixtures."""
import pytest

from src.targets.target_manager import TargetManager


@pytest.fixture(scope="session")
def target_manager() -> TargetManager:
    return TargetManager()
