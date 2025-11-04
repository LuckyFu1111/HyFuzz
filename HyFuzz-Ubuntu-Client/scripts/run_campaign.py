#!/usr/bin/env python3
"""HyFuzz Ubuntu Client Campaign Runner.

This script executes fuzzing campaigns on the Ubuntu client side by:
- Receiving payload execution requests from the Windows server
- Running payloads in sandboxed environments
- Capturing instrumentation data (strace, ltrace, coverage)
- Monitoring for crashes and anomalies
- Sending results back to the server

Usage:
    python run_campaign.py --server http://localhost:8080
    python run_campaign.py --config config/campaign.yaml
    python run_campaign.py --protocol coap --target localhost:5683
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class CampaignConfig:
    """Configuration for client-side campaign execution."""

    server_url: str = "http://localhost:8080"
    protocol: str = "coap"
    target: str = "localhost:5683"
    max_executions: int = 100
    timeout: int = 30
    sandbox_enabled: bool = True
    instrumentation_enabled: bool = True
    log_level: str = "INFO"


class ClientCampaignRunner:
    """Client-side campaign executor."""

    def __init__(self, config: CampaignConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.executed_count = 0

    def _setup_logging(self) -> logging.Logger:
        """Initialize logging configuration."""
        log_path = PROJECT_ROOT / "logs" / "campaign_client.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(levelname)s - [Client] - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_path, encoding="utf-8"),
            ],
        )
        return logging.getLogger("hyfuzz.client.campaign")

    def execute_payload(self, payload: Dict) -> Dict:
        """Execute a single payload.

        Args:
            payload: Payload data including protocol, target, and data

        Returns:
            Execution result dictionary
        """
        payload_id = payload.get("id", "unknown")
        self.logger.info(f"Executing payload: {payload_id}")

        # Mock execution for now
        # In real implementation, this would call the Orchestrator
        result = {
            "payload_id": payload_id,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "output": f"Mock execution result for {payload_id}",
            "exit_code": 0,
            "execution_time_ms": 15,
            "instrumentation": {
                "syscalls": ["open", "read", "write", "close"],
                "network_calls": ["socket", "connect", "send", "recv"],
                "crashes": [],
            },
        }

        self.executed_count += 1
        return result

    def run(self) -> int:
        """Run the campaign."""
        self.logger.info("Starting client campaign")
        self.logger.info(f"Server: {self.config.server_url}")
        self.logger.info(f"Protocol: {self.config.protocol}")
        self.logger.info(f"Target: {self.config.target}")

        # Mock campaign execution
        mock_payloads = [
            {"id": f"payload-{i}", "protocol": self.config.protocol, "data": f"test{i}"}
            for i in range(min(10, self.config.max_executions))
        ]

        results = []
        for payload in mock_payloads:
            result = self.execute_payload(payload)
            results.append(result)

        self.logger.info(f"Campaign completed: {self.executed_count} payloads executed")

        # Save results
        output_file = PROJECT_ROOT / "results" / f"client_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Results saved to: {output_file}")
        return 0


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HyFuzz Ubuntu Client campaign runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--server",
        type=str,
        default="http://localhost:8080",
        help="Server URL (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--protocol",
        type=str,
        default="coap",
        help="Protocol to test (default: coap)",
    )
    parser.add_argument(
        "--target",
        type=str,
        default="localhost:5683",
        help="Target endpoint (default: localhost:5683)",
    )
    parser.add_argument(
        "--max-executions",
        type=int,
        default=100,
        help="Maximum number of payloads to execute (default: 100)",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    config = CampaignConfig(
        server_url=args.server,
        protocol=args.protocol,
        target=args.target,
        max_executions=args.max_executions,
        log_level=args.log_level,
    )

    runner = ClientCampaignRunner(config)

    print("🚀 Starting HyFuzz Client Campaign")
    print(f"   Server: {config.server_url}")
    print(f"   Protocol: {config.protocol}")
    print(f"   Target: {config.target}")
    print()

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
