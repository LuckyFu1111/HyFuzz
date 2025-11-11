# Contributing to HyFuzz

Thank you for your interest in contributing to HyFuzz! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/HyFuzz.git
   cd HyFuzz
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/LuckyFu1111/HyFuzz.git
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## How to Contribute

We accept various types of contributions:

### Bug Fixes
- Fix existing bugs reported in Issues
- Add test cases to prevent regressions
- Update documentation if behavior changes

### New Features
- Discuss major features in GitHub Discussions first
- Keep changes focused and atomic
- Include tests and documentation
- Update relevant README files

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Translate documentation (future)
- Update API documentation

### Testing
- Add unit tests for new code
- Improve test coverage
- Add integration tests
- Performance benchmarking

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Virtual environment tool (venv or conda)

### Component-Specific Setup

Each component has its own development environment:

#### Windows Server
```bash
cd HyFuzz-Windows-Server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-dev.txt
```

#### macOS Server
```bash
cd HyFuzz-Mac-Server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

#### Ubuntu Client
```bash
cd HyFuzz-Ubuntu-Client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Organized using isort
- **Formatting**: Use Black formatter
- **Type hints**: Required for public APIs
- **Docstrings**: Google-style docstrings

### Code Quality Tools

Run these before submitting:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
pylint src/

# Type check
mypy src/

# Security scan
bandit -r src/
```

### Pre-commit Hooks

We use pre-commit hooks to enforce standards:

```bash
pip install pre-commit
pre-commit install
```

This will run automatically on `git commit`.

## Testing Requirements

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run tests matching pattern
pytest -k "test_pattern"
```

### Test Coverage

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage required
- **Integration tests**: Required for new features
- **Documentation tests**: doctest for examples

### Writing Tests

```python
"""Example test following our conventions."""
import pytest
from src.module import function_to_test

def test_function_behavior():
    """Test that function behaves correctly with valid input."""
    result = function_to_test("input")
    assert result == "expected"

def test_function_error_handling():
    """Test that function raises appropriate errors."""
    with pytest.raises(ValueError):
        function_to_test(None)
```

## Submitting Changes

### Commit Messages

Follow the Conventional Commits specification:

```
type(scope): brief description

Longer description if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or tooling changes

**Examples:**
```
feat(server): add support for gRPC protocol
fix(client): resolve crash on malformed payload
docs(readme): update installation instructions
```

### Pull Request Process

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests** and ensure they pass

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results summary

5. **Address review feedback** promptly

6. **Squash commits** if requested before merge

### PR Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No security vulnerabilities introduced
- [ ] Backward compatibility maintained
- [ ] Performance impact considered

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Verify the bug** on the latest version
3. **Check documentation** for known limitations

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - Component: [Windows Server / macOS Server / Ubuntu Client]
 - OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
 - Python Version: [e.g., 3.9.7]
 - HyFuzz Version: [e.g., 2.0.0]

**Additional context**
Any other relevant information.
```

## Feature Requests

### Proposing New Features

1. **Open a Discussion** first for major features
2. **Describe the use case** and benefits
3. **Provide examples** of how it would work
4. **Consider alternatives** you've explored

### Feature Request Template

```markdown
**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
Describe your proposed solution.

**Alternatives Considered**
What alternatives have you considered?

**Additional Context**
Any other relevant information.
```

## Documentation

### Documentation Standards

- **Clear and concise**: Write for clarity
- **Examples**: Include practical examples
- **Up-to-date**: Update docs with code changes
- **Consistent**: Follow existing style
- **Accessible**: Use simple language

### Documentation Locations

- **README files**: Component overviews and setup
- **docs/ folders**: Detailed technical documentation
- **Code comments**: Complex logic explanations
- **Docstrings**: API documentation
- **CHANGELOG.md**: Version history

### Building Documentation

```bash
# Generate API documentation
pdoc --html src/ -o docs/api/

# Build Sphinx docs (if applicable)
cd docs/
make html
```

## Component-Specific Guidelines

For detailed component-specific guidelines, see:

- [Windows Server Contributing](HyFuzz-Windows-Server/CONTRIBUTING.md)
- [macOS Server Contributing](HyFuzz-Mac-Server/CONTRIBUTING.md)
- [Ubuntu Client Contributing](HyFuzz-Ubuntu-Client/CONTRIBUTING.md)

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Contact the maintainers

## Recognition

Contributors will be:
- Listed in AUTHORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing to HyFuzz! 🎉
