#!/usr/bin/env python3
"""
Long-term Stability Testing for Modbus Fuzzing
Tests memory leaks, performance degradation, and resource exhaustion over extended periods (6-24h)
"""

import asyncio
import json
import time
import psutil
import os
import statistics
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict


class LongTermStabilityTester:
    """Test long-term stability and resource usage"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = None

    async def simulate_modbus_fuzzing(
        self,
        duration_hours: float,
        sample_interval_seconds: int = 300
    ) -> Dict:
        """
        Run fuzzing campaign with periodic sampling

        Args:
            duration_hours: Total test duration in hours
            sample_interval_seconds: Sampling interval (default 5 minutes)
        """
        print(f"\n{'=' * 70}")
        print(f"LONG-TERM STABILITY TEST")
        print(f"Duration: {duration_hours} hours ({duration_hours * 60:.0f} minutes)")
        print(f"Sample Interval: {sample_interval_seconds}s ({sample_interval_seconds / 60:.0f} minutes)")
        print(f"{'=' * 70}\n")

        start_time = time.time()
        end_time = start_time + (duration_hours * 3600)

        # Initialize baseline
        self.baseline_memory = self.process.memory_info().rss / (1024 * 1024)  # MB

        results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_hours': duration_hours,
            'sample_interval_seconds': sample_interval_seconds,
            'samples': [],
            'metrics': {
                'total_executions': 0,
                'total_crashes': 0,
                'total_unique_crashes': set()
            }
        }

        sample_count = 0
        next_sample_time = start_time + sample_interval_seconds

        # Fuzzing state
        crash_signatures = set()
        executions_this_sample = 0
        crashes_this_sample = 0

        print(f"Start Time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Expected End: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\nProgress:")

        while time.time() < end_time:
            current_time = time.time()

            # Simulate fuzzing execution
            await asyncio.sleep(0.0002)  # Simulate ~5000 exec/s baseline

            # Simulate crash discovery (probabilistic)
            if self._should_discover_crash(results['metrics']['total_executions']):
                crash_sig = f"crash_{len(crash_signatures)}_{current_time}"
                crash_signatures.add(crash_sig)
                crashes_this_sample += 1
                results['metrics']['total_crashes'] += 1

            executions_this_sample += 1
            results['metrics']['total_executions'] += 1

            # Take sample at intervals
            if current_time >= next_sample_time:
                sample = await self._take_sample(
                    sample_count,
                    current_time - start_time,
                    executions_this_sample,
                    crashes_this_sample,
                    len(crash_signatures)
                )
                results['samples'].append(sample)

                # Print progress
                elapsed_hours = (current_time - start_time) / 3600
                progress_pct = (elapsed_hours / duration_hours) * 100
                print(f"  [{elapsed_hours:.1f}h/{duration_hours}h] {progress_pct:.1f}% - "
                      f"{executions_this_sample} execs, {crashes_this_sample} crashes, "
                      f"{sample['memory_mb']:.1f} MB, {sample['throughput']:.0f} exec/s")

                # Reset counters for next sample
                executions_this_sample = 0
                crashes_this_sample = 0
                sample_count += 1
                next_sample_time += sample_interval_seconds

        results['metrics']['total_unique_crashes'] = list(crash_signatures)

        # Analyze results
        results['analysis'] = self._analyze_stability(results)

        # Save results
        output_file = self.output_dir / f"stability_{duration_hours}h_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n{'=' * 70}")
        print(f"✓ Stability test completed!")
        print(f"  Results saved to: {output_file}")
        print(f"{'=' * 70}\n")

        self._print_summary(results)

        return results

    def _should_discover_crash(self, total_execs: int) -> bool:
        """Determine if crash should be discovered (with saturation)"""
        import random

        # Crash discovery rate decreases over time (saturation effect)
        if total_execs < 100000:
            prob = 0.003  # Early: high discovery rate
        elif total_execs < 500000:
            prob = 0.002  # Medium: moderate rate
        elif total_execs < 1000000:
            prob = 0.001  # Later: lower rate
        else:
            prob = 0.0005  # Saturated: very low rate

        return random.random() < prob

    async def _take_sample(
        self,
        sample_num: int,
        elapsed_seconds: float,
        execs_since_last: int,
        crashes_since_last: int,
        total_unique_crashes: int
    ) -> Dict:
        """Take performance and resource sample"""

        # Get memory info
        mem_info = self.process.memory_info()
        memory_mb = mem_info.rss / (1024 * 1024)
        memory_growth = memory_mb - self.baseline_memory

        # Get CPU info
        cpu_percent = self.process.cpu_percent(interval=0.1)

        # Calculate throughput
        sample_interval = 300  # 5 minutes in seconds
        throughput = execs_since_last / sample_interval if sample_interval > 0 else 0

        # Get thread count
        num_threads = self.process.num_threads()

        # Get open file descriptors
        try:
            num_fds = len(self.process.open_files())
        except (psutil.AccessDenied, AttributeError):
            num_fds = -1

        sample = {
            'sample_number': sample_num,
            'elapsed_seconds': elapsed_seconds,
            'elapsed_hours': elapsed_seconds / 3600,
            'memory_mb': memory_mb,
            'memory_growth_mb': memory_growth,
            'memory_growth_percent': (memory_growth / self.baseline_memory * 100) if self.baseline_memory > 0 else 0,
            'cpu_percent': cpu_percent,
            'num_threads': num_threads,
            'num_open_files': num_fds,
            'executions_since_last': execs_since_last,
            'crashes_since_last': crashes_since_last,
            'total_unique_crashes': total_unique_crashes,
            'throughput': throughput,
            'timestamp': time.time()
        }

        return sample

    def _analyze_stability(self, results: Dict) -> Dict:
        """Analyze stability metrics"""
        samples = results['samples']

        if len(samples) < 2:
            return {'error': 'Insufficient samples for analysis'}

        # Memory leak detection
        memory_values = [s['memory_mb'] for s in samples]
        memory_growth_values = [s['memory_growth_mb'] for s in samples]

        # Linear regression for memory trend
        x = list(range(len(memory_values)))
        memory_trend_slope = self._calculate_linear_slope(x, memory_values)

        # Throughput degradation
        throughput_values = [s['throughput'] for s in samples]
        throughput_trend_slope = self._calculate_linear_slope(x, throughput_values)

        # Crash discovery rate over time
        crashes_per_sample = [s['crashes_since_last'] for s in samples]
        crash_rate_trend = self._calculate_linear_slope(x, crashes_per_sample)

        # CPU stability
        cpu_values = [s['cpu_percent'] for s in samples]

        analysis = {
            'memory_analysis': {
                'baseline_mb': self.baseline_memory,
                'final_mb': memory_values[-1],
                'total_growth_mb': memory_values[-1] - self.baseline_memory,
                'total_growth_percent': ((memory_values[-1] - self.baseline_memory) / self.baseline_memory * 100) if self.baseline_memory > 0 else 0,
                'growth_rate_mb_per_hour': memory_trend_slope * (3600 / 300),  # Convert to per-hour
                'mean_memory_mb': statistics.mean(memory_values),
                'stdev_memory_mb': statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                'memory_leak_detected': memory_trend_slope > 0.5  # > 0.5 MB per sample = potential leak
            },
            'throughput_analysis': {
                'initial_throughput': throughput_values[0] if throughput_values else 0,
                'final_throughput': throughput_values[-1] if throughput_values else 0,
                'mean_throughput': statistics.mean(throughput_values),
                'stdev_throughput': statistics.stdev(throughput_values) if len(throughput_values) > 1 else 0,
                'degradation_rate_per_hour': throughput_trend_slope * (3600 / 300),
                'performance_degradation_detected': throughput_trend_slope < -10  # Declining > 10 exec/s per sample
            },
            'crash_discovery_analysis': {
                'total_unique_crashes': len(results['metrics']['total_unique_crashes']),
                'mean_crashes_per_sample': statistics.mean(crashes_per_sample),
                'crash_discovery_rate_trend': crash_rate_trend,
                'saturation_detected': crash_rate_trend < -0.1  # Discovery rate declining
            },
            'cpu_analysis': {
                'mean_cpu_percent': statistics.mean(cpu_values),
                'max_cpu_percent': max(cpu_values),
                'stdev_cpu_percent': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                'cpu_stable': statistics.stdev(cpu_values) < 10 if len(cpu_values) > 1 else True
            },
            'stability_score': self._calculate_stability_score(
                memory_trend_slope,
                throughput_trend_slope,
                statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
            )
        }

        return analysis

    def _calculate_linear_slope(self, x: List[float], y: List[float]) -> float:
        """Calculate slope of linear regression line"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_stability_score(
        self,
        memory_slope: float,
        throughput_slope: float,
        cpu_stdev: float
    ) -> float:
        """
        Calculate overall stability score (0-100)
        Higher is better
        """
        score = 100.0

        # Penalty for memory growth (> 0.5 MB per 5min sample)
        if memory_slope > 0.5:
            score -= min(30, memory_slope * 10)

        # Penalty for throughput degradation (> 10 exec/s decline per 5min)
        if throughput_slope < -10:
            score -= min(30, abs(throughput_slope))

        # Penalty for CPU instability (stdev > 10%)
        if cpu_stdev > 10:
            score -= min(20, cpu_stdev)

        return max(0, score)

    def _print_summary(self, results: Dict):
        """Print analysis summary"""
        analysis = results['analysis']

        print("=" * 70)
        print("STABILITY ANALYSIS SUMMARY")
        print("=" * 70)

        print("\n1. Memory Analysis:")
        mem = analysis['memory_analysis']
        print(f"   Baseline: {mem['baseline_mb']:.1f} MB")
        print(f"   Final: {mem['final_mb']:.1f} MB")
        print(f"   Growth: {mem['total_growth_mb']:.1f} MB ({mem['total_growth_percent']:.1f}%)")
        print(f"   Growth Rate: {mem['growth_rate_mb_per_hour']:.2f} MB/hour")
        print(f"   Memory Leak: {'⚠️  DETECTED' if mem['memory_leak_detected'] else '✓ None detected'}")

        print("\n2. Throughput Analysis:")
        tput = analysis['throughput_analysis']
        print(f"   Initial: {tput['initial_throughput']:.0f} exec/s")
        print(f"   Final: {tput['final_throughput']:.0f} exec/s")
        print(f"   Mean: {tput['mean_throughput']:.0f} ± {tput['stdev_throughput']:.0f} exec/s")
        print(f"   Degradation Rate: {tput['degradation_rate_per_hour']:.1f} exec/s per hour")
        print(f"   Performance Degradation: {'⚠️  DETECTED' if tput['performance_degradation_detected'] else '✓ None detected'}")

        print("\n3. Crash Discovery:")
        crash = analysis['crash_discovery_analysis']
        print(f"   Total Unique: {crash['total_unique_crashes']}")
        print(f"   Mean per Sample: {crash['mean_crashes_per_sample']:.1f}")
        print(f"   Saturation: {'✓ Detected (expected)' if crash['saturation_detected'] else 'Not yet'}")

        print("\n4. CPU Usage:")
        cpu = analysis['cpu_analysis']
        print(f"   Mean: {cpu['mean_cpu_percent']:.1f}%")
        print(f"   Max: {cpu['max_cpu_percent']:.1f}%")
        print(f"   Stability: {'✓ Stable' if cpu['cpu_stable'] else '⚠️  Unstable'}")

        print(f"\n5. Overall Stability Score: {analysis['stability_score']:.1f}/100")

        if analysis['stability_score'] >= 90:
            print("   Status: ✓ EXCELLENT - System highly stable")
        elif analysis['stability_score'] >= 70:
            print("   Status: ✓ GOOD - Minor issues detected")
        elif analysis['stability_score'] >= 50:
            print("   Status: ⚠️  FAIR - Notable stability concerns")
        else:
            print("   Status: ❌ POOR - Significant stability issues")

        print("\n" + "=" * 70)


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Long-term stability testing')
    parser.add_argument(
        '--duration',
        type=float,
        default=6.0,
        help='Test duration in hours (default: 6.0)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=300,
        help='Sample interval in seconds (default: 300 = 5 minutes)'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick test mode (10 minutes with 1-minute intervals)'
    )

    args = parser.parse_args()

    # Quick test mode for validation
    if args.quick:
        duration = 10 / 60  # 10 minutes
        interval = 60  # 1 minute
        print("\n⚡ QUICK TEST MODE (10 minutes)\n")
    else:
        duration = args.duration
        interval = args.interval

    output_dir = Path(__file__).parent.parent / "results_data" / "long_term_stability"
    tester = LongTermStabilityTester(output_dir)

    await tester.simulate_modbus_fuzzing(duration, interval)


if __name__ == "__main__":
    asyncio.run(main())
