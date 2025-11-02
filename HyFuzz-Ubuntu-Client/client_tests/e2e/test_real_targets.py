from src.targets.target_manager import TargetManager


def test_real_targets_discovery():
    manager = TargetManager()
    profiles = manager.discover()
    assert profiles[0].host == "localhost"
