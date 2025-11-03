"""HyFuzz Campaign Runner.

This script orchestrates complete fuzzing campaigns by coordinating:
- LLM-driven payload generation
- Target protocol execution
- Defense system integration
- Judge feedback evaluation
- Result aggregation and reporting

It serves as the main entry point for running automated fuzzing campaigns
against protocol implementations with integrated defense awareness.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class CampaignConfig:
    """Configuration for a fuzzing campaign."""

    name: str
    protocol: str
    target: str
    payload_count: int = 10
    model: str = "mistral"
    config_file: Optional[str] = None
    output_dir: str = "results"
    log_level: str = "INFO"
    dry_run: bool = False


class CampaignRunner:
    """Main orchestrator for fuzzing campaigns."""

    def __init__(self, config: CampaignConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.start_time = datetime.now()
        self.results = {
            "campaign_name": config.name,
            "protocol": config.protocol,
            "target": config.target,
            "start_time": self.start_time.isoformat(),
            "payloads": [],
            "executions": [],
            "statistics": {},
        }

    def _setup_logging(self) -> logging.Logger:
        """Initialize logging configuration."""
        log_path = PROJECT_ROOT / "logs" / "campaigns" / f"{self.config.name}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(levelname)s - [Campaign] - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_path, encoding="utf-8"),
            ],
        )
        return logging.getLogger(f"hyfuzz.campaign.{self.config.name}")

    def _load_campaign_config(self) -> Dict:
        """Load campaign configuration from YAML file if specified."""
        if not self.config.config_file:
            return {}

        try:
            import yaml
            config_path = Path(self.config.config_file)
            if not config_path.exists():
                self.logger.warning(f"Config file not found: {config_path}")
                return {}

            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except ImportError:
            self.logger.warning("PyYAML not installed, skipping config file")
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return {}

    def _generate_payloads(self) -> List[str]:
        """Generate fuzzing payloads using LLM.

        Returns:
            List of generated payload strings
        """
        self.logger.info(f"Generating {self.config.payload_count} payloads for {self.config.protocol}")

        payloads = []
        for i in range(self.config.payload_count):
            # In a real implementation, this would call the PayloadGenerator
            # For now, generate mock payloads based on protocol
            if self.config.protocol == "coap":
                payload = f"{{\"method\": \"GET\", \"path\": \"/test{i}\", \"token\": \"{i:04x}\"}}"
            elif self.config.protocol == "modbus":
                payload = f"{{\"function_code\": 3, \"address\": {i*10}, \"count\": 1}}"
            elif self.config.protocol == "mqtt":
                payload = f"{{\"topic\": \"test/{i}\", \"qos\": 1, \"payload\": \"test_payload_{i}\"}}"
            else:
                payload = f"{{\"protocol\": \"{self.config.protocol}\", \"data\": \"payload_{i}\"}}"

            payloads.append(payload)
            self.logger.debug(f"Generated payload {i+1}/{self.config.payload_count}")

        self.results["payloads"] = payloads
        return payloads

    def _execute_payload(self, payload: str, index: int) -> Dict:
        """Execute a single payload against the target.

        Args:
            payload: Payload data to execute
            index: Payload index number

        Returns:
            Execution result dictionary
        """
        self.logger.info(f"Executing payload {index+1}/{self.config.payload_count}")

        # Mock execution result
        # In real implementation, this would coordinate with the Ubuntu client
        execution_result = {
            "payload_id": f"{self.config.name}-{index}",
            "payload": payload,
            "target": self.config.target,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "response": {
                "status": "executed",
                "output": f"Mock execution result for payload {index}",
                "error": None,
            },
            "metrics": {
                "execution_time_ms": 10 + (index % 5),
                "memory_usage_kb": 1024 + (index * 10),
            },
            "defense_verdict": self._get_defense_verdict(payload),
            "judge_score": 0.5 + (index % 5) * 0.1,
        }

        return execution_result

    def _get_defense_verdict(self, payload: str) -> str:
        """Get defense system verdict for a payload.

        Args:
            payload: Payload to evaluate

        Returns:
            Verdict string: monitor, investigate, block, or escalate
        """
        # Mock defense verdict logic
        # In real implementation, this would call the DefenseIntegrator
        import random
        verdicts = ["monitor", "investigate", "block", "escalate"]
        weights = [0.5, 0.3, 0.15, 0.05]  # Probabilities
        return random.choices(verdicts, weights=weights)[0]

    def _run_campaign(self) -> None:
        """Execute the complete fuzzing campaign."""
        self.logger.info(f"Starting campaign: {self.config.name}")
        self.logger.info(f"Protocol: {self.config.protocol}")
        self.logger.info(f"Target: {self.config.target}")
        self.logger.info(f"Payload count: {self.config.payload_count}")

        # Load additional configuration
        campaign_config = self._load_campaign_config()
        if campaign_config:
            self.logger.info(f"Loaded configuration from: {self.config.config_file}")

        # Generate payloads
        payloads = self._generate_payloads()

        # Execute payloads
        self.logger.info("Executing payloads...")
        for i, payload in enumerate(payloads):
            if self.config.dry_run:
                self.logger.info(f"[DRY RUN] Would execute payload {i+1}: {payload[:50]}...")
            else:
                result = self._execute_payload(payload, i)
                self.results["executions"].append(result)

        # Calculate statistics
        self._calculate_statistics()

        # Save results
        self._save_results()

        self.logger.info(f"Campaign completed: {self.config.name}")

    def _calculate_statistics(self) -> None:
        """Calculate campaign statistics."""
        if not self.results["executions"]:
            return

        total_executions = len(self.results["executions"])
        successful = sum(1 for e in self.results["executions"] if e["success"])

        defense_verdicts = {}
        for execution in self.results["executions"]:
            verdict = execution.get("defense_verdict", "unknown")
            defense_verdicts[verdict] = defense_verdicts.get(verdict, 0) + 1

        judge_scores = [e.get("judge_score", 0.0) for e in self.results["executions"]]
        avg_score = sum(judge_scores) / len(judge_scores) if judge_scores else 0.0

        execution_times = [
            e["metrics"]["execution_time_ms"]
            for e in self.results["executions"]
            if "metrics" in e
        ]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0

        self.results["statistics"] = {
            "total_executions": total_executions,
            "successful_executions": successful,
            "success_rate": successful / total_executions if total_executions > 0 else 0.0,
            "defense_verdicts": defense_verdicts,
            "average_judge_score": round(avg_score, 3),
            "average_execution_time_ms": round(avg_time, 2),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
        }

    def _save_results(self) -> None:
        """Save campaign results to file."""
        output_dir = Path(self.config.output_dir) / self.config.protocol
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"{self.config.name}_{timestamp}.json"

        self.results["end_time"] = datetime.now().isoformat()

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        self.logger.info(f"Results saved to: {output_file}")

        # Print summary
        self._print_summary()

    def _print_summary(self) -> None:
        """Print campaign summary to console."""
        stats = self.results["statistics"]

        print("\n" + "="*70)
        print(f"Campaign Summary: {self.config.name}")
        print("="*70)
        print(f"Protocol:              {self.config.protocol}")
        print(f"Target:                {self.config.target}")
        print(f"Total Executions:      {stats['total_executions']}")
        print(f"Successful:            {stats['successful_executions']} ({stats['success_rate']*100:.1f}%)")
        print(f"Avg Execution Time:    {stats['average_execution_time_ms']:.2f} ms")
        print(f"Avg Judge Score:       {stats['average_judge_score']:.3f}")
        print(f"Duration:              {stats['duration_seconds']:.1f} seconds")
        print("\nDefense Verdicts:")
        for verdict, count in stats['defense_verdicts'].items():
            percentage = (count / stats['total_executions']) * 100
            print(f"  {verdict:12s}: {count:3d} ({percentage:5.1f}%)")
        print("="*70 + "\n")

    def run(self) -> int:
        """Run the campaign and return exit code."""
        try:
            self._run_campaign()
            return 0
        except KeyboardInterrupt:
            self.logger.info("Campaign interrupted by user")
            return 130
        except Exception as e:
            self.logger.error(f"Campaign failed: {e}", exc_info=True)
            return 1


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HyFuzz fuzzing campaign runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a basic CoAP campaign
  python run_fuzzing_campaign.py --name test-coap --protocol coap --target coap://localhost:5683

  # Run with configuration file
  python run_fuzzing_campaign.py --name demo --config configs/phase3_demo.yaml

  # Dry run to test without execution
  python run_fuzzing_campaign.py --name test --protocol modbus --target modbus://localhost:502 --dry-run

  # Generate 50 payloads with custom model
  python run_fuzzing_campaign.py --name large-test --protocol mqtt \\
      --target mqtt://localhost:1883 --payloads 50 --model llama2
        """,
    )

    parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Campaign name (used for logging and results)",
    )
    parser.add_argument(
        "--protocol",
        type=str,
        default="coap",
        choices=["coap", "modbus", "mqtt", "http", "custom"],
        help="Target protocol (default: coap)",
    )
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        help="Target endpoint (e.g., coap://localhost:5683)",
    )
    parser.add_argument(
        "--payloads",
        type=int,
        default=10,
        help="Number of payloads to generate (default: 10)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mistral",
        help="LLM model for payload generation (default: mistral)",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML configuration file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results",
        help="Output directory for results (default: results)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (generate payloads but don't execute)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()

    # Build configuration
    config = CampaignConfig(
        name=args.name,
        protocol=args.protocol,
        target=args.target,
        payload_count=args.payloads,
        model=args.model,
        config_file=args.config,
        output_dir=args.output,
        log_level=args.log_level,
        dry_run=args.dry_run,
    )

    # Create and run campaign
    runner = CampaignRunner(config)

    print(f"🚀 Starting HyFuzz Campaign: {config.name}")
    print(f"   Protocol: {config.protocol}")
    print(f"   Target: {config.target}")
    print(f"   Payloads: {config.payload_count}")
    if config.dry_run:
        print(f"   Mode: DRY RUN")
    print()

    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
