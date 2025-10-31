#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HyFuzz MCP Server - Python Package Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Get the long description from README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Get version from package
version_file = Path(__file__).parent / "src" / "__version__.py"
if version_file.exists():
    version_data = {}
    exec(version_file.read_text(), version_data)
    version = version_data.get("__version__", "1.0.0")
else:
    version = "1.0.0"

# Core dependencies
install_requires = [
    "requests>=2.28.0",
    "aiohttp>=3.8.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
    "PyYAML>=6.0.0",
    "tiktoken>=0.5.0",
    "jsonschema>=4.20.0",
    "numpy>=1.26.0",
    "pandas>=2.1.0",
    "networkx>=3.2",
    "cachetools>=5.3.0",
    "python-json-logger>=2.0.0",
    "click>=8.1.0",
    "colorama>=0.4.6",
    "decorator>=5.1.0",
]

# Development dependencies
extras_require = {
    "dev": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-xdist>=3.5.0",
        "pytest-mock>=3.12.0",
        "black>=23.12.0",
        "flake8>=6.1.0",
        "mypy>=1.7.0",
        "isort>=5.13.0",
        "pylint>=3.0.0",
        "Sphinx>=7.2.0",
        "sphinx-rtd-theme>=2.0.0",
        "ipython>=8.18.0",
        "jupyter>=1.0.0",
        "jupyterlab>=4.0.0",
    ],
    "docs": [
        "Sphinx>=7.2.0",
        "sphinx-rtd-theme>=2.0.0",
        "sphinx-markdown-parser>=0.2.0",
    ],
    "test": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-xdist>=3.5.0",
        "pytest-mock>=3.12.0",
        "responses>=0.24.0",
    ],
}

# All dependencies combined
extras_require["all"] = []
for deps in extras_require.values():
    extras_require["all"].extend(deps)

setup(
    # Package metadata
    name="hyfuzz-server",
    version=version,
    description="HyFuzz MCP Server - Intelligent Payload Generation with LLM",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Package author
    author="HyFuzz Team",
    author_email="team@hyfuzz.org",
    url="https://github.com/your-org/hyfuzz-server-windows",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/hyfuzz-server-windows/issues",
        "Documentation": "https://docs.hyfuzz.org",
        "Source Code": "https://github.com/your-org/hyfuzz-server-windows",
    },

    # License
    license="MIT",

    # Classification
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
        "Topic :: System :: Networking",
    ],

    # Keywords
    keywords=[
        "mcp",
        "model-context-protocol",
        "fuzzing",
        "llm",
        "deepseek",
        "ollama",
        "hyfuzz",
        "security",
        "testing",
    ],

    # Package discovery
    packages=find_packages(
        where=".",
        include=["src*"],
        exclude=["tests*", "docs*", "scripts*"],
    ),
    package_dir={
        "": ".",
    },

    # Include package data
    include_package_data=True,
    package_data={
        "src": [
            "config/default_config.yaml",
            "config/logging_config.yaml",
            "data/sample_cwe.json",
            "data/sample_cve.json",
        ],
    },

    # Python requirement (only define once!)
    python_requires=">=3.9,<4.0",

    # Dependencies
    install_requires=install_requires,
    extras_require=extras_require,

    # Entry points
    entry_points={
        "console_scripts": [
            "hyfuzz-server=src.__main__:main",
        ],
    },

    # Additional options
    zip_safe=False,

    # URLs
    download_url="https://github.com/your-org/hyfuzz-server-windows/releases",
)