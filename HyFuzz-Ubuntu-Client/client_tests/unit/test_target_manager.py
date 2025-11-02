from src.targets.target_manager import TargetManager


def test_target_manager_discovers_profiles():
    manager = TargetManager()
    profiles = manager.discover()
    assert profiles
    assert profiles[0].protocol == "coap"
