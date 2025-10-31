# Target Management Guide

Target discovery and profiling ensure campaigns run against the correct assets with appropriate context.

## Discovery Workflow

1. Scan networks for supported protocols:
   ```bash
   python scripts/targets/scan_targets.py --network 192.168.1.0/24 --protocols coap,modbus
   ```
2. Detect services and versions:
   ```bash
   python scripts/targets/fingerprint_service.py --target-id TARGET_UUID
   ```
3. Profile targets for capabilities and risk:
   ```bash
   python scripts/targets/profile_target.py --target-id TARGET_UUID
   ```
4. Sync with the server:
   ```bash
   python scripts/targets/profile_target.py --sync
   ```

## Data Model

Targets are stored in the SQLite database and exported to `data/targets/*.json`.

| Field | Description |
|-------|-------------|
| `id` | UUID for the target |
| `address` | Hostname or IP |
| `protocols` | Supported protocols (coap, modbus, mqtt, http, grpc, etc.) |
| `port` | Port number |
| `service` | Detected service banner |
| `version` | Software version or firmware build |
| `risk_score` | Derived from vulnerability mapper |

## Vulnerability Mapping

- `src/targets/vulnerability_mapper.py` correlates detected versions with CVE/CWE records in the local
  knowledge base.
- High-risk targets are prioritised in the execution queue; adjust weighting in `analysis_config.yaml` if
  necessary.

## Target Lists

- `data/targets/coap_targets.json`, `modbus_targets.json`, `mqtt_targets.json`, `http_targets.json` store
  curated targets for quick campaigns.
- Use `target_profiles.json` to maintain metadata such as authentication requirements, rate limits, and
  safety constraints.
- `target_fingerprints.json` tracks known-good fingerprints for anomaly detection.

## Best Practices

- Run scans during maintenance windows to avoid service disruption.
- Respect legal and organisational policies when scanning external networks.
- Keep fingerprints updated; outdated signatures can miss protocol upgrades.
- Use sandboxing and throttling when testing production systems.
- Tag targets with business context (owner, environment) to simplify reporting.

## Validation

```bash
pytest tests/unit/test_target_manager.py
pytest tests/integration/test_target_integration.py
```

For integration with campaign orchestration, consult [`USAGE.md`](USAGE.md). For mapping results into
reports, see [`REPORTING_GUIDE.md`](REPORTING_GUIDE.md).
