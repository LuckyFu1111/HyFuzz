#!/usr/bin/env python3
"""
macOS Performance Optimization Script

This script detects the macOS environment and applies optimal performance
settings for HyFuzz Server, with special optimizations for Apple Silicon.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


class MacOSOptimizer:
    """Optimize HyFuzz Server for macOS environment."""

    def __init__(self):
        self.is_apple_silicon = self._detect_apple_silicon()
        self.cpu_count = os.cpu_count() or 4
        self.total_memory_gb = self._get_total_memory()
        self.macos_version = self._get_macos_version()

    def _detect_apple_silicon(self) -> bool:
        """Detect if running on Apple Silicon (M1/M2/M3/M4)."""
        machine = platform.machine()
        return machine == "arm64"

    def _get_total_memory(self) -> float:
        """Get total system memory in GB."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                check=True
            )
            memory_bytes = int(result.stdout.strip())
            return memory_bytes / (1024 ** 3)  # Convert to GB
        except Exception:
            return 8.0  # Default fallback

    def _get_macos_version(self) -> Tuple[int, int]:
        """Get macOS version (major, minor)."""
        try:
            result = subprocess.run(
                ["sw_vers", "-productVersion"],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            major, minor = map(int, version.split('.')[:2])
            return (major, minor)
        except Exception:
            return (12, 0)  # Default to Monterey

    def _get_cpu_info(self) -> Dict[str, int]:
        """Get CPU core information."""
        info = {
            "total_cores": self.cpu_count,
            "performance_cores": self.cpu_count,
            "efficiency_cores": 0
        }

        if self.is_apple_silicon:
            # Try to detect P-cores and E-cores on Apple Silicon
            try:
                # Performance cores
                result = subprocess.run(
                    ["sysctl", "-n", "hw.perflevel0.physicalcpu"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    info["performance_cores"] = int(result.stdout.strip())

                # Efficiency cores
                result = subprocess.run(
                    ["sysctl", "-n", "hw.perflevel1.physicalcpu"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    info["efficiency_cores"] = int(result.stdout.strip())
            except Exception:
                pass

        return info

    def get_optimal_settings(self) -> Dict:
        """Calculate optimal settings based on hardware."""
        cpu_info = self._get_cpu_info()

        # Calculate optimal worker pool size
        if self.is_apple_silicon:
            # Use P-cores * 2 + E-cores for worker pool
            worker_pool_size = (cpu_info["performance_cores"] * 2 +
                              cpu_info["efficiency_cores"])
        else:
            # Intel: use logical cores
            worker_pool_size = self.cpu_count

        # Determine performance profile based on memory
        if self.total_memory_gb >= 32:
            profile = "max_performance"
            cache_size_mb = 4096
            llm_batch_size = 16
        elif self.total_memory_gb >= 16:
            profile = "balanced"
            cache_size_mb = 2048
            llm_batch_size = 8
        else:
            profile = "power_saving"
            cache_size_mb = 1024
            llm_batch_size = 4

        settings = {
            "platform": {
                "is_apple_silicon": self.is_apple_silicon,
                "cpu_count": self.cpu_count,
                "performance_cores": cpu_info["performance_cores"],
                "efficiency_cores": cpu_info["efficiency_cores"],
                "total_memory_gb": self.total_memory_gb,
                "macos_version": f"{self.macos_version[0]}.{self.macos_version[1]}"
            },
            "recommended_settings": {
                "profile": profile,
                "worker_pool_size": worker_pool_size,
                "cache_size_mb": cache_size_mb,
                "llm_batch_size": llm_batch_size,
                "use_metal": self.is_apple_silicon,
                "num_threads": worker_pool_size,
                "max_memory_percent": 75 if self.total_memory_gb >= 16 else 60
            }
        }

        return settings

    def apply_system_optimizations(self) -> bool:
        """Apply macOS system-level optimizations."""
        print("Applying macOS system optimizations...")

        try:
            # Increase file descriptor limits
            self._set_ulimit()

            # Set environment variables for optimal performance
            self._set_environment_vars()

            # Configure Ollama for optimal performance
            if self.is_apple_silicon:
                self._configure_ollama_apple_silicon()

            print("✓ System optimizations applied successfully")
            return True

        except Exception as e:
            print(f"⚠ Warning: Could not apply all optimizations: {e}")
            return False

    def _set_ulimit(self):
        """Set file descriptor limits."""
        try:
            # Check current limits
            result = subprocess.run(
                ["launchctl", "limit", "maxfiles"],
                capture_output=True,
                text=True
            )
            print(f"  Current maxfiles limit: {result.stdout.strip()}")

            # Note: Changing limits requires sudo, so we just inform the user
            print("  Note: To increase file descriptor limits, run:")
            print("    sudo launchctl limit maxfiles 65536 200000")
        except Exception as e:
            print(f"  Could not check ulimits: {e}")

    def _set_environment_vars(self):
        """Set optimal environment variables."""
        env_vars = {
            # Python optimizations
            "PYTHONOPTIMIZE": "1",
            "PYTHONUNBUFFERED": "1",

            # macOS specific
            "OBJC_DISABLE_INITIALIZE_FORK_SAFETY": "YES",

            # Performance tuning
            "OMP_NUM_THREADS": str(self.cpu_count),
        }

        if self.is_apple_silicon:
            # Apple Silicon specific
            env_vars.update({
                "PYTORCH_ENABLE_MPS_FALLBACK": "1",
                "METAL_DEVICE_WRAPPER_TYPE": "1",
            })

        # Create a shell script to export these
        env_file = PROJECT_ROOT / ".env.macos"
        with open(env_file, "w") as f:
            f.write("# macOS Performance Environment Variables\n")
            f.write("# Source this file: source .env.macos\n\n")
            for key, value in env_vars.items():
                f.write(f"export {key}={value}\n")

        print(f"  ✓ Environment variables written to {env_file}")
        print(f"    Run: source {env_file}")

    def _configure_ollama_apple_silicon(self):
        """Configure Ollama for optimal Apple Silicon performance."""
        print("\n  Configuring Ollama for Apple Silicon:")

        # Check if Ollama is installed
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True
            )
            print(f"  ✓ Ollama version: {result.stdout.strip()}")
        except FileNotFoundError:
            print("  ⚠ Ollama not found. Install with: brew install ollama")
            return

        # Create Ollama configuration
        ollama_config = PROJECT_ROOT / "config" / "ollama_macos.env"
        with open(ollama_config, "w") as f:
            f.write("# Ollama Configuration for Apple Silicon\n\n")
            f.write("# Enable Metal acceleration\n")
            f.write("export OLLAMA_USE_METAL=1\n\n")
            f.write("# Optimize for unified memory\n")
            f.write(f"export OLLAMA_NUM_PARALLEL={self.cpu_count}\n\n")
            f.write("# GPU memory allocation (adjust based on total RAM)\n")
            gpu_memory_mb = int(self.total_memory_gb * 1024 * 0.5)  # Use 50% for GPU
            f.write(f"export OLLAMA_GPU_MEMORY={gpu_memory_mb}\n\n")

        print(f"  ✓ Ollama config written to {ollama_config}")

    def create_launchd_plist(self):
        """Create a launchd plist for running HyFuzz as a service."""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hyfuzz.server</string>

    <key>ProgramArguments</key>
    <array>
        <string>{PROJECT_ROOT}/venv/bin/python</string>
        <string>-m</string>
        <string>src</string>
    </array>

    <key>WorkingDirectory</key>
    <string>{PROJECT_ROOT}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>{PROJECT_ROOT}/logs/server.log</string>

    <key>StandardErrorPath</key>
    <string>{PROJECT_ROOT}/logs/server.error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>

    <key>ProcessType</key>
    <string>Interactive</string>

    <key>Nice</key>
    <integer>-5</integer>
</dict>
</plist>
"""

        plist_file = PROJECT_ROOT / "com.hyfuzz.server.plist"
        with open(plist_file, "w") as f:
            f.write(plist_content)

        print(f"\n✓ LaunchD plist created: {plist_file}")
        print("\nTo install as a service:")
        print(f"  cp {plist_file} ~/Library/LaunchAgents/")
        print("  launchctl load ~/Library/LaunchAgents/com.hyfuzz.server.plist")

    def print_report(self):
        """Print optimization report."""
        settings = self.get_optimal_settings()

        print("\n" + "="*60)
        print("HyFuzz macOS Performance Optimization Report")
        print("="*60)

        print("\n📊 System Information:")
        print(f"  Platform: macOS {settings['platform']['macos_version']}")
        print(f"  Architecture: {'Apple Silicon (ARM64)' if self.is_apple_silicon else 'Intel (x86_64)'}")
        print(f"  Total Cores: {settings['platform']['cpu_count']}")

        if self.is_apple_silicon:
            print(f"  Performance Cores: {settings['platform']['performance_cores']}")
            print(f"  Efficiency Cores: {settings['platform']['efficiency_cores']}")

        print(f"  Total Memory: {settings['platform']['total_memory_gb']:.1f} GB")

        print("\n⚡ Recommended Settings:")
        rec = settings['recommended_settings']
        print(f"  Profile: {rec['profile'].upper()}")
        print(f"  Worker Pool Size: {rec['worker_pool_size']}")
        print(f"  Cache Size: {rec['cache_size_mb']} MB")
        print(f"  LLM Batch Size: {rec['llm_batch_size']}")
        print(f"  Use Metal: {'Yes' if rec['use_metal'] else 'No'}")
        print(f"  Max Memory: {rec['max_memory_percent']}%")

        print("\n🚀 Performance Tips:")
        if self.is_apple_silicon:
            print("  • Ollama with Metal acceleration is highly optimized for Apple Silicon")
            print("  • Consider using larger models (7B-13B) with unified memory")
            print("  • Enable FP16 inference for faster processing")
        else:
            print("  • Consider using smaller models (3B-7B) for better performance")
            print("  • Enable AVX2 optimizations if available")

        if self.total_memory_gb < 16:
            print("  ⚠ Memory is limited. Consider closing other applications.")

        print("\n" + "="*60)


def main():
    """Main optimization routine."""
    print("HyFuzz macOS Performance Optimizer\n")

    # Check if running on macOS
    if platform.system() != "Darwin":
        print("❌ Error: This script is designed for macOS only")
        sys.exit(1)

    optimizer = MacOSOptimizer()

    # Print system report
    optimizer.print_report()

    # Apply optimizations
    print("\n🔧 Applying Optimizations...")
    optimizer.apply_system_optimizations()

    # Create launchd service file
    optimizer.create_launchd_plist()

    # Write settings to config
    settings = optimizer.get_optimal_settings()
    import yaml
    config_file = PROJECT_ROOT / "config" / "auto_optimized.yaml"
    with open(config_file, "w") as f:
        yaml.dump(settings, f, default_flow_style=False)

    print(f"\n✓ Optimized settings written to: {config_file}")
    print("\n✅ Optimization complete!")
    print("\nNext steps:")
    print("  1. Review the generated configuration files")
    print("  2. Source the environment: source .env.macos")
    print("  3. Start the server: ./scripts/start_server.sh")


if __name__ == "__main__":
    main()
