# Protocol Support Guide

HyFuzz client ships with handlers for CoAP, Modbus, MQTT, HTTP, and gRPC. Each handler shares common
interfaces but provides protocol-specific parsing, validation, and vulnerability heuristics.

## Handler Overview

| Protocol | Module | Key Features |
|----------|--------|--------------|
| CoAP | `src/protocols/coap_handler.py` | DTLS-aware fuzzing, option permutation, block-wise transfers |
| Modbus | `src/protocols/modbus_handler.py` | Function code mutations, unit identifier fuzzing, register sweeps |
| MQTT | `src/protocols/mqtt_handler.py` | CONNECT/DISCONNECT abuse cases, retained message manipulation |
| HTTP | `src/protocols/http_handler.py` | Header smuggling, chunked encoding, pipeline desync |
| gRPC | `src/protocols/grpc_handler.py` | Proto descriptor awareness, method fuzzing, reflection usage |

All handlers derive from `base_handler.py` and are instantiated via `protocol_factory.py` based on
campaign metadata.

## Enabling/Disabling Protocols

Edit `config/protocol_config.yaml`:

```yaml
protocols:
  coap:
    enabled: true
    max_payload_size: 512
  modbus:
    enabled: true
  mqtt:
    enabled: true
  http:
    enabled: false
  grpc:
    enabled: false
```

Protocol availability is negotiated with the server by the MCP client. If a protocol is disabled locally,
tasks referencing it will be rejected with a descriptive status.

## Adding a New Protocol

1. Create a handler in `src/protocols/` inheriting from `BaseProtocolHandler`.
2. Implement required hooks: `prepare_target`, `generate_payload`, `execute`, and `validate_response`.
3. Register the handler in `protocol_registry.py` and `protocol_factory.py`.
4. Add vulnerability heuristics and dictionaries (e.g., `mqtt_vulnerabilities.py`).
5. Write unit tests under `tests/unit/test_<protocol>_handler.py` and integration tests if applicable.
6. Update configuration files (`protocol_config.yaml`, example configs) to expose the new protocol.

## Protocol Validation

- `protocol_validator.py` performs schema and sanity checks on generated payloads.
- Custom validators can be added per protocol for additional guardrails.
- Validation failures are logged to `logs/protocol.log` and sent to the server for analysis.

## Target Discovery & Mapping

- `data/targets/*.json` files hold preconfigured targets grouped by protocol.
- The target subsystem aligns discovered services with protocol handlers, ensuring the correct adapter is
  used during execution.

## Security Considerations

- Use TLS/DTLS options in configuration for network protocols when testing production-like systems.
- Respect rate limits defined in `protocol_config.yaml` to avoid overwhelming fragile devices.
- Combine protocol handlers with the sandbox to isolate untrusted inputs from the host system.

For end-to-end examples, review `tests/integration/test_<protocol>_fuzzing.py` files and the notebooks in
`notebooks/02_protocol_testing.ipynb`.
