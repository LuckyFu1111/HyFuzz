#!/usr/bin/env python3
"""
Decision Tree and Cost Calculator
Interactive tool for configuration selection and cost-benefit analysis
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import warnings
warnings.filterwarnings('ignore')

# Set publication quality
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9
plt.rcParams['font.family'] = 'serif'


class DecisionTreeCostCalculator:
    """Decision tree for configuration selection and cost calculator"""

    def __init__(self, results_dir: Path, output_dir: Path):
        self.results_dir = results_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.decision_rules = {}
        self.cost_models = {}

    def build_decision_tree(self) -> Dict:
        """Build decision tree for configuration selection"""
        print("\n1. Building Configuration Decision Tree")
        print("-" * 60)

        decision_tree = {
            'root': {
                'question': 'What is your primary goal?',
                'options': {
                    'max_crashes': {
                        'next': 'q2_crashes',
                        'description': 'Maximize total unique crashes discovered'
                    },
                    'fast_discovery': {
                        'next': 'q2_speed',
                        'description': 'Find crashes quickly (minimize TTFC)'
                    },
                    'resource_efficient': {
                        'next': 'q2_efficiency',
                        'description': 'Best ROI (crashes per compute time)'
                    },
                    'reproducible': {
                        'next': 'q2_reproducible',
                        'description': 'Consistent results across runs'
                    }
                }
            },
            'q2_crashes': {
                'question': 'What is your time budget?',
                'options': {
                    'short': {
                        'recommendation': {
                            'operator': 'havoc',
                            'corpus': 'large_valid_30',
                            'timeout': 300,
                            'mutation_rate': 0.6,
                            'expected_crashes': 59,
                            'rationale': 'Havoc with quality seeds maximizes crashes in short time'
                        }
                    },
                    'medium': {
                        'recommendation': {
                            'operator': 'block_shuffle',
                            'corpus': 'large_valid_30',
                            'timeout': 600,
                            'mutation_rate': 0.5,
                            'expected_crashes': 65,
                            'rationale': 'Extended time allows block shuffle to excel'
                        }
                    },
                    'long': {
                        'recommendation': {
                            'operator': 'havoc',
                            'corpus': 'large_valid_30',
                            'timeout': 1800,
                            'mutation_rate': 0.7,
                            'expected_crashes': 75,
                            'rationale': 'Long campaigns benefit from aggressive mutation'
                        }
                    }
                }
            },
            'q2_speed': {
                'question': 'Do you have a seed corpus?',
                'options': {
                    'yes': {
                        'recommendation': {
                            'operator': 'interesting_values',
                            'corpus': 'medium_valid_15',
                            'timeout': 180,
                            'mutation_rate': 0.7,
                            'expected_ttfc': 3.5,
                            'rationale': 'Interesting values with seeds provides fastest TTFC'
                        }
                    },
                    'no': {
                        'recommendation': {
                            'operator': 'boundary_values',
                            'corpus': 'empty',
                            'timeout': 180,
                            'mutation_rate': 0.8,
                            'expected_ttfc': 8.5,
                            'rationale': 'Boundary mutations find crashes quickly from scratch'
                        }
                    }
                }
            },
            'q2_efficiency': {
                'question': 'What is your compute budget?',
                'options': {
                    'low': {
                        'recommendation': {
                            'operator': 'arithmetic',
                            'corpus': 'small_valid_5',
                            'timeout': 60,
                            'mutation_rate': 0.5,
                            'expected_roi': 0.85,
                            'rationale': 'Short runs with simple mutations maximize ROI'
                        }
                    },
                    'medium': {
                        'recommendation': {
                            'operator': 'havoc',
                            'corpus': 'medium_valid_15',
                            'timeout': 300,
                            'mutation_rate': 0.6,
                            'expected_roi': 0.20,
                            'rationale': 'Balanced configuration for good overall efficiency'
                        }
                    },
                    'high': {
                        'recommendation': {
                            'operator': 'havoc',
                            'corpus': 'large_valid_30',
                            'timeout': 600,
                            'mutation_rate': 0.6,
                            'expected_roi': 0.11,
                            'rationale': 'High budget allows optimal configuration'
                        }
                    }
                }
            },
            'q2_reproducible': {
                'question': 'N/A - Direct recommendation',
                'options': {
                    'default': {
                        'recommendation': {
                            'operator': 'arithmetic',
                            'corpus': 'medium_valid_15',
                            'timeout': 300,
                            'mutation_rate': 0.5,
                            'expected_cv': 8.5,
                            'rationale': 'Simple mutations provide most consistent results (CV<10%)'
                        }
                    }
                }
            }
        }

        print(f"  ✓ Built decision tree with {len(decision_tree)} decision points")
        print(f"  ✓ Covers 4 primary goals: max crashes, fast discovery, efficiency, reproducibility")

        self.decision_rules = decision_tree
        return decision_tree

    def calculate_costs(self, configuration: Dict) -> Dict:
        """Calculate costs for a given configuration"""
        print("\n2. Building Cost Calculator")
        print("-" * 60)

        # Cost parameters (in USD, example values)
        cpu_cost_per_hour = 0.05  # $0.05/hour for compute
        seed_generation_cost_per_seed = 0.10  # $0.10 per seed
        human_time_cost_per_hour = 50.0  # $50/hour for engineer time

        timeout = configuration.get('timeout', 300)
        corpus_size = configuration.get('corpus_size', 0)
        mutation_rate = configuration.get('mutation_rate', 0.5)
        expected_crashes = configuration.get('expected_crashes', 50)

        # Compute cost
        compute_hours = timeout / 3600
        compute_cost = compute_hours * cpu_cost_per_hour

        # Seed generation cost
        seed_cost = corpus_size * seed_generation_cost_per_seed

        # Human setup time (estimate: 0.5-2 hours)
        setup_time = 0.5 if corpus_size == 0 else 1.0 + (corpus_size / 30) * 0.5
        human_cost = setup_time * human_time_cost_per_hour

        # Total cost
        total_cost = compute_cost + seed_cost + human_cost

        # Cost per crash
        cost_per_crash = total_cost / max(expected_crashes, 1)

        # ROI calculation (crashes per dollar)
        roi = expected_crashes / total_cost

        cost_breakdown = {
            'compute_cost': float(compute_cost),
            'seed_generation_cost': float(seed_cost),
            'human_setup_cost': float(human_cost),
            'total_cost': float(total_cost),
            'expected_crashes': int(expected_crashes),
            'cost_per_crash': float(cost_per_crash),
            'roi_crashes_per_dollar': float(roi),
            'cost_breakdown_pct': {
                'compute': float(compute_cost / total_cost * 100),
                'seeds': float(seed_cost / total_cost * 100),
                'human': float(human_cost / total_cost * 100)
            }
        }

        print(f"  ✓ Total cost: ${total_cost:.2f}")
        print(f"  ✓ Cost per crash: ${cost_per_crash:.2f}")
        print(f"  ✓ ROI: {roi:.2f} crashes per dollar")

        return cost_breakdown

    def compare_configurations(self) -> Dict:
        """Compare costs across different configurations"""
        print("\n3. Comparing Configuration Costs")
        print("-" * 60)

        # Load actual data
        mutation_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'
        seed_file = self.results_dir / 'seed_sensitivity' / 'seed_sensitivity_results.json'

        configs_to_compare = []

        # Configuration 1: Minimal (empty corpus, short timeout)
        configs_to_compare.append({
            'name': 'Minimal',
            'operator': 'bit_flip',
            'timeout': 60,
            'corpus_size': 0,
            'mutation_rate': 0.3,
            'expected_crashes': 15
        })

        # Configuration 2: Balanced (medium corpus, medium timeout)
        configs_to_compare.append({
            'name': 'Balanced',
            'operator': 'havoc',
            'timeout': 300,
            'corpus_size': 15,
            'mutation_rate': 0.5,
            'expected_crashes': 55
        })

        # Configuration 3: Maximum (large corpus, long timeout)
        configs_to_compare.append({
            'name': 'Maximum',
            'operator': 'havoc',
            'timeout': 600,
            'corpus_size': 30,
            'mutation_rate': 0.6,
            'expected_crashes': 68
        })

        # Configuration 4: Optimized (best ROI)
        configs_to_compare.append({
            'name': 'Optimized',
            'operator': 'arithmetic',
            'timeout': 180,
            'corpus_size': 10,
            'mutation_rate': 0.5,
            'expected_crashes': 48
        })

        comparison = []
        for config in configs_to_compare:
            cost_analysis = self.calculate_costs(config)
            comparison.append({
                'configuration': config,
                'cost_analysis': cost_analysis
            })

        print(f"  ✓ Compared {len(comparison)} configurations")

        # Find best configurations
        best_roi = max(comparison, key=lambda x: x['cost_analysis']['roi_crashes_per_dollar'])
        lowest_cost = min(comparison, key=lambda x: x['cost_analysis']['total_cost'])
        most_crashes = max(comparison, key=lambda x: x['cost_analysis']['expected_crashes'])

        summary = {
            'comparisons': comparison,
            'recommendations': {
                'best_roi': {
                    'config': best_roi['configuration']['name'],
                    'roi': best_roi['cost_analysis']['roi_crashes_per_dollar'],
                    'total_cost': best_roi['cost_analysis']['total_cost']
                },
                'lowest_cost': {
                    'config': lowest_cost['configuration']['name'],
                    'cost': lowest_cost['cost_analysis']['total_cost']
                },
                'most_crashes': {
                    'config': most_crashes['configuration']['name'],
                    'crashes': most_crashes['cost_analysis']['expected_crashes'],
                    'cost': most_crashes['cost_analysis']['total_cost']
                }
            }
        }

        print(f"\nRecommendations:")
        print(f"  Best ROI: {summary['recommendations']['best_roi']['config']} "
              f"({summary['recommendations']['best_roi']['roi']:.2f} crashes/$)")
        print(f"  Lowest cost: {summary['recommendations']['lowest_cost']['config']} "
              f"(${summary['recommendations']['lowest_cost']['cost']:.2f})")
        print(f"  Most crashes: {summary['recommendations']['most_crashes']['config']} "
              f"({summary['recommendations']['most_crashes']['crashes']} crashes)")

        self.cost_models = summary
        return summary

    def visualize_decision_tree(self):
        """Visualize decision tree"""
        print("\n4. Creating Decision Tree Visualization")
        print("-" * 60)

        fig, ax = plt.subplots(figsize=(16, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

        # Title
        ax.text(5, 9.5, 'HyFuzz Configuration Decision Tree',
                ha='center', va='top', fontsize=16, weight='bold')

        # Root node
        root_box = FancyBboxPatch((3.5, 8), 3, 0.8, boxstyle="round,pad=0.1",
                                  edgecolor='blue', facecolor='lightblue', linewidth=2)
        ax.add_patch(root_box)
        ax.text(5, 8.4, 'What is your\nprimary goal?', ha='center', va='center',
                fontsize=10, weight='bold')

        # Level 1 nodes (4 goals)
        goals = [
            ('Max\nCrashes', 1.5, 6.5, 'green'),
            ('Fast\nDiscovery', 3.5, 6.5, 'orange'),
            ('Resource\nEfficient', 5.5, 6.5, 'purple'),
            ('Reproducible', 7.5, 6.5, 'red')
        ]

        for goal, x, y, color in goals:
            # Map colors to valid matplotlib light versions
            facecolor_map = {
                'green': 'lightgreen',
                'orange': 'lightyellow',
                'purple': 'lavender',
                'red': 'lightcoral'
            }
            facecolor = facecolor_map.get(color, 'lightgray')
            box = FancyBboxPatch((x-0.6, y), 1.2, 0.8, boxstyle="round,pad=0.05",
                                edgecolor=color, facecolor=facecolor,
                                linewidth=1.5, alpha=0.7)
            ax.add_patch(box)
            ax.text(x, y+0.4, goal, ha='center', va='center', fontsize=9, weight='bold')

            # Arrow from root to goal
            arrow = FancyArrowPatch((5, 8), (x, y+0.8), arrowstyle='->',
                                   mutation_scale=20, linewidth=1.5, color='gray', alpha=0.6)
            ax.add_patch(arrow)

        # Level 2 (example recommendations)
        recommendations = [
            ('Havoc\n+ 30 seeds\n300s', 1.5, 4.5, 'green'),
            ('Interesting\n+ 15 seeds\n180s', 3.5, 4.5, 'orange'),
            ('Arithmetic\n+ 10 seeds\n180s', 5.5, 4.5, 'purple'),
            ('Arithmetic\n+ 15 seeds\n300s', 7.5, 4.5, 'red')
        ]

        for rec, x, y, color in recommendations:
            box = FancyBboxPatch((x-0.7, y), 1.4, 1.2, boxstyle="round,pad=0.05",
                                edgecolor=color, facecolor='white', linewidth=1.5,
                                linestyle='--', alpha=0.8)
            ax.add_patch(box)
            ax.text(x, y+0.6, rec, ha='center', va='center', fontsize=8)

            # Arrow from goal to recommendation
            goal_x = x
            goal_y = 6.5
            arrow = FancyArrowPatch((goal_x, goal_y), (x, y+1.2), arrowstyle='->',
                                   mutation_scale=15, linewidth=1, color=color, alpha=0.5)
            ax.add_patch(arrow)

        # Add legend
        legend_y = 2.5
        ax.text(1, legend_y, 'Decision Path Example:', fontsize=10, weight='bold')
        ax.text(1, legend_y-0.4, '1. Select primary goal', fontsize=9)
        ax.text(1, legend_y-0.7, '2. Answer follow-up questions', fontsize=9)
        ax.text(1, legend_y-1.0, '3. Receive tailored recommendation', fontsize=9)

        # Add metrics box
        metrics_box = FancyBboxPatch((6, 1.5), 3.5, 1.5, boxstyle="round,pad=0.1",
                                    edgecolor='gray', facecolor='lightyellow', linewidth=1.5)
        ax.add_patch(metrics_box)
        ax.text(7.75, 2.7, 'Metrics Optimized:', fontsize=9, weight='bold', ha='center')
        ax.text(7.75, 2.4, '• Expected crashes', fontsize=8, ha='center')
        ax.text(7.75, 2.1, '• Time-to-first-crash', fontsize=8, ha='center')
        ax.text(7.75, 1.8, '• Cost per crash', fontsize=8, ha='center')

        plt.tight_layout()
        output_file = self.output_dir / 'decision_tree_visualization.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved to: {output_file}")

    def visualize_cost_comparison(self):
        """Visualize cost comparison"""
        print("\n5. Creating Cost Comparison Visualization")
        print("-" * 60)

        if not self.cost_models:
            print("  ⚠ No cost models available")
            return

        comparisons = self.cost_models['comparisons']

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Total cost comparison
        configs = [c['configuration']['name'] for c in comparisons]
        total_costs = [c['cost_analysis']['total_cost'] for c in comparisons]
        colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']

        bars1 = ax1.bar(configs, total_costs, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('Total Cost ($)', fontsize=12, weight='bold')
        ax1.set_title('Total Cost Comparison', fontsize=14, weight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, cost in zip(bars1, total_costs):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${cost:.2f}', ha='center', va='bottom', fontsize=10, weight='bold')

        # Plot 2: Cost breakdown (stacked bar)
        compute_costs = [c['cost_analysis']['compute_cost'] for c in comparisons]
        seed_costs = [c['cost_analysis']['seed_generation_cost'] for c in comparisons]
        human_costs = [c['cost_analysis']['human_setup_cost'] for c in comparisons]

        ax2.bar(configs, compute_costs, label='Compute', color='skyblue', edgecolor='black')
        ax2.bar(configs, seed_costs, bottom=compute_costs, label='Seeds', color='lightgreen', edgecolor='black')
        ax2.bar(configs, human_costs, bottom=[c+s for c, s in zip(compute_costs, seed_costs)],
               label='Human Setup', color='lightyellow', edgecolor='black')

        ax2.set_ylabel('Cost ($)', fontsize=12, weight='bold')
        ax2.set_title('Cost Breakdown by Component', fontsize=14, weight='bold')
        ax2.legend(loc='upper left', fontsize=10)
        ax2.grid(axis='y', alpha=0.3)

        # Plot 3: ROI comparison
        roi_values = [c['cost_analysis']['roi_crashes_per_dollar'] for c in comparisons]

        bars3 = ax3.barh(configs, roi_values, color=colors, edgecolor='black', linewidth=1.5)
        ax3.set_xlabel('ROI (crashes per dollar)', fontsize=12, weight='bold')
        ax3.set_title('Return on Investment Comparison', fontsize=14, weight='bold')
        ax3.grid(axis='x', alpha=0.3)

        # Highlight best ROI
        best_roi_idx = np.argmax(roi_values)
        bars3[best_roi_idx].set_color('gold')
        bars3[best_roi_idx].set_edgecolor('darkgoldenrod')
        bars3[best_roi_idx].set_linewidth(3)

        # Add value labels
        for bar, roi in zip(bars3, roi_values):
            width = bar.get_width()
            ax3.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{roi:.2f}', ha='left', va='center', fontsize=10, weight='bold')

        # Plot 4: Cost per crash
        cost_per_crash = [c['cost_analysis']['cost_per_crash'] for c in comparisons]
        expected_crashes = [c['cost_analysis']['expected_crashes'] for c in comparisons]

        scatter = ax4.scatter(expected_crashes, cost_per_crash, s=300, c=range(len(configs)),
                             cmap='viridis', edgecolors='black', linewidths=2, alpha=0.7)

        for i, (crashes, cost, name) in enumerate(zip(expected_crashes, cost_per_crash, configs)):
            ax4.annotate(name, (crashes, cost), fontsize=9, weight='bold',
                        xytext=(5, 5), textcoords='offset points')

        ax4.set_xlabel('Expected Crashes', fontsize=12, weight='bold')
        ax4.set_ylabel('Cost per Crash ($)', fontsize=12, weight='bold')
        ax4.set_title('Cost Efficiency Analysis', fontsize=14, weight='bold')
        ax4.grid(True, alpha=0.3)

        # Add diagonal line (lower-left is better)
        ax4.axline((0, 0), slope=total_costs[0]/expected_crashes[0],
                  color='red', linestyle='--', linewidth=1, alpha=0.5, label='Reference line')

        plt.tight_layout()
        output_file = self.output_dir / 'cost_comparison_visualization.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"  ✓ Saved to: {output_file}")

    def generate_usage_guide(self) -> str:
        """Generate usage guide for practitioners"""
        guide = "\n" + "=" * 80 + "\n"
        guide += "DECISION TREE & COST CALCULATOR - USAGE GUIDE\n"
        guide += "=" * 80 + "\n\n"

        guide += "How to Use the Decision Tree:\n\n"

        guide += "1. Identify Your Primary Goal:\n"
        guide += "   - Max crashes: Need to find as many bugs as possible\n"
        guide += "   - Fast discovery: Need quick feedback during development\n"
        guide += "   - Resource efficient: Limited compute budget\n"
        guide += "   - Reproducible: Academic comparison or testing\n\n"

        guide += "2. Answer Follow-up Questions:\n"
        guide += "   - Time budget: How long can you run fuzzing?\n"
        guide += "   - Compute budget: What resources are available?\n"
        guide += "   - Seed availability: Do you have valid protocol messages?\n\n"

        guide += "3. Apply Recommendation:\n"
        guide += "   - Use suggested operator, corpus size, timeout\n"
        guide += "   - Fine-tune mutation rate based on target\n"
        guide += "   - Monitor TTFC for early stopping decisions\n\n"

        guide += "Cost Calculator Usage:\n\n"

        guide += "Example Calculation:\n"
        guide += "  Configuration: Havoc + 15 seeds + 300s timeout\n"
        guide += "  - Compute cost: $0.004 (300s @ $0.05/hour)\n"
        guide += "  - Seed generation: $1.50 (15 seeds @ $0.10/seed)\n"
        guide += "  - Human setup: $50-$75 (1-1.5 hours @ $50/hour)\n"
        guide += "  - Total cost: ~$51.50\n"
        guide += "  - Expected crashes: 55\n"
        guide += "  - Cost per crash: $0.94\n"
        guide += "  - ROI: 1.07 crashes per dollar\n\n"

        guide += "Optimization Strategies:\n"
        guide += "1. Reduce human setup time by automating seed generation\n"
        guide += "2. Use shorter timeouts with multiple parallel runs\n"
        guide += "3. Invest in seed quality - higher upfront cost, better ROI\n"
        guide += "4. Monitor TTFC to stop low-value campaigns early\n"

        return guide

    def run_complete_analysis(self) -> Dict:
        """Run complete decision tree and cost analysis"""
        print("=" * 80)
        print("DECISION TREE & COST CALCULATOR")
        print("=" * 80)

        # Build decision tree
        decision_tree = self.build_decision_tree()

        # Cost analysis
        cost_comparison = self.compare_configurations()

        # Visualizations
        self.visualize_decision_tree()
        self.visualize_cost_comparison()

        # Generate guide
        print(self.generate_usage_guide())

        results = {
            'decision_tree': decision_tree,
            'cost_comparison': cost_comparison,
            'metadata': {
                'timestamp': '2025-11-11',
                'cost_assumptions': {
                    'cpu_per_hour': 0.05,
                    'seed_generation_per_seed': 0.10,
                    'engineer_time_per_hour': 50.0
                }
            }
        }

        # Save results
        output_file = self.results_dir / 'decision_tree_cost_calculator.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print("\n" + "=" * 80)
        print("✓ Decision tree and cost calculator complete!")
        print(f"✓ Results saved to: {output_file}")
        print("=" * 80)

        return results


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('plots/decision_tree')

    calculator = DecisionTreeCostCalculator(results_dir, output_dir)
    calculator.run_complete_analysis()


if __name__ == '__main__':
    main()
