#!/usr/bin/env python3
"""
Statistical Analysis Script
Calculate confidence intervals, effect sizes, and statistical significance
"""

import json
import statistics
import math
from pathlib import Path
from typing import Dict, List, Tuple


class StatisticalAnalyzer:
    """Statistical analysis for thesis results"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir

    def calculate_confidence_interval(
        self,
        data: List[float],
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate confidence interval"""
        if len(data) < 2:
            return (0, 0)

        mean = statistics.mean(data)
        stdev = statistics.stdev(data)
        n = len(data)

        # t-distribution critical value (approximation for n > 30)
        if n > 30:
            z = 1.96  # 95% confidence
        else:
            # Simplified t-values
            t_values = {3: 4.303, 5: 2.776, 10: 2.262, 20: 2.093, 30: 2.042}
            z = t_values.get(n, 2.0)

        margin = z * (stdev / math.sqrt(n))
        return (mean - margin, mean + margin)

    def cohens_d(
        self,
        group1: List[float],
        group2: List[float]
    ) -> float:
        """Calculate Cohen's d effect size"""
        if len(group1) < 2 or len(group2) < 2:
            return 0.0

        mean1 = statistics.mean(group1)
        mean2 = statistics.mean(group2)
        std1 = statistics.stdev(group1)
        std2 = statistics.stdev(group2)
        n1 = len(group1)
        n2 = len(group2)

        # Pooled standard deviation
        pooled_std = math.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))

        if pooled_std == 0:
            return 0.0

        return (mean1 - mean2) / pooled_std

    def interpret_effect_size(self, d: float) -> str:
        """Interpret Cohen's d"""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        elif abs_d < 1.2:
            return "large"
        else:
            return "very large"

    def analyze_modbus_extended(self) -> Dict:
        """Analyze extended Modbus results"""
        file_path = self.results_dir / "modbus_extended" / "modbus_extended_results.json"

        if not file_path.exists():
            return {}

        with open(file_path) as f:
            data = json.load(f)

        analysis = {
            'configurations': []
        }

        for config in data['configurations']:
            # Extract crash data from trials
            crash_counts = []
            exec_counts = []
            throughput_values = []

            for trial in config['trials']:
                crash_counts.append(len(trial['unique_crashes']))
                exec_counts.append(trial['total_execs'])
                if 'throughput_stats' in trial:
                    throughput_values.append(trial['throughput_stats']['mean_exec_per_sec'])

            # Calculate confidence intervals
            crash_ci = self.calculate_confidence_interval(crash_counts)
            exec_ci = self.calculate_confidence_interval(exec_counts)
            throughput_ci = self.calculate_confidence_interval(throughput_values) if throughput_values else (0, 0)

            config_analysis = {
                'config_name': config['config_name'],
                'mutation_level': config['mutation_level'],
                'crashes': {
                    'mean': config['aggregate']['unique_crashes']['mean'],
                    'ci_95': crash_ci,
                    'cv': config['aggregate']['unique_crashes'].get('cv', 0)
                },
                'executions': {
                    'mean': config['aggregate']['execs']['mean'],
                    'ci_95': exec_ci,
                    'cv': config['aggregate']['execs'].get('cv', 0)
                },
                'throughput': {
                    'mean': config['aggregate']['throughput']['mean'],
                    'ci_95': throughput_ci
                }
            }

            analysis['configurations'].append(config_analysis)

        # Compare mutation levels
        low_crashes = []
        medium_crashes = []
        aggressive_crashes = []

        for config in data['configurations']:
            if config['mutation_level'] == 'low' and config['duration_seconds'] == 60:
                for trial in config['trials']:
                    low_crashes.append(len(trial['unique_crashes']))
            elif config['mutation_level'] == 'medium' and config['duration_seconds'] == 60:
                for trial in config['trials']:
                    medium_crashes.append(len(trial['unique_crashes']))
            elif config['mutation_level'] == 'aggressive' and config['duration_seconds'] == 60:
                for trial in config['trials']:
                    aggressive_crashes.append(len(trial['unique_crashes']))

        if low_crashes and aggressive_crashes:
            analysis['mutation_comparison'] = {
                'low_vs_aggressive': {
                    'cohens_d': self.cohens_d(aggressive_crashes, low_crashes),
                    'interpretation': self.interpret_effect_size(self.cohens_d(aggressive_crashes, low_crashes)),
                    'low_mean': statistics.mean(low_crashes),
                    'aggressive_mean': statistics.mean(aggressive_crashes),
                    'improvement_percent': ((statistics.mean(aggressive_crashes) - statistics.mean(low_crashes)) / statistics.mean(low_crashes) * 100)
                }
            }

        return analysis

    def analyze_coap_extended(self) -> Dict:
        """Analyze extended CoAP results"""
        file_path = self.results_dir / "coap_extended" / "coap_extended_results.json"

        if not file_path.exists():
            return {}

        with open(file_path) as f:
            data = json.load(f)

        analysis = {
            'test_modes': []
        }

        for mode in data['test_modes']:
            crash_counts = []
            exec_counts = []

            for trial in mode['trials']:
                crash_counts.append(len(trial['unique_crashes']))
                exec_counts.append(trial['total_execs'])

            crash_ci = self.calculate_confidence_interval(crash_counts)
            exec_ci = self.calculate_confidence_interval(exec_counts)

            mode_analysis = {
                'test_mode': mode['test_mode'],
                'dtls_enabled': mode['dtls_enabled'],
                'crashes': {
                    'mean': mode['aggregate']['crashes']['mean'],
                    'ci_95': crash_ci
                },
                'executions': {
                    'mean': mode['aggregate']['execs']['mean'],
                    'ci_95': exec_ci
                },
                'throughput': {
                    'mean': mode['aggregate']['throughput']['mean']
                }
            }

            analysis['test_modes'].append(mode_analysis)

        # Compare DTLS impact
        normal_no_dtls = next((m for m in data['test_modes'] if m['test_mode'] == 'normal' and not m['dtls_enabled']), None)
        normal_with_dtls = next((m for m in data['test_modes'] if m['test_mode'] == 'normal' and m['dtls_enabled']), None)

        if normal_no_dtls and normal_with_dtls:
            no_dtls_execs = [t['total_execs'] for t in normal_no_dtls['trials']]
            with_dtls_execs = [t['total_execs'] for t in normal_with_dtls['trials']]

            analysis['dtls_impact'] = {
                'cohens_d': self.cohens_d(no_dtls_execs, with_dtls_execs),
                'interpretation': self.interpret_effect_size(self.cohens_d(no_dtls_execs, with_dtls_execs)),
                'no_dtls_mean': statistics.mean(no_dtls_execs),
                'with_dtls_mean': statistics.mean(with_dtls_execs),
                'overhead_percent': ((statistics.mean(no_dtls_execs) - statistics.mean(with_dtls_execs)) / statistics.mean(no_dtls_execs) * 100)
            }

        return analysis

    def generate_report(self):
        """Generate statistical analysis report"""
        print("=" * 70)
        print("STATISTICAL ANALYSIS REPORT")
        print("=" * 70)

        # Modbus analysis
        print("\n1. MODBUS EXTENDED ANALYSIS")
        print("-" * 70)

        modbus_analysis = self.analyze_modbus_extended()

        if modbus_analysis:
            for config in modbus_analysis['configurations']:
                print(f"\n{config['config_name']}:")
                print(f"  Crashes: {config['crashes']['mean']:.1f} "
                      f"[95% CI: {config['crashes']['ci_95'][0]:.1f}, {config['crashes']['ci_95'][1]:.1f}]")
                print(f"  CV: {config['crashes']['cv']:.1%}")
                print(f"  Executions: {config['executions']['mean']:.0f} "
                      f"[95% CI: {config['executions']['ci_95'][0]:.0f}, {config['executions']['ci_95'][1]:.0f}]")

            if 'mutation_comparison' in modbus_analysis:
                comp = modbus_analysis['mutation_comparison']['low_vs_aggressive']
                print(f"\nMutation Level Comparison (Low vs Aggressive):")
                print(f"  Cohen's d: {comp['cohens_d']:.3f} ({comp['interpretation']})")
                print(f"  Improvement: {comp['improvement_percent']:+.1f}%")
                print(f"  Low mean: {comp['low_mean']:.1f} crashes")
                print(f"  Aggressive mean: {comp['aggressive_mean']:.1f} crashes")

        # CoAP analysis
        print("\n2. CoAP EXTENDED ANALYSIS")
        print("-" * 70)

        coap_analysis = self.analyze_coap_extended()

        if coap_analysis:
            for mode in coap_analysis['test_modes']:
                dtls_str = "DTLS" if mode['dtls_enabled'] else "Plain"
                print(f"\n{mode['test_mode']} ({dtls_str}):")
                print(f"  Crashes: {mode['crashes']['mean']:.1f} "
                      f"[95% CI: {mode['crashes']['ci_95'][0]:.1f}, {mode['crashes']['ci_95'][1]:.1f}]")
                print(f"  Executions: {mode['executions']['mean']:.0f} "
                      f"[95% CI: {mode['executions']['ci_95'][0]:.0f}, {mode['executions']['ci_95'][1]:.0f}]")

            if 'dtls_impact' in coap_analysis:
                dtls = coap_analysis['dtls_impact']
                print(f"\nDTLS Impact Analysis:")
                print(f"  Cohen's d: {dtls['cohens_d']:.3f} ({dtls['interpretation']})")
                print(f"  Overhead: {dtls['overhead_percent']:.1f}%")
                print(f"  No DTLS mean: {dtls['no_dtls_mean']:.0f} execs")
                print(f"  With DTLS mean: {dtls['with_dtls_mean']:.0f} execs")

        # Save analysis
        all_analysis = {
            'modbus_extended': modbus_analysis,
            'coap_extended': coap_analysis
        }

        output_file = self.results_dir / "statistical_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(all_analysis, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Statistical analysis saved to: {output_file}")
        print(f"{'=' * 70}")


def main():
    results_dir = Path(__file__).parent.parent / "results_data"
    analyzer = StatisticalAnalyzer(results_dir)
    analyzer.generate_report()


if __name__ == "__main__":
    main()
