#!/usr/bin/env python3
"""
Results Analysis Script
Analyze and aggregate all test results for thesis
"""

import json
import statistics
from pathlib import Path
from typing import Dict, List
import sys


class ResultsAnalyzer:
    """Analyze thesis test results"""

    def __init__(self, results_dir: Path):
        self.results_dir = results_dir

    def load_json(self, filepath: Path) -> Dict:
        """Load JSON results file"""
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return {}

        with open(filepath, 'r') as f:
            return json.load(f)

    def analyze_modbus_results(self) -> Dict:
        """Analyze Modbus test results"""
        print("\nAnalyzing Modbus results...")

        validity_file = self.results_dir / "modbus_validity" / "modbus_validity_results.json"
        state_file = self.results_dir / "modbus_validity" / "modbus_state_progress.json"
        fuzzing_file = self.results_dir / "modbus_fuzzing" / "modbus_fuzzing_results.json"

        validity_data = self.load_json(validity_file)
        state_data = self.load_json(state_file)
        fuzzing_data = self.load_json(fuzzing_file)

        analysis = {
            'validity': {
                'PSR': validity_data.get('PSR', 0),
                'EXR': validity_data.get('EXR', 0),
                'mean_latency_ms': validity_data.get('latency_stats', {}).get('mean_ms', 0)
            },
            'state_coverage': {
                'unique_states': state_data.get('unique_states', 0),
                'fc_address_combinations': len(state_data.get('fc_address_coverage', []))
            },
            'fuzzing': {
                'mean_execs_per_trial': fuzzing_data.get('aggregate', {}).get('execs', {}).get('mean', 0),
                'mean_unique_crashes': fuzzing_data.get('aggregate', {}).get('unique_crashes', {}).get('mean', 0),
                'mean_throughput': fuzzing_data.get('aggregate', {}).get('throughput_exec_per_sec', {}).get('mean', 0)
            }
        }

        return analysis

    def analyze_coap_results(self) -> Dict:
        """Analyze CoAP test results"""
        print("\nAnalyzing CoAP results...")

        validity_file = self.results_dir / "coap_validity" / "coap_validity_results.json"
        fuzzing_file = self.results_dir / "coap_fuzzing" / "coap_fuzzing_results.json"

        validity_data = self.load_json(validity_file)
        fuzzing_data = self.load_json(fuzzing_file)

        analysis = {
            'coherence_no_dtls': {
                'ack_ratio': validity_data.get('coherence_no_dtls', {}).get('ack_ratio', 0),
                'token_coherence': validity_data.get('coherence_no_dtls', {}).get('token_coherence_rate', 0)
            },
            'coherence_with_dtls': {
                'ack_ratio': validity_data.get('coherence_with_dtls', {}).get('ack_ratio', 0),
                'token_coherence': validity_data.get('coherence_with_dtls', {}).get('token_coherence_rate', 0)
            },
            'milestones_no_dtls': {
                'observe_registrations': validity_data.get('milestones_no_dtls', {}).get('observe', {}).get('registration_success', 0),
                'block1_completions': validity_data.get('milestones_no_dtls', {}).get('blockwise', {}).get('block1_completions', 0)
            },
            'milestones_with_dtls': {
                'observe_registrations': validity_data.get('milestones_with_dtls', {}).get('observe', {}).get('registration_success', 0),
                'block1_completions': validity_data.get('milestones_with_dtls', {}).get('blockwise', {}).get('block1_completions', 0)
            },
            'dtls_overhead': fuzzing_data.get('comparison', {}).get('dtls_overhead_percent', 0)
        }

        return analysis

    def analyze_baseline_comparison(self) -> Dict:
        """Analyze baseline comparison results"""
        print("\nAnalyzing baseline comparisons...")

        comparison_file = self.results_dir / "baseline_comparison" / "baseline_comparison_results.json"
        comparison_data = self.load_json(comparison_file)

        analysis = {
            'modbus': {},
            'coap': {}
        }

        for target in ['modbus', 'coap']:
            target_data = comparison_data.get(target, {})
            effects = target_data.get('effect_sizes', {})

            analysis[target] = {
                'effect_sizes': effects,
                'fuzzer_rankings': self._rank_fuzzers(target_data.get('results', {}))
            }

        return analysis

    def _rank_fuzzers(self, results: Dict) -> List[Dict]:
        """Rank fuzzers by performance"""
        fuzzer_results = results.get('fuzzer_results', {})

        rankings = []
        for fuzzer_name, data in fuzzer_results.items():
            aggregate = data.get('aggregate', {})
            rankings.append({
                'fuzzer': fuzzer_name,
                'mean_crashes': aggregate.get('unique_crashes', {}).get('mean', 0),
                'mean_coverage': aggregate.get('coverage', {}).get('mean', 0),
                'mean_execs': aggregate.get('execs', {}).get('mean', 0)
            })

        # Sort by crashes (descending)
        rankings.sort(key=lambda x: x['mean_crashes'], reverse=True)

        return rankings

    def generate_summary_table(self, modbus_analysis: Dict, coap_analysis: Dict, baseline_analysis: Dict) -> str:
        """Generate summary table for thesis"""
        table = []
        table.append("=" * 80)
        table.append("THESIS RESULTS SUMMARY")
        table.append("=" * 80)

        # Modbus Summary
        table.append("\nMODBUS/TCP RESULTS:")
        table.append("-" * 80)
        table.append(f"  Protocol Success Rate (PSR): {modbus_analysis['validity']['PSR']:.2%}")
        table.append(f"  Exception Rate (EXR): {modbus_analysis['validity']['EXR']:.2%}")
        table.append(f"  Mean Latency: {modbus_analysis['validity']['mean_latency_ms']:.2f} ms")
        table.append(f"  Unique States Discovered: {modbus_analysis['state_coverage']['unique_states']}")
        table.append(f"  Mean Unique Crashes: {modbus_analysis['fuzzing']['mean_unique_crashes']:.1f}")
        table.append(f"  Mean Throughput: {modbus_analysis['fuzzing']['mean_throughput']:.1f} exec/s")

        # CoAP Summary
        table.append("\nCoAP RESULTS:")
        table.append("-" * 80)
        table.append("  WITHOUT DTLS:")
        table.append(f"    ACK Ratio: {coap_analysis['coherence_no_dtls']['ack_ratio']:.2%}")
        table.append(f"    Token Coherence: {coap_analysis['coherence_no_dtls']['token_coherence']:.2%}")
        table.append(f"    Observe Registrations: {coap_analysis['milestones_no_dtls']['observe_registrations']}")
        table.append("  WITH DTLS:")
        table.append(f"    ACK Ratio: {coap_analysis['coherence_with_dtls']['ack_ratio']:.2%}")
        table.append(f"    Token Coherence: {coap_analysis['coherence_with_dtls']['token_coherence']:.2%}")
        table.append(f"    Observe Registrations: {coap_analysis['milestones_with_dtls']['observe_registrations']}")
        table.append(f"  DTLS Overhead: {coap_analysis['dtls_overhead']:.1f}%")

        # Baseline Comparison
        table.append("\nBASELINE COMPARISON (vs AFL):")
        table.append("-" * 80)
        for target in ['modbus', 'coap']:
            table.append(f"\n  {target.upper()}:")
            effects = baseline_analysis[target]['effect_sizes']
            for metric, data in effects.items():
                if data:
                    table.append(f"    {metric}: {data['improvement_percent']:+.1f}%")

            # Fuzzer rankings
            table.append(f"\n  Fuzzer Rankings (by crashes):")
            for i, fuzzer in enumerate(baseline_analysis[target]['fuzzer_rankings'], 1):
                table.append(f"    {i}. {fuzzer['fuzzer']}: {fuzzer['mean_crashes']:.1f} crashes")

        table.append("\n" + "=" * 80)

        return "\n".join(table)

    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 80)
        print("THESIS RESULTS ANALYSIS")
        print("=" * 80)

        # Analyze all components
        modbus_analysis = self.analyze_modbus_results()
        coap_analysis = self.analyze_coap_results()
        baseline_analysis = self.analyze_baseline_comparison()

        # Generate summary
        summary = self.generate_summary_table(modbus_analysis, coap_analysis, baseline_analysis)

        # Save analysis
        output_data = {
            'modbus': modbus_analysis,
            'coap': coap_analysis,
            'baseline': baseline_analysis
        }

        output_file = self.results_dir / "analysis_summary.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✓ Analysis saved to: {output_file}")

        # Save text summary
        summary_file = self.results_dir / "summary.txt"
        with open(summary_file, 'w') as f:
            f.write(summary)

        print(f"✓ Summary saved to: {summary_file}")

        # Print summary
        print(f"\n{summary}")


def main():
    results_dir = Path(__file__).parent.parent / "results_data"

    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        print("Please run the test scripts first to generate results.")
        sys.exit(1)

    analyzer = ResultsAnalyzer(results_dir)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
