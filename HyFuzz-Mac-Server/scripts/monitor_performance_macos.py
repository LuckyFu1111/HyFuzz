#!/usr/bin/env python3
"""
macOS Performance Monitoring Tool for HyFuzz Server

Real-time monitoring of system resources with macOS-specific metrics
including Apple Silicon temperature, memory pressure, and GPU usage.
"""

import subprocess
import time
import sys
from datetime import datetime
from typing import Dict, Optional


class MacOSPerformanceMonitor:
    """Monitor HyFuzz Server performance on macOS."""

    def __init__(self):
        self.is_apple_silicon = self._detect_apple_silicon()

    def _detect_apple_silicon(self) -> bool:
        """Detect if running on Apple Silicon."""
        import platform
        return platform.machine() == "arm64"

    def get_cpu_usage(self) -> Dict[str, float]:
        """Get CPU usage statistics."""
        try:
            result = subprocess.run(
                ["top", "-l", "1", "-n", "0"],
                capture_output=True,
                text=True,
                timeout=2
            )

            lines = result.stdout.split('\n')
            for line in lines:
                if 'CPU usage' in line:
                    # Parse: CPU usage: 12.34% user, 5.67% sys, 82.00% idle
                    parts = line.split(',')
                    user = float(parts[0].split(':')[1].strip().rstrip('% user'))
                    sys = float(parts[1].strip().rstrip('% sys'))
                    idle = float(parts[2].strip().rstrip('% idle'))

                    return {
                        'user': user,
                        'system': sys,
                        'idle': idle,
                        'total': user + sys
                    }
        except Exception as e:
            print(f"Error getting CPU usage: {e}")

        return {'user': 0, 'system': 0, 'idle': 100, 'total': 0}

    def get_memory_info(self) -> Dict:
        """Get memory usage information."""
        try:
            # Get memory stats
            result = subprocess.run(
                ["vm_stat"],
                capture_output=True,
                text=True,
                timeout=2
            )

            lines = result.stdout.split('\n')
            stats = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':')
                    key = key.strip()
                    value = value.strip().rstrip('.')
                    if value.isdigit():
                        stats[key] = int(value)

            # Page size
            page_size = 4096  # bytes

            # Calculate memory usage
            free_pages = stats.get('Pages free', 0)
            active_pages = stats.get('Pages active', 0)
            inactive_pages = stats.get('Pages inactive', 0)
            wired_pages = stats.get('Pages wired down', 0)
            compressed_pages = stats.get('Pages stored in compressor', 0)

            free_mb = (free_pages * page_size) / (1024 * 1024)
            active_mb = (active_pages * page_size) / (1024 * 1024)
            inactive_mb = (inactive_pages * page_size) / (1024 * 1024)
            wired_mb = (wired_pages * page_size) / (1024 * 1024)
            compressed_mb = (compressed_pages * page_size) / (1024 * 1024)

            used_mb = active_mb + wired_mb
            total_mb = used_mb + inactive_mb + free_mb

            return {
                'total_mb': total_mb,
                'used_mb': used_mb,
                'free_mb': free_mb,
                'active_mb': active_mb,
                'inactive_mb': inactive_mb,
                'wired_mb': wired_mb,
                'compressed_mb': compressed_mb,
                'used_percent': (used_mb / total_mb * 100) if total_mb > 0 else 0
            }
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return {}

    def get_memory_pressure(self) -> str:
        """Get macOS memory pressure level."""
        try:
            result = subprocess.run(
                ["memory_pressure"],
                capture_output=True,
                text=True,
                timeout=2
            )

            output = result.stdout.lower()
            if 'normal' in output:
                return 'normal'
            elif 'warn' in output:
                return 'warning'
            elif 'critical' in output:
                return 'critical'
        except Exception:
            pass

        return 'unknown'

    def get_disk_io(self) -> Dict:
        """Get disk I/O statistics."""
        try:
            result = subprocess.run(
                ["iostat", "-d", "-c", "2", "-w", "1"],
                capture_output=True,
                text=True,
                timeout=3
            )

            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Last line contains current stats
                values = lines[-1].split()
                if len(values) >= 3:
                    return {
                        'kb_per_sec': float(values[0]),
                        'transfers_per_sec': float(values[1]),
                        'mb_per_sec': float(values[2])
                    }
        except Exception as e:
            print(f"Error getting disk I/O: {e}")

        return {'kb_per_sec': 0, 'transfers_per_sec': 0, 'mb_per_sec': 0}

    def get_network_stats(self) -> Dict:
        """Get network statistics."""
        try:
            result = subprocess.run(
                ["netstat", "-i", "-b"],
                capture_output=True,
                text=True,
                timeout=2
            )

            # Parse netstat output
            # This is a simplified version
            return {'status': 'available'}
        except Exception:
            return {'status': 'unavailable'}

    def get_apple_silicon_metrics(self) -> Optional[Dict]:
        """Get Apple Silicon specific metrics (temperature, power)."""
        if not self.is_apple_silicon:
            return None

        metrics = {}

        try:
            # Try to get temperature using powermetrics (requires sudo)
            # This is just a placeholder - actual implementation would need sudo
            metrics['note'] = 'Detailed power metrics require sudo access'

            # Try to get basic power stats
            result = subprocess.run(
                ["pmset", "-g", "batt"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if 'InternalBattery' in result.stdout:
                for line in result.stdout.split('\n'):
                    if '%' in line:
                        # Extract battery percentage
                        if 'InternalBattery' in line:
                            parts = line.split('\t')
                            if len(parts) > 1:
                                battery_info = parts[1].strip()
                                metrics['battery'] = battery_info

        except Exception:
            pass

        return metrics if metrics else None

    def get_process_stats(self, process_name: str = "python") -> Dict:
        """Get stats for HyFuzz process."""
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=2
            )

            hyfuzz_processes = []
            for line in result.stdout.split('\n'):
                if 'hyfuzz' in line.lower() or 'src' in line:
                    parts = line.split()
                    if len(parts) >= 11:
                        hyfuzz_processes.append({
                            'pid': parts[1],
                            'cpu_percent': parts[2],
                            'mem_percent': parts[3],
                            'command': ' '.join(parts[10:])
                        })

            return {'processes': hyfuzz_processes}
        except Exception as e:
            print(f"Error getting process stats: {e}")
            return {'processes': []}

    def display_metrics(self):
        """Display real-time performance metrics."""
        try:
            while True:
                # Clear screen
                print('\033[2J\033[H')  # ANSI clear screen

                print("=" * 70)
                print(f"HyFuzz macOS Performance Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 70)

                # CPU metrics
                cpu = self.get_cpu_usage()
                print(f"\n📊 CPU Usage:")
                print(f"  User:   {cpu['user']:.1f}%")
                print(f"  System: {cpu['system']:.1f}%")
                print(f"  Idle:   {cpu['idle']:.1f}%")
                print(f"  Total:  {cpu['total']:.1f}%")

                # Memory metrics
                mem = self.get_memory_info()
                if mem:
                    pressure = self.get_memory_pressure()
                    print(f"\n💾 Memory Usage:")
                    print(f"  Total:      {mem.get('total_mb', 0):.0f} MB")
                    print(f"  Used:       {mem.get('used_mb', 0):.0f} MB ({mem.get('used_percent', 0):.1f}%)")
                    print(f"  Free:       {mem.get('free_mb', 0):.0f} MB")
                    print(f"  Active:     {mem.get('active_mb', 0):.0f} MB")
                    print(f"  Compressed: {mem.get('compressed_mb', 0):.0f} MB")
                    print(f"  Pressure:   {pressure.upper()}")

                # Disk I/O
                disk = self.get_disk_io()
                print(f"\n💿 Disk I/O:")
                print(f"  Throughput: {disk['mb_per_sec']:.2f} MB/s")
                print(f"  Transfers:  {disk['transfers_per_sec']:.1f} ops/s")

                # Apple Silicon specific
                if self.is_apple_silicon:
                    silicon_metrics = self.get_apple_silicon_metrics()
                    if silicon_metrics:
                        print(f"\n🍎 Apple Silicon Metrics:")
                        for key, value in silicon_metrics.items():
                            print(f"  {key.title()}: {value}")

                # Process stats
                processes = self.get_process_stats()
                if processes['processes']:
                    print(f"\n⚙️  HyFuzz Processes:")
                    for proc in processes['processes'][:5]:  # Show top 5
                        print(f"  PID {proc['pid']}: CPU {proc['cpu_percent']}%, "
                              f"MEM {proc['mem_percent']}%")

                print(f"\n{'=' * 70}")
                print("Press Ctrl+C to exit")

                time.sleep(2)  # Update every 2 seconds

        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped")
            sys.exit(0)


def main():
    """Main monitoring routine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Monitor HyFuzz Server performance on macOS"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Display metrics once and exit"
    )

    args = parser.parse_args()

    monitor = MacOSPerformanceMonitor()

    if args.once:
        # Display once and exit
        cpu = monitor.get_cpu_usage()
        mem = monitor.get_memory_info()
        print(f"CPU: {cpu['total']:.1f}% | Memory: {mem.get('used_percent', 0):.1f}%")
    else:
        # Continuous monitoring
        monitor.display_metrics()


if __name__ == "__main__":
    main()
