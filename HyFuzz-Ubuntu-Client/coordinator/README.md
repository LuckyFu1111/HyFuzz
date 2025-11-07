# Campaign Coordinator

## Overview

The **Campaign Coordinator** is HyFuzz's central orchestration engine that seamlessly integrates the Windows-based control plane with Ubuntu execution agents. It provides a unified Python API for coordinating distributed fuzzing campaigns across multiple protocols, targets, and clients.

### Key Features

- **Unified Campaign Management**: Single API for multi-protocol, multi-target fuzzing campaigns
- **Server-Client Integration**: Automatic coordination between control plane and execution agents
- **LLM-Driven Generation**: Intelligent payload generation using configured language models
- **Defense Integration**: Real-time defense system analysis and verdict correlation
- **Feedback Loops**: Continuous learning from execution results and judgments
- **Protocol Agnostic**: Supports CoAP, Modbus, MQTT, HTTP, and custom protocols
- **Distributed Execution**: Orchestrates payloads across multiple execution agents
- **Result Aggregation**: Comprehensive campaign summaries with statistics and analytics

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Campaign Coordinator                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Payload    │  │   Protocol   │  │   Defense    │          │
│  │  Generator   │  │   Factory    │  │  Integrator  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  LLM Judge   │  │   Feedback   │  │ Orchestrator │          │
│  │              │  │     Loop     │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
           │                                       │
           ▼                                       ▼
  ┌──────────────────┐                  ┌──────────────────┐
  │  Windows Server  │                  │  Ubuntu Client   │
  │  Control Plane   │                  │  Execution Agent │
  └──────────────────┘                  └──────────────────┘
```

### Component Responsibilities

| Component | Purpose | Location |
|-----------|---------|----------|
| `coordinator.py` | Main coordination engine that orchestrates campaign execution | This module |
| `__init__.py` | Public API exports and convenience helpers | This module |
| `FuzzingCoordinator` | High-level facade coordinating all campaign components | `coordinator.py` |
| `CampaignTarget` | Target specification (protocol, endpoint, name) | `coordinator.py` |
| `ExecutionDetail` | Detailed execution record with results and analysis | `coordinator.py` |
| `CampaignRunSummary` | Aggregated campaign results and statistics | `coordinator.py` |

## Directory Structure

```
coordinator/
├── __init__.py           # Public API exports
├── coordinator.py        # Core coordination engine
├── README.md            # This file
└── __pycache__/         # Python bytecode cache
```

## Installation

The coordinator is automatically available when you install HyFuzz. No separate installation is required.

### Prerequisites

Ensure both server and client dependencies are installed:

```bash
# Install server dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt

# Install client dependencies
cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt
```

## Usage

### Basic Python API

#### Simple Campaign

```python
from coordinator import FuzzingCoordinator, CampaignTarget

# Initialize coordinator
coordinator = FuzzingCoordinator(model_name="mistral")

# Define targets
targets = [
    CampaignTarget(
        name="coap-server",
        protocol="coap",
        endpoint="coap://192.168.1.100:5683"
    )
]

# Run campaign
summary = coordinator.run_campaign(targets)

# Access results
print(f"Total executions: {len(summary.executions)}")
print(f"Verdict breakdown: {summary.verdict_breakdown()}")
print(f"Average judgment score: {summary.average_judgment_score()}")
```

#### Multi-Protocol Campaign

```python
from coordinator import FuzzingCoordinator, CampaignTarget

coordinator = FuzzingCoordinator(model_name="mistral")

# Define multiple targets across different protocols
targets = [
    CampaignTarget(
        name="iot-coap-device",
        protocol="coap",
        endpoint="coap://192.168.1.100:5683"
    ),
    CampaignTarget(
        name="scada-modbus-server",
        protocol="modbus",
        endpoint="modbus://192.168.1.200:502"
    ),
    CampaignTarget(
        name="mqtt-broker",
        protocol="mqtt",
        endpoint="mqtt://192.168.1.150:1883"
    ),
    CampaignTarget(
        name="http-api",
        protocol="http",
        endpoint="http://192.168.1.180:8080/api"
    )
]

# Run coordinated campaign
summary = coordinator.run_campaign(targets)

# Analyze results
for execution in summary.executions:
    print(f"\nTarget: {execution.target.name}")
    print(f"  Protocol: {execution.target.protocol}")
    print(f"  Success: {execution.execution.success}")
    print(f"  Defense Verdict: {execution.defense.verdict if execution.defense else 'N/A'}")
    print(f"  Judgment Score: {execution.judgment.score}")
```

#### Accessing Detailed Results

```python
# Run campaign
summary = coordinator.run_campaign(targets)

# Export to dictionary
results_dict = summary.to_dict()

# Save to JSON
import json
with open('campaign_results.json', 'w') as f:
    json.dump(results_dict, f, indent=2)

# Analyze individual executions
for execution in summary.executions:
    detail_dict = execution.to_dict()

    # Access execution details
    print(f"Request ID: {detail_dict['request_id']}")
    print(f"Payload: {detail_dict['payload']}")

    # Access execution results
    exec_result = detail_dict['execution']
    print(f"Success: {exec_result['success']}")
    print(f"Output: {exec_result['output']}")

    # Access defense analysis
    defense = detail_dict['defense']
    print(f"Verdict: {defense['verdict']}")
    print(f"Risk Score: {defense['risk_score']}")

    # Access LLM judgment
    judgment = detail_dict['judgment']
    print(f"Score: {judgment['score']}")
    print(f"Reasoning: {judgment['reasoning']}")
```

### Command Line Interface

The coordinator can also be run directly from the command line for quick testing and automation.

#### Basic Usage

```bash
# Run from project root
python -m coordinator.coordinator
```

This will execute a default demo campaign with CoAP and Modbus targets.

#### Using Configuration Files

```bash
# Run with custom configuration
python -m coordinator.coordinator --plan configs/campaign_demo.yaml
```

#### Configuration File Format

Create a YAML configuration file to define campaign parameters:

```yaml
# campaign_config.yaml
campaign:
  name: "Multi-Protocol Security Assessment"
  description: "Comprehensive fuzzing of IoT and industrial control systems"

targets:
  - name: "building-automation-coap"
    protocol: "coap"
    endpoint: "coap://192.168.1.100:5683"

  - name: "hvac-modbus-controller"
    protocol: "modbus"
    endpoint: "modbus://192.168.1.200:502"

  - name: "sensor-mqtt-gateway"
    protocol: "mqtt"
    endpoint: "mqtt://192.168.1.150:1883"

fuzzing:
  model: "mistral"
  strategy: "adaptive"
  timeout: 30
  max_retries: 3

judge:
  model: "gpt-4"
  criteria:
    - effectiveness
    - coverage
    - stability

feedback_loop:
  enabled: true
  learning_rate: 0.1
```

### Integration with Testing

The coordinator integrates seamlessly with pytest for automated testing.

#### Basic Test

```python
# tests/test_coordinator.py
import pytest
from coordinator import FuzzingCoordinator, CampaignTarget

def test_coap_campaign():
    """Test CoAP fuzzing campaign."""
    coordinator = FuzzingCoordinator()

    targets = [
        CampaignTarget(
            name="test-coap",
            protocol="coap",
            endpoint="coap://localhost:5683"
        )
    ]

    summary = coordinator.run_campaign(targets)

    # Assertions
    assert len(summary.executions) > 0
    assert summary.average_judgment_score() >= 0.0
    assert summary.verdict_breakdown() is not None
```

#### Run Tests

```bash
# Run coordinator tests
pytest tests/test_coordinator.py -v

# Run all integration tests
pytest tests/ -v -k "coordinator"
```

## API Reference

### FuzzingCoordinator

Main coordination engine for campaign execution.

#### Constructor

```python
FuzzingCoordinator(*, model_name: str = "mistral")
```

**Parameters:**
- `model_name` (str, optional): LLM model to use for payload generation and judgment. Default: "mistral"

**Example:**
```python
coordinator = FuzzingCoordinator(model_name="gpt-4")
```

#### Methods

##### run_campaign

```python
run_campaign(targets: Sequence[CampaignTarget]) -> CampaignRunSummary
```

Execute a coordinated fuzzing campaign across multiple targets.

**Parameters:**
- `targets`: Sequence of `CampaignTarget` objects defining what to fuzz

**Returns:**
- `CampaignRunSummary`: Comprehensive campaign results with execution details, statistics, and feedback history

**Example:**
```python
summary = coordinator.run_campaign([
    CampaignTarget(name="target1", protocol="coap", endpoint="coap://host1"),
    CampaignTarget(name="target2", protocol="modbus", endpoint="modbus://host2")
])
```

### CampaignTarget

Specification of a fuzzing target.

#### Constructor

```python
CampaignTarget(name: str, protocol: str, endpoint: str)
```

**Parameters:**
- `name` (str): Human-readable target identifier
- `protocol` (str): Protocol name (coap, modbus, mqtt, http, etc.)
- `endpoint` (str): Target URL or connection string

**Example:**
```python
target = CampaignTarget(
    name="production-coap-server",
    protocol="coap",
    endpoint="coap://192.168.1.100:5683/sensor"
)
```

### ExecutionDetail

Detailed record of a single payload execution.

#### Attributes

- `target` (CampaignTarget): Target that was fuzzed
- `payload` (str): Generated payload
- `request_id` (str): Unique execution identifier
- `request_parameters` (Dict[str, str]): Protocol-specific parameters
- `execution` (ExecutionResult): Execution outcome from client
- `defense` (Optional[DefenseResult]): Defense system analysis
- `judgment` (Judgment): LLM judgment of execution quality

#### Methods

##### to_dict

```python
to_dict() -> Dict[str, object]
```

Export execution detail to dictionary format.

**Returns:**
- Dictionary containing all execution information

**Example:**
```python
detail_dict = execution.to_dict()
print(json.dumps(detail_dict, indent=2))
```

### CampaignRunSummary

Aggregated summary of campaign execution.

#### Attributes

- `executions` (List[ExecutionDetail]): All execution details
- `feedback_history` (List[str]): Feedback loop history

#### Methods

##### verdict_breakdown

```python
verdict_breakdown() -> Dict[str, int]
```

Get count of each defense verdict.

**Returns:**
- Dictionary mapping verdict names to counts

**Example:**
```python
breakdown = summary.verdict_breakdown()
# {'monitor': 850, 'investigate': 6, 'block': 0, 'escalate': 0}
```

##### average_judgment_score

```python
average_judgment_score() -> float
```

Calculate average LLM judgment score across all executions.

**Returns:**
- Average score (0.0 to 1.0)

**Example:**
```python
avg_score = summary.average_judgment_score()
print(f"Average quality: {avg_score:.2f}")
```

##### to_dict

```python
to_dict() -> Dict[str, object]
```

Export summary to dictionary format.

**Returns:**
- Dictionary containing executions, feedback, statistics

**Example:**
```python
summary_dict = summary.to_dict()
with open('results.json', 'w') as f:
    json.dump(summary_dict, f, indent=2)
```

## Advanced Topics

### Custom Defense Modules

You can extend the coordinator with custom defense modules:

```python
from coordinator import FuzzingCoordinator
from hyfuzz_server.defense.defense_integrator import BaseDefenseModule

class CustomDefenseModule(BaseDefenseModule):
    def handle_signal(self, signal):
        # Custom defense logic
        return DefenseResult(...)

# Register custom module
coordinator = FuzzingCoordinator()
coordinator.defense_integrator.register_integrator("custom", CustomDefenseModule())
```

### Custom Protocol Handlers

Add support for new protocols:

1. **Implement server-side handler** in `HyFuzz-Windows-Server/src/protocols/`
2. **Implement client-side handler** in `HyFuzz-Ubuntu-Client/src/protocols/`
3. **Register protocol** in protocol registry
4. **Use in campaigns**:

```python
target = CampaignTarget(
    name="my-custom-protocol",
    protocol="custom",
    endpoint="custom://target:port"
)
```

### Feedback Loop Customization

Customize the feedback loop behavior:

```python
coordinator = FuzzingCoordinator()

# Access feedback loop
feedback_loop = coordinator.feedback_loop

# Add custom feedback
feedback_loop.add_feedback("custom:high-value-finding")

# Access history
print(feedback_loop.history)
```

## Extending the Coordinator

### Adding New Features

1. **Identify the requirement**: Determine what functionality is needed
2. **Update coordinator.py**: Add methods or attributes to `FuzzingCoordinator`
3. **Update data models**: Modify `ExecutionDetail` or `CampaignRunSummary` if needed
4. **Add tests**: Create tests in `tests/test_coordinator.py`
5. **Update documentation**: Document new features in this README

### Contributing

When extending the coordinator:

1. Maintain backward compatibility
2. Add comprehensive docstrings
3. Include usage examples
4. Update type hints
5. Add tests for new functionality
6. Update this README

## Troubleshooting

### Import Errors

If you encounter import errors:

```python
ModuleNotFoundError: No module named 'hyfuzz_server'
```

**Solution**: The coordinator automatically manages namespaces. Ensure you're running from the project root and both components are installed.

### Connection Issues

If targets are unreachable:

```python
ConnectionError: Failed to connect to coap://target:5683
```

**Solutions:**
- Verify target is running and accessible
- Check firewall rules
- Confirm protocol and port are correct
- Test with a local mock target first

### Performance Issues

For large campaigns:

1. **Reduce parallelism**: Lower the number of concurrent executions
2. **Increase timeouts**: Some targets may need longer response times
3. **Filter targets**: Focus on specific protocols or endpoints
4. **Use caching**: Enable result caching where applicable

## Examples

### Complete Campaign Script

```python
#!/usr/bin/env python3
"""Complete campaign automation script."""

import json
import sys
from pathlib import Path
from coordinator import FuzzingCoordinator, CampaignTarget

def main():
    # Initialize coordinator
    coordinator = FuzzingCoordinator(model_name="mistral")

    # Load targets from configuration
    targets = [
        CampaignTarget(
            name=f"target-{i}",
            protocol="coap",
            endpoint=f"coap://192.168.1.{100+i}:5683"
        )
        for i in range(5)
    ]

    print(f"Starting campaign with {len(targets)} targets...")

    # Run campaign
    summary = coordinator.run_campaign(targets)

    # Display results
    print(f"\n{'='*60}")
    print("Campaign Results")
    print(f"{'='*60}")
    print(f"Total Executions: {len(summary.executions)}")
    print(f"Average Judgment: {summary.average_judgment_score():.2f}")
    print(f"\nVerdict Breakdown:")
    for verdict, count in summary.verdict_breakdown().items():
        print(f"  {verdict}: {count}")

    # Save results
    output_file = Path("results") / "campaign_results.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(summary.to_dict(), f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Related Documentation

- **Main README**: [`../README.md`](../README.md) - Project overview and setup
- **Server Documentation**: [`../HyFuzz-Windows-Server/README.md`](../HyFuzz-Windows-Server/README.md) - Server component details
- **Client Documentation**: [`../HyFuzz-Ubuntu-Client/README.md`](../HyFuzz-Ubuntu-Client/README.md) - Client component details
- **API Reference**: [`../API.md`](../API.md) - Complete API documentation
- **Deployment Guide**: [`../DEPLOYMENT.md`](../DEPLOYMENT.md) - Deployment instructions
- **Troubleshooting**: [`../TROUBLESHOOTING.md`](../TROUBLESHOOTING.md) - Common issues and solutions

## Support

For questions, issues, or contributions:

1. Check this README and related documentation
2. Review existing issues and discussions
3. Consult the troubleshooting guide
4. Open a new issue with detailed information

---

**Last Updated**: 2024-01-01
**Version**: 1.0.0
**Maintainers**: HyFuzz Development Team
