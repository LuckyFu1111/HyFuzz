#!/usr/bin/env python3
"""
Results Plotting Script
Generate plots for thesis results chapter
"""

import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np
from pathlib import Path
from typing import Dict, List
import sys


class ResultsPlotter:
    """Generate plots for thesis"""

    def __init__(self, results_dir: Path, plots_dir: Path):
        self.results_dir = results_dir
        self.plots_dir = plots_dir
        self.plots_dir.mkdir(parents=True, exist_ok=True)

        # Set plot style
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 11

    def load_json(self, filepath: Path) -> Dict:
        """Load JSON file"""
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {}
        with open(filepath, 'r') as f:
            return json.load(f)

    def plot_modbus_validity(self):
        """Plot Modbus validity profiles"""
        print("Generating Modbus validity plots...")

        data_file = self.results_dir / "modbus_validity" / "modbus_validity_results.json"
        data = self.load_json(data_file)

        if not data:
            return

        # Plot 1: PSR vs EXR by function code
        fig, ax = plt.subplots()

        fc_data = data.get('per_function_code', {})
        function_codes = sorted([int(fc) for fc in fc_data.keys()])
        psr_values = [fc_data[str(fc)]['PSR'] for fc in function_codes]
        exr_values = [fc_data[str(fc)]['EXR'] for fc in function_codes]

        x = np.arange(len(function_codes))
        width = 0.35

        ax.bar(x - width/2, psr_values, width, label='PSR (Success)', color='green', alpha=0.7)
        ax.bar(x + width/2, exr_values, width, label='EXR (Exception)', color='red', alpha=0.7)

        ax.set_xlabel('Function Code')
        ax.set_ylabel('Rate')
        ax.set_title('Modbus Protocol Success vs Exception Rate by Function Code')
        ax.set_xticks(x)
        ax.set_xticklabels(function_codes)
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.plots_dir / 'modbus_psr_exr.png', dpi=300)
        plt.close()

        print(f"  ✓ Saved: modbus_psr_exr.png")

    def plot_modbus_state_coverage(self):
        """Plot Modbus state coverage growth"""
        print("Generating Modbus state coverage plots...")

        data_file = self.results_dir / "modbus_validity" / "modbus_state_progress.json"
        data = self.load_json(data_file)

        if not data or 'state_transitions' not in data:
            return

        # Extract coverage growth
        transitions = data['state_transitions']
        trials = [t['trial'] for t in transitions]
        coverage = [t['coverage_size'] for t in transitions]

        fig, ax = plt.subplots()
        ax.plot(trials, coverage, linewidth=2, color='blue')
        ax.set_xlabel('Trial Number')
        ax.set_ylabel('Unique States Discovered')
        ax.set_title('Modbus State Coverage Growth')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(self.plots_dir / 'modbus_state_coverage.png', dpi=300)
        plt.close()

        print(f"  ✓ Saved: modbus_state_coverage.png")

    def plot_coap_coherence(self):
        """Plot CoAP coherence comparison"""
        print("Generating CoAP coherence plots...")

        data_file = self.results_dir / "coap_validity" / "coap_validity_results.json"
        data = self.load_json(data_file)

        if not data:
            return

        # Compare DTLS vs no DTLS
        categories = ['ACK Ratio', 'Token\nCoherence', '2xx Success']
        no_dtls = [
            data.get('coherence_no_dtls', {}).get('ack_ratio', 0),
            data.get('coherence_no_dtls', {}).get('token_coherence_rate', 0),
            data.get('coherence_no_dtls', {}).get('response_mix', {}).get('2xx_percent', 0)
        ]
        with_dtls = [
            data.get('coherence_with_dtls', {}).get('ack_ratio', 0),
            data.get('coherence_with_dtls', {}).get('token_coherence_rate', 0),
            data.get('coherence_with_dtls', {}).get('response_mix', {}).get('2xx_percent', 0)
        ]

        x = np.arange(len(categories))
        width = 0.35

        fig, ax = plt.subplots()
        ax.bar(x - width/2, no_dtls, width, label='Without DTLS', color='blue', alpha=0.7)
        ax.bar(x + width/2, with_dtls, width, label='With DTLS', color='orange', alpha=0.7)

        ax.set_ylabel('Rate')
        ax.set_title('CoAP Coherence Metrics: DTLS Impact')
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim([0, 1.1])

        plt.tight_layout()
        plt.savefig(self.plots_dir / 'coap_coherence_dtls.png', dpi=300)
        plt.close()

        print(f"  ✓ Saved: coap_coherence_dtls.png")

    def plot_baseline_comparison(self):
        """Plot baseline fuzzer comparison"""
        print("Generating baseline comparison plots...")

        data_file = self.results_dir / "baseline_comparison" / "baseline_comparison_results.json"
        data = self.load_json(data_file)

        if not data:
            return

        # Plot for Modbus
        modbus_data = data.get('modbus', {}).get('results', {}).get('fuzzer_results', {})

        if modbus_data:
            fuzzers = list(modbus_data.keys())
            crashes = [modbus_data[f]['aggregate']['unique_crashes']['mean'] for f in fuzzers]
            throughput = [modbus_data[f]['aggregate']['execs']['mean'] / 60 for f in fuzzers]  # execs/sec

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Crashes comparison
            colors = ['red' if f == 'HyFuzz' else 'blue' for f in fuzzers]
            ax1.barh(fuzzers, crashes, color=colors, alpha=0.7)
            ax1.set_xlabel('Mean Unique Crashes')
            ax1.set_title('Modbus: Bug-Finding Comparison')
            ax1.grid(True, alpha=0.3, axis='x')

            # Throughput comparison
            ax2.barh(fuzzers, throughput, color=colors, alpha=0.7)
            ax2.set_xlabel('Mean Exec/s')
            ax2.set_title('Modbus: Throughput Comparison')
            ax2.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()
            plt.savefig(self.plots_dir / 'baseline_comparison_modbus.png', dpi=300)
            plt.close()

            print(f"  ✓ Saved: baseline_comparison_modbus.png")

        # Plot for CoAP
        coap_data = data.get('coap', {}).get('results', {}).get('fuzzer_results', {})

        if coap_data:
            fuzzers = list(coap_data.keys())
            crashes = [coap_data[f]['aggregate']['unique_crashes']['mean'] for f in fuzzers]
            coverage = [coap_data[f]['aggregate']['coverage']['mean'] for f in fuzzers]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Crashes comparison
            colors = ['red' if f == 'HyFuzz' else 'blue' for f in fuzzers]
            ax1.barh(fuzzers, crashes, color=colors, alpha=0.7)
            ax1.set_xlabel('Mean Unique Crashes')
            ax1.set_title('CoAP: Bug-Finding Comparison')
            ax1.grid(True, alpha=0.3, axis='x')

            # Coverage comparison
            ax2.barh(fuzzers, coverage, color=colors, alpha=0.7)
            ax2.set_xlabel('Mean Coverage')
            ax2.set_title('CoAP: Coverage Comparison')
            ax2.grid(True, alpha=0.3, axis='x')

            plt.tight_layout()
            plt.savefig(self.plots_dir / 'baseline_comparison_coap.png', dpi=300)
            plt.close()

            print(f"  ✓ Saved: baseline_comparison_coap.png")

    def plot_fuzzing_efficiency(self):
        """Plot fuzzing efficiency metrics"""
        print("Generating fuzzing efficiency plots...")

        modbus_file = self.results_dir / "modbus_fuzzing" / "modbus_fuzzing_results.json"
        coap_file = self.results_dir / "coap_fuzzing" / "coap_fuzzing_results.json"

        modbus_data = self.load_json(modbus_file)
        coap_data = self.load_json(coap_file)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Modbus throughput
        if modbus_data and 'trials' in modbus_data:
            trial_nums = range(1, len(modbus_data['trials']) + 1)
            throughputs = [t['throughput_stats']['mean_exec_per_sec'] for t in modbus_data['trials']]

            ax1.plot(trial_nums, throughputs, marker='o', linewidth=2, markersize=8, color='blue')
            ax1.set_xlabel('Trial Number')
            ax1.set_ylabel('Mean Exec/s')
            ax1.set_title('Modbus Fuzzing Throughput')
            ax1.grid(True, alpha=0.3)

        # CoAP DTLS overhead
        if coap_data and 'comparison' in coap_data:
            no_dtls_execs = coap_data['comparison']['no_dtls']['mean_execs']
            with_dtls_execs = coap_data['comparison']['with_dtls']['mean_execs']

            categories = ['Without DTLS', 'With DTLS']
            values = [no_dtls_execs, with_dtls_execs]

            ax2.bar(categories, values, color=['blue', 'orange'], alpha=0.7)
            ax2.set_ylabel('Mean Executions')
            ax2.set_title('CoAP: DTLS Overhead Impact')
            ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(self.plots_dir / 'fuzzing_efficiency.png', dpi=300)
        plt.close()

        print(f"  ✓ Saved: fuzzing_efficiency.png")

    def generate_all_plots(self):
        """Generate all plots"""
        print("=" * 80)
        print("GENERATING THESIS PLOTS")
        print("=" * 80)

        self.plot_modbus_validity()
        self.plot_modbus_state_coverage()
        self.plot_coap_coherence()
        self.plot_baseline_comparison()
        self.plot_fuzzing_efficiency()

        print("\n" + "=" * 80)
        print(f"All plots saved to: {self.plots_dir}")
        print("=" * 80)


def main():
    results_dir = Path(__file__).parent.parent / "results_data"
    plots_dir = Path(__file__).parent.parent / "plots"

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the test scripts first.")
        sys.exit(1)

    plotter = ResultsPlotter(results_dir, plots_dir)
    plotter.generate_all_plots()


if __name__ == "__main__":
    main()
