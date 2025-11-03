# HyFuzz Phase 3 Platform Workspace

The **HyFuzz Phase 3** workspace combines the Windows-hosted control plane and the Ubuntu execution
agent into a single mono-repository. It captures every artifact required to reproduce the
stateful, defense-aware fuzzing campaigns described in the Phase 3 specification, including the
coordinator glue code that links both halves together for end-to-end validation.

This repository is organised as a meta-project:

| Directory | Role |
| --------- | ---- |
| [`HyFuzz-Windows-Server/`](HyFuzz-Windows-Server/README.md) | Windows 10/11 service that orchestrates LLM-driven payload generation, defense telemetry, reporting, and distributed scheduling. |
| [`HyFuzz-Ubuntu-Client/`](HyFuzz-Ubuntu-Client/README.md) | Ubuntu 22.04+ execution agent that sandboxes payloads, captures instrumentation signals, and feeds results back to the server. |
| [`phase3/`](phase3/README.md) | Shared coordinator that wires protocol templates, result correlation, and feedback loops across the server and client. |
| [`tests/`](tests/README.md) | Cross-repository regression checks that ensure the combined platform stays aligned. |

> **Language note**: Source code, configuration, and documentation are written in English in order to
> interoperate with existing tooling, even though the day-to-day conversations with contributors may
> happen in Chinese.

---

## Quick Start

### 1. Provision the Environment

- Install Python 3.10+ on both the Windows host and the Ubuntu guest/VM.
- Configure Ollama (or an OpenAI-compatible endpoint) on the server host and download the preferred
  models (e.g. `mistral`, `llama2`, `codellama`).
- On Ubuntu, install instrumentation helpers (`strace`, `ltrace`, `gdb`, `perf`, sanitizers) and
  optional container tooling (`docker`, `podman`).

Detailed setup steps live in:

- [`HyFuzz-Windows-Server/SETUP_GUIDE.md`](HyFuzz-Windows-Server/SETUP_GUIDE.md)
- [`HyFuzz-Ubuntu-Client/docs/SETUP.md`](HyFuzz-Ubuntu-Client/docs/SETUP.md)

### 2. Configure Credentials and Connectivity

1. Copy the environment templates:
   ```bash
   cp HyFuzz-Windows-Server/.env.example HyFuzz-Windows-Server/.env
   cp HyFuzz-Ubuntu-Client/config/.env.template HyFuzz-Ubuntu-Client/.env
   ```
2. Populate API keys, database URLs, and queue credentials.
3. Ensure the Windows host can reach the Ubuntu guest over the configured MCP/HTTP/WebSocket ports.

### 3. Run the Distributed Stack

1. **Start the server control plane**
   ```bash
   cd HyFuzz-Windows-Server
   python scripts/start_server.py --config config/server_config.yaml
   ```
2. **Launch Celery workers / task executors** (optional but recommended)
   ```bash
   python scripts/start_workers.py --concurrency 4
   ```
3. **Start the Ubuntu execution agent**
   ```bash
   cd ../HyFuzz-Ubuntu-Client
   python scripts/start_client.py --config config/client_config.yaml
   ```
4. Monitor the dashboards, defense feedback, and campaign status via the Windows server’s APIs or
   the optional web dashboard (`scripts/start_dashboard.py`).

### 4. Validate with the Shared Phase 3 Coordinator

The [`phase3`](phase3/README.md) package can execute fully automated smoke tests that exercise the
protocol registry, payload pipeline, judge feedback loop, and defense telemetry in tandem:

```bash
pytest tests/test_phase3_coordinator.py -v
```

To target a specific protocol campaign:

```bash
python -m phase3.coordinator --protocol coap --plan configs/phase3_demo.yaml
```

(See the coordinator README for configuration examples.)

### 5. Understand Stateful vs. Stateless Protocols

Phase 3 introduces an explicit capability model so that fuzzing campaigns can mix stateless
protocols (e.g. CoAP, HTTP) and stateful transports (e.g. Modbus). The Windows server publishes
`ProtocolSpec` descriptors through `src/protocols/`, while the Ubuntu client exposes matching
`ProtocolCapabilities` records in `src/protocols/`.

- **Stateless protocols** run with a single request/response template and do not require session
  correlation. Their specs declare `stateful=False`, so the coordinator omits session identifiers.
- **Stateful protocols** declare `stateful=True`. The coordinator automatically provisions session
  identifiers, the client `ProtocolStateManager` keeps per-session telemetry, and diagnostics emitted
  by `ExecutionResult` include the captured state snapshot. Modbus serves as the reference
  implementation.

When adding a new protocol, register its metadata on both sides so that the coordinator can decide
whether to allocate sessions and which default parameters to seed into generated payloads.

---

## Documentation Map

Each component repository ships with its own documentation portal, but the most useful entry points
are collected here for convenience:

- **Server knowledge base**: [`HyFuzz-Windows-Server/docs/README.md`](HyFuzz-Windows-Server/docs/README.md)
- **Client knowledge base**: [`HyFuzz-Ubuntu-Client/docs/README.md`](HyFuzz-Ubuntu-Client/docs/README.md)
- **Defense integration**: [`HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md`](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md)
- **Instrumentation guide**: [`HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md`](HyFuzz-Ubuntu-Client/docs/INSTRUMENTATION.md)
- **Protocol matrix**: [`HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md`](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md) & [`HyFuzz-Ubuntu-Client/docs/PROTOCOLS.md`](HyFuzz-Ubuntu-Client/docs/PROTOCOLS.md)
- **Testing strategy**: [`tests/README.md`](tests/README.md)

If you expand the platform (new protocol handler, additional defense integrator, etc.), update the
relevant README files and link them from this document to keep the knowledge base coherent.

---

## Contributing

1. Fork the repository and create a feature branch from `work`.
2. Follow the linting and testing instructions in `HyFuzz-Windows-Server/CONTRIBUTING.md` and
   `HyFuzz-Ubuntu-Client/CONTRIBUTING.md`.
3. Run the shared regression suite before opening a pull request:
   ```bash
   pytest
   ```
4. Open a PR that references the planned feature or bugfix, and include relevant screenshots/logs if
   you touched UI elements or dashboards.

See [`HyFuzz-Windows-Server/CODE_OF_CONDUCT.md`](HyFuzz-Windows-Server/CODE_OF_CONDUCT.md) for
community guidelines and escalation paths.

---

## Licensing & Citation

- **License**: [MIT License](LICENSE)
- **Academic citation**: [`HyFuzz-Windows-Server/CITATION.cff`](HyFuzz-Windows-Server/CITATION.cff)

If you publish academic work based on HyFuzz, please reference the citation metadata and mention the
Phase 3 coordinator where applicable.

