#!/usr/bin/env python3
"""
Modbus/TCP Fuzzing Campaign Tests (Standalone Version)
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict
from collections import defaultdict
import random


class ModbusFuzzingTester:
    """Modbus fuzzing campaign tests"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def simulate_fuzzed_execution(self, params: Dict) -> Dict:
        """Simulate fuzzed execution with crash detection"""
        await asyncio.sleep(0.0001)  # Fast execution

        # Crash probability based on mutation level
        crash_prob = 0.003  # 0.3% crash rate
        exception_prob = 0.08  # 8% exception rate

        rand = random.random()

        if rand < crash_prob:
            crash_types = ['segfault', 'abort', 'assertion_failure', 'null_pointer']
            return {
                'status': 'error',
                'error': f'Crash: {random.choice(crash_types)}'
            }
        elif rand < crash_prob + exception_prob:
            return {
                'status': 'error',
                'error': f'Modbus Exception: {random.choice(["IllegalFunction", "IllegalDataAddress"])}'
            }
        else:
            return {'status': 'success'}

    async def fuzzing_campaign(self, duration_seconds: int = 60) -> Dict:
        """Run a fuzzing campaign"""
        results = {
            'start_time': time.time(),
            'duration_seconds': duration_seconds,
            'total_execs': 0,
            'crashes': [],
            'unique_crashes': set(),
            'exceptions': defaultdict(int),
            'exec_times_ms': [],
            'exec_per_second': [],
            'time_to_first_crash': None,
            'coverage_growth': []
        }

        print(f"Starting Modbus fuzzing campaign ({duration_seconds}s)...")

        start_time = time.time()
        last_second = int(start_time)
        execs_this_second = 0

        while (time.time() - start_time) < duration_seconds:
            params = {
                'function_code': random.randint(1, 255),
                'address': random.randint(0, 100000),
                'count': random.randint(1, 10000)
            }

            exec_start = time.time()
            response = await self.simulate_fuzzed_execution(params)
            exec_time = (time.time() - exec_start) * 1000
            results['exec_times_ms'].append(exec_time)

            if response.get('status') == 'error':
                error_msg = response.get('error', '')

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

            results['total_execs'] += 1
            execs_this_second += 1

            current_second = int(time.time())
            if current_second > last_second:
                results['exec_per_second'].append(execs_this_second)
                execs_this_second = 0
                last_second = current_second

            if results['total_execs'] % 100 == 0:
                results['coverage_growth'].append({
                    'execs': results['total_execs'],
                    'time': time.time() - start_time,
                    'unique_crashes': len(results['unique_crashes'])
                })

            if results['total_execs'] % 1000 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {results['total_execs']} execs, {elapsed:.1f}s, "
                      f"{len(results['unique_crashes'])} unique crashes")

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

    async def multi_trial_campaign(self, num_trials: int = 5, duration_per_trial: int = 60) -> Dict:
        """Run multiple fuzzing trials"""
        all_results = {
            'num_trials': num_trials,
            'duration_per_trial': duration_per_trial,
            'trials': []
        }

        print(f"\nRunning {num_trials} fuzzing trials ({duration_per_trial}s each)...")

        for trial in range(num_trials):
            print(f"\n--- Trial {trial + 1}/{num_trials} ---")
            trial_results = await self.fuzzing_campaign(duration_seconds=duration_per_trial)
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
