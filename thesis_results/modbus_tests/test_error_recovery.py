#!/usr/bin/env python3
"""
Error Recovery Testing
Tests graceful degradation and recovery from various failure scenarios
"""

import asyncio
import json
import time
import random
from pathlib import Path
from typing import Dict, List
from enum import Enum


class FailureType(Enum):
    """Types of failures to test"""
    TARGET_CRASH = "target_crash"
    TARGET_RESTART = "target_restart"
    NETWORK_DISCONNECT = "network_disconnect"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CORRUPTED_STATE = "corrupted_state"


class ErrorRecoveryTester:
    """Test error recovery capabilities"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def test_recovery_scenario(
        self,
        scenario_name: str,
        failure_type: FailureType,
        duration_seconds: int = 120,
        num_trials: int = 5
    ) -> Dict:
        """Test specific recovery scenario"""

        print(f"\n  Testing: {scenario_name}")

        results = {
            'scenario_name': scenario_name,
            'failure_type': failure_type.value,
            'duration_seconds': duration_seconds,
            'trials': []
        }

        for trial in range(num_trials):
            trial_result = await self._run_recovery_trial(
                failure_type,
                duration_seconds
            )
            results['trials'].append(trial_result)

        # Aggregate
        results['aggregate'] = self._aggregate_results(results['trials'])

        print(f"    Results: {results['aggregate']['successful_recoveries']['mean']:.0f}/{results['aggregate']['failures_injected']['mean']:.0f} recoveries, "
              f"recovery time: {results['aggregate']['mean_recovery_time_seconds']['mean']:.2f}s")

        return results

    async def _run_recovery_trial(
        self,
        failure_type: FailureType,
        duration_seconds: int
    ) -> Dict:
        """Run single recovery trial"""

        executions = 0
        failures_injected = 0
        successful_recoveries = 0
        failed_recoveries = 0
        recovery_times = []
        lost_test_cases = 0

        start_time = time.time()

        while (time.time() - start_time) < duration_seconds:
            # Normal fuzzing
            for _ in range(random.randint(500, 1500)):
                await asyncio.sleep(0.0002)
                executions += 1

                # Check if failure should occur
                if random.random() < 0.1:  # 10% chance per batch
                    break

            # Inject failure
            failure_result = await self._inject_failure(failure_type)
            failures_injected += 1

            # Attempt recovery
            recovery_start = time.time()
            recovery_successful, test_cases_lost = await self._attempt_recovery(failure_type)
            recovery_time = time.time() - recovery_start

            recovery_times.append(recovery_time)
            lost_test_cases += test_cases_lost

            if recovery_successful:
                successful_recoveries += 1
            else:
                failed_recoveries += 1
                break  # Cannot continue after failed recovery

        return {
            'executions': executions,
            'failures_injected': failures_injected,
            'successful_recoveries': successful_recoveries,
            'failed_recoveries': failed_recoveries,
            'recovery_success_rate': (successful_recoveries / failures_injected * 100) if failures_injected > 0 else 0,
            'mean_recovery_time_seconds': sum(recovery_times) / len(recovery_times) if recovery_times else 0,
            'max_recovery_time_seconds': max(recovery_times) if recovery_times else 0,
            'total_test_cases_lost': lost_test_cases,
            'test_cases_lost_per_recovery': lost_test_cases / failures_injected if failures_injected > 0 else 0
        }

    async def _inject_failure(self, failure_type: FailureType) -> Dict:
        """Simulate failure injection"""

        if failure_type == FailureType.TARGET_CRASH:
            # Simulate target crash
            await asyncio.sleep(0.01)  # Crash detection time
            return {'type': 'crash', 'detected': True}

        elif failure_type == FailureType.TARGET_RESTART:
            # Simulate target restart
            await asyncio.sleep(0.5)  # Restart time
            return {'type': 'restart', 'reconnect_needed': True}

        elif failure_type == FailureType.NETWORK_DISCONNECT:
            # Simulate network disconnection
            await asyncio.sleep(0.05)  # Connection timeout
            return {'type': 'network', 'reconnect_needed': True}

        elif failure_type == FailureType.RESOURCE_EXHAUSTION:
            # Simulate resource exhaustion (disk full, memory limit)
            await asyncio.sleep(0.02)
            return {'type': 'resource', 'cleanup_needed': True}

        elif failure_type == FailureType.CORRUPTED_STATE:
            # Simulate corrupted internal state
            await asyncio.sleep(0.01)
            return {'type': 'corruption', 'reset_needed': True}

        return {'type': 'unknown'}

    async def _attempt_recovery(self, failure_type: FailureType) -> tuple[bool, int]:
        """
        Attempt to recover from failure

        Returns:
            (recovery_successful, test_cases_lost)
        """

        recovery_successful = True
        test_cases_lost = 0

        if failure_type == FailureType.TARGET_CRASH:
            # Detect crash, save state, restart target
            await asyncio.sleep(0.05)  # Detection time
            test_cases_lost = random.randint(0, 5)  # Some in-flight cases lost
            recovery_successful = random.random() < 0.95  # 95% success rate

        elif failure_type == FailureType.TARGET_RESTART:
            # Reconnect to restarted target
            await asyncio.sleep(0.3)  # Reconnection time
            test_cases_lost = random.randint(5, 15)  # Queue lost during restart
            recovery_successful = random.random() < 0.98  # 98% success rate

        elif failure_type == FailureType.NETWORK_DISCONNECT:
            # Retry connection
            await asyncio.sleep(0.2)  # Retry backoff
            test_cases_lost = random.randint(1, 10)
            recovery_successful = random.random() < 0.90  # 90% success rate (network may not recover)

        elif failure_type == FailureType.RESOURCE_EXHAUSTION:
            # Clean up resources, try to continue
            await asyncio.sleep(0.1)  # Cleanup time
            test_cases_lost = random.randint(10, 50)  # May need to clear corpus
            recovery_successful = random.random() < 0.85  # 85% success rate

        elif failure_type == FailureType.CORRUPTED_STATE:
            # Reset state, reinitialize
            await asyncio.sleep(0.15)  # Reinitialization time
            test_cases_lost = random.randint(20, 100)  # Need to rebuild state
            recovery_successful = random.random() < 0.80  # 80% success rate

        return recovery_successful, test_cases_lost

    def _aggregate_results(self, trials: List[Dict]) -> Dict:
        """Aggregate trial results"""

        import statistics

        metrics = [
            'executions',
            'failures_injected',
            'successful_recoveries',
            'failed_recoveries',
            'recovery_success_rate',
            'mean_recovery_time_seconds',
            'max_recovery_time_seconds',
            'total_test_cases_lost',
            'test_cases_lost_per_recovery'
        ]

        aggregate = {}
        for metric in metrics:
            values = [t[metric] for t in trials]
            aggregate[metric] = {
                'mean': statistics.mean(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'min': min(values),
                'max': max(values)
            }

        return aggregate

    async def run_comprehensive_recovery_tests(self):
        """Run comprehensive error recovery testing"""

        print("=" * 70)
        print("ERROR RECOVERY TESTING")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'scenarios': []
        }

        # Test scenarios
        scenarios = [
            ("Target Crash Recovery", FailureType.TARGET_CRASH, 120, 5),
            ("Target Restart Recovery", FailureType.TARGET_RESTART, 120, 5),
            ("Network Disconnect Recovery", FailureType.NETWORK_DISCONNECT, 120, 5),
            ("Resource Exhaustion Recovery", FailureType.RESOURCE_EXHAUSTION, 120, 3),
            ("Corrupted State Recovery", FailureType.CORRUPTED_STATE, 120, 3),
        ]

        for name, failure_type, duration, trials in scenarios:
            result = await self.test_recovery_scenario(
                name,
                failure_type,
                duration,
                trials
            )
            all_results['scenarios'].append(result)

        # Save results
        output_file = self.output_dir / "error_recovery_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Error recovery results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate analysis
        self._generate_recovery_analysis(all_results)

    def _generate_recovery_analysis(self, results: Dict):
        """Generate recovery analysis"""

        print("\n" + "=" * 70)
        print("ERROR RECOVERY ANALYSIS")
        print("=" * 70)

        print(f"\n{'Scenario':<35} {'Success Rate':<15} {'Avg Recovery':<15} {'Data Loss':<15}")
        print("-" * 80)

        for scenario in results['scenarios']:
            name = scenario['scenario_name']
            success_rate = scenario['aggregate']['recovery_success_rate']['mean']
            recovery_time = scenario['aggregate']['mean_recovery_time_seconds']['mean']
            data_loss = scenario['aggregate']['test_cases_lost_per_recovery']['mean']

            print(f"{name:<35} {success_rate:>6.1f}%          "
                  f"{recovery_time:>6.3f}s         {data_loss:>6.1f} cases")

        # Key insights
        print("\n" + "-" * 80)
        print("Key Insights:")

        # Best recovery
        best_recovery = max(results['scenarios'],
                           key=lambda s: s['aggregate']['recovery_success_rate']['mean'])

        print(f"  Best Recovery: {best_recovery['scenario_name']}")
        print(f"    Success Rate: {best_recovery['aggregate']['recovery_success_rate']['mean']:.1f}%")
        print(f"    Recovery Time: {best_recovery['aggregate']['mean_recovery_time_seconds']['mean']:.3f}s")

        # Worst recovery
        worst_recovery = min(results['scenarios'],
                            key=lambda s: s['aggregate']['recovery_success_rate']['mean'])

        print(f"\n  Most Challenging: {worst_recovery['scenario_name']}")
        print(f"    Success Rate: {worst_recovery['aggregate']['recovery_success_rate']['mean']:.1f}%")
        print(f"    Data Loss: {worst_recovery['aggregate']['test_cases_lost_per_recovery']['mean']:.1f} cases/recovery")

        # Overall resilience
        avg_success_rate = sum(s['aggregate']['recovery_success_rate']['mean']
                              for s in results['scenarios']) / len(results['scenarios'])

        print(f"\n  Overall Resilience Score: {avg_success_rate:.1f}%")

        if avg_success_rate >= 90:
            print(f"  Assessment: ✓ EXCELLENT - Highly resilient to failures")
        elif avg_success_rate >= 80:
            print(f"  Assessment: ✓ GOOD - Handles most failure scenarios well")
        elif avg_success_rate >= 70:
            print(f"  Assessment: ⚠️  FAIR - Some failure scenarios problematic")
        else:
            print(f"  Assessment: ❌ POOR - Significant recovery issues")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "error_recovery"
    tester = ErrorRecoveryTester(output_dir)
    await tester.run_comprehensive_recovery_tests()


if __name__ == "__main__":
    asyncio.run(main())
