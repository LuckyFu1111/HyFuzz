# Server Test Suites

The `tests` directory houses the Windows server regression coverage. Pytest discovers the suites
recursively, and each subfolder focuses on a specific depth of validation.

## Structure

| Subdirectory | Focus |
| ------------ | ----- |
| `unit/` | Module-level tests for API routes, LLM services, protocol specs/handlers, defense utilities, etc. |
| `integration/` | MCP transport flows, dashboard asset loading, server-client message exchange. |
| `performance/` | Benchmark runners for payload generation, fuzzing throughput, distributed scheduling. |
| `e2e/` | Full campaign simulations covering payload generation → execution → defense feedback. |
| `fixtures/` | Reusable mocks, sample payloads, defense logs, and protocol fixtures. |

A top-level `conftest.py` configures the Python path, event loop helpers, and shared fixtures so that
tests can import the `src` package without installing it as a wheel.

## Running

```bash
cd HyFuzz-Windows-Server
pytest
```

To run a single suite:

```bash
pytest tests/integration/test_server_client.py -v
```

## Writing New Tests

1. Place the file under the appropriate subdirectory using the `test_*.py` naming convention.
2. Import shared fixtures from `tests/fixtures/` when possible to keep scenarios consistent.
3. Update this README if you introduce a brand-new category or folder.

