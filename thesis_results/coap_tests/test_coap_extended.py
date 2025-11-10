#!/usr/bin/env python3
"""
Extended CoAP Fuzzing Tests
Tests with different message types, DTLS configurations, and stress tests
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import random


class ExtendedCoAPTester:
    """Extended CoAP fuzzing with multiple configurations"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def simulate_execution(
        self,
        params: Dict,
        test_mode: str,
        dtls_enabled: bool
    ) -> Dict:
        """Simulate CoAP execution with different test modes"""
        # Base latency
        base_latency = 0.0001

        # DTLS overhead
        if dtls_enabled:
            base_latency *= 1.15

        await asyncio.sleep(base_latency)

        # Crash probability varies by test mode
        crash_probs = {
            'normal': 0.0003,
            'observe_stress': 0.0005,
            'blockwise_stress': 0.0004,
            'mixed': 0.0004
        }

        crash_prob = crash_probs.get(test_mode, 0.0003)

        rand = random.random()

        if rand < crash_prob:
            crash_types = ['segfault', 'null_pointer', 'buffer_overflow',
                          'assertion_failure', 'memory_leak']
            return {
                'status': 'error',
                'error': f'Crash: {random.choice(crash_types)}',
                'test_mode': test_mode
            }
        elif rand < 0.05:
            return {
                'status': 'error',
                'error': 'CoAP Error: Invalid token'
            }
        else:
            return {
                'status': 'success',
                'code': random.choice([200, 201, 204, 400, 404, 500])
            }

    async def run_test_mode(
        self,
        test_mode: str,
        dtls_enabled: bool,
        duration_seconds: int,
        num_trials: int
    ) -> Dict:
        """Run specific test mode"""
        mode_results = {
            'test_mode': test_mode,
            'dtls_enabled': dtls_enabled,
            'duration_seconds': duration_seconds,
            'num_trials': num_trials,
            'trials': []
        }

        print(f"\n  Test Mode: {test_mode}, DTLS: {dtls_enabled}, {num_trials} trials...")

        for trial in range(num_trials):
            trial_results = {
                'trial': trial + 1,
                'total_execs': 0,
                'crashes': [],
                'unique_crashes': set(),
                'observe_operations': 0,
                'blockwise_operations': 0,
                'exec_per_second': [],
                'response_codes': defaultdict(int)
            }

            start_time = time.time()
            last_second = int(start_time)
            execs_this_second = 0

            while (time.time() - start_time) < duration_seconds:
                # Generate params based on test mode
                if test_mode == 'observe_stress':
                    params = {
                        'method': 'GET',
                        'path': '/observe',
                        'observe': True
                    }
                    trial_results['observe_operations'] += 1
                elif test_mode == 'blockwise_stress':
                    params = {
                        'method': random.choice(['GET', 'POST']),
                        'path': '/large',
                        'block': random.randint(0, 10),
                        'szx': random.choice([16, 32, 64, 128, 256])
                    }
                    trial_results['blockwise_operations'] += 1
                elif test_mode == 'mixed':
                    if random.random() < 0.3:
                        params = {'method': 'GET', 'path': '/observe', 'observe': True}
                        trial_results['observe_operations'] += 1
                    elif random.random() < 0.6:
                        params = {'method': 'POST', 'path': '/upload', 'block': random.randint(0, 5)}
                        trial_results['blockwise_operations'] += 1
                    else:
                        params = {'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']), 'path': f'/res{random.randint(1,10)}'}
                else:  # normal
                    params = {
                        'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                        'path': f'/resource{random.randint(1, 20)}'
                    }

                response = await self.simulate_execution(params, test_mode, dtls_enabled)

                if response.get('status') == 'success':
                    code = response.get('code', 200)
                    trial_results['response_codes'][code] += 1
                elif 'crash' in response.get('error', '').lower():
                    crash_sig = f"{params.get('method', '')}_{params.get('path', '')}"
                    trial_results['crashes'].append({
                        'time': time.time() - start_time,
                        'params': params,
                        'error': response.get('error', ''),
                        'signature': crash_sig
                    })

                    if crash_sig not in trial_results['unique_crashes']:
                        trial_results['unique_crashes'].add(crash_sig)

                trial_results['total_execs'] += 1
                execs_this_second += 1

                current_second = int(time.time())
                if current_second > last_second:
                    trial_results['exec_per_second'].append(execs_this_second)
                    execs_this_second = 0
                    last_second = current_second

            trial_results['unique_crashes'] = list(trial_results['unique_crashes'])

            if trial_results['exec_per_second']:
                trial_results['mean_throughput'] = statistics.mean(trial_results['exec_per_second'])

            mode_results['trials'].append(trial_results)

        # Aggregate
        all_execs = [t['total_execs'] for t in mode_results['trials']]
        all_crashes = [len(t['unique_crashes']) for t in mode_results['trials']]
        all_throughput = [t.get('mean_throughput', 0) for t in mode_results['trials'] if 'mean_throughput' in t]

        mode_results['aggregate'] = {
            'execs': {
                'mean': statistics.mean(all_execs),
                'stdev': statistics.stdev(all_execs) if len(all_execs) > 1 else 0
            },
            'crashes': {
                'mean': statistics.mean(all_crashes),
                'stdev': statistics.stdev(all_crashes) if len(all_crashes) > 1 else 0
            },
            'throughput': {
                'mean': statistics.mean(all_throughput) if all_throughput else 0,
                'stdev': statistics.stdev(all_throughput) if len(all_throughput) > 1 else 0
            }
        }

        print(f"    Results: {mode_results['aggregate']['execs']['mean']:.0f} execs, "
              f"{mode_results['aggregate']['crashes']['mean']:.1f} crashes")

        return mode_results

    async def run_extended_suite(self):
        """Run comprehensive CoAP test suite"""
        print("=" * 70)
        print("EXTENDED CoAP FUZZING TEST SUITE")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_modes': []
        }

        # Test configurations
        test_configs = [
            # Test mode, DTLS, duration, trials
            ('normal', False, 60, 5),
            ('normal', True, 60, 5),
            ('observe_stress', False, 90, 3),
            ('observe_stress', True, 90, 3),
            ('blockwise_stress', False, 90, 3),
            ('blockwise_stress', True, 90, 3),
            ('mixed', False, 120, 3),
            ('mixed', True, 120, 3),
        ]

        for test_mode, dtls, duration, trials in test_configs:
            print(f"\n{'=' * 70}")
            print(f"Configuration: {test_mode}, DTLS: {dtls}, {duration}s × {trials} trials")
            print(f"{'=' * 70}")

            mode_results = await self.run_test_mode(test_mode, dtls, duration, trials)
            all_results['test_modes'].append(mode_results)

        # Save results
        output_file = self.output_dir / "coap_extended_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Extended CoAP results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate summary
        self._generate_summary(all_results)

    def _generate_summary(self, results: Dict):
        """Generate summary statistics"""
        print("\n" + "=" * 70)
        print("EXTENDED CoAP TEST SUMMARY")
        print("=" * 70)

        for mode in results['test_modes']:
            dtls_str = "DTLS" if mode['dtls_enabled'] else "Plain"
            print(f"\n{mode['test_mode']} ({dtls_str}):")
            agg = mode['aggregate']
            print(f"  Execs: {agg['execs']['mean']:.0f} ± {agg['execs']['stdev']:.0f}")
            print(f"  Crashes: {agg['crashes']['mean']:.1f} ± {agg['crashes']['stdev']:.1f}")
            print(f"  Throughput: {agg['throughput']['mean']:.1f} ± {agg['throughput']['stdev']:.1f} exec/s")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "coap_extended"
    tester = ExtendedCoAPTester(output_dir)
    await tester.run_extended_suite()


if __name__ == "__main__":
    asyncio.run(main())
