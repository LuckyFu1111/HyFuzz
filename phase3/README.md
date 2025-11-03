# Phase 3 Cross-Repository Coordinator

The `phase3` package hosts light-weight orchestration utilities that connect the Windows HyFuzz server
and the Ubuntu HyFuzz client inside this combined workspace. It mirrors the production workflow by
wiring protocol-specific payload templates, execution bookkeeping, defense telemetry correlation, and
LLM feedback aggregation into a single Python API.

## Components

| Module | Description |
| ------ | ----------- |
| [`coordinator.py`](coordinator.py) | High-level façade that loads protocol templates, attaches client/server shims, assigns request IDs, allocates sessions, and aggregates verdicts. |
| [`__init__.py`](__init__.py) | Exposes the public `Phase3Coordinator` class and convenience helpers for scripts and tests. |

The coordinator avoids import conflicts by dynamically adding both component repositories to
`sys.path`. When invoked from this mono-repo it automatically discovers the latest builds of the
server and client packages.

## Usage

### Python API

```python
from phase3 import Phase3Coordinator

coordinator = Phase3Coordinator()
result = coordinator.run_campaign(
    protocol="coap",
    target_name="demo-coap-server",
    seed_payloads=["01ff02"],
)

print(result.summary)
```

### Command Line

The module can also run from the command line for quick smoke tests:

```bash
python -m phase3.coordinator --protocol modbus --campaign sample
```

Key arguments:

- `--protocol`: `coap`, `modbus`, or any protocol supported by the server registry.
- `--campaign`: Named preset defined in `HyFuzz-Windows-Server/config/fuzzing_config.yaml`.
- `--max-samples`: Limit the number of payload executions.
- `--dump-json`: Write a structured report to `results/phase3/<timestamp>.json`.

### Pytest Integration

The repository-level test suite includes [`tests/test_phase3_coordinator.py`](../tests/test_phase3_coordinator.py),
which runs deterministic CoAP and Modbus campaigns. Run it as part of CI or before opening a pull request:

```bash
pytest tests/test_phase3_coordinator.py -v
```

## Extending the Coordinator

1. Register the new protocol inside `HyFuzz-Windows-Server/src/protocols/` with an accurate
   `ProtocolSpec` (including statefulness and default parameters) and update the Ubuntu client handler
   in `HyFuzz-Ubuntu-Client/src/protocols/` with matching `ProtocolCapabilities`.
2. Use the factory helpers in `coordinator.py` to introspect those specs instead of hard-coding
   metadata.
3. Add fixtures and assertions to `tests/test_phase3_coordinator.py` to cover the new workflow,
   including stateful session tracking when relevant.
4. Update the root [`README.md`](../README.md) and the relevant docs/READMEs to mention the addition.

Keep this README up-to-date whenever you expose new entry points or configuration knobs so that other
contributors can quickly run the shared orchestration layer.

