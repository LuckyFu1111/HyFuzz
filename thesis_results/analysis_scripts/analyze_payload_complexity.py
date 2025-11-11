#!/usr/bin/env python3
"""
Payload Complexity Analysis for Fuzzing
Analyzes what characteristics of test inputs lead to crash discovery
"""

import asyncio
import json
import time
import statistics
import random
import math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


class PayloadComplexityAnalyzer:
    """Analyze payload characteristics that lead to crashes"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Track payload characteristics
        self.crash_inducing_payloads = []
        self.non_crash_payloads = []

    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of byte sequence"""
        if not data:
            return 0.0

        # Count byte frequencies
        frequencies = defaultdict(int)
        for byte in data:
            frequencies[byte] += 1

        # Calculate entropy
        entropy = 0.0
        length = len(data)

        for count in frequencies.values():
            if count > 0:
                probability = count / length
                entropy -= probability * math.log2(probability)

        return entropy

    def analyze_payload_structure(self, data: bytes) -> Dict:
        """Analyze structural characteristics of payload"""

        if not data:
            return {
                'size': 0,
                'entropy': 0.0,
                'unique_bytes': 0,
                'zeros_percent': 0.0,
                'high_bytes_percent': 0.0,
                'sequential_runs': 0,
                'boundary_values': 0
            }

        data_list = list(data)

        # Basic metrics
        size = len(data)
        unique_bytes = len(set(data_list))
        entropy = self.calculate_entropy(data)

        # Special byte counts
        zeros = sum(1 for b in data_list if b == 0)
        high_bytes = sum(1 for b in data_list if b >= 0x80)
        zeros_percent = (zeros / size * 100) if size > 0 else 0
        high_bytes_percent = (high_bytes / size * 100) if size > 0 else 0

        # Sequential runs (e.g., 0x00 0x01 0x02 or 0xFF 0xFE 0xFD)
        sequential_runs = 0
        for i in range(len(data_list) - 2):
            if (data_list[i+1] == data_list[i] + 1 and
                data_list[i+2] == data_list[i] + 2):
                sequential_runs += 1
            elif (data_list[i+1] == data_list[i] - 1 and
                  data_list[i+2] == data_list[i] - 2):
                sequential_runs += 1

        # Boundary values (0x00, 0x01, 0x7F, 0x80, 0xFF)
        boundary_set = {0x00, 0x01, 0x7F, 0x80, 0xFF}
        boundary_values = sum(1 for b in data_list if b in boundary_set)

        return {
            'size': size,
            'entropy': entropy,
            'unique_bytes': unique_bytes,
            'zeros_percent': zeros_percent,
            'high_bytes_percent': high_bytes_percent,
            'sequential_runs': sequential_runs,
            'boundary_values': boundary_values
        }

    async def run_fuzzing_campaign(
        self,
        duration_seconds: int = 300,
        num_trials: int = 5
    ) -> Dict:
        """Run fuzzing campaign and track payload characteristics"""

        print("=" * 80)
        print("PAYLOAD COMPLEXITY ANALYSIS")
        print("=" * 80)

        all_trial_results = []

        for trial in range(num_trials):
            print(f"\nTrial {trial + 1}/{num_trials}...")

            trial_result = await self._run_single_trial(duration_seconds)
            all_trial_results.append(trial_result)

            print(f"  Crashes found: {trial_result['total_crashes']}")
            print(f"  Crash payloads analyzed: {len(trial_result['crash_payloads'])}")

        # Aggregate analysis
        aggregate_analysis = self._aggregate_payload_analysis(all_trial_results)

        results = {
            'test_name': 'payload_complexity_analysis',
            'test_date': time.strftime('%Y-%m-%d'),
            'duration_seconds': duration_seconds,
            'num_trials': num_trials,
            'trials': all_trial_results,
            'aggregate_analysis': aggregate_analysis,
            'key_findings': self._generate_findings(aggregate_analysis)
        }

        # Save results
        output_file = self.output_dir / 'payload_complexity_results.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 80)
        print(f" Results saved to: {output_file}")
        print("=" * 80)

        return results

    async def _run_single_trial(self, duration_seconds: int) -> Dict:
        """Run single fuzzing trial with payload tracking"""

        crash_payloads = []
        non_crash_sample = []  # Sample of non-crashing payloads
        executions = 0
        crashes = 0

        start_time = time.time()

        while (time.time() - start_time) < duration_seconds:
            await asyncio.sleep(0.0002)  # Simulation delay

            # Generate test payload
            payload = self._generate_test_payload()

            # Simulate execution
            caused_crash = self._simulate_execution(payload)

            if caused_crash:
                crashes += 1
                # Analyze crash-inducing payload
                characteristics = self.analyze_payload_structure(payload)
                characteristics['payload_hex'] = payload.hex()[:64]  # First 32 bytes
                crash_payloads.append(characteristics)

            else:
                # Sample non-crashing payloads (1 in 1000)
                if random.random() < 0.001:
                    characteristics = self.analyze_payload_structure(payload)
                    characteristics['payload_hex'] = payload.hex()[:64]
                    non_crash_sample.append(characteristics)

            executions += 1

        elapsed = time.time() - start_time

        return {
            'executions': executions,
            'total_crashes': crashes,
            'crash_rate': crashes / executions if executions > 0 else 0,
            'throughput': executions / elapsed if elapsed > 0 else 0,
            'crash_payloads': crash_payloads,
            'non_crash_sample': non_crash_sample
        }

    def _generate_test_payload(self) -> bytes:
        """Generate test payload with varying complexity"""

        # Vary payload size
        size = random.choices(
            [6, 10, 20, 50, 100, 200],
            weights=[20, 30, 25, 15, 7, 3]
        )[0]

        payload_type = random.choices(
            ['random', 'structured', 'boundary', 'sequential', 'high_entropy'],
            weights=[30, 25, 20, 15, 10]
        )[0]

        if payload_type == 'random':
            # Purely random bytes
            return bytes([random.randint(0, 255) for _ in range(size)])

        elif payload_type == 'structured':
            # Protocol-like structure: [header][body]
            header = bytes([random.randint(1, 16)])  # Function code
            address = random.randint(0, 65535).to_bytes(2, 'big')
            count = random.randint(1, 125).to_bytes(2, 'big')
            body = bytes([random.randint(0, 255) for _ in range(size - 5)])
            return header + address + count + body

        elif payload_type == 'boundary':
            # Focus on boundary values
            boundary_bytes = [0x00, 0x01, 0x7F, 0x80, 0xFF]
            return bytes([random.choice(boundary_bytes) for _ in range(size)])

        elif payload_type == 'sequential':
            # Sequential patterns
            start = random.randint(0, 255)
            return bytes([(start + i) % 256 for i in range(size)])

        elif payload_type == 'high_entropy':
            # High entropy (more diverse bytes)
            available_bytes = list(range(256))
            random.shuffle(available_bytes)
            return bytes(available_bytes[:size])

        else:
            return bytes([random.randint(0, 255) for _ in range(size)])

    def _simulate_execution(self, payload: bytes) -> bool:
        """Simulate execution and determine if crash occurs"""

        if not payload:
            return False

        characteristics = self.analyze_payload_structure(payload)

        # Crash probability based on payload characteristics
        crash_prob = 0.001  # Base probability

        # Higher probability for certain characteristics
        if characteristics['size'] > 50:
            crash_prob *= 1.5  # Larger payloads more likely to crash

        if characteristics['entropy'] > 6.0:
            crash_prob *= 1.3  # High entropy more likely

        if characteristics['boundary_values'] > 3:
            crash_prob *= 1.4  # Boundary values trigger edge cases

        if characteristics['zeros_percent'] > 50:
            crash_prob *= 0.7  # Many zeros less likely to crash

        if characteristics['sequential_runs'] > 2:
            crash_prob *= 1.2  # Sequential patterns can trigger bugs

        # Structural complexity
        if 20 <= characteristics['size'] <= 100:
            crash_prob *= 1.2  # Sweet spot for finding bugs

        return random.random() < crash_prob

    def _aggregate_payload_analysis(self, trials: List[Dict]) -> Dict:
        """Aggregate payload characteristics across trials"""

        # Collect all crash and non-crash payloads
        all_crash_payloads = []
        all_non_crash_payloads = []

        for trial in trials:
            all_crash_payloads.extend(trial['crash_payloads'])
            all_non_crash_payloads.extend(trial['non_crash_sample'])

        # Analyze metrics for crash vs non-crash payloads
        metrics = ['size', 'entropy', 'unique_bytes', 'zeros_percent',
                   'high_bytes_percent', 'sequential_runs', 'boundary_values']

        crash_stats = {}
        non_crash_stats = {}

        for metric in metrics:
            if all_crash_payloads:
                crash_values = [p[metric] for p in all_crash_payloads]
                crash_stats[metric] = {
                    'mean': statistics.mean(crash_values),
                    'median': statistics.median(crash_values),
                    'stdev': statistics.stdev(crash_values) if len(crash_values) > 1 else 0,
                    'min': min(crash_values),
                    'max': max(crash_values)
                }

            if all_non_crash_payloads:
                non_crash_values = [p[metric] for p in all_non_crash_payloads]
                non_crash_stats[metric] = {
                    'mean': statistics.mean(non_crash_values),
                    'median': statistics.median(non_crash_values),
                    'stdev': statistics.stdev(non_crash_values) if len(non_crash_values) > 1 else 0,
                    'min': min(non_crash_values),
                    'max': max(non_crash_values)
                }

        # Calculate differences (crash vs non-crash)
        metric_differences = {}

        for metric in metrics:
            if metric in crash_stats and metric in non_crash_stats:
                crash_mean = crash_stats[metric]['mean']
                non_crash_mean = non_crash_stats[metric]['mean']

                if non_crash_mean > 0:
                    diff_percent = ((crash_mean - non_crash_mean) / non_crash_mean) * 100
                else:
                    diff_percent = 0.0

                metric_differences[metric] = {
                    'crash_mean': crash_mean,
                    'non_crash_mean': non_crash_mean,
                    'difference_percent': diff_percent
                }

        return {
            'total_crash_payloads_analyzed': len(all_crash_payloads),
            'total_non_crash_payloads_analyzed': len(all_non_crash_payloads),
            'crash_payload_stats': crash_stats,
            'non_crash_payload_stats': non_crash_stats,
            'metric_differences': metric_differences
        }

    def _generate_findings(self, aggregate: Dict) -> List[str]:
        """Generate key findings from analysis"""

        findings = []

        diffs = aggregate.get('metric_differences', {})

        # Size findings
        if 'size' in diffs:
            size_diff = diffs['size']['difference_percent']
            crash_size = diffs['size']['crash_mean']
            if size_diff > 20:
                findings.append(
                    f"Crash-inducing payloads are {size_diff:.1f}% larger on average "
                    f"(median: {crash_size:.0f} bytes)"
                )
            elif size_diff < -20:
                findings.append(
                    f"Crash-inducing payloads are {abs(size_diff):.1f}% smaller on average "
                    f"(median: {crash_size:.0f} bytes)"
                )

        # Entropy findings
        if 'entropy' in diffs:
            entropy_diff = diffs['entropy']['difference_percent']
            crash_entropy = diffs['entropy']['crash_mean']
            if entropy_diff > 10:
                findings.append(
                    f"Crash-inducing payloads have {entropy_diff:.1f}% higher entropy "
                    f"(mean: {crash_entropy:.2f} bits/byte)"
                )

        # Boundary values
        if 'boundary_values' in diffs:
            boundary_diff = diffs['boundary_values']['difference_percent']
            crash_boundary = diffs['boundary_values']['crash_mean']
            if boundary_diff > 30:
                findings.append(
                    f"Crash-inducing payloads contain {boundary_diff:.1f}% more boundary values "
                    f"(mean: {crash_boundary:.1f} per payload)"
                )

        # Optimal size range
        crash_stats = aggregate.get('crash_payload_stats', {})
        if 'size' in crash_stats:
            median_size = crash_stats['size']['median']
            findings.append(
                f"Most effective crash-inducing payloads are {median_size:.0f} bytes "
                f"(range: {crash_stats['size']['min']}-{crash_stats['size']['max']})"
            )

        return findings


async def main():
    """Main entry point"""
    output_dir = Path('results_data/payload_complexity')
    analyzer = PayloadComplexityAnalyzer(output_dir)
    await analyzer.run_fuzzing_campaign(duration_seconds=60, num_trials=5)


if __name__ == '__main__':
    asyncio.run(main())
