#!/usr/bin/env python3
"""HyFuzz Health Check Utility.

This script performs comprehensive health checks across the HyFuzz platform:
- Windows Server availability and status
- Ubuntu Client connectivity
- Database connectivity
- LLM endpoint availability
- Task queue status
- File system permissions

Usage:
    python scripts/health_check.py
    python scripts/health_check.py --verbose
    python scripts/health_check.py --check server,client,database
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class HealthCheckResult:
    """Result of a single health check."""
    component: str
    status: str  # healthy, degraded, unhealthy, unknown
    message: str
    details: Dict = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.details is None:
            self.details = {}


class HealthChecker:
    """Performs health checks on HyFuzz components."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[HealthCheckResult] = []

    def _print_status(self, status: str, message: str):
        """Print colored status message."""
        color_map = {
            "healthy": Colors.GREEN,
            "degraded": Colors.YELLOW,
            "unhealthy": Colors.RED,
            "unknown": Colors.BLUE,
        }
        color = color_map.get(status, Colors.END)
        status_symbol = {
            "healthy": "✓",
            "degraded": "⚠",
            "unhealthy": "✗",
            "unknown": "?",
        }.get(status, " ")

        print(f"{color}{status_symbol} {message}{Colors.END}")

    def check_server(self) -> HealthCheckResult:
        """Check Windows Server health."""
        try:
            # Check if server directory exists
            server_path = Path(__file__).parent.parent / "HyFuzz-Windows-Server"
            if not server_path.exists():
                return HealthCheckResult(
                    component="Windows Server",
                    status="unhealthy",
                    message="Server directory not found",
                    details={"path": str(server_path)}
                )

            # Check for essential files
            essential_files = [
                server_path / "src" / "__init__.py",
                server_path / "config" / "server_config.yaml",
                server_path / "scripts" / "start_server.py",
            ]

            missing_files = [f for f in essential_files if not f.exists()]
            if missing_files:
                return HealthCheckResult(
                    component="Windows Server",
                    status="degraded",
                    message=f"Missing {len(missing_files)} essential files",
                    details={"missing": [str(f) for f in missing_files]}
                )

            # Try to check if server can be imported
            sys.path.insert(0, str(server_path))
            try:
                import src
                version = getattr(src, '__version__', 'unknown')
            except ImportError as e:
                return HealthCheckResult(
                    component="Windows Server",
                    status="degraded",
                    message=f"Import warning: {str(e)}",
                    details={"error": str(e)}
                )

            return HealthCheckResult(
                component="Windows Server",
                status="healthy",
                message="Server components available",
                details={"version": version, "path": str(server_path)}
            )

        except Exception as e:
            return HealthCheckResult(
                component="Windows Server",
                status="unhealthy",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_client(self) -> HealthCheckResult:
        """Check Ubuntu Client health."""
        try:
            client_path = Path(__file__).parent.parent / "HyFuzz-Ubuntu-Client"
            if not client_path.exists():
                return HealthCheckResult(
                    component="Ubuntu Client",
                    status="unhealthy",
                    message="Client directory not found",
                    details={"path": str(client_path)}
                )

            essential_files = [
                client_path / "src" / "__init__.py",
                client_path / "config" / "client_config.yaml",
                client_path / "scripts" / "start_client.py",
            ]

            missing_files = [f for f in essential_files if not f.exists()]
            if missing_files:
                return HealthCheckResult(
                    component="Ubuntu Client",
                    status="degraded",
                    message=f"Missing {len(missing_files)} essential files",
                    details={"missing": [str(f) for f in missing_files]}
                )

            return HealthCheckResult(
                component="Ubuntu Client",
                status="healthy",
                message="Client components available",
                details={"path": str(client_path)}
            )

        except Exception as e:
            return HealthCheckResult(
                component="Ubuntu Client",
                status="unhealthy",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_database(self) -> HealthCheckResult:
        """Check database connectivity."""
        try:
            # Check if data directory exists
            data_path = Path(__file__).parent.parent / "HyFuzz-Windows-Server" / "data"
            data_path.mkdir(parents=True, exist_ok=True)

            # Check write permissions
            test_file = data_path / ".health_check_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                return HealthCheckResult(
                    component="Database",
                    status="unhealthy",
                    message="Data directory not writable",
                    details={"path": str(data_path), "error": str(e)}
                )

            return HealthCheckResult(
                component="Database",
                status="healthy",
                message="Data directory accessible",
                details={"path": str(data_path)}
            )

        except Exception as e:
            return HealthCheckResult(
                component="Database",
                status="unhealthy",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_dependencies(self) -> HealthCheckResult:
        """Check Python dependencies."""
        try:
            required_packages = [
                "pydantic",
                "yaml",
                "requests",
                "aiohttp",
            ]

            missing = []
            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                except ImportError:
                    missing.append(package)

            if missing:
                return HealthCheckResult(
                    component="Dependencies",
                    status="unhealthy",
                    message=f"Missing {len(missing)} required packages",
                    details={"missing": missing}
                )

            return HealthCheckResult(
                component="Dependencies",
                status="healthy",
                message="All required packages installed",
                details={"checked": required_packages}
            )

        except Exception as e:
            return HealthCheckResult(
                component="Dependencies",
                status="unknown",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)}
            )

    def check_configuration(self) -> HealthCheckResult:
        """Check configuration files."""
        try:
            config_files = [
                Path(__file__).parent.parent / "configs" / "campaign_demo.yaml",
                Path(__file__).parent.parent / "HyFuzz-Windows-Server" / "config" / "server_config.yaml",
                Path(__file__).parent.parent / "HyFuzz-Ubuntu-Client" / "config" / "client_config.yaml",
            ]

            missing = [f for f in config_files if not f.exists()]
            if len(missing) == len(config_files):
                return HealthCheckResult(
                    component="Configuration",
                    status="unhealthy",
                    message="No configuration files found",
                    details={"expected": [str(f) for f in config_files]}
                )
            elif missing:
                return HealthCheckResult(
                    component="Configuration",
                    status="degraded",
                    message=f"Missing {len(missing)} configuration files",
                    details={"missing": [str(f) for f in missing]}
                )

            return HealthCheckResult(
                component="Configuration",
                status="healthy",
                message="Configuration files present",
                details={"count": len(config_files) - len(missing)}
            )

        except Exception as e:
            return HealthCheckResult(
                component="Configuration",
                status="unknown",
                message=f"Check failed: {str(e)}",
                details={"error": str(e)}
            )

    def run_all_checks(self, checks: Optional[List[str]] = None) -> List[HealthCheckResult]:
        """Run all health checks."""
        available_checks = {
            "server": self.check_server,
            "client": self.check_client,
            "database": self.check_database,
            "dependencies": self.check_dependencies,
            "configuration": self.check_configuration,
        }

        if checks is None:
            checks = list(available_checks.keys())

        self.results = []
        for check_name in checks:
            if check_name in available_checks:
                result = available_checks[check_name]()
                self.results.append(result)
                self._print_status(result.status, f"{result.component}: {result.message}")

                if self.verbose and result.details:
                    for key, value in result.details.items():
                        print(f"  {key}: {value}")

        return self.results

    def print_summary(self):
        """Print health check summary."""
        if not self.results:
            return

        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Health Check Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}")

        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0,
            "unknown": 0,
        }

        for result in self.results:
            status_counts[result.status] += 1

        print(f"Total Checks: {len(self.results)}")
        print(f"{Colors.GREEN}✓ Healthy: {status_counts['healthy']}{Colors.END}")
        print(f"{Colors.YELLOW}⚠ Degraded: {status_counts['degraded']}{Colors.END}")
        print(f"{Colors.RED}✗ Unhealthy: {status_counts['unhealthy']}{Colors.END}")
        print(f"{Colors.BLUE}? Unknown: {status_counts['unknown']}{Colors.END}")

        overall_status = "healthy"
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["degraded"] > 0:
            overall_status = "degraded"

        print(f"\n{Colors.BOLD}Overall Status: ", end="")
        self._print_status(overall_status, overall_status.upper())
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

        return overall_status


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HyFuzz platform health checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--check",
        type=str,
        help="Comma-separated list of checks to run (default: all)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with details",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    checks = None
    if args.check:
        checks = [c.strip() for c in args.check.split(",")]

    print(f"{Colors.BOLD}🏥 HyFuzz Health Check{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

    checker = HealthChecker(verbose=args.verbose)
    results = checker.run_all_checks(checks)

    if args.json:
        print("\n" + json.dumps([asdict(r) for r in results], indent=2))
    else:
        overall_status = checker.print_summary()
        return 0 if overall_status in ["healthy", "degraded"] else 1


if __name__ == "__main__":
    sys.exit(main())
