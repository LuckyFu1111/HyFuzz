import pytest

from src.execution.sandbox_manager import SandboxManager
from src.utils.exceptions import SandboxViolation


def test_sandbox_blocks_network():
    sandbox = SandboxManager(allow_network=False)
    with pytest.raises(SandboxViolation):
        sandbox.validate("curl http://example.com")
