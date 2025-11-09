#!/usr/bin/env python3
"""
Modbus/TCP Fuzzing Campaign Tests
Bug-finding, crash detection, and efficiency metrics
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HyFuzz-Ubuntu-Client" / "src"))

from protocols.modbus_handler import ModbusHandler
from fuzzing.mutation_engine import MutationEngine
from fuzzing.corpus_manager import CorpusManager


class ModbusFuzzingTester:
    """Modbus fuzzing campaign tests"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.handler = ModbusHandler()
        self.mutation_engine = MutationEngine()

    def generate_fuzz_params(self, mutation_level: str = "medium") -> Dict:
        """Generate fuzzed Modbus parameters"""
        base_params = {
            'function_code': random.choice([1, 2, 3, 4, 5, 6, 15, 16, 23]),
            'address': random.randint(0, 65535),
            'count': random.randint(1, 2000),  # Some beyond valid range
        }

        # Apply mutations
        if mutation_level == "aggressive":
            # Invalid function codes
            if random.random() < 0.3:
                base_params['function_code'] = random.randint(100, 255)
            # Out of range addresses
            if random.random() < 0.3:
                base_params['address'] = random.randint(65536, 100000)
            # Invalid counts
            if random.random() < 0.3:
                base_params['count'] = random.randint(2000, 10000)

        return base_params

    async def fuzzing_campaign(
        self,
        duration_seconds: int = 300,
        mutation_level: str = "medium"
    ) -> Dict:
        """
        Run a fuzzing campaign

        Args:
            duration_seconds: Campaign duration
            mutation_level: 'low', 'medium', 'aggressive'
        """
        results = {
            'start_time': time.time(),
            'duration_seconds': duration_seconds,
            'mutation_level': mutation_level,
            'total_execs': 0,
            'crashes': [],
            'unique_crashes': set(),
            'exceptions': defaultdict(int),
            'exec_times_ms': [],
            'exec_per_second': [],
            'time_to_first_crash': None,
            'coverage_growth': []
        }

        print(f"Starting Modbus fuzzing campaign ({duration_seconds}s, {mutation_level} mutations)...")

        start_time = time.time()
        last_second = int(start_time)
        execs_this_second = 0

        while (time.time() - start_time) < duration_seconds:
            # Generate fuzzed input
            params = self.generate_fuzz_params(mutation_level)

            # Execute
            exec_start = time.time()
            try:
                response = await self.handler.execute(params)
                exec_time = (time.time() - exec_start) * 1000
                results['exec_times_ms'].append(exec_time)

                # Check for crashes/exceptions
                if response.get('status') == 'error':
                    error_msg = response.get('error', '')

                    # Classify error
                    if any(keyword in error_msg.lower() for keyword in ['crash', 'segfault', 'abort']):
                        crash_sig = f"{params['function_code']}_{params['address']}"
                        results['crashes'].append({
                            'time': time.time() - start_time,
                            'params': params,
                            'error': error_msg,
                            'signature': crash_sig
                        })

                        if crash_sig not in results['unique_crashes']:
                            results['unique_crashes'].add(crash_sig)
                            if results['time_to_first_crash'] is None:
                                results['time_to_first_crash'] = time.time() - start_time

                    elif 'exception' in error_msg.lower():
                        results['exceptions'][error_msg] += 1

            except Exception as e:
                print(f"Error during fuzzing: {e}")

            results['total_execs'] += 1
            execs_this_second += 1

            # Track exec/s
            current_second = int(time.time())
            if current_second > last_second:
                results['exec_per_second'].append(execs_this_second)
                execs_this_second = 0
                last_second = current_second

            # Track coverage growth periodically
            if results['total_execs'] % 100 == 0:
                results['coverage_growth'].append({
                    'execs': results['total_execs'],
                    'time': time.time() - start_time,
                    'unique_crashes': len(results['unique_crashes'])
                })

            # Progress update
            if results['total_execs'] % 500 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {results['total_execs']} execs, {elapsed:.1f}s, "
                      f"{len(results['unique_crashes'])} unique crashes")

        # Calculate statistics
        results['end_time'] = time.time()
        results['actual_duration'] = results['end_time'] - results['start_time']

        if results['exec_times_ms']:
            results['exec_stats'] = {
                'mean_ms': statistics.mean(results['exec_times_ms']),
                'median_ms': statistics.median(results['exec_times_ms']),
                'min_ms': min(results['exec_times_ms']),
                'max_ms': max(results['exec_times_ms'])
            }

        if results['exec_per_second']:
            results['throughput_stats'] = {
                'mean_exec_per_sec': statistics.mean(results['exec_per_second']),
                'max_exec_per_sec': max(results['exec_per_second']),
                'total_execs': results['total_execs']
            }

        results['unique_crashes'] = list(results['unique_crashes'])

        return results

    async def multi_trial_campaign(
        self,
        num_trials: int = 5,
        duration_per_trial: int = 60
    ) -> Dict:
        """Run multiple fuzzing trials"""
        all_results = {
            'num_trials': num_trials,
            'duration_per_trial': duration_per_trial,
            'trials': []
        }

        print(f"\nRunning {num_trials} fuzzing trials ({duration_per_trial}s each)...")

        for trial in range(num_trials):
            print(f"\n--- Trial {trial + 1}/{num_trials} ---")

            trial_results = await self.fuzzing_campaign(
                duration_seconds=duration_per_trial,
                mutation_level="medium"
            )

            all_results['trials'].append(trial_results)

            print(f"\nTrial {trial + 1} Summary:")
            print(f"  Total execs: {trial_results['total_execs']}")
            print(f"  Unique crashes: {len(trial_results['unique_crashes'])}")
            print(f"  Mean exec/s: {trial_results['throughput_stats']['mean_exec_per_sec']:.1f}")

        # Aggregate statistics
        all_execs = [t['total_execs'] for t in all_results['trials']]
        all_crashes = [len(t['unique_crashes']) for t in all_results['trials']]
        all_throughput = [t['throughput_stats']['mean_exec_per_sec'] for t in all_results['trials']]

        all_results['aggregate'] = {
            'execs': {
                'mean': statistics.mean(all_execs),
                'median': statistics.median(all_execs),
                'stdev': statistics.stdev(all_execs) if len(all_execs) > 1 else 0
            },
            'unique_crashes': {
                'mean': statistics.mean(all_crashes),
                'median': statistics.median(all_crashes),
                'stdev': statistics.stdev(all_crashes) if len(all_crashes) > 1 else 0
            },
            'throughput_exec_per_sec': {
                'mean': statistics.mean(all_throughput),
                'median': statistics.median(all_throughput),
                'stdev': statistics.stdev(all_throughput) if len(all_throughput) > 1 else 0
            }
        }

        return all_results

    async def run_all_tests(self):
        """Run all fuzzing tests"""
        print("=" * 60)
        print("MODBUS FUZZING CAMPAIGN TESTS")
        print("=" * 60)

        # Multi-trial campaign
        results = await self.multi_trial_campaign(num_trials=5, duration_per_trial=60)

        output_file = self.output_dir / "modbus_fuzzing_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Fuzzing results saved to: {output_file}")

        print("\n" + "=" * 60)
        print("AGGREGATE RESULTS (5 trials, 60s each)")
        print("=" * 60)
        print(f"Mean execs per trial: {results['aggregate']['execs']['mean']:.0f} ± {results['aggregate']['execs']['stdev']:.0f}")
        print(f"Mean unique crashes: {results['aggregate']['unique_crashes']['mean']:.1f} ± {results['aggregate']['unique_crashes']['stdev']:.1f}")
        print(f"Mean throughput: {results['aggregate']['throughput_exec_per_sec']['mean']:.1f} exec/s")
        print("=" * 60)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "modbus_fuzzing"
    tester = ModbusFuzzingTester(output_dir)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
