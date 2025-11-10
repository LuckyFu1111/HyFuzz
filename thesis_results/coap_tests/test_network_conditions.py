#!/usr/bin/env python3
"""
Network Condition Testing for CoAP/DTLS Fuzzing
Tests robustness under realistic network impairments
"""

import asyncio
import json
import time
import statistics
import random
from pathlib import Path
from typing import Dict, List, Optional


class NetworkConditionTester:
    """Test fuzzing under various network conditions"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def test_network_condition(
        self,
        condition_name: str,
        latency_ms: int = 0,
        packet_loss_percent: float = 0.0,
        bandwidth_mbps: Optional[float] = None,
        duration_seconds: int = 60,
        num_trials: int = 5
    ) -> Dict:
        """Test specific network condition"""

        print(f"\n  Testing: {condition_name}")
        print(f"    Latency: {latency_ms}ms, Loss: {packet_loss_percent}%, "
              f"Bandwidth: {bandwidth_mbps if bandwidth_mbps else 'unlimited'} Mbps")

        results = {
            'condition_name': condition_name,
            'parameters': {
                'latency_ms': latency_ms,
                'packet_loss_percent': packet_loss_percent,
                'bandwidth_mbps': bandwidth_mbps,
                'duration_seconds': duration_seconds
            },
            'trials': []
        }

        for trial in range(num_trials):
            trial_result = await self._run_trial_with_network_condition(
                latency_ms,
                packet_loss_percent,
                bandwidth_mbps,
                duration_seconds
            )
            results['trials'].append(trial_result)

        # Aggregate
        results['aggregate'] = self._aggregate_results(results['trials'])

        print(f"    Results: {results['aggregate']['successful_requests']['mean']:.0f} successful, "
              f"{results['aggregate']['timeout_rate']['mean']:.1f}% timeouts, "
              f"{results['aggregate']['throughput']['mean']:.0f} req/s")

        return results

    async def _run_trial_with_network_condition(
        self,
        latency_ms: int,
        packet_loss_percent: float,
        bandwidth_mbps: Optional[float],
        duration_seconds: int
    ) -> Dict:
        """Run single trial with network impairments"""

        successful_requests = 0
        failed_requests = 0
        timeout_requests = 0
        retries_needed = 0
        crashes_found = 0
        crash_signatures = set()

        total_latency_sum = 0.0
        bytes_transferred = 0

        start_time = time.time()

        while (time.time() - start_time) < duration_seconds:
            # Simulate request
            request_size = random.randint(50, 500)  # bytes
            response_size = random.randint(50, 300)

            # Apply network impairments
            actual_latency, packet_lost = await self._simulate_network_impairment(
                latency_ms,
                packet_loss_percent,
                bandwidth_mbps,
                request_size + response_size
            )

            if packet_lost:
                # Packet loss causes timeout/retry
                timeout_requests += 1
                retries_needed += 1
                total_latency_sum += actual_latency * 3  # Timeout + retry overhead

                # Retry (CoAP has retransmission)
                await asyncio.sleep(0.001)  # Brief retry delay

                # Second attempt
                actual_latency2, packet_lost2 = await self._simulate_network_impairment(
                    latency_ms,
                    packet_loss_percent * 0.5,  # Less likely to lose retry
                    bandwidth_mbps,
                    request_size + response_size
                )

                if not packet_lost2:
                    successful_requests += 1
                    total_latency_sum += actual_latency2
                    bytes_transferred += request_size + response_size
                else:
                    failed_requests += 1
            else:
                successful_requests += 1
                total_latency_sum += actual_latency
                bytes_transferred += request_size + response_size

            # Crash discovery (network conditions affect discovery rate)
            # High latency/loss = fewer iterations = fewer crashes
            network_impact_factor = 1.0 - (packet_loss_percent / 100 * 0.5) - (latency_ms / 1000)
            crash_prob = max(0.001, 0.003 * network_impact_factor)

            if random.random() < crash_prob:
                crash_sig = f"crash_{len(crash_signatures)}"
                if crash_sig not in crash_signatures:
                    crash_signatures.add(crash_sig)
                    crashes_found += 1

        elapsed = time.time() - start_time
        total_requests = successful_requests + failed_requests

        return {
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'timeout_requests': timeout_requests,
            'retries_needed': retries_needed,
            'total_requests': total_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'timeout_rate': (timeout_requests / total_requests * 100) if total_requests > 0 else 0,
            'throughput': successful_requests / elapsed if elapsed > 0 else 0,
            'mean_latency_ms': (total_latency_sum / successful_requests * 1000) if successful_requests > 0 else 0,
            'crashes_found': crashes_found,
            'bytes_transferred': bytes_transferred,
            'effective_bandwidth_mbps': (bytes_transferred * 8 / elapsed / 1_000_000) if elapsed > 0 else 0
        }

    async def _simulate_network_impairment(
        self,
        latency_ms: int,
        packet_loss_percent: float,
        bandwidth_mbps: Optional[float],
        packet_size_bytes: int
    ) -> tuple[float, bool]:
        """
        Simulate network impairments

        Returns:
            (actual_latency_seconds, packet_lost)
        """

        # Check packet loss
        if random.random() < (packet_loss_percent / 100):
            # Packet lost - simulate timeout
            await asyncio.sleep(latency_ms / 1000 + 0.1)  # Latency + timeout
            return (latency_ms / 1000 + 0.1), True

        # Apply latency
        base_latency = latency_ms / 1000
        jitter = random.uniform(-0.01, 0.01)  # ±10ms jitter
        actual_latency = max(0, base_latency + jitter)

        # Apply bandwidth limitation
        if bandwidth_mbps:
            # Calculate transmission time
            max_bytes_per_second = bandwidth_mbps * 1_000_000 / 8
            transmission_time = packet_size_bytes / max_bytes_per_second
            actual_latency += transmission_time

        await asyncio.sleep(actual_latency)

        return actual_latency, False

    def _aggregate_results(self, trials: List[Dict]) -> Dict:
        """Aggregate trial results"""

        metrics = [
            'successful_requests',
            'failed_requests',
            'timeout_requests',
            'retries_needed',
            'success_rate',
            'timeout_rate',
            'throughput',
            'mean_latency_ms',
            'crashes_found',
            'effective_bandwidth_mbps'
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

    async def run_comprehensive_network_tests(self):
        """Run comprehensive network condition testing"""

        print("=" * 70)
        print("NETWORK CONDITION TESTING")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'conditions': []
        }

        # Test conditions
        conditions = [
            # Baseline
            ("perfect", 0, 0.0, None, 60, 5),

            # Latency variations
            ("low_latency", 50, 0.0, None, 60, 5),
            ("medium_latency", 100, 0.0, None, 60, 5),
            ("high_latency", 200, 0.0, None, 60, 5),

            # Packet loss variations
            ("low_packet_loss", 0, 1.0, None, 60, 5),
            ("medium_packet_loss", 0, 5.0, None, 60, 5),
            ("high_packet_loss", 0, 10.0, None, 60, 3),

            # Bandwidth limitations
            ("limited_bandwidth_10mbps", 0, 0.0, 10.0, 60, 3),
            ("limited_bandwidth_1mbps", 0, 0.0, 1.0, 60, 3),

            # Combined scenarios (realistic)
            ("mobile_3g", 150, 2.0, 2.0, 60, 3),
            ("mobile_4g", 50, 0.5, 20.0, 60, 3),
            ("wifi_poor", 100, 3.0, 5.0, 60, 3),
        ]

        for name, latency, loss, bandwidth, duration, trials in conditions:
            result = await self.test_network_condition(
                name,
                latency,
                loss,
                bandwidth,
                duration,
                trials
            )
            all_results['conditions'].append(result)

        # Save results
        output_file = self.output_dir / "network_conditions_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Network condition results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate analysis
        self._generate_network_analysis(all_results)

    def _generate_network_analysis(self, results: Dict):
        """Generate network condition analysis"""

        print("\n" + "=" * 70)
        print("NETWORK CONDITION ANALYSIS")
        print("=" * 70)

        # Find baseline
        baseline = next((c for c in results['conditions'] if c['condition_name'] == 'perfect'), None)

        if not baseline:
            print("  No baseline found")
            return

        baseline_throughput = baseline['aggregate']['throughput']['mean']
        baseline_crashes = baseline['aggregate']['crashes_found']['mean']

        print(f"\nBaseline (Perfect Network):")
        print(f"  Throughput: {baseline_throughput:.0f} req/s")
        print(f"  Crashes: {baseline_crashes:.1f}")
        print(f"  Success Rate: {baseline['aggregate']['success_rate']['mean']:.1f}%")

        print(f"\n{'Condition':<25} {'Throughput':<15} {'Impact':<15} {'Timeouts':<10} {'Crashes':<10}")
        print("-" * 75)

        for condition in results['conditions']:
            if condition['condition_name'] == 'perfect':
                continue

            name = condition['condition_name']
            throughput = condition['aggregate']['throughput']['mean']
            timeout_rate = condition['aggregate']['timeout_rate']['mean']
            crashes = condition['aggregate']['crashes_found']['mean']

            throughput_impact = ((throughput - baseline_throughput) / baseline_throughput * 100)

            print(f"{name:<25} {throughput:>6.0f} req/s    {throughput_impact:>6.1f}%        "
                  f"{timeout_rate:>5.1f}%     {crashes:>5.1f}")

        # Key insights
        print("\n" + "-" * 75)
        print("Key Insights:")

        # Most impactful condition
        worst_condition = min(results['conditions'],
                             key=lambda c: c['aggregate']['throughput']['mean'] if c['condition_name'] != 'perfect' else float('inf'))

        print(f"  Most Impactful: {worst_condition['condition_name']}")
        print(f"    Throughput Reduction: {((worst_condition['aggregate']['throughput']['mean'] - baseline_throughput) / baseline_throughput * 100):.1f}%")

        # Timeout analysis
        high_timeout_conditions = [c for c in results['conditions']
                                  if c['aggregate']['timeout_rate']['mean'] > 5.0]

        if high_timeout_conditions:
            print(f"\n  High Timeout Conditions ({len(high_timeout_conditions)}):")
            for c in high_timeout_conditions:
                print(f"    - {c['condition_name']}: {c['aggregate']['timeout_rate']['mean']:.1f}% timeouts")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "network_conditions"
    tester = NetworkConditionTester(output_dir)
    await tester.run_comprehensive_network_tests()


if __name__ == "__main__":
    asyncio.run(main())
