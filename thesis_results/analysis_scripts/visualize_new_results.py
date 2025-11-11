#!/usr/bin/env python3
"""
Visualization Script for New Thesis Tests
Creates publication-quality plots for all 4 new tests
"""

import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# Use non-interactive backend
matplotlib.use('Agg')

# Set publication quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13


class NewTestsVisualizer:
    """Create visualizations for new tests"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def visualize_all(self):
        """Generate all visualizations"""
        print("=" * 80)
        print("GENERATING VISUALIZATIONS FOR NEW TESTS")
        print("=" * 80)

        # Generate each visualization
        self.visualize_seed_sensitivity()
        self.visualize_payload_complexity()
        self.visualize_reproducibility()
        self.visualize_mutation_ablation()

        print("\n" + "=" * 80)
        print("✓ All visualizations generated!")
        print(f"✓ Saved to: {self.output_dir}")
        print("=" * 80)

    def visualize_seed_sensitivity(self):
        """Visualize seed sensitivity results"""
        print("\n1. Generating seed sensitivity visualizations...")

        results_file = self.results_dir / 'seed_sensitivity' / 'seed_sensitivity_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found, skipping...")
            return

        with open(results_file) as f:
            data = json.load(f)

        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        # Extract data
        configs = []
        ttfc_means = []
        ttfc_errors = []
        crashes_means = []
        crashes_errors = []

        for config in data['configurations']:
            configs.append(f"{config['corpus_type']}\n({config['corpus_size']})")

            ttfc = config['aggregate']['time_to_first_crash']
            ttfc_means.append(ttfc['mean'])
            ttfc_errors.append(ttfc['stdev'])

            crashes = config['aggregate']['unique_crashes']
            crashes_means.append(crashes['mean'])
            crashes_errors.append(crashes['stdev'])

        x = np.arange(len(configs))

        # Plot 1: Time to First Crash
        ax1.bar(x, ttfc_means, yerr=ttfc_errors, capsize=5, alpha=0.7, color='#2E86AB')
        ax1.set_xlabel('Corpus Configuration')
        ax1.set_ylabel('Time to First Crash (seconds)')
        ax1.set_title('Impact of Seed Corpus on TTFC')
        ax1.set_xticks(x)
        ax1.set_xticklabels(configs, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)

        # Plot 2: Final Crashes
        ax2.bar(x, crashes_means, yerr=crashes_errors, capsize=5, alpha=0.7, color='#A23B72')
        ax2.set_xlabel('Corpus Configuration')
        ax2.set_ylabel('Unique Crashes Discovered')
        ax2.set_title('Impact of Seed Corpus on Crash Discovery')
        ax2.set_xticks(x)
        ax2.set_xticklabels(configs, rotation=45, ha='right')
        ax2.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / 'seed_sensitivity.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved: {output_file}")

    def visualize_payload_complexity(self):
        """Visualize payload complexity results"""
        print("\n2. Generating payload complexity visualizations...")

        results_file = self.results_dir / 'payload_complexity' / 'payload_complexity_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found, skipping...")
            return

        with open(results_file) as f:
            data = json.load(f)

        agg = data.get('aggregate_analysis', {})
        diffs = agg.get('metric_differences', {})

        if not diffs:
            print("   ⚠ No metric differences found, skipping...")
            return

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(10, 6))

        metrics = list(diffs.keys())
        crash_means = [diffs[m]['crash_mean'] for m in metrics]
        non_crash_means = [diffs[m]['non_crash_mean'] for m in metrics]

        x = np.arange(len(metrics))
        width = 0.35

        bars1 = ax.bar(x - width/2, crash_means, width, label='Crash-inducing',
                       alpha=0.8, color='#E63946')
        bars2 = ax.bar(x + width/2, non_crash_means, width, label='Non-crash',
                       alpha=0.8, color='#457B9D')

        ax.set_xlabel('Payload Characteristics')
        ax.set_ylabel('Mean Value')
        ax.set_title('Payload Characteristics: Crash vs Non-Crash Inputs')
        ax.set_xticks(x)
        ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics],
                           rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        output_file = self.output_dir / 'payload_complexity.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved: {output_file}")

    def visualize_reproducibility(self):
        """Visualize reproducibility results"""
        print("\n3. Generating reproducibility visualizations...")

        results_file = self.results_dir / 'reproducibility' / 'reproducibility_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found, skipping...")
            return

        with open(results_file) as f:
            data = json.load(f)

        summary = data.get('summary', {})

        # Create figure with 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        # Plot 1: Reproducibility Scores
        scores = [
            summary.get('fixed_seed_reproducibility', {}).get('score', 0),
            summary.get('cross_platform_consistency', {}).get('avg_score', 0),
            summary.get('overall_reproducibility', {}).get('score', 0)
        ]
        labels = ['Fixed Seed', 'Cross-Platform', 'Overall']
        colors = ['#06A77D', '#F77F00', '#005F73']

        axes[0].bar(labels, scores, color=colors, alpha=0.7)
        axes[0].set_ylabel('Reproducibility Score (%)')
        axes[0].set_title('Reproducibility Scores')
        axes[0].set_ylim([0, 105])
        axes[0].axhline(y=90, color='r', linestyle='--', alpha=0.5, label='90% threshold')
        axes[0].legend()
        axes[0].grid(axis='y', alpha=0.3)

        # Plot 2: Natural Variance CV
        variance = summary.get('natural_variance', {})
        cv_values = [
            variance.get('crash_cv', 0),
            variance.get('coverage_cv', 0)
        ]
        cv_labels = ['Crashes', 'Coverage']

        axes[1].bar(cv_labels, cv_values, color='#D62828', alpha=0.7)
        axes[1].set_ylabel('Coefficient of Variation (%)')
        axes[1].set_title('Natural Variance (Without Fixed Seed)')
        axes[1].axhline(y=15, color='g', linestyle='--', alpha=0.5, label='15% threshold')
        axes[1].legend()
        axes[1].grid(axis='y', alpha=0.3)

        # Plot 3: Status indicators
        statuses = {
            'Deterministic': summary.get('overall_reproducibility', {}).get('deterministic', False),
            'Production\nReady': summary.get('overall_reproducibility', {}).get('production_ready', False),
            'Acceptable\nVariance': summary.get('natural_variance', {}).get('acceptable', False)
        }

        status_labels = list(statuses.keys())
        status_values = [1 if v else 0 for v in statuses.values()]
        status_colors = ['#06A77D' if v else '#E63946' for v in statuses.values()]

        axes[2].bar(status_labels, status_values, color=status_colors, alpha=0.7)
        axes[2].set_ylabel('Status (1=Pass, 0=Fail)')
        axes[2].set_title('Quality Checks')
        axes[2].set_ylim([0, 1.2])
        axes[2].set_yticks([0, 1])
        axes[2].set_yticklabels(['Fail', 'Pass'])

        plt.tight_layout()
        output_file = self.output_dir / 'reproducibility.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved: {output_file}")

    def visualize_mutation_ablation(self):
        """Visualize mutation ablation results"""
        print("\n4. Generating mutation ablation visualizations...")

        results_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found, skipping...")
            return

        with open(results_file) as f:
            data = json.load(f)

        rankings = data.get('rankings', {})

        if not rankings:
            print("   ⚠ No rankings found, skipping...")
            return

        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Crashes by operator
        crash_rankings = rankings.get('by_crashes', [])[:9]  # Top 9
        operators = [r['operator'].replace('_', ' ').title() for r in crash_rankings]
        crashes = [r['value'] for r in crash_rankings]

        colors = plt.cm.viridis(np.linspace(0, 1, len(operators)))

        ax1.barh(operators, crashes, color=colors, alpha=0.8)
        ax1.set_xlabel('Mean Unique Crashes')
        ax1.set_title('Mutation Operators Ranked by Crash Discovery')
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()  # Highest at top

        # Plot 2: Coverage by operator
        coverage_rankings = rankings.get('by_coverage', [])[:9]
        operators2 = [r['operator'].replace('_', ' ').title() for r in coverage_rankings]
        coverage = [r['value'] for r in coverage_rankings]

        colors2 = plt.cm.plasma(np.linspace(0, 1, len(operators2)))

        ax2.barh(operators2, coverage, color=colors2, alpha=0.8)
        ax2.set_xlabel('Mean Coverage')
        ax2.set_title('Mutation Operators Ranked by Coverage')
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()

        plt.tight_layout()
        output_file = self.output_dir / 'mutation_ablation.png'
        plt.savefig(output_file, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved: {output_file}")


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('plots/new_tests')

    visualizer = NewTestsVisualizer(results_dir, output_dir)
    visualizer.visualize_all()


if __name__ == '__main__':
    main()
