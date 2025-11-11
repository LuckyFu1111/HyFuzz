#!/usr/bin/env python3
"""
Resource Usage Profiling
Monitors CPU, memory, disk, and network usage during fuzzing
"""

import asyncio
import json
import time
import psutil
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


class ResourceProfiler:
    """Profile resource usage during fuzzing"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process = psutil.Process(os.getpid())

    async def profile_fuzzing_session(
        self,
        session_name: str,
        duration_seconds: int = 300,
        sample_interval_seconds: int = 1
    ) -> Dict:
        """
        Profile a fuzzing session

        Args:
            session_name: Name of the session
            duration_seconds: Total duration
            sample_interval_seconds: Sampling interval
        """

        print(f"\n{'=' * 70}")
        print(f"PROFILING SESSION: {session_name}")
        print(f"Duration: {duration_seconds}s, Sampling: every {sample_interval_seconds}s")
        print(f"{'=' * 70}\n")

        results = {
            'session_name': session_name,
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': duration_seconds,
            'sample_interval_seconds': sample_interval_seconds,
            'samples': []
        }

        # Get baseline
        baseline = self._take_baseline_sample()
        results['baseline'] = baseline

        print(f"Baseline: {baseline['memory_mb']:.1f} MB, {baseline['cpu_percent']:.1f}% CPU")
        print(f"\nProfiling...")

        start_time = time.time()
        sample_count = 0

        # Simulate fuzzing with resource tracking
        fuzzing_task = asyncio.create_task(
            self._simulate_fuzzing_workload(duration_seconds)
        )

        while (time.time() - start_time) < duration_seconds:
            # Take sample
            sample = self._take_resource_sample(sample_count, time.time() - start_time)
            results['samples'].append(sample)

            if sample_count % 10 == 0:
                print(f"  [{sample_count}s] CPU: {sample['cpu_percent']:.1f}%, "
                      f"Mem: {sample['memory_mb']:.1f} MB, "
                      f"Disk R: {sample['disk_read_mb']:.2f} MB, "
                      f"Net Sent: {sample['net_sent_mb']:.2f} MB")

            sample_count += 1
            await asyncio.sleep(sample_interval_seconds)

        # Wait for fuzzing to complete
        await fuzzing_task

        # Analyze results
        results['analysis'] = self._analyze_resource_usage(results)

        # Save results
        output_file = self.output_dir / f"resource_profile_{session_name}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Resource profile saved to: {output_file}")
        print(f"{'=' * 70}\n")

        self._print_profile_summary(results)

        return results

    def _take_baseline_sample(self) -> Dict:
        """Take baseline resource sample before fuzzing"""

        mem_info = self.process.memory_info()
        cpu_percent = self.process.cpu_percent(interval=0.1)

        # Get disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            disk_read_bytes = disk_io.read_bytes if disk_io else 0
            disk_write_bytes = disk_io.write_bytes if disk_io else 0
        except Exception:
            disk_read_bytes = 0
            disk_write_bytes = 0

        # Get network I/O
        try:
            net_io = psutil.net_io_counters()
            net_sent_bytes = net_io.bytes_sent if net_io else 0
            net_recv_bytes = net_io.bytes_recv if net_io else 0
        except Exception:
            net_sent_bytes = 0
            net_recv_bytes = 0

        return {
            'memory_mb': mem_info.rss / (1024 * 1024),
            'memory_percent': self.process.memory_percent(),
            'cpu_percent': cpu_percent,
            'num_threads': self.process.num_threads(),
            'disk_read_bytes': disk_read_bytes,
            'disk_write_bytes': disk_write_bytes,
            'net_sent_bytes': net_sent_bytes,
            'net_recv_bytes': net_recv_bytes
        }

    def _take_resource_sample(self, sample_num: int, elapsed_seconds: float) -> Dict:
        """Take resource usage sample"""

        mem_info = self.process.memory_info()
        cpu_times = self.process.cpu_times()

        # CPU usage
        cpu_percent = self.process.cpu_percent(interval=0.1)

        # Per-core CPU (if available)
        try:
            cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)
        except Exception:
            cpu_per_core = []

        # Memory details
        memory_mb = mem_info.rss / (1024 * 1024)
        memory_percent = self.process.memory_percent()

        try:
            memory_vms_mb = mem_info.vms / (1024 * 1024)
        except Exception:
            memory_vms_mb = memory_mb

        # Thread count
        num_threads = self.process.num_threads()

        # File descriptors
        try:
            num_fds = len(self.process.open_files())
        except (psutil.AccessDenied, AttributeError):
            num_fds = -1

        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
        except Exception:
            disk_read_mb = 0
            disk_write_mb = 0

        # Network I/O
        try:
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
            net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0
        except Exception:
            net_sent_mb = 0
            net_recv_mb = 0

        # System-wide resources
        system_memory_percent = psutil.virtual_memory().percent
        system_cpu_percent = psutil.cpu_percent(interval=0)

        return {
            'sample_number': sample_num,
            'elapsed_seconds': elapsed_seconds,
            'cpu_percent': cpu_percent,
            'cpu_user_time': cpu_times.user,
            'cpu_system_time': cpu_times.system,
            'cpu_per_core': cpu_per_core,
            'memory_mb': memory_mb,
            'memory_vms_mb': memory_vms_mb,
            'memory_percent': memory_percent,
            'num_threads': num_threads,
            'num_open_files': num_fds,
            'disk_read_mb': disk_read_mb,
            'disk_write_mb': disk_write_mb,
            'net_sent_mb': net_sent_mb,
            'net_recv_mb': net_recv_mb,
            'system_memory_percent': system_memory_percent,
            'system_cpu_percent': system_cpu_percent,
            'timestamp': time.time()
        }

    async def _simulate_fuzzing_workload(self, duration_seconds: int):
        """Simulate fuzzing workload"""

        start_time = time.time()

        while (time.time() - start_time) < duration_seconds:
            # Simulate fuzzing activity
            await asyncio.sleep(0.0002)

            # Simulate some CPU work
            _ = sum(range(1000))

            # Simulate memory allocation/deallocation
            if int(time.time()) % 10 == 0:
                temp_data = [0] * 10000
                del temp_data

    def _analyze_resource_usage(self, results: Dict) -> Dict:
        """Analyze resource usage patterns"""

        samples = results['samples']
        baseline = results['baseline']

        if not samples:
            return {'error': 'No samples collected'}

        # Extract metrics
        cpu_values = [s['cpu_percent'] for s in samples]
        memory_values = [s['memory_mb'] for s in samples]
        disk_read_values = [s['disk_read_mb'] for s in samples]
        disk_write_values = [s['disk_write_mb'] for s in samples]
        net_sent_values = [s['net_sent_mb'] for s in samples]

        # Calculate statistics
        import statistics

        analysis = {
            'cpu_usage': {
                'mean': statistics.mean(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values),
                'stdev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                'median': statistics.median(cpu_values)
            },
            'memory_usage': {
                'baseline_mb': baseline['memory_mb'],
                'peak_mb': max(memory_values),
                'mean_mb': statistics.mean(memory_values),
                'growth_mb': max(memory_values) - baseline['memory_mb'],
                'growth_percent': ((max(memory_values) - baseline['memory_mb']) / baseline['memory_mb'] * 100) if baseline['memory_mb'] > 0 else 0
            },
            'disk_io': {
                'total_read_mb': disk_read_values[-1] - disk_read_values[0] if len(disk_read_values) > 1 else 0,
                'total_write_mb': disk_write_values[-1] - disk_write_values[0] if len(disk_write_values) > 1 else 0,
                'read_rate_mbps': (disk_read_values[-1] - disk_read_values[0]) / results['duration_seconds'] if results['duration_seconds'] > 0 and len(disk_read_values) > 1 else 0,
                'write_rate_mbps': (disk_write_values[-1] - disk_write_values[0]) / results['duration_seconds'] if results['duration_seconds'] > 0 and len(disk_write_values) > 1 else 0
            },
            'network_io': {
                'total_sent_mb': net_sent_values[-1] - net_sent_values[0] if len(net_sent_values) > 1 else 0,
                'send_rate_mbps': (net_sent_values[-1] - net_sent_values[0]) / results['duration_seconds'] if results['duration_seconds'] > 0 and len(net_sent_values) > 1 else 0
            },
            'bottlenecks': self._identify_bottlenecks(samples)
        }

        return analysis

    def _identify_bottlenecks(self, samples: List[Dict]) -> List[str]:
        """Identify resource bottlenecks"""

        bottlenecks = []

        # Check CPU bottleneck
        high_cpu_samples = [s for s in samples if s['cpu_percent'] > 80]
        if len(high_cpu_samples) > len(samples) * 0.1:  # >10% of samples
            bottlenecks.append("CPU: High utilization (>80%) detected")

        # Check memory bottleneck
        memory_values = [s['memory_percent'] for s in samples]
        if any(m > 80 for m in memory_values):
            bottlenecks.append("Memory: High utilization (>80%) detected")

        # Check system-wide resource pressure
        system_cpu_high = [s for s in samples if s['system_cpu_percent'] > 90]
        if len(system_cpu_high) > len(samples) * 0.05:
            bottlenecks.append("System CPU: System-wide CPU pressure detected")

        if not bottlenecks:
            bottlenecks.append("None: No bottlenecks detected")

        return bottlenecks

    def _print_profile_summary(self, results: Dict):
        """Print profiling summary"""

        analysis = results['analysis']

        print("=" * 70)
        print("RESOURCE PROFILING SUMMARY")
        print("=" * 70)

        print("\n1. CPU Usage:")
        cpu = analysis['cpu_usage']
        print(f"   Mean: {cpu['mean']:.1f}%")
        print(f"   Peak: {cpu['max']:.1f}%")
        print(f"   Stdev: {cpu['stdev']:.1f}%")

        print("\n2. Memory Usage:")
        mem = analysis['memory_usage']
        print(f"   Baseline: {mem['baseline_mb']:.1f} MB")
        print(f"   Peak: {mem['peak_mb']:.1f} MB")
        print(f"   Mean: {mem['mean_mb']:.1f} MB")
        print(f"   Growth: {mem['growth_mb']:.1f} MB ({mem['growth_percent']:.1f}%)")

        print("\n3. Disk I/O:")
        disk = analysis['disk_io']
        print(f"   Total Read: {disk['total_read_mb']:.2f} MB")
        print(f"   Total Write: {disk['total_write_mb']:.2f} MB")
        print(f"   Read Rate: {disk['read_rate_mbps']:.3f} MB/s")
        print(f"   Write Rate: {disk['write_rate_mbps']:.3f} MB/s")

        print("\n4. Network I/O:")
        net = analysis['network_io']
        print(f"   Total Sent: {net['total_sent_mb']:.2f} MB")
        print(f"   Send Rate: {net['send_rate_mbps']:.3f} MB/s")

        print("\n5. Bottlenecks:")
        for bottleneck in analysis['bottlenecks']:
            print(f"   • {bottleneck}")

        print("\n" + "=" * 70)

    async def run_profiling_suite(self):
        """Run comprehensive profiling suite"""

        print("=" * 70)
        print("COMPREHENSIVE RESOURCE PROFILING")
        print("=" * 70)

        sessions = [
            ("baseline_light", 60),
            ("standard_fuzzing", 300),
            ("heavy_load", 180),
        ]

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sessions': []
        }

        for session_name, duration in sessions:
            result = await self.profile_fuzzing_session(session_name, duration, 1)
            all_results['sessions'].append(result)

        # Save combined results
        output_file = self.output_dir / "comprehensive_resource_profile.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Comprehensive profile saved to: {output_file}")
        print(f"{'=' * 70}\n")


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "resource_profiling"
    profiler = ResourceProfiler(output_dir)

    # Quick profile (5 minutes)
    await profiler.profile_fuzzing_session("quick_profile", 300, 1)


if __name__ == "__main__":
    asyncio.run(main())
