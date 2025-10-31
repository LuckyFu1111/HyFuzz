from src.targets.target_manager import TargetManager
from src.targets.vulnerability_mapper import VulnerabilityMapper


def test_target_integration_maps_vulnerabilities():
    manager = TargetManager()
    mapper = VulnerabilityMapper()
    profiles = manager.discover()
    mapped = mapper.map(profiles[0].protocol)
    assert mapped
