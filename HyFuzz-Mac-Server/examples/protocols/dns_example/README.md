# DNS Protocol Example

This example demonstrates how to create a complete custom protocol implementation for HyFuzz.

## Files

- `dns_protocol.py` - Server-side protocol handler
- `dns_handler.py` - Client-side protocol handler
- `test_dns.py` - Test suite for the DNS protocol
- `run_dns_campaign.py` - Example fuzzing campaign

## Installation

1. Copy the protocol handlers to the appropriate directories:

```bash
# Server-side handler
cp dns_protocol.py ../../HyFuzz-Windows-Server/src/protocols/

# Client-side handler
cp dns_handler.py ../../HyFuzz-Ubuntu-Client/src/protocols/
```

2. The protocols will be automatically discovered and registered.

## Usage

### Running Tests

```bash
python test_dns.py
```

### Running a Campaign

```bash
python run_dns_campaign.py
```

### Using the Protocol

```python
from coordinator import FuzzingCoordinator, CampaignTarget

coordinator = FuzzingCoordinator(model_name="mistral")

target = CampaignTarget(
    name="google-dns",
    protocol="dns",
    endpoint="dns://8.8.8.8:53"
)

summary = coordinator.run_campaign([target], payload_count=100)
print(f"Results: {summary.verdict_breakdown()}")
```

## Protocol Metadata

```python
DNS_PROTOCOL_METADATA = ProtocolMetadata(
    name="dns",
    version="1.0.0",
    description="Domain Name System protocol fuzzer",
    stateful=False,
    default_parameters={
        "query_type": "A",
        "recursive": True,
        "timeout": 5
    },
    supports_fragmentation=False,
    supports_encryption=False,
    supports_authentication=False
)
```

## Extending the Protocol

To add new features:

1. **Add query types**: Update `_build_dns_query()` to support more record types
2. **Add DNSSEC support**: Implement DO bit and signature validation
3. **Add TCP support**: Implement fallback to TCP for large responses
4. **Add DoH/DoT**: Implement DNS over HTTPS/TLS

## Testing

The example includes comprehensive tests:

- Unit tests for server-side handler
- Unit tests for client-side handler
- Integration tests with real DNS servers
- Edge case and error handling tests

## License

MIT
