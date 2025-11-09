#!/usr/bin/env python3
"""
CoAP Fuzzing Campaign Tests
Bug-finding and efficiency with DTLS support
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict
from collections import defaultdict
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HyFuzz-Ubuntu-Client" / "src"))

from protocols.coap_handler import CoAPHandler


class CoAPFuzzingTester:
    """CoAP fuzzing tests"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.handler = CoAPHandler()

    def generate_fuzz_params(self, dtls_enabled: bool = False) -> Dict:
        """Generate fuzzed CoAP parameters"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'INVALID', '']
        paths = ['/', '/test', '/../../etc/passwd', '/' + 'A' * 1000, '/\x00\x01\x02']

        params = {
            'method': random.choice(methods),
            'path': random.choice(paths),
            'confirmable': random.choice([True, False]),
            'dtls': dtls_enabled
        }

        # Add random options
        if random.random() < 0.3:
            params['observe'] = random.choice([True, False, 2, -1, 999])

        if random.random() < 0.3:
            params['block1'] = random.randint(-1, 100)
            params['szx'] = random.choice([16, 32, 64, 128, 256, 512, 1024, 2048, 10000])

        return params

    async def fuzzing_campaign(
        self,
        duration_seconds: int = 300,
        dtls_enabled: bool = False
    ) -> Dict:
        """
        Run CoAP fuzzing campaign

        Args:
            duration_seconds: Campaign duration
            dtls_enabled: Whether DTLS is enabled
        """
        results = {
            'start_time': time.time(),
            'duration_seconds': duration_seconds,
            'dtls_enabled': dtls_enabled,
            'total_execs': 0,
            'crashes': [],
            'unique_crashes': set(),
            'exceptions': defaultdict(int),
            'exec_times_ms': [],
            'exec_per_second': [],
            'time_to_first_crash': None,
            'dtls_handshake_times_ms': []
        }

        print(f"Starting CoAP fuzzing (DTLS: {dtls_enabled}, {duration_seconds}s)...")

        start_time = time.time()
        last_second = int(start_time)
        execs_this_second = 0

        # Simulate DTLS handshake if enabled
        if dtls_enabled:
            handshake_start = time.time()
            await asyncio.sleep(0.1)  # Simulate handshake
            handshake_time = (time.time() - handshake_start) * 1000
            results['dtls_handshake_times_ms'].append(handshake_time)
            print(f"  DTLS handshake completed in {handshake_time:.2f}ms")

        while (time.time() - start_time) < duration_seconds:
            params = self.generate_fuzz_params(dtls_enabled)

            exec_start = time.time()
            try:
                response = await self.handler.execute(params)
                exec_time = (time.time() - exec_start) * 1000
                results['exec_times_ms'].append(exec_time)

                # Check for crashes
                if response.get('status') == 'error':
                    error_msg = response.get('error', '')

                    if any(keyword in error_msg.lower() for keyword in ['crash', 'segfault', 'abort', 'assert']):
                        crash_sig = f"{params.get('method', '')}_{params.get('path', '')}"
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

            if results['total_execs'] % 500 == 0:
                elapsed = time.time() - start_time
                print(f"  Progress: {results['total_execs']} execs, {elapsed:.1f}s, "
                      f"{len(results['unique_crashes'])} unique crashes")

        # Statistics
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

    async def compare_dtls_impact(
        self,
        num_trials: int = 3,
        duration_per_trial: int = 60
    ) -> Dict:
        """Compare fuzzing with and without DTLS"""
        results = {
            'num_trials': num_trials,
            'duration_per_trial': duration_per_trial,
            'no_dtls_trials': [],
            'with_dtls_trials': []
        }

        print("=" * 60)
        print("DTLS IMPACT COMPARISON")
        print("=" * 60)

        # Without DTLS
        print(f"\nRunning {num_trials} trials WITHOUT DTLS...")
        for trial in range(num_trials):
            print(f"\n--- NO DTLS Trial {trial + 1}/{num_trials} ---")
            trial_result = await self.fuzzing_campaign(duration_per_trial, dtls_enabled=False)
            results['no_dtls_trials'].append(trial_result)

        # With DTLS
        print(f"\nRunning {num_trials} trials WITH DTLS...")
        for trial in range(num_trials):
            print(f"\n--- DTLS Trial {trial + 1}/{num_trials} ---")
            trial_result = await self.fuzzing_campaign(duration_per_trial, dtls_enabled=True)
            results['with_dtls_trials'].append(trial_result)

        # Aggregate comparison
        no_dtls_execs = [t['total_execs'] for t in results['no_dtls_trials']]
        with_dtls_execs = [t['total_execs'] for t in results['with_dtls_trials']]

        no_dtls_crashes = [len(t['unique_crashes']) for t in results['no_dtls_trials']]
        with_dtls_crashes = [len(t['unique_crashes']) for t in results['with_dtls_trials']]

        results['comparison'] = {
            'no_dtls': {
                'mean_execs': statistics.mean(no_dtls_execs),
                'mean_crashes': statistics.mean(no_dtls_crashes)
            },
            'with_dtls': {
                'mean_execs': statistics.mean(with_dtls_execs),
                'mean_crashes': statistics.mean(with_dtls_crashes)
            }
        }

        # Calculate overhead
        exec_overhead = (results['comparison']['no_dtls']['mean_execs'] -
                        results['comparison']['with_dtls']['mean_execs']) / \
                       results['comparison']['no_dtls']['mean_execs']

        results['comparison']['dtls_overhead_percent'] = exec_overhead * 100

        return results

    async def run_all_tests(self):
        """Run all CoAP fuzzing tests"""
        print("=" * 60)
        print("CoAP FUZZING CAMPAIGN TESTS")
        print("=" * 60)

        results = await self.compare_dtls_impact(num_trials=3, duration_per_trial=60)

        output_file = self.output_dir / "coap_fuzzing_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")

        print("\n" + "=" * 60)
        print("DTLS COMPARISON SUMMARY")
        print("=" * 60)
        print(f"WITHOUT DTLS:")
        print(f"  Mean execs: {results['comparison']['no_dtls']['mean_execs']:.0f}")
        print(f"  Mean unique crashes: {results['comparison']['no_dtls']['mean_crashes']:.1f}")

        print(f"\nWITH DTLS:")
        print(f"  Mean execs: {results['comparison']['with_dtls']['mean_execs']:.0f}")
        print(f"  Mean unique crashes: {results['comparison']['with_dtls']['mean_crashes']:.1f}")

        print(f"\nDTLS Overhead: {results['comparison']['dtls_overhead_percent']:.1f}%")
        print("=" * 60)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "coap_fuzzing"
    tester = CoAPFuzzingTester(output_dir)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
