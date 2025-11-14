# Fuzzing Tests for HyFuzz

This directory contains comprehensive fuzzing tests for the HyFuzz system, designed to discover bugs, edge cases, and security vulnerabilities through automated testing with malformed, unexpected, and boundary-case inputs.

## Overview

Fuzzing is a software testing technique that provides invalid, unexpected, or random data as inputs to a program. The fuzzing tests in this directory cover:

1. **MCP Protocol Fuzzing** - Tests for Model Context Protocol implementation
2. **Database Fuzzing** - Tests for database operations and SQL injection resistance
3. **Transport Layer Fuzzing** - Tests for stdio, HTTP, and WebSocket transports

## Test Files

### test_mcp_fuzzing.py
Comprehensive fuzzing tests for MCP protocol implementation:
- Message format fuzzing (malformed JSON-RPC messages)
- Parameter injection and manipulation
- Request ID, method name, and params fuzzing
- Batch message processing
- Resource, tool, and prompt handler fuzzing
- Concurrent request fuzzing
- Error handling robustness
- Performance stress testing

### test_database_fuzzing.py
Database operation fuzzing tests:
- SQL injection attack patterns
- Query parameter fuzzing
- Data type and boundary value testing
- Special character handling
- Unicode string support
- Concurrent access testing
- Large data handling
- CVE database specific tests

### test_mcp_transport_fuzzing.py
Transport layer fuzzing tests:
- Message framing fuzzing
- Binary data handling
- HTTP header injection attacks
- WebSocket frame fuzzing
- Content-Length attacks
- Protocol upgrade fuzzing
- Character encoding fuzzing
- Network error simulation

## Running the Tests

### Run All Fuzzing Tests
```bash
cd /home/user/HyFuzz/HyFuzz-Windows-Server
pytest tests/fuzzing/ -v
```

### Run Specific Test File
```bash
# MCP protocol fuzzing
pytest tests/fuzzing/test_mcp_fuzzing.py -v

# Database fuzzing
pytest tests/fuzzing/test_database_fuzzing.py -v

# Transport fuzzing
pytest tests/fuzzing/test_mcp_transport_fuzzing.py -v
```

### Run Specific Test Class
```bash
pytest tests/fuzzing/test_mcp_fuzzing.py::TestMCPMessageFuzzing -v
```

### Run with Coverage
```bash
pytest tests/fuzzing/ --cov=src --cov-report=html
```

### Run with Timeout (Recommended)
Some fuzzing tests may take a long time, so using timeout is recommended:
```bash
pytest tests/fuzzing/ -v --timeout=300
```

## Test Configuration

### Requirements
Install required dependencies:
```bash
pip install pytest pytest-asyncio pytest-timeout pytest-cov
```

### Environment Variables
Some tests may use environment variables for configuration:
```bash
export FUZZING_ITERATIONS=1000  # Number of fuzzing iterations
export FUZZING_TIMEOUT=60       # Timeout per test in seconds
```

## Fuzzing Strategies

### 1. Random Fuzzing
Generates completely random data to find unexpected crashes:
- Random strings, integers, floats
- Random dictionary structures
- Random JSON objects

### 2. Mutation-Based Fuzzing
Takes valid inputs and mutates them:
- Bit flipping
- Byte insertion/deletion
- Format string manipulation

### 3. Grammar-Based Fuzzing
Uses protocol specifications to generate semi-valid inputs:
- JSON-RPC 2.0 protocol format
- MCP message structure
- SQL query syntax

### 4. Attack Pattern Fuzzing
Tests known vulnerability patterns:
- SQL injection patterns
- XSS attempts
- Path traversal
- Command injection
- Header injection

## Expected Behavior

### Good Test Results
Tests should:
- **Never crash** with unhandled exceptions
- **Return proper errors** for invalid inputs
- **Maintain data integrity** even with malicious inputs
- **Handle edge cases** gracefully
- **Prevent injection attacks** through parameterization

### Potential Issues to Watch For
- Unhandled exceptions
- Resource leaks (memory, file descriptors)
- Deadlocks in concurrent tests
- Data corruption
- Injection vulnerabilities
- Denial of service conditions

## Interpreting Results

### Test Pass
```
✓ Test passed - System handled fuzzed input correctly
```

### Test Failure
```
✗ Test failed - Unexpected behavior detected
```

### Important Metrics
1. **Pass Rate**: Percentage of fuzzing inputs handled correctly
2. **Error Types**: Categories of errors encountered
3. **Performance**: Response time under fuzzing stress
4. **Coverage**: Code paths exercised by fuzzing

## Security Considerations

These fuzzing tests include:
- **SQL Injection Patterns**: Tests that database operations are properly parameterized
- **XSS Attempts**: Tests that input is properly sanitized
- **Path Traversal**: Tests that file paths are validated
- **Command Injection**: Tests that system commands are properly escaped
- **Header Injection**: Tests that HTTP headers are validated

## Performance Testing

Fuzzing tests also serve as performance tests:
- High-volume message processing
- Concurrent request handling
- Large data processing
- Resource usage under stress

## Continuous Integration

To integrate with CI/CD:
```yaml
# Example GitHub Actions workflow
- name: Run Fuzzing Tests
  run: |
    pytest tests/fuzzing/ -v --timeout=300 --junitxml=fuzzing-results.xml
```

## Troubleshooting

### Tests Timing Out
```bash
# Increase timeout
pytest tests/fuzzing/ --timeout=600
```

### Memory Issues
```bash
# Run tests sequentially
pytest tests/fuzzing/ -v --maxfail=1
```

### Debug Specific Failure
```bash
# Run with verbose output and stop on first failure
pytest tests/fuzzing/test_mcp_fuzzing.py -vv -x --tb=long
```

## Contributing

When adding new fuzzing tests:
1. Follow existing test structure
2. Document what vulnerability/bug you're testing for
3. Include both positive and negative test cases
4. Add timeout decorators for long-running tests
5. Clean up resources properly (databases, files, etc.)

## References

- [OWASP Fuzzing Guide](https://owasp.org/www-community/Fuzzing)
- [Python Fuzzing Best Practices](https://docs.python.org/3/library/unittest.html)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

## License

Same as parent project - see main LICENSE file.
