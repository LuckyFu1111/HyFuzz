#!/usr/bin/env python3
"""
Enhanced Visualizations for Thesis
Creates publication-quality correlation heatmaps, scatter plots, and comparison charts
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Tuple
import seaborn as sns

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


class EnhancedVisualizer:
    """Create enhanced visualizations for thesis"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}

    def load_data(self):
        """Load all test results"""
        print("Loading test results...")

        # Load cross-analysis
        cross_file = self.results_dir / 'cross_analysis.json'
        if cross_file.exists():
            with open(cross_file) as f:
                self.data['cross_analysis'] = json.load(f)
            print("  ✓ Cross-analysis data loaded")

        # Load enhanced stats
        stats_file = self.results_dir / 'enhanced_statistical_analysis.json'
        if stats_file.exists():
            with open(stats_file) as f:
                self.data['enhanced_stats'] = json.load(f)
            print("  ✓ Enhanced statistics loaded")

        # Load mutation ablation
        mutation_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'
        if mutation_file.exists():
            with open(mutation_file) as f:
                self.data['mutation'] = json.load(f)
            print("  ✓ Mutation ablation data loaded")

        # Load seed sensitivity
        seed_file = self.results_dir / 'seed_sensitivity' / 'seed_sensitivity_results.json'
        if seed_file.exists():
            with open(seed_file) as f:
                self.data['seed'] = json.load(f)
            print("  ✓ Seed sensitivity data loaded")

    def create_correlation_heatmap(self):
        """Create correlation heatmap of all key metrics"""
        print("\n1. Creating correlation heatmap...")

        if 'cross_analysis' not in self.data:
            print("   ⚠ Insufficient data")
            return

        cross_data = self.data['cross_analysis']

        # Extract TTFC vs crashes data
        ttfc_data = cross_data.get('ttfc_crashes', {})
        data_points = ttfc_data.get('data_points', [])

        if not data_points:
            print("   ⚠ No data points found")
            return

        # Extract metrics for correlation matrix
        metrics = {
            'TTFC (s)': [p['ttfc'] for p in data_points],
            'Crashes': [p['crashes'] for p in data_points],
        }

        # Add coverage-efficiency data if available
        cov_eff_data = cross_data.get('coverage_efficiency', {})
        if cov_eff_data.get('data_points'):
            metrics['Coverage'] = [p['coverage'] for p in cov_eff_data['data_points']]
            metrics['Efficiency'] = [p['efficiency'] for p in cov_eff_data['data_points']]

        # Calculate correlation matrix
        metric_names = list(metrics.keys())
        n_metrics = len(metric_names)
        corr_matrix = np.zeros((n_metrics, n_metrics))

        for i, name1 in enumerate(metric_names):
            for j, name2 in enumerate(metric_names):
                if i == j:
                    corr_matrix[i, j] = 1.0
                else:
                    values1 = metrics[name1]
                    values2 = metrics[name2]
                    # Align lengths
                    min_len = min(len(values1), len(values2))
                    if min_len >= 3:
                        corr = np.corrcoef(values1[:min_len], values2[:min_len])[0, 1]
                        corr_matrix[i, j] = corr

        # Create heatmap
        fig, ax = plt.subplots(figsize=(8, 6))

        # Use diverging colormap
        im = ax.imshow(corr_matrix, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

        # Set ticks
        ax.set_xticks(np.arange(n_metrics))
        ax.set_yticks(np.arange(n_metrics))
        ax.set_xticklabels(metric_names)
        ax.set_yticklabels(metric_names)

        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add correlation values
        for i in range(n_metrics):
            for j in range(n_metrics):
                text = ax.text(j, i, f'{corr_matrix[i, j]:.2f}',
                              ha="center", va="center",
                              color="white" if abs(corr_matrix[i, j]) > 0.5 else "black",
                              fontsize=9, weight='bold')

        ax.set_title('Correlation Matrix: Key Fuzzing Metrics')
        fig.colorbar(im, ax=ax, label='Pearson Correlation Coefficient')

        plt.tight_layout()
        output_file = self.output_dir / 'correlation_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved to: {output_file}")

    def create_ttfc_vs_crashes_scatter(self):
        """Create scatter plot: TTFC vs Final Crashes with correlation"""
        print("\n2. Creating TTFC vs Crashes scatter plot...")

        if 'cross_analysis' not in self.data:
            print("   ⚠ Insufficient data")
            return

        ttfc_data = self.data['cross_analysis'].get('ttfc_crashes', {})
        data_points = ttfc_data.get('data_points', [])

        if not data_points:
            print("   ⚠ No data points")
            return

        # Extract data
        ttfc_values = [p['ttfc'] for p in data_points]
        crash_values = [p['crashes'] for p in data_points]
        corpus_types = [p['corpus_type'] for p in data_points]

        # Get correlation
        correlation = ttfc_data.get('correlation', {})
        r = correlation.get('pearson_r', 0)
        p_value = correlation.get('p_value', 1)

        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Color by corpus type
        colors = []
        for ct in corpus_types:
            if 'empty' in ct:
                colors.append('#e74c3c')  # Red
            elif 'random' in ct:
                colors.append('#f39c12')  # Orange
            elif 'minimal' in ct:
                colors.append('#3498db')  # Blue
            elif 'medium' in ct:
                colors.append('#2ecc71')  # Green
            else:
                colors.append('#9b59b6')  # Purple

        # Scatter plot
        scatter = ax.scatter(ttfc_values, crash_values, c=colors, s=150,
                           alpha=0.7, edgecolors='black', linewidth=1.5)

        # Add labels for each point
        for i, (ttfc, crashes, corpus) in enumerate(zip(ttfc_values, crash_values, corpus_types)):
            ax.annotate(f'{corpus}', (ttfc, crashes),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=7, alpha=0.8)

        # Fit line
        z = np.polyfit(ttfc_values, crash_values, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(ttfc_values), max(ttfc_values), 100)
        ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2,
               label=f'Linear fit (r={r:.3f}, p={p_value:.4f})')

        ax.set_xlabel('Time to First Crash (seconds)', fontsize=12)
        ax.set_ylabel('Total Unique Crashes', fontsize=12)
        ax.set_title('Early Crash Discovery Predicts Campaign Effectiveness', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        # Add correlation box
        textstr = f'Correlation: r = {r:.3f}\np-value = {p_value:.4f}\n' + \
                  ('Highly Significant' if p_value < 0.01 else 'Significant' if p_value < 0.05 else 'Not Significant')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)

        plt.tight_layout()
        output_file = self.output_dir / 'ttfc_vs_crashes_scatter.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved to: {output_file}")

    def create_coverage_efficiency_scatter(self):
        """Create scatter plot: Coverage vs Efficiency"""
        print("\n3. Creating Coverage vs Efficiency scatter plot...")

        if 'cross_analysis' not in self.data:
            print("   ⚠ Insufficient data")
            return

        cov_eff_data = self.data['cross_analysis'].get('coverage_efficiency', {})
        data_points = cov_eff_data.get('data_points', [])

        if not data_points:
            print("   ⚠ No data points")
            return

        # Extract data
        coverage_values = [p['coverage'] for p in data_points]
        efficiency_values = [p['efficiency'] for p in data_points]
        operators = [p['operator'] for p in data_points]

        # Get correlation
        correlation = cov_eff_data.get('correlation', {})
        r = correlation.get('pearson_r', 0)

        # Create scatter plot
        fig, ax = plt.subplots(figsize=(10, 6))

        # Color by operator complexity
        colors = []
        for op in operators:
            if op in ['bit_flip', 'byte_flip']:
                colors.append('#3498db')  # Blue - simple
            elif op in ['arithmetic', 'block_delete', 'block_duplicate', 'block_shuffle']:
                colors.append('#f39c12')  # Orange - medium
            else:
                colors.append('#e74c3c')  # Red - complex

        # Scatter plot
        scatter = ax.scatter(coverage_values, efficiency_values, c=colors, s=150,
                           alpha=0.7, edgecolors='black', linewidth=1.5)

        # Add labels
        for i, (cov, eff, op) in enumerate(zip(coverage_values, efficiency_values, operators)):
            ax.annotate(op, (cov, eff),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=7, alpha=0.8)

        # Fit line
        z = np.polyfit(coverage_values, efficiency_values, 1)
        p = np.poly1d(z)
        x_line = np.linspace(min(coverage_values), max(coverage_values), 100)
        ax.plot(x_line, p(x_line), "g--", alpha=0.8, linewidth=2,
               label=f'Linear fit (r={r:.3f})')

        ax.set_xlabel('Code Coverage (branches)', fontsize=12)
        ax.set_ylabel('Crash Efficiency (crashes per 1k execs)', fontsize=12)
        ax.set_title('Coverage and Efficiency: Strong Positive Synergy', fontsize=13, weight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        # Add legend for operator types
        blue_patch = mpatches.Patch(color='#3498db', label='Simple')
        orange_patch = mpatches.Patch(color='#f39c12', label='Medium')
        red_patch = mpatches.Patch(color='#e74c3c', label='Complex')
        ax.legend(handles=[blue_patch, orange_patch, red_patch],
                 title='Operator Complexity', loc='upper left')

        # Add correlation box
        textstr = f'r = {r:.3f}\n' + \
                  ('No tradeoff!\nCan optimize both' if r > 0.7 else 'Moderate synergy')
        props = dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
        ax.text(0.95, 0.05, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='bottom', horizontalalignment='right', bbox=props)

        plt.tight_layout()
        output_file = self.output_dir / 'coverage_efficiency_scatter.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved to: {output_file}")

    def create_mutation_operators_comparison(self):
        """Create horizontal bar chart comparing mutation operators"""
        print("\n4. Creating mutation operators comparison chart...")

        if 'mutation' not in self.data:
            print("   ⚠ Insufficient data")
            return

        mutation_data = self.data['mutation']
        operators = mutation_data.get('operator_results', [])

        if not operators:
            print("   ⚠ No operators found")
            return

        # Extract data
        op_names = []
        crashes = []
        coverage = []
        efficiency = []

        for op in operators:
            op_name = op.get('operator_name', op.get('operator', 'unknown'))
            op_names.append(op_name)
            crashes.append(op.get('aggregate', {}).get('unique_crashes', {}).get('mean', 0))
            coverage.append(op.get('aggregate', {}).get('coverage', {}).get('mean', 0))
            efficiency.append(op.get('aggregate', {}).get('crashes_per_1k_execs', {}).get('mean', 0))

        # Sort by overall score
        overall_scores = [c * e for c, e in zip(crashes, efficiency)]
        sorted_indices = sorted(range(len(overall_scores)), key=lambda i: overall_scores[i], reverse=True)

        op_names = [op_names[i] for i in sorted_indices]
        crashes = [crashes[i] for i in sorted_indices]
        coverage = [coverage[i] for i in sorted_indices]
        efficiency = [efficiency[i] for i in sorted_indices]

        # Create figure with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 6))

        y_pos = np.arange(len(op_names))

        # Plot 1: Crashes
        bars1 = ax1.barh(y_pos, crashes, color='#e74c3c', alpha=0.7, edgecolor='black')
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(op_names)
        ax1.set_xlabel('Unique Crashes')
        ax1.set_title('Crash Discovery', weight='bold')
        ax1.grid(axis='x', alpha=0.3)

        # Add values
        for i, v in enumerate(crashes):
            ax1.text(v + 0.1, i, f'{v:.1f}', va='center', fontsize=8)

        # Plot 2: Coverage
        bars2 = ax2.barh(y_pos, coverage, color='#3498db', alpha=0.7, edgecolor='black')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([])  # Hide labels for middle plot
        ax2.set_xlabel('Code Coverage')
        ax2.set_title('Coverage Achieved', weight='bold')
        ax2.grid(axis='x', alpha=0.3)

        # Add values
        for i, v in enumerate(coverage):
            ax2.text(v + 5, i, f'{v:.0f}', va='center', fontsize=8)

        # Plot 3: Efficiency
        bars3 = ax3.barh(y_pos, efficiency, color='#2ecc71', alpha=0.7, edgecolor='black')
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels([])  # Hide labels for right plot
        ax3.set_xlabel('Efficiency (crashes/1k execs)')
        ax3.set_title('Crash Efficiency', weight='bold')
        ax3.grid(axis='x', alpha=0.3)

        # Add values
        for i, v in enumerate(efficiency):
            ax3.text(v + 0.02, i, f'{v:.2f}', va='center', fontsize=8)

        # Highlight best operator
        bars1[0].set_color('#c0392b')
        bars1[0].set_alpha(0.9)
        bars2[0].set_color('#2980b9')
        bars2[0].set_alpha(0.9)
        bars3[0].set_color('#27ae60')
        bars3[0].set_alpha(0.9)

        fig.suptitle('Mutation Operator Performance Comparison', fontsize=14, weight='bold')
        plt.tight_layout()

        output_file = self.output_dir / 'mutation_operators_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved to: {output_file}")

    def create_seed_corpus_impact_chart(self):
        """Create chart showing seed corpus impact"""
        print("\n5. Creating seed corpus impact chart...")

        if 'seed' not in self.data:
            print("   ⚠ Insufficient data")
            return

        seed_data = self.data['seed']
        configs = seed_data.get('configurations', [])

        if not configs:
            print("   ⚠ No configurations found")
            return

        # Extract data
        config_labels = []
        crashes_means = []
        ttfc_means = []
        coverage_means = []

        for config in configs:
            corpus_type = config['corpus_type']
            corpus_size = config['corpus_size']
            config_labels.append(f"{corpus_type}\n({corpus_size})")

            crashes_means.append(config['aggregate']['unique_crashes']['mean'])
            ttfc_means.append(config['aggregate']['time_to_first_crash']['mean'])
            coverage_means.append(config['aggregate'].get('final_coverage', config['aggregate'].get('coverage', {})).get('mean', 0))

        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        x = np.arange(len(config_labels))
        width = 0.35

        # Plot 1: Crashes and Coverage
        ax1_2 = ax1.twinx()

        bars1 = ax1.bar(x - width/2, crashes_means, width, label='Unique Crashes',
                       color='#e74c3c', alpha=0.7, edgecolor='black')
        bars2 = ax1_2.bar(x + width/2, coverage_means, width, label='Coverage',
                         color='#3498db', alpha=0.7, edgecolor='black')

        ax1.set_xlabel('Seed Corpus Configuration')
        ax1.set_ylabel('Unique Crashes', color='#e74c3c')
        ax1_2.set_ylabel('Code Coverage', color='#3498db')
        ax1.set_title('Impact of Seed Corpus Quality on Fuzzing Effectiveness', weight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(config_labels, rotation=45, ha='right')
        ax1.tick_params(axis='y', labelcolor='#e74c3c')
        ax1_2.tick_params(axis='y', labelcolor='#3498db')
        ax1.grid(axis='y', alpha=0.3)

        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax1_2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        # Plot 2: Time to First Crash (inverted - lower is better)
        bars3 = ax2.bar(x, ttfc_means, color='#f39c12', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('Seed Corpus Configuration')
        ax2.set_ylabel('Time to First Crash (seconds)')
        ax2.set_title('Seed Quality Impact on Early Crash Discovery (Lower is Better)', weight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(config_labels, rotation=45, ha='right')
        ax2.invert_yaxis()  # Invert so lower TTFC is "higher" on the chart
        ax2.grid(axis='y', alpha=0.3)

        # Add values
        for i, v in enumerate(ttfc_means):
            ax2.text(i, v, f'{v:.1f}s', ha='center', va='bottom', fontsize=8)

        plt.tight_layout()

        output_file = self.output_dir / 'seed_corpus_impact.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"   ✓ Saved to: {output_file}")

    def run_all_visualizations(self):
        """Run all visualization generators"""
        print("=" * 80)
        print("ENHANCED VISUALIZATIONS GENERATION")
        print("=" * 80)

        self.load_data()

        if not self.data:
            print("\n⚠ No data loaded")
            return

        self.create_correlation_heatmap()
        self.create_ttfc_vs_crashes_scatter()
        self.create_coverage_efficiency_scatter()
        self.create_mutation_operators_comparison()
        self.create_seed_corpus_impact_chart()

        print("\n" + "=" * 80)
        print("✓ All visualizations generated!")
        print(f"✓ Output directory: {self.output_dir}")
        print("=" * 80)


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('plots/enhanced')

    visualizer = EnhancedVisualizer(results_dir, output_dir)
    visualizer.run_all_visualizations()


if __name__ == '__main__':
    main()
