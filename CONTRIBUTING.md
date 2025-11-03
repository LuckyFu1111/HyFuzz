# Contributing to HyFuzz

Thank you for your interest in contributing to HyFuzz! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project follows the code of conduct outlined in [`HyFuzz-Windows-Server/CODE_OF_CONDUCT.md`](HyFuzz-Windows-Server/CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Docker (optional, for containerized development)
- Ollama or OpenAI API access (for LLM features)

### First Steps

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/HyFuzz.git
   cd HyFuzz
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/original-org/HyFuzz.git
   ```

4. Create a feature branch from `work`:
   ```bash
   git checkout work
   git pull upstream work
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### 1. Install Dependencies

```bash
# Install Windows Server dependencies
cd HyFuzz-Windows-Server
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Ubuntu Client dependencies
cd ../HyFuzz-Ubuntu-Client
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install testing dependencies
cd ..
pip install pytest pytest-asyncio pytest-cov
```

### 2. Configure Environment

```bash
# Copy environment templates
cp HyFuzz-Windows-Server/.env.example HyFuzz-Windows-Server/.env
cp HyFuzz-Ubuntu-Client/.env.example HyFuzz-Ubuntu-Client/.env

# Edit .env files with your local settings
```

### 3. Verify Installation

```bash
# Run health check
python scripts/health_check.py --verbose

# Run tests
pytest tests/ -v
```

## Contribution Workflow

### 1. Create an Issue

Before starting work, create or comment on an existing issue to:
- Describe the problem or feature
- Discuss the approach
- Get feedback from maintainers

### 2. Develop Your Changes

- Write clean, well-documented code
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_integration.py -v

# Run with coverage
pytest --cov=HyFuzz-Windows-Server/src --cov=HyFuzz-Ubuntu-Client/src

# Run linting
ruff check .
black --check .
mypy HyFuzz-Windows-Server/src
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "Add: Brief description of what you added"
```

Commit message prefixes:
- `Add:` - New features
- `Fix:` - Bug fixes
- `Update:` - Updates to existing features
- `Refactor:` - Code refactoring
- `Docs:` - Documentation changes
- `Test:` - Adding or updating tests
- `Chore:` - Maintenance tasks

### 5. Keep Your Branch Updated

```bash
git fetch upstream
git rebase upstream/work
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Comments**: Write in English, be clear and concise

### Code Formatting

We use automated tools for code formatting:

```bash
# Format code with Black
black HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src phase3

# Sort imports with isort
isort HyFuzz-Windows-Server/src HyFuzz-Ubuntu-Client/src phase3

# Lint with Ruff
ruff check . --fix
```

### Type Hints

Always use type hints:

```python
from typing import Dict, List, Optional

def process_payload(
    payload: str,
    protocol: str,
    timeout: int = 30
) -> Dict[str, any]:
    """Process a fuzzing payload.

    Args:
        payload: Payload data to process
        protocol: Target protocol (coap, modbus, etc.)
        timeout: Execution timeout in seconds

    Returns:
        Dictionary containing execution results

    Raises:
        ValueError: If payload is invalid
        TimeoutError: If execution exceeds timeout
    """
    pass
```

### Documentation

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """Brief description of function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative

    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test interaction between components
- **End-to-end tests**: Test complete workflows

### Writing Tests

```python
import pytest
from your_module import YourClass

class TestYourClass:
    """Test suite for YourClass."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        obj = YourClass()
        result = obj.method()
        assert result is not None

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        obj = YourClass()
        result = await obj.async_method()
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling."""
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.method_that_raises()
```

### Test Coverage

- Aim for >80% code coverage for new features
- Test both success and failure cases
- Test edge cases and boundary conditions

### Running Tests

```bash
# Run all tests
pytest

# Run specific test markers
pytest -m unit
pytest -m integration
pytest -m asyncio

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v -s
```

## Documentation

### Required Documentation

When adding new features, update:

1. **Code docstrings**: Document all public classes and functions
2. **README files**: Update relevant README files
3. **Configuration examples**: Add examples to `.env.example` or config files
4. **QUICKSTART.md**: Update if it affects quick start procedures

### Documentation Style

- Write in English
- Use Markdown for documentation files
- Keep explanations clear and concise
- Include code examples where helpful
- Update table of contents when adding sections

## Pull Request Process

### Before Submitting

Ensure your PR:

- [ ] Passes all tests (`pytest`)
- [ ] Passes linting (`ruff check .`)
- [ ] Is formatted correctly (`black .`)
- [ ] Has appropriate test coverage
- [ ] Updates relevant documentation
- [ ] Has a clear, descriptive title
- [ ] References related issues

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran and how to reproduce.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] I have updated the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs automatically
2. **Code review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, maintainers will merge

### After Merge

- Delete your feature branch
- Update your fork:
  ```bash
  git checkout work
  git pull upstream work
  git push origin work
  ```

## Component-Specific Guidelines

### Windows Server (HyFuzz-Windows-Server)

- Focus on LLM integration, defense systems, orchestration
- Ensure compatibility with Windows and Linux
- Test MCP server functionality thoroughly

### Ubuntu Client (HyFuzz-Ubuntu-Client)

- Focus on payload execution, instrumentation, sandboxing
- Test on Ubuntu 22.04+
- Ensure proper privilege handling for instrumentation

### Phase 3 Coordinator (phase3/)

- Maintain backward compatibility
- Update tests when changing interfaces
- Document protocol-specific behaviors

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with the bug template
- **Features**: Create an issue with the feature request template
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## Recognition

Contributors will be:
- Listed in [`AUTHORS.md`](HyFuzz-Windows-Server/AUTHORS.md)
- Mentioned in release notes for significant contributions
- Eligible for contributor badge/recognition

## Additional Resources

- [Architecture Documentation](HyFuzz-Windows-Server/docs/README.md)
- [Protocol Guide](HyFuzz-Windows-Server/docs/PROTOCOL_GUIDE.md)
- [Defense Integration](HyFuzz-Windows-Server/docs/DEFENSE_INTEGRATION.md)
- [Testing Strategy](tests/README.md)

---

Thank you for contributing to HyFuzz! 🎯
