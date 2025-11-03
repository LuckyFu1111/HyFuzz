# Client Test Suites

This directory stores the Ubuntu client regression coverage. The layout mirrors the Windows server
tests but focuses on the execution agent, instrumentation hooks, and crash analysis pipeline.

## Structure

| Subdirectory | Focus |
| ------------ | ----- |
| `unit/` | Handler-level tests for protocol logic, orchestrator helpers, judge metrics, etc. |
| `integration/` | End-to-end client pipelines including MCP message handling and execution flows. |
| `performance/` | Benchmarks for execution throughput, instrumentation overhead, distributed runs. |
| `e2e/` | Complete campaign walkthroughs from target discovery to reporting. |
| `fixtures/` | Sample payloads, mock targets, protocol simulators, reusable fixture builders. |

## Running

```bash
cd HyFuzz-Ubuntu-Client
pytest
```

To narrow down to a particular area:

```bash
pytest tests/unit/test_client.py -v
```

## Guidelines

1. Prefer fixtures from `tests/fixtures/` to keep scenarios consistent and reduce duplication.
2. Use `pytest.mark.integration`, `pytest.mark.performance`, etc., to help CI pipelines select subsets.
3. Update this README if you add new directories or change how the suites are grouped.

