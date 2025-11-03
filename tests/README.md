# Shared Test Harness

The root-level `tests` package provides integration coverage for behaviours that span both the
Windows server and the Ubuntu client repositories. These checks guarantee that the Phase 3
coordinator, configuration defaults, and protocol templates stay compatible as the two projects
evolve independently.

## Layout

| Path | Purpose |
| ---- | ------- |
| [`tests/test_phase3_coordinator.py`](test_phase3_coordinator.py) | Executes CoAP and Modbus campaigns through the shared `Phase3Coordinator` and validates payload templates, verdict correlation, and feedback aggregation. |

The directory also exposes an empty `tests/__init__.py` to allow relative imports from pytest and a
repository-level `conftest.py` that primes `sys.path` for both component packages.

## Running the Suite

From the repository root:

```bash
pytest
```

The command above will run the shared tests plus any additional files you add under this directory.
To run only the coordinator coverage:

```bash
pytest tests/test_phase3_coordinator.py -v
```

## Adding New Checks

1. Create a new file inside `tests/` and follow pytest naming conventions (`test_*.py`).
2. Import the necessary client/server components through the `phase3` package or by referencing the
   sub-repositories directly (the root `conftest.py` already amends `sys.path`).
3. Update [`README.md`](../README.md) if the new tests introduce additional workflows or
   configuration requirements.

Keep this README in sync with the suite as you add new regression scenarios.

