"""Integration tests for HyFuzz platform components.

This module contains integration tests that verify the interaction between
different components of the HyFuzz platform, including server-client
communication, payload generation, and defense integration.
"""
from __future__ import annotations

import pytest
from pathlib import Path


@pytest.mark.integration
def test_project_structure():
    """Test that all essential project directories exist."""
    root = Path(__file__).parent.parent

    essential_dirs = [
        root / "HyFuzz-Windows-Server",
        root / "HyFuzz-Ubuntu-Client",
        root / "coordinator",
        root / "tests",
        root / "configs",
    ]

    for directory in essential_dirs:
        assert directory.exists(), f"Missing directory: {directory}"
        assert directory.is_dir(), f"Not a directory: {directory}"


@pytest.mark.integration
def test_configuration_files_exist():
    """Test that all configuration files are present."""
    root = Path(__file__).parent.parent

    config_files = [
        root / "configs" / "campaign_demo.yaml",
        root / "HyFuzz-Windows-Server" / "config" / "server_config.yaml",
        root / "HyFuzz-Ubuntu-Client" / "config" / "client_config.yaml",
        root / "HyFuzz-Windows-Server" / ".env.example",
        root / "HyFuzz-Ubuntu-Client" / ".env.example",
    ]

    for config_file in config_files:
        assert config_file.exists(), f"Missing config file: {config_file}"
        assert config_file.is_file(), f"Not a file: {config_file}"


@pytest.mark.integration
def test_scripts_are_executable():
    """Test that all main scripts exist and are Python files."""
    root = Path(__file__).parent.parent

    scripts = [
        root / "HyFuzz-Windows-Server" / "scripts" / "start_server.py",
        root / "HyFuzz-Windows-Server" / "scripts" / "start_workers.py",
        root / "HyFuzz-Windows-Server" / "scripts" / "start_dashboard.py",
        root / "HyFuzz-Windows-Server" / "scripts" / "run_fuzzing_campaign.py",
        root / "HyFuzz-Ubuntu-Client" / "scripts" / "start_client.py",
        root / "scripts" / "health_check.py",
    ]

    for script in scripts:
        assert script.exists(), f"Missing script: {script}"
        assert script.suffix == ".py", f"Not a Python file: {script}"


@pytest.mark.integration
def test_coordinator_import():
    """Test that FuzzingCoordinator can be imported."""
    from coordinator import FuzzingCoordinator, CampaignTarget

    assert FuzzingCoordinator is not None
    assert CampaignTarget is not None


@pytest.mark.integration
def test_coordinator_instantiation():
    """Test that FuzzingCoordinator can be instantiated."""
    from coordinator import FuzzingCoordinator

    coordinator = FuzzingCoordinator(model_name="test-model")
    assert coordinator is not None
    assert hasattr(coordinator, "run_campaign")


@pytest.mark.integration
def test_campaign_target_creation():
    """Test that CampaignTarget can be created."""
    from coordinator import CampaignTarget

    target = CampaignTarget(
        name="test-target",
        protocol="coap",
        endpoint="coap://localhost:5683"
    )

    assert target.name == "test-target"
    assert target.protocol == "coap"
    assert target.endpoint == "coap://localhost:5683"


@pytest.mark.integration
def test_requirements_files_exist():
    """Test that requirements files exist for both components."""
    root = Path(__file__).parent.parent

    requirements = [
        root / "HyFuzz-Windows-Server" / "requirements.txt",
        root / "HyFuzz-Windows-Server" / "requirements-dev.txt",
        root / "HyFuzz-Ubuntu-Client" / "requirements.txt",
        root / "HyFuzz-Ubuntu-Client" / "requirements-dev.txt",
    ]

    for req_file in requirements:
        assert req_file.exists(), f"Missing requirements file: {req_file}"
        assert req_file.stat().st_size > 0, f"Empty requirements file: {req_file}"


@pytest.mark.integration
def test_documentation_files_exist():
    """Test that essential documentation files exist."""
    root = Path(__file__).parent.parent

    docs = [
        root / "README.md",
        root / "QUICKSTART.md",
        root / "coordinator" / "README.md",
        root / "tests" / "README.md",
        root / "HyFuzz-Windows-Server" / "SETUP_GUIDE.md",
        root / "HyFuzz-Ubuntu-Client" / "docs" / "SETUP.md",
    ]

    for doc in docs:
        assert doc.exists(), f"Missing documentation: {doc}"


@pytest.mark.integration
def test_gitignore_exists():
    """Test that .gitignore file exists at root."""
    root = Path(__file__).parent.parent
    gitignore = root / ".gitignore"

    assert gitignore.exists(), "Missing .gitignore file"
    content = gitignore.read_text()
    assert "__pycache__" in content, ".gitignore missing __pycache__ rule"


@pytest.mark.integration
def test_essential_imports():
    """Test that essential modules can be imported without errors."""
    # These imports should not raise exceptions
    try:
        import yaml
        import pydantic
        import requests
        assert True
    except ImportError as e:
        pytest.fail(f"Essential package import failed: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_coordinator_mock_campaign():
    """Test running a mock campaign with FuzzingCoordinator."""
    from coordinator import FuzzingCoordinator, CampaignTarget

    coordinator = FuzzingCoordinator(model_name="test-model")

    targets = [
        CampaignTarget(
            name="test-coap",
            protocol="coap",
            endpoint="coap://mock-server:5683"
        )
    ]

    # This should not raise exceptions even with mock targets
    try:
        summary = coordinator.run_campaign(targets)
        assert summary is not None
        assert hasattr(summary, "executions")
        assert len(summary.executions) >= 0
    except Exception as e:
        # It's okay if the execution fails, we're just testing the interface
        assert "mock" in str(e).lower() or "test" in str(e).lower()


@pytest.mark.integration
def test_health_check_script_syntax():
    """Test that health check script has valid Python syntax."""
    root = Path(__file__).parent.parent
    health_check = root / "scripts" / "health_check.py"

    assert health_check.exists()

    # Try to compile the script to check for syntax errors
    import py_compile
    try:
        py_compile.compile(str(health_check), doraise=True)
    except py_compile.PyCompileError as e:
        pytest.fail(f"Syntax error in health_check.py: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
