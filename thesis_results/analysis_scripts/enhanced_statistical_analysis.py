#!/usr/bin/env python3
"""
Enhanced Statistical Analysis for Thesis Results
Adds Cohen's d effect sizes, p-values, and comprehensive statistical testing
"""

import json
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from scipy import stats


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)


class EnhancedStatisticalAnalyzer:
    """Enhanced statistical analysis with effect sizes and significance testing"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir

    def calculate_cohens_d(self, group1: List[float], group2: List[float]) -> Dict:
        """
        Calculate Cohen's d effect size

        Interpretation:
        - |d| < 0.2: negligible
        - 0.2 <= |d| < 0.5: small
        - 0.5 <= |d| < 0.8: medium
        - |d| >= 0.8: large
        """
        if not group1 or not group2:
            return {'d': None, 'interpretation': 'insufficient_data'}

        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)

        n1, n2 = len(group1), len(group2)

        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return {'d': None, 'interpretation': 'zero_variance'}

        d = (mean1 - mean2) / pooled_std

        # Interpret effect size
        abs_d = abs(d)
        if abs_d < 0.2:
            interpretation = 'negligible'
        elif abs_d < 0.5:
            interpretation = 'small'
        elif abs_d < 0.8:
            interpretation = 'medium'
        else:
            interpretation = 'large'

        return {
            'd': d,
            'abs_d': abs_d,
            'interpretation': interpretation,
            'pooled_std': pooled_std,
            'mean_diff': mean1 - mean2
        }

    def perform_t_test(self, group1: List[float], group2: List[float]) -> Dict:
        """
        Perform independent samples t-test
        Returns t-statistic, p-value, and significance
        """
        if not group1 or not group2 or len(group1) < 2 or len(group2) < 2:
            return {
                't_statistic': None,
                'p_value': None,
                'significant_005': None,
                'significant_001': None
            }

        t_stat, p_value = stats.ttest_ind(group1, group2)

        return {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant_005': p_value < 0.05,
            'significant_001': p_value < 0.01,
            'df': len(group1) + len(group2) - 2
        }

    def calculate_confidence_interval(
        self,
        data: List[float],
        confidence: float = 0.95
    ) -> Dict:
        """Calculate confidence interval using t-distribution"""
        if not data or len(data) < 2:
            return {'lower': None, 'upper': None, 'margin': None}

        n = len(data)
        mean = np.mean(data)
        se = stats.sem(data)
        margin = se * stats.t.ppf((1 + confidence) / 2, n - 1)

        return {
            'mean': float(mean),
            'lower': float(mean - margin),
            'upper': float(mean + margin),
            'margin': float(margin),
            'confidence': confidence
        }

    def analyze_seed_sensitivity_enhanced(self) -> Dict:
        """Enhanced analysis of seed sensitivity results"""
        print("\n1. Enhanced Seed Sensitivity Analysis...")

        results_file = self.results_dir / 'seed_sensitivity' / 'seed_sensitivity_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found")
            return {}

        with open(results_file) as f:
            data = json.load(f)

        # Extract configuration data
        configs = data.get('configurations', [])

        # Find baseline (empty corpus)
        baseline_config = None
        for config in configs:
            if config['corpus_type'] == 'empty':
                baseline_config = config
                break

        if not baseline_config:
            print("   ⚠ Baseline configuration not found")
            return {}

        # Extract baseline metrics
        baseline_crashes = [trial['unique_crashes'] for trial in baseline_config['trials']]
        baseline_ttfc = [trial['time_to_first_crash'] for trial in baseline_config['trials']]
        baseline_coverage = [trial['coverage'] for trial in baseline_config['trials']]

        # Analyze each configuration vs baseline
        comparisons = []

        for config in configs:
            if config['corpus_type'] == 'empty':
                continue

            config_crashes = [trial['unique_crashes'] for trial in config['trials']]
            config_ttfc = [trial['time_to_first_crash'] for trial in config['trials']]
            config_coverage = [trial['coverage'] for trial in config['trials']]

            comparison = {
                'corpus_type': config['corpus_type'],
                'corpus_size': config['corpus_size'],
                'crashes': {
                    'cohens_d': self.calculate_cohens_d(config_crashes, baseline_crashes),
                    't_test': self.perform_t_test(config_crashes, baseline_crashes),
                    'ci_95': self.calculate_confidence_interval(config_crashes)
                },
                'ttfc': {
                    'cohens_d': self.calculate_cohens_d(baseline_ttfc, config_ttfc),  # Reversed: lower is better
                    't_test': self.perform_t_test(baseline_ttfc, config_ttfc),
                    'ci_95': self.calculate_confidence_interval(config_ttfc)
                },
                'coverage': {
                    'cohens_d': self.calculate_cohens_d(config_coverage, baseline_coverage),
                    't_test': self.perform_t_test(config_coverage, baseline_coverage),
                    'ci_95': self.calculate_confidence_interval(config_coverage)
                }
            }

            comparisons.append(comparison)

        # Summary
        summary = {
            'baseline': {
                'corpus_type': baseline_config['corpus_type'],
                'crashes_mean': float(np.mean(baseline_crashes)),
                'ttfc_mean': float(np.mean(baseline_ttfc)),
                'coverage_mean': float(np.mean(baseline_coverage))
            },
            'comparisons': comparisons,
            'best_configurations': {
                'crashes': max(comparisons, key=lambda x: x['crashes']['ci_95'].get('mean', 0)),
                'ttfc': min(comparisons, key=lambda x: x['ttfc']['ci_95'].get('mean', 999999)),
                'coverage': max(comparisons, key=lambda x: x['coverage']['ci_95'].get('mean', 0))
            }
        }

        print(f"   ✓ Analyzed {len(comparisons)} configurations vs baseline")
        print(f"   ✓ Best for crashes: {summary['best_configurations']['crashes']['corpus_type']} "
              f"({summary['best_configurations']['crashes']['corpus_size']} seeds)")

        return summary

    def analyze_payload_complexity_enhanced(self) -> Dict:
        """Enhanced analysis of payload complexity"""
        print("\n2. Enhanced Payload Complexity Analysis...")

        results_file = self.results_dir / 'payload_complexity' / 'payload_complexity_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found")
            return {}

        with open(results_file) as f:
            data = json.load(f)

        # Extract payload data
        crash_payloads = []
        non_crash_payloads = []

        for trial in data.get('trials', []):
            crash_payloads.extend(trial.get('crash_payloads', []))
            non_crash_payloads.extend(trial.get('non_crash_sample', []))

        if not crash_payloads or not non_crash_payloads:
            print("   ⚠ Insufficient payload data")
            return {}

        # Analyze each metric
        metrics = ['size', 'entropy', 'unique_bytes', 'zeros_percent',
                   'high_bytes_percent', 'sequential_runs', 'boundary_values']

        metric_analysis = {}

        for metric in metrics:
            crash_values = [p[metric] for p in crash_payloads if metric in p]
            non_crash_values = [p[metric] for p in non_crash_payloads if metric in p]

            if crash_values and non_crash_values:
                metric_analysis[metric] = {
                    'crash_stats': {
                        'mean': float(np.mean(crash_values)),
                        'std': float(np.std(crash_values)),
                        'median': float(np.median(crash_values)),
                        'ci_95': self.calculate_confidence_interval(crash_values)
                    },
                    'non_crash_stats': {
                        'mean': float(np.mean(non_crash_values)),
                        'std': float(np.std(non_crash_values)),
                        'median': float(np.median(non_crash_values)),
                        'ci_95': self.calculate_confidence_interval(non_crash_values)
                    },
                    'cohens_d': self.calculate_cohens_d(crash_values, non_crash_values),
                    't_test': self.perform_t_test(crash_values, non_crash_values)
                }

        # Find most discriminative metrics
        discriminative_metrics = sorted(
            [(m, data['cohens_d']['abs_d']) for m, data in metric_analysis.items()
             if data['cohens_d']['abs_d'] is not None],
            key=lambda x: x[1],
            reverse=True
        )

        summary = {
            'total_crash_payloads': len(crash_payloads),
            'total_non_crash_payloads': len(non_crash_payloads),
            'metric_analysis': metric_analysis,
            'most_discriminative_metrics': [
                {'metric': m, 'effect_size': d, 'interpretation': metric_analysis[m]['cohens_d']['interpretation']}
                for m, d in discriminative_metrics[:5]
            ]
        }

        print(f"   ✓ Analyzed {len(crash_payloads)} crash payloads vs {len(non_crash_payloads)} non-crash")
        print(f"   ✓ Most discriminative: {discriminative_metrics[0][0]} (d={discriminative_metrics[0][1]:.3f})")

        return summary

    def analyze_reproducibility_enhanced(self) -> Dict:
        """Enhanced reproducibility analysis"""
        print("\n3. Enhanced Reproducibility Analysis...")

        results_file = self.results_dir / 'reproducibility' / 'reproducibility_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found")
            return {}

        with open(results_file) as f:
            data = json.load(f)

        # Analyze fixed seed reproducibility
        fixed_seed_tests = [t for t in data.get('tests', []) if t.get('test_type') == 'fixed_seed']
        natural_variance_tests = [t for t in data.get('tests', []) if t.get('test_type') == 'natural_variance']

        analysis = {}

        # Fixed seed analysis
        if fixed_seed_tests:
            for test in fixed_seed_tests:
                runs = test.get('runs', [])
                crashes = [r['unique_crashes'] for r in runs]
                coverage = [r['coverage'] for r in runs]

                analysis['fixed_seed'] = {
                    'random_seed': test.get('random_seed'),
                    'crashes': {
                        'values': crashes,
                        'cv': float(np.std(crashes) / np.mean(crashes)) if np.mean(crashes) > 0 else 0,
                        'range': float(max(crashes) - min(crashes)),
                        'perfect_reproducibility': len(set(crashes)) == 1
                    },
                    'coverage': {
                        'values': coverage,
                        'cv': float(np.std(coverage) / np.mean(coverage)) if np.mean(coverage) > 0 else 0,
                        'range': float(max(coverage) - min(coverage)),
                        'perfect_reproducibility': len(set(coverage)) == 1
                    }
                }

        # Natural variance analysis
        if natural_variance_tests:
            for test in natural_variance_tests:
                runs = test.get('runs', [])
                crashes = [r['unique_crashes'] for r in runs]
                coverage = [r['coverage'] for r in runs]

                analysis['natural_variance'] = {
                    'crashes': {
                        'mean': float(np.mean(crashes)),
                        'std': float(np.std(crashes)),
                        'cv': float(np.std(crashes) / np.mean(crashes)) if np.mean(crashes) > 0 else 0,
                        'ci_95': self.calculate_confidence_interval(crashes),
                        'acceptable': float(np.std(crashes) / np.mean(crashes)) < 0.15  # CV < 15%
                    },
                    'coverage': {
                        'mean': float(np.mean(coverage)),
                        'std': float(np.std(coverage)),
                        'cv': float(np.std(coverage) / np.mean(coverage)) if np.mean(coverage) > 0 else 0,
                        'ci_95': self.calculate_confidence_interval(coverage),
                        'acceptable': float(np.std(coverage) / np.mean(coverage)) < 0.15
                    }
                }

        print(f"   ✓ Fixed seed CV: {analysis.get('fixed_seed', {}).get('crashes', {}).get('cv', 0):.4f}")
        print(f"   ✓ Natural variance CV: {analysis.get('natural_variance', {}).get('crashes', {}).get('cv', 0):.4f}")

        return analysis

    def analyze_mutation_ablation_enhanced(self) -> Dict:
        """Enhanced mutation ablation analysis"""
        print("\n4. Enhanced Mutation Ablation Analysis...")

        results_file = self.results_dir / 'mutation_ablation' / 'mutation_ablation_results.json'

        if not results_file.exists():
            print("   ⚠ Results file not found")
            return {}

        with open(results_file) as f:
            data = json.load(f)

        # Try both data structures
        operators = data.get('operators', [])
        if not operators:
            operator_results = data.get('operator_results', [])
            if not operator_results:
                print("   ⚠ No operator data found")
                return {}
            # Convert operator_results format to operators format
            operators = [
                {
                    'operator': op.get('operator_name', op.get('operator', 'unknown')),
                    'trials': op.get('trials', []),
                    'aggregate': op.get('aggregate', {})
                }
                for op in operator_results
            ]

        if len(operators) < 2:
            print("   ⚠ Insufficient operators for comparison")
            return {}

        # Find best operator (reference)
        best_operator = max(operators, key=lambda x: x['aggregate']['unique_crashes']['mean'])

        # Compare all operators to best
        comparisons = []

        for op in operators:
            if op['operator'] == best_operator['operator']:
                continue

            # Use aggregate data since trials are empty
            best_crashes_mean = best_operator['aggregate']['unique_crashes']['mean']
            op_crashes_mean = op['aggregate']['unique_crashes']['mean']

            best_coverage_mean = best_operator['aggregate']['coverage']['mean']
            op_coverage_mean = op['aggregate']['coverage']['mean']

            # Calculate relative differences
            crashes_diff_percent = ((op_crashes_mean - best_crashes_mean) / best_crashes_mean * 100)
            coverage_diff_percent = ((op_coverage_mean - best_coverage_mean) / best_coverage_mean * 100)

            comparison = {
                'operator': op['operator'],
                'crashes': {
                    'mean': float(op_crashes_mean),
                    'vs_best_diff_percent': float(crashes_diff_percent),
                    'cv_percent': op['aggregate']['unique_crashes'].get('cv_percent', 0)
                },
                'coverage': {
                    'mean': float(op_coverage_mean),
                    'vs_best_diff_percent': float(coverage_diff_percent),
                    'cv_percent': op['aggregate']['coverage'].get('cv_percent', 0)
                },
                'efficiency': {
                    'crashes_per_1k': op['aggregate'].get('crashes_per_1k_execs', {}).get('mean', 0)
                }
            }

            comparisons.append(comparison)

        # Group operators by effectiveness
        summary = {
            'best_operator': {
                'name': best_operator['operator'],
                'crashes_mean': float(best_operator['aggregate']['unique_crashes']['mean']),
                'coverage_mean': float(best_operator['aggregate']['coverage']['mean']),
                'efficiency': float(best_operator['aggregate'].get('crashes_per_1k_execs', {}).get('mean', 0))
            },
            'comparisons': comparisons,
            'tier_1_operators': [
                comp['operator'] for comp in comparisons
                if comp['crashes']['vs_best_diff_percent'] > -20
            ],  # Within 20% of best
            'tier_2_operators': [
                comp['operator'] for comp in comparisons
                if -50 < comp['crashes']['vs_best_diff_percent'] <= -20
            ],  # 20-50% below best
            'tier_3_operators': [
                comp['operator'] for comp in comparisons
                if comp['crashes']['vs_best_diff_percent'] <= -50
            ]  # More than 50% below best
        }

        print(f"   ✓ Best operator: {summary['best_operator']['name']}")
        print(f"   ✓ Tier 1 (competitive): {len(summary['tier_1_operators'])} operators")
        print(f"   ✓ Tier 2 (moderate): {len(summary['tier_2_operators'])} operators")
        print(f"   ✓ Tier 3 (poor): {len(summary['tier_3_operators'])} operators")

        return summary

    def run_complete_analysis(self) -> Dict:
        """Run complete enhanced statistical analysis"""
        print("=" * 80)
        print("ENHANCED STATISTICAL ANALYSIS")
        print("=" * 80)

        analysis = {
            'analysis_date': '2025-11-11',
            'seed_sensitivity': self.analyze_seed_sensitivity_enhanced(),
            'payload_complexity': self.analyze_payload_complexity_enhanced(),
            'reproducibility': self.analyze_reproducibility_enhanced(),
            'mutation_ablation': self.analyze_mutation_ablation_enhanced()
        }

        # Save results
        output_file = self.results_dir / 'enhanced_statistical_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, cls=NumpyEncoder)

        print("\n" + "=" * 80)
        print(f"✓ Enhanced statistical analysis complete!")
        print(f"✓ Results saved to: {output_file}")
        print("=" * 80)

        return analysis


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    analyzer = EnhancedStatisticalAnalyzer(results_dir)
    analyzer.run_complete_analysis()


if __name__ == '__main__':
    main()
