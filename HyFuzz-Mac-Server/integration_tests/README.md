# HyFuzz Test Suite

## Overview

The root-level `tests/` directory provides comprehensive integration and end-to-end testing for the HyFuzz platform. These tests ensure that the campaign coordinator, server components, client execution engine, and all protocol handlers work together correctly across the distributed system.

## Purpose

This test suite validates:
- **Cross-component Integration**: Server and client interaction through the coordinator
- **Protocol Compatibility**: All supported protocols (CoAP, Modbus, MQTT, HTTP) work correctly
- **Defense System Integration**: Defense modules correctly analyze execution results
- **LLM Integration**: Payload generation and judgment functionality
- **Configuration Consistency**: All configuration files are valid and complete
- **End-to-End Workflows**: Complete campaign execution from creation to completion

## Test Structure

### Integration Tests

| Test File | Purpose | Components Tested |
|-----------|---------|-------------------|
| [`test_coordinator.py`](test_coordinator.py) | Campaign coordination across multiple protocols | Coordinator, Server, Client |
| [`test_integration.py`](test_integration.py) | Platform-wide integration checks | All components |

### What Gets Tested

**test_coordinator.py**:
- Multi-protocol campaign execution (CoAP, Modbus)
- Payload generation through LLM integration
- Defense verdict correlation
- Execution result aggregation
- Feedback loop functionality
- Campaign statistics and summaries

**test_integration.py**:
- Project structure validation
- Configuration file existence and validity
- Script availability and syntax
- Module imports
- Documentation completeness
- Git ignore rules

## Running Tests

### Run All Tests

From the repository root:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=coordinator --cov=HyFuzz-Windows-Server/src --cov=HyFuzz-Ubuntu-Client/src
```

### Run Specific Test Suites

```bash
# Run coordinator tests only
pytest tests/test_coordinator.py -v

# Run integration tests only
pytest tests/test_integration.py -v

# Run tests matching a pattern
pytest -k "coordinator" -v

# Run integration-marked tests only
pytest -m integration -v
```

### Run with Different Options

```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest -l

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Generate HTML coverage report
pytest --cov=coordinator --cov-report=html
```

## Test Configuration

### pytest Configuration

The repository includes a `conftest.py` at the root level that:
- Configures Python path for importing coordinator, server, and client modules
- Sets up test fixtures
- Configures pytest markers

### Test Markers

Available markers:
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.asyncio`: Asynchronous tests
- `@pytest.mark.slow`: Long-running tests

## Writing New Tests

### 1. Create Test File

Follow pytest naming conventions (`test_*.py`):

```python
# tests/test_my_feature.py
"""
Tests for my new feature.

This module tests the integration between...
"""
import pytest
from coordinator import FuzzingCoordinator, CampaignTarget


@pytest.mark.integration
def test_my_feature():
    """Test description."""
    # Arrange
    coordinator = FuzzingCoordinator(model_name="test")

    # Act
    result = coordinator.run_campaign([...])

    # Assert
    assert result is not None
```

### 2. Import Components

Import from the appropriate modules:

```python
# Coordinator
from coordinator import FuzzingCoordinator, CampaignTarget, CampaignRunSummary

# Server components (if needed)
from hyfuzz_server.llm import PayloadGenerator
from hyfuzz_server.defense import DefenseIntegrator

# Client components (if needed)
from hyfuzz_client.execution import Orchestrator
```

### 3. Add Test Documentation

- Add docstrings to test functions
- Document what is being tested
- Include expected outcomes
- Note any dependencies or prerequisites

### 4. Update This README

When adding new test files:
1. Add entry to the test structure table
2. Document what the test covers
3. Add any new pytest markers used
4. Update running instructions if needed

## Test Data

### Mock Data

Tests use mock data and test models:
- `model_name="test"` or `model_name="test-model"` for LLM operations
- Mock targets: `coap://demo`, `modbus://demo`, etc.
- Test payloads are auto-generated

### Configuration Files

Tests validate real configuration files:
- `configs/campaign_demo.yaml`
- `HyFuzz-Windows-Server/.env.example`
- `HyFuzz-Ubuntu-Client/.env.example`

## Continuous Integration

These tests run automatically on:
- Every push to main, work, or develop branches
- Every pull request
- Manual workflow dispatch

See `.github/workflows/ci.yml` for the complete CI/CD pipeline.

## Test Coverage Goals

Target coverage:
- **Coordinator**: 90%+
- **Server**: 85%+
- **Client**: 80%+
- **Integration**: 75%+

View coverage report:
```bash
pytest --cov=coordinator --cov-report=term --cov-report=html
open htmlcov/index.html  # View detailed report
```

## Troubleshooting

### Import Errors

If you encounter import errors:

```python
ModuleNotFoundError: No module named 'coordinator'
```

**Solution**: Ensure you're running from the repository root and `conftest.py` is present.

### Missing Dependencies

```bash
# Install test dependencies
pip install -r HyFuzz-Windows-Server/requirements-dev.txt
pip install pytest pytest-asyncio pytest-cov
```

### Test Failures

For test failures:
1. Run with `-v` for verbose output
2. Use `-l` to show local variables
3. Check the test logs in CI artifacts
4. Ensure all services are properly configured

## Best Practices

### Test Independence

- Each test should be independent
- Don't rely on test execution order
- Clean up resources after tests
- Use fixtures for common setup

### Test Naming

- Use descriptive names: `test_coordinator_multi_protocol_campaign`
- Follow pattern: `test_<what>_<condition>_<expected_result>`
- Be specific about what is being tested

### Assertions

- Use specific assertions: `assert len(summary.executions) == 2`
- Include helpful messages: `assert value > 0, "Score should be positive"`
- Test both positive and negative cases

### Documentation

- Add docstrings to all test functions
- Document any special setup or teardown
- Explain complex test logic
- Link to related issues or PRs

## Related Documentation

- **Contributing Guide**: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
- **Coordinator Documentation**: [`../coordinator/README.md`](../coordinator/README.md)
- **CI/CD Pipeline**: [`../.github/workflows/ci.yml`](../.github/workflows/ci.yml)
- **Troubleshooting**: [`../TROUBLESHOOTING.md`](../TROUBLESHOOTING.md)

## Support

For questions about testing:
1. Check this README
2. Review existing tests for examples
3. Consult the contributing guide
4. Open a discussion on GitHub

---

**Keep this README updated as tests evolve!**

Last Updated: 2024-01-01
