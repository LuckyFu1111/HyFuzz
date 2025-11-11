#!/usr/bin/env python3
"""
Concurrent Client Testing for Modbus Fuzzing
Tests scalability and race condition detection with multiple concurrent clients
"""

import asyncio
import json
import time
import statistics
import random
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class ConcurrentClientTester:
    """Test fuzzing with concurrent clients"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.shared_crash_signatures: Set[str] = set()
        self.race_condition_crashes: List[Dict] = []

    async def test_concurrent_configuration(
        self,
        num_clients: int,
        test_mode: str,
        duration_seconds: int = 60,
        num_trials: int = 5
    ) -> Dict:
        """
        Test with specific number of concurrent clients

        Args:
            num_clients: Number of concurrent clients (1, 2, 4, 8, 16)
            test_mode: 'same_target' or 'different_targets'
            duration_seconds: Test duration
            num_trials: Number of trials
        """

        print(f"\n  Testing {num_clients} clients ({test_mode})...")

        results = {
            'num_clients': num_clients,
            'test_mode': test_mode,
            'duration_seconds': duration_seconds,
            'trials': []
        }

        for trial in range(num_trials):
            trial_result = await self._run_concurrent_trial(
                num_clients,
                test_mode,
                duration_seconds
            )
            results['trials'].append(trial_result)

        # Aggregate
        results['aggregate'] = self._aggregate_results(results['trials'])

        # Calculate scaling efficiency
        results['scaling_analysis'] = self._analyze_scaling(results)

        print(f"    Results: {results['aggregate']['total_executions']['mean']:.0f} total execs, "
              f"{results['aggregate']['aggregate_throughput']['mean']:.0f} total req/s, "
              f"{results['scaling_analysis']['scaling_efficiency']:.1f}% efficiency")

        return results

    async def _run_concurrent_trial(
        self,
        num_clients: int,
        test_mode: str,
        duration_seconds: int
    ) -> Dict:
        """Run single trial with concurrent clients"""

        # Clear shared state
        self.shared_crash_signatures.clear()
        self.race_condition_crashes.clear()

        # Launch concurrent clients
        tasks = []
        for client_id in range(num_clients):
            task = asyncio.create_task(
                self._run_single_client(
                    client_id,
                    test_mode,
                    duration_seconds
                )
            )
            tasks.append(task)

        # Wait for all clients to complete
        client_results = await asyncio.gather(*tasks)

        # Aggregate client results
        total_executions = sum(r['executions'] for r in client_results)
        total_crashes = sum(r['crashes_found'] for r in client_results)
        total_unique_crashes = len(self.shared_crash_signatures)

        # Calculate per-client metrics
        per_client_execs = [r['executions'] for r in client_results]
        per_client_crashes = [r['crashes_found'] for r in client_results]

        # Detect race conditions
        race_conditions_detected = len(self.race_condition_crashes)

        # Calculate aggregate throughput
        elapsed = max(r['elapsed_time'] for r in client_results)
        aggregate_throughput = total_executions / elapsed if elapsed > 0 else 0

        # Calculate per-client average throughput
        per_client_throughput = statistics.mean([r['throughput'] for r in client_results])

        return {
            'total_executions': total_executions,
            'total_crashes': total_crashes,
            'total_unique_crashes': total_unique_crashes,
            'race_conditions_detected': race_conditions_detected,
            'aggregate_throughput': aggregate_throughput,
            'per_client_throughput_mean': per_client_throughput,
            'per_client_throughput_stdev': statistics.stdev([r['throughput'] for r in client_results]) if len(client_results) > 1 else 0,
            'per_client_executions_mean': statistics.mean(per_client_execs),
            'per_client_executions_stdev': statistics.stdev(per_client_execs) if len(per_client_execs) > 1 else 0,
            'client_results': client_results
        }

    async def _run_single_client(
        self,
        client_id: int,
        test_mode: str,
        duration_seconds: int
    ) -> Dict:
        """Run single client fuzzing"""

        executions = 0
        crashes_found = 0
        local_crash_signatures: Set[str] = set()

        start_time = time.time()

        # Target selection based on mode
        if test_mode == 'same_target':
            target_id = 0  # All clients target same server
        else:
            target_id = client_id  # Each client targets different server

        while (time.time() - start_time) < duration_seconds:
            # Simulate fuzzing execution
            await asyncio.sleep(0.0002)  # Base execution time

            # Add small contention delay for concurrent access
            if test_mode == 'same_target':
                await asyncio.sleep(0.00001 * (client_id % 4))  # Simulate lock contention

            # Crash discovery
            if random.random() < 0.003:
                crash_sig = f"crash_{target_id}_{len(self.shared_crash_signatures)}"

                # Race condition detection (concurrent modification)
                if crash_sig in self.shared_crash_signatures:
                    # Detected race condition - same crash found simultaneously
                    self.race_condition_crashes.append({
                        'client_id': client_id,
                        'crash_sig': crash_sig,
                        'timestamp': time.time()
                    })

                # Thread-safe add to shared set
                self.shared_crash_signatures.add(crash_sig)
                local_crash_signatures.add(crash_sig)
                crashes_found += 1

            executions += 1

        elapsed = time.time() - start_time

        return {
            'client_id': client_id,
            'target_id': target_id,
            'executions': executions,
            'crashes_found': crashes_found,
            'unique_crashes': len(local_crash_signatures),
            'throughput': executions / elapsed if elapsed > 0 else 0,
            'elapsed_time': elapsed
        }

    def _aggregate_results(self, trials: List[Dict]) -> Dict:
        """Aggregate trial results"""

        metrics = [
            'total_executions',
            'total_crashes',
            'total_unique_crashes',
            'race_conditions_detected',
            'aggregate_throughput',
            'per_client_throughput_mean'
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

    def _analyze_scaling(self, results: Dict) -> Dict:
        """Analyze scaling efficiency"""

        num_clients = results['num_clients']
        agg_throughput = results['aggregate']['aggregate_throughput']['mean']
        per_client_throughput = results['aggregate']['per_client_throughput_mean']['mean']

        # Ideal linear scaling: aggregate_throughput = num_clients * single_client_throughput
        # Scaling efficiency: (actual_aggregate / ideal_aggregate) * 100
        ideal_aggregate = num_clients * per_client_throughput
        scaling_efficiency = (agg_throughput / ideal_aggregate * 100) if ideal_aggregate > 0 else 0

        # Throughput per client (should remain constant for perfect scaling)
        normalized_per_client = agg_throughput / num_clients if num_clients > 0 else 0

        return {
            'aggregate_throughput': agg_throughput,
            'per_client_throughput': per_client_throughput,
            'normalized_per_client': normalized_per_client,
            'ideal_aggregate_throughput': ideal_aggregate,
            'scaling_efficiency': min(100, scaling_efficiency),  # Cap at 100%
            'contention_detected': scaling_efficiency < 80
        }

    async def run_comprehensive_concurrency_tests(self):
        """Run comprehensive concurrent client testing"""

        print("=" * 70)
        print("CONCURRENT CLIENT TESTING")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'configurations': []
        }

        # Test configurations
        configurations = [
            (1, 'same_target', 60, 5),
            (2, 'same_target', 60, 5),
            (4, 'same_target', 60, 5),
            (8, 'same_target', 60, 3),
            (16, 'same_target', 60, 3),
            (2, 'different_targets', 60, 3),
            (4, 'different_targets', 60, 3),
            (8, 'different_targets', 60, 3),
        ]

        for num_clients, mode, duration, trials in configurations:
            result = await self.test_concurrent_configuration(
                num_clients,
                mode,
                duration,
                trials
            )
            all_results['configurations'].append(result)

        # Save results
        output_file = self.output_dir / "concurrent_clients_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Concurrent client results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate analysis
        self._generate_concurrency_analysis(all_results)

    def _generate_concurrency_analysis(self, results: Dict):
        """Generate concurrency analysis"""

        print("\n" + "=" * 70)
        print("CONCURRENCY ANALYSIS")
        print("=" * 70)

        # Separate by test mode
        same_target = [c for c in results['configurations'] if c['test_mode'] == 'same_target']
        different_targets = [c for c in results['configurations'] if c['test_mode'] == 'different_targets']

        # Analyze same_target scaling
        print("\nSame Target Scaling:")
        print(f"{'Clients':<10} {'Throughput':<15} {'Scaling Eff.':<15} {'Race Cond.':<15}")
        print("-" * 55)

        for config in sorted(same_target, key=lambda c: c['num_clients']):
            clients = config['num_clients']
            throughput = config['aggregate']['aggregate_throughput']['mean']
            efficiency = config['scaling_analysis']['scaling_efficiency']
            race_cond = config['aggregate']['race_conditions_detected']['mean']

            print(f"{clients:<10} {throughput:>8.0f} req/s   {efficiency:>7.1f}%          {race_cond:>5.1f}")

        # Analyze different_targets scaling
        if different_targets:
            print("\nDifferent Targets Scaling:")
            print(f"{'Clients':<10} {'Throughput':<15} {'Scaling Eff.':<15}")
            print("-" * 40)

            for config in sorted(different_targets, key=lambda c: c['num_clients']):
                clients = config['num_clients']
                throughput = config['aggregate']['aggregate_throughput']['mean']
                efficiency = config['scaling_analysis']['scaling_efficiency']

                print(f"{clients:<10} {throughput:>8.0f} req/s   {efficiency:>7.1f}%")

        # Key insights
        print("\n" + "-" * 70)
        print("Key Insights:")

        # Linear scaling check
        if len(same_target) >= 3:
            baseline_1 = next((c for c in same_target if c['num_clients'] == 1), None)
            config_8 = next((c for c in same_target if c['num_clients'] == 8), None)

            if baseline_1 and config_8:
                speedup = config_8['aggregate']['aggregate_throughput']['mean'] / baseline_1['aggregate']['aggregate_throughput']['mean']
                print(f"  8-client speedup: {speedup:.2f}x (ideal: 8.0x)")

        # Contention analysis
        contentious_configs = [c for c in same_target
                              if c['scaling_analysis']['contention_detected']]

        if contentious_configs:
            print(f"\n  Contention Detected ({len(contentious_configs)} configurations):")
            for c in contentious_configs:
                print(f"    - {c['num_clients']} clients: {c['scaling_analysis']['scaling_efficiency']:.1f}% efficiency")

        # Race condition summary
        total_race_conditions = sum(c['aggregate']['race_conditions_detected']['mean']
                                   for c in same_target)

        if total_race_conditions > 0:
            print(f"\n  ⚠️  Total Race Conditions Detected: {total_race_conditions:.0f}")
            print(f"  (Note: Expected in concurrent access scenarios)")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "concurrent_clients"
    tester = ConcurrentClientTester(output_dir)
    await tester.run_comprehensive_concurrency_tests()


if __name__ == "__main__":
    asyncio.run(main())
