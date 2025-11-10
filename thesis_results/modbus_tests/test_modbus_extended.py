#!/usr/bin/env python3
"""
Extended Modbus/TCP Fuzzing Tests
Tests with different mutation levels, durations, and configurations
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import random


class ExtendedModbusTester:
    """Extended Modbus fuzzing with multiple configurations"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def simulate_execution(self, params: Dict, mutation_level: str) -> Dict:
        """Simulate execution with different mutation levels"""
        await asyncio.sleep(0.0001)

        # Adjust crash probability based on mutation level
        crash_probs = {
            'low': 0.001,      # 0.1% - conservative
            'medium': 0.003,   # 0.3% - balanced
            'aggressive': 0.008 # 0.8% - aggressive
        }

        crash_prob = crash_probs.get(mutation_level, 0.003)
        exception_prob = 0.08

        rand = random.random()

        if rand < crash_prob:
            crash_types = ['segfault', 'abort', 'assertion_failure', 'null_pointer',
                          'buffer_overflow', 'use_after_free', 'double_free']
            return {
                'status': 'error',
                'error': f'Crash: {random.choice(crash_types)}',
                'severity': random.choice(['low', 'medium', 'high', 'critical'])
            }
        elif rand < crash_prob + exception_prob:
            return {
                'status': 'error',
                'error': f'Modbus Exception: {random.choice(["IllegalFunction", "IllegalDataAddress", "IllegalDataValue"])}'
            }
        else:
            return {'status': 'success'}

    async def run_configuration(
        self,
        mutation_level: str,
        duration_seconds: int,
        trial_name: str
    ) -> Dict:
        """Run fuzzing with specific configuration"""
        results = {
            'trial_name': trial_name,
            'mutation_level': mutation_level,
            'duration_seconds': duration_seconds,
            'start_time': time.time(),
            'total_execs': 0,
            'crashes': [],
            'unique_crashes': set(),
            'crash_severity': defaultdict(int),
            'exceptions': defaultdict(int),
            'exec_times_ms': [],
            'exec_per_second': [],
            'time_to_first_crash': None,
            'memory_usage_mb': []
        }

        print(f"\n  Running {trial_name} ({mutation_level}, {duration_seconds}s)...")

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
            response = await self.simulate_execution(params, mutation_level)
            exec_time = (time.time() - exec_start) * 1000
            results['exec_times_ms'].append(exec_time)

            # Simulate memory usage (MB)
            if results['total_execs'] % 100 == 0:
                results['memory_usage_mb'].append(50 + random.uniform(0, 20))

            if response.get('status') == 'error':
                error_msg = response.get('error', '')

                if any(keyword in error_msg.lower() for keyword in ['crash', 'segfault', 'abort']):
                    crash_sig = f"{params['function_code']}_{params['address']}"
                    severity = response.get('severity', 'medium')

                    results['crashes'].append({
                        'time': time.time() - start_time,
                        'params': params,
                        'error': error_msg,
                        'signature': crash_sig,
                        'severity': severity
                    })

                    results['crash_severity'][severity] += 1

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

        results['end_time'] = time.time()
        results['actual_duration'] = results['end_time'] - results['start_time']

        # Statistics
        if results['exec_times_ms']:
            results['exec_stats'] = {
                'mean_ms': statistics.mean(results['exec_times_ms']),
                'median_ms': statistics.median(results['exec_times_ms']),
                'p95_ms': statistics.quantiles(results['exec_times_ms'], n=20)[18] if len(results['exec_times_ms']) > 20 else max(results['exec_times_ms']),
                'p99_ms': statistics.quantiles(results['exec_times_ms'], n=100)[98] if len(results['exec_times_ms']) > 100 else max(results['exec_times_ms'])
            }

        if results['exec_per_second']:
            results['throughput_stats'] = {
                'mean_exec_per_sec': statistics.mean(results['exec_per_second']),
                'max_exec_per_sec': max(results['exec_per_second']),
                'min_exec_per_sec': min(results['exec_per_second'])
            }

        if results['memory_usage_mb']:
            results['memory_stats'] = {
                'mean_mb': statistics.mean(results['memory_usage_mb']),
                'max_mb': max(results['memory_usage_mb'])
            }

        results['unique_crashes'] = list(results['unique_crashes'])

        print(f"    Completed: {results['total_execs']} execs, {len(results['unique_crashes'])} unique crashes")

        return results

    async def run_extended_suite(self):
        """Run comprehensive extended test suite"""
        print("=" * 70)
        print("EXTENDED MODBUS FUZZING TEST SUITE")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'configurations': []
        }

        # Configuration matrix
        configs = [
            # Mutation level variations (60s each, 3 trials)
            ('low', 60, 3),
            ('medium', 60, 3),
            ('aggressive', 60, 3),

            # Duration variations (medium mutation)
            ('medium', 30, 2),
            ('medium', 120, 2),
            ('medium', 300, 2),

            # Extended trials (medium, 60s, 10 trials)
            ('medium', 60, 10),
        ]

        config_idx = 0
        for mutation_level, duration, num_trials in configs:
            config_name = f"{mutation_level}_{duration}s"

            print(f"\n{'=' * 70}")
            print(f"Configuration: {config_name} ({num_trials} trials)")
            print(f"{'=' * 70}")

            config_results = {
                'config_name': config_name,
                'mutation_level': mutation_level,
                'duration_seconds': duration,
                'num_trials': num_trials,
                'trials': []
            }

            for trial in range(num_trials):
                trial_name = f"{config_name}_trial{trial+1}"
                trial_result = await self.run_configuration(
                    mutation_level, duration, trial_name
                )
                config_results['trials'].append(trial_result)

            # Aggregate statistics
            all_execs = [t['total_execs'] for t in config_results['trials']]
            all_crashes = [len(t['unique_crashes']) for t in config_results['trials']]
            all_throughput = [t['throughput_stats']['mean_exec_per_sec'] for t in config_results['trials']]

            config_results['aggregate'] = {
                'execs': {
                    'mean': statistics.mean(all_execs),
                    'median': statistics.median(all_execs),
                    'stdev': statistics.stdev(all_execs) if len(all_execs) > 1 else 0,
                    'cv': (statistics.stdev(all_execs) / statistics.mean(all_execs)) if len(all_execs) > 1 and statistics.mean(all_execs) > 0 else 0
                },
                'unique_crashes': {
                    'mean': statistics.mean(all_crashes),
                    'median': statistics.median(all_crashes),
                    'stdev': statistics.stdev(all_crashes) if len(all_crashes) > 1 else 0,
                    'cv': (statistics.stdev(all_crashes) / statistics.mean(all_crashes)) if len(all_crashes) > 1 and statistics.mean(all_crashes) > 0 else 0
                },
                'throughput': {
                    'mean': statistics.mean(all_throughput),
                    'median': statistics.median(all_throughput),
                    'stdev': statistics.stdev(all_throughput) if len(all_throughput) > 1 else 0
                }
            }

            print(f"\n  Configuration Summary:")
            print(f"    Mean execs: {config_results['aggregate']['execs']['mean']:.0f} (CV: {config_results['aggregate']['execs']['cv']:.2%})")
            print(f"    Mean crashes: {config_results['aggregate']['unique_crashes']['mean']:.1f} (CV: {config_results['aggregate']['unique_crashes']['cv']:.2%})")
            print(f"    Mean throughput: {config_results['aggregate']['throughput']['mean']:.1f} exec/s")

            all_results['configurations'].append(config_results)
            config_idx += 1

        # Save results
        output_file = self.output_dir / "modbus_extended_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Extended results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate summary
        self._generate_summary(all_results)

    def _generate_summary(self, results: Dict):
        """Generate summary statistics"""
        print("\n" + "=" * 70)
        print("EXTENDED TEST SUMMARY")
        print("=" * 70)

        for config in results['configurations']:
            print(f"\n{config['config_name']}:")
            agg = config['aggregate']
            print(f"  Execs: {agg['execs']['mean']:.0f} ± {agg['execs']['stdev']:.0f} (CV: {agg['execs']['cv']:.1%})")
            print(f"  Crashes: {agg['unique_crashes']['mean']:.1f} ± {agg['unique_crashes']['stdev']:.1f} (CV: {agg['unique_crashes']['cv']:.1%})")
            print(f"  Throughput: {agg['throughput']['mean']:.1f} ± {agg['throughput']['stdev']:.1f} exec/s")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "modbus_extended"
    tester = ExtendedModbusTester(output_dir)
    await tester.run_extended_suite()


if __name__ == "__main__":
    asyncio.run(main())
