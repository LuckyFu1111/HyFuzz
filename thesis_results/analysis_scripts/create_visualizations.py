#!/usr/bin/env python3
"""
Visualization Script for Thesis Results
Generates publication-quality plots from test results
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("Warning: matplotlib not installed. Install with: pip3 install matplotlib numpy")


class ThesisVisualizer:
    """Generate visualizations for thesis"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set publication-quality defaults
        if HAS_MATPLOTLIB:
            plt.rcParams['figure.figsize'] = (10, 6)
            plt.rcParams['figure.dpi'] = 300
            plt.rcParams['font.size'] = 11
            plt.rcParams['font.family'] = 'serif'
            plt.rcParams['axes.labelsize'] = 12
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['legend.fontsize'] = 10
            plt.rcParams['xtick.labelsize'] = 10
            plt.rcParams['ytick.labelsize'] = 10

    def load_json(self, filepath: Path) -> Dict:
        """Load JSON file"""
        if not filepath.exists():
            return {}
        with open(filepath) as f:
            return json.load(f)

    def plot_modbus_mutation_comparison(self):
        """Plot mutation level impact on crashes"""
        if not HAS_MATPLOTLIB:
            return

        data_file = self.results_dir / "modbus_extended" / "modbus_extended_results.json"
        data = self.load_json(data_file)

        if not data:
            print("  Skipping: modbus_extended data not found")
            return

        # Extract data for 60s trials
        mutation_data = {}
        for config in data.get('configurations', []):
            if config['duration_seconds'] == 60:
                level = config['mutation_level']
                crashes = [len(t['unique_crashes']) for t in config['trials']]
                mutation_data[level] = crashes

        if not mutation_data:
            print("  Skipping: no 60s mutation data")
            return

        # Plot
        fig, ax = plt.subplots()

        levels = ['low', 'medium', 'aggressive']
        colors = ['#2ecc71', '#3498db', '#e74c3c']
        positions = range(len(levels))

        for i, level in enumerate(levels):
            if level in mutation_data:
                crashes = mutation_data[level]
                # Violin plot or box plot
                parts = ax.violinplot([crashes], positions=[i], widths=0.5,
                                     showmeans=True, showextrema=True)
                for pc in parts['bodies']:
                    pc.set_facecolor(colors[i])
                    pc.set_alpha(0.7)

        ax.set_xticks(positions)
        ax.set_xticklabels([l.capitalize() for l in levels])
        ax.set_xlabel('Mutation Level')
        ax.set_ylabel('Unique Crashes Discovered')
        ax.set_title('Modbus Fuzzing: Mutation Level Impact')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_file = self.output_dir / 'modbus_mutation_impact.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Created: {output_file.name}")

    def plot_coap_dtls_comparison(self):
        """Plot DTLS impact across test modes"""
        if not HAS_MATPLOTLIB:
            return

        data_file = self.results_dir / "coap_extended" / "coap_extended_results.json"
        data = self.load_json(data_file)

        if not data:
            print("  Skipping: coap_extended data not found")
            return

        # Extract data
        modes = []
        no_dtls_execs = []
        with_dtls_execs = []

        for mode_data in data.get('test_modes', []):
            mode_name = mode_data['test_mode']
            dtls = mode_data['dtls_enabled']

            if not dtls:
                # Find matching dtls=true
                matching = next((m for m in data['test_modes']
                               if m['test_mode'] == mode_name and m['dtls_enabled']), None)
                if matching:
                    modes.append(mode_name.replace('_', ' ').title())
                    no_dtls_execs.append(mode_data['aggregate']['execs']['mean'])
                    with_dtls_execs.append(matching['aggregate']['execs']['mean'])

        if not modes:
            print("  Skipping: no matching DTLS pairs")
            return

        # Plot
        fig, ax = plt.subplots()

        x = np.arange(len(modes))
        width = 0.35

        ax.bar(x - width/2, no_dtls_execs, width, label='Without DTLS',
               color='#3498db', alpha=0.8)
        ax.bar(x + width/2, with_dtls_execs, width, label='With DTLS',
               color='#e67e22', alpha=0.8)

        ax.set_xlabel('Test Mode')
        ax.set_ylabel('Mean Executions')
        ax.set_title('CoAP: DTLS Overhead Across Test Modes')
        ax.set_xticks(x)
        ax.set_xticklabels(modes, rotation=15, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_file = self.output_dir / 'coap_dtls_overhead.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Created: {output_file.name}")

    def plot_baseline_comparison(self):
        """Plot baseline fuzzer comparison"""
        if not HAS_MATPLOTLIB:
            return

        data_file = self.results_dir / "baseline_comparison" / "baseline_comparison_results.json"
        data = self.load_json(data_file)

        if not data:
            print("  Skipping: baseline data not found")
            return

        # Modbus comparison
        modbus_data = data.get('modbus', {}).get('results', {}).get('fuzzer_results', {})

        if modbus_data:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            fuzzers = list(modbus_data.keys())
            crashes = [modbus_data[f]['aggregate']['unique_crashes']['mean'] for f in fuzzers]
            coverage = [modbus_data[f]['aggregate']['coverage']['mean'] for f in fuzzers]

            # Highlight HyFuzz
            colors = ['#e74c3c' if f == 'HyFuzz' else '#95a5a6' for f in fuzzers]

            # Crashes
            ax1.barh(fuzzers, crashes, color=colors, alpha=0.8)
            ax1.set_xlabel('Mean Unique Crashes')
            ax1.set_title('Modbus: Crash Discovery Comparison')
            ax1.grid(True, alpha=0.3, axis='x')

            # Coverage
            ax2.barh(fuzzers, coverage, color=colors, alpha=0.8)
            ax2.set_xlabel('Mean Coverage')
            ax2.set_title('Modbus: Coverage Comparison')
            ax2.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()
            output_file = self.output_dir / 'baseline_comparison.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"  ✓ Created: {output_file.name}")

    def plot_duration_impact(self):
        """Plot duration impact on crash discovery"""
        if not HAS_MATPLOTLIB:
            return

        data_file = self.results_dir / "modbus_extended" / "modbus_extended_results.json"
        data = self.load_json(data_file)

        if not data:
            return

        # Extract medium mutation data for different durations
        duration_data = {}
        for config in data.get('configurations', []):
            if config['mutation_level'] == 'medium':
                duration = config['duration_seconds']
                crashes = [len(t['unique_crashes']) for t in config['trials']]
                duration_data[duration] = {
                    'mean': np.mean(crashes),
                    'std': np.std(crashes)
                }

        if len(duration_data) < 2:
            print("  Skipping: insufficient duration data")
            return

        durations = sorted(duration_data.keys())
        means = [duration_data[d]['mean'] for d in durations]
        stds = [duration_data[d]['std'] for d in durations]

        fig, ax = plt.subplots()

        ax.errorbar(durations, means, yerr=stds, marker='o', linewidth=2,
                   markersize=8, capsize=5, color='#3498db')

        ax.set_xlabel('Fuzzing Duration (seconds)')
        ax.set_ylabel('Mean Unique Crashes')
        ax.set_title('Modbus: Crash Discovery vs Duration')
        ax.grid(True, alpha=0.3)

        # Add efficiency annotation (crashes per minute)
        for d, m in zip(durations, means):
            rate = (m / d) * 60  # crashes per minute
            ax.annotate(f'{rate:.1f}/min', xy=(d, m), xytext=(5, 5),
                       textcoords='offset points', fontsize=8)

        plt.tight_layout()
        output_file = self.output_dir / 'duration_impact.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Created: {output_file.name}")

    def generate_all_plots(self):
        """Generate all visualizations"""
        print("=" * 70)
        print("GENERATING THESIS VISUALIZATIONS")
        print("=" * 70)

        if not HAS_MATPLOTLIB:
            print("\nERROR: matplotlib not installed!")
            print("Install with: pip3 install matplotlib numpy")
            return

        print("\n1. Modbus mutation impact...")
        self.plot_modbus_mutation_comparison()

        print("\n2. CoAP DTLS overhead...")
        self.plot_coap_dtls_comparison()

        print("\n3. Baseline comparison...")
        self.plot_baseline_comparison()

        print("\n4. Duration impact...")
        self.plot_duration_impact()

        print(f"\n{'=' * 70}")
        print(f"Visualizations saved to: {self.output_dir}")
        print(f"{'=' * 70}")

        # List generated files
        plots = list(self.output_dir.glob('*.png'))
        if plots:
            print(f"\nGenerated {len(plots)} plots:")
            for plot in sorted(plots):
                print(f"  - {plot.name}")


def main():
    if not HAS_MATPLOTLIB:
        print("ERROR: matplotlib not available")
        print("Install with: pip3 install matplotlib numpy")
        sys.exit(1)

    results_dir = Path(__file__).parent.parent / "results_data"
    plots_dir = Path(__file__).parent.parent / "plots"

    visualizer = ThesisVisualizer(results_dir, plots_dir)
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()
