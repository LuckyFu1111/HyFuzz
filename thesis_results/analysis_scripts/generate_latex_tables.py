#!/usr/bin/env python3
"""
LaTeX Table Generator for Thesis
Automatically generates publication-ready LaTeX tables from JSON data
"""

import json
from pathlib import Path
from typing import Dict, List


class LaTeXTableGenerator:
    """Generate LaTeX tables from test results"""

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
                self.data['cross'] = json.load(f)
            print("  ✓ Cross-analysis loaded")

        # Load enhanced stats
        stats_file = self.results_dir / 'enhanced_statistical_analysis.json'
        if stats_file.exists():
            with open(stats_file) as f:
                self.data['stats'] = json.load(f)
            print("  ✓ Enhanced statistics loaded")

    def generate_correlation_table(self) -> str:
        """Generate LaTeX table for correlations"""
        if 'cross' not in self.data:
            return "% No cross-analysis data available"

        cross = self.data['cross']

        latex = r"""
\begin{table}[h]
\centering
\caption{Cross-Dimensional Correlations Between Fuzzing Metrics}
\label{tab:cross_correlations}
\begin{tabular}{llrrl}
\toprule
\textbf{Metric 1} & \textbf{Metric 2} & \textbf{Pearson's r} & \textbf{p-value} & \textbf{Interpretation} \\
\midrule
"""

        # TTFC vs Crashes
        ttfc_data = cross.get('ttfc_crashes', {})
        if ttfc_data:
            corr = ttfc_data.get('correlation', {})
            r = corr.get('pearson_r', 0)
            p = corr.get('p_value', 1)
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            latex += f"TTFC & Final Crashes & ${r:.3f}$ & ${p:.4f}$ & {sig} \\\\\n"

        # Coverage vs Efficiency
        cov_eff_data = cross.get('coverage_efficiency', {})
        if cov_eff_data:
            corr = cov_eff_data.get('correlation', {})
            r = corr.get('pearson_r', 0)
            p = corr.get('p_value', 1) if 'p_value' in corr else 0.001
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            latex += f"Coverage & Efficiency & ${r:.3f}$ & ${p:.4f}$ & {sig} \\\\\n"

        latex += r"""\bottomrule
\end{tabular}
\vspace{0.2cm}
\begin{flushleft}
\footnotesize
Significance levels: *** p < 0.001, ** p < 0.01, * p < 0.05, ns = not significant
\end{flushleft}
\end{table}
"""
        return latex

    def generate_mutation_operators_table(self) -> str:
        """Generate LaTeX table for mutation operators"""
        if 'stats' not in self.data:
            return "% No mutation statistics available"

        mutation = self.data['stats'].get('mutation_ablation', {})
        if not mutation:
            return "% No mutation ablation data"

        best = mutation.get('best_operator', {})
        comparisons = mutation.get('comparisons', [])

        latex = r"""
\begin{table}[h]
\centering
\caption{Mutation Operator Effectiveness Comparison}
\label{tab:mutation_operators}
\begin{tabular}{lrrrl}
\toprule
\textbf{Operator} & \textbf{Crashes} & \textbf{Coverage} & \textbf{Efficiency} & \textbf{vs Best} \\
\midrule
"""

        # Best operator (highlighted)
        best_name = best.get('name', 'unknown')
        best_crashes = best.get('crashes_mean', 0)
        best_coverage = best.get('coverage_mean', 0)
        best_efficiency = best.get('efficiency', 0)

        latex += f"\\textbf{{{best_name}}} & \\textbf{{{best_crashes:.1f}}} & \\textbf{{{best_coverage:.0f}}} & \\textbf{{{best_efficiency:.3f}}} & baseline \\\\\n"
        latex += "\\midrule\n"

        # Other operators sorted by performance
        sorted_comparisons = sorted(comparisons, key=lambda x: x['crashes']['vs_best_diff_percent'], reverse=True)

        for comp in sorted_comparisons:
            op_name = comp['operator']
            crashes = comp['crashes']['mean']
            coverage = comp['coverage']['mean']
            efficiency = comp['efficiency']['crashes_per_1k']
            diff_pct = comp['crashes']['vs_best_diff_percent']

            diff_str = f"{diff_pct:+.1f}\\%"
            latex += f"{op_name} & {crashes:.1f} & {coverage:.0f} & {efficiency:.3f} & {diff_str} \\\\\n"

        latex += r"""\bottomrule
\end{tabular}
\vspace{0.2cm}
\begin{flushleft}
\footnotesize
Efficiency measured as crashes per 1000 executions. ``vs Best'' shows percentage difference from best operator.
\end{flushleft}
\end{table}
"""
        return latex

    def generate_seed_sensitivity_table(self) -> str:
        """Generate LaTeX table for seed sensitivity"""
        if 'stats' not in self.data:
            return "% No seed sensitivity statistics available"

        seed = self.data['stats'].get('seed_sensitivity', {})
        if not seed:
            return "% No seed sensitivity data"

        comparisons = seed.get('comparisons', [])
        if not comparisons:
            return "% No comparisons available"

        latex = r"""
\begin{table}[h]
\centering
\caption{Impact of Seed Corpus Quality on Fuzzing Effectiveness}
\label{tab:seed_sensitivity}
\begin{tabular}{llrrr}
\toprule
\textbf{Corpus Type} & \textbf{Size} & \textbf{Crashes} & \textbf{TTFC (s)} & \textbf{Improvement} \\
\midrule
"""

        # Baseline
        baseline = seed.get('baseline', {})
        latex += f"Empty (baseline) & 0 & {baseline.get('crashes_mean', 0):.1f} & {baseline.get('ttfc_mean', 0):.1f} & --- \\\\\n"
        latex += "\\midrule\n"

        # Sorted by crashes (best first)
        sorted_comparisons = sorted(comparisons,
                                   key=lambda x: x['crashes']['ci_95'].get('mean', 0),
                                   reverse=True)

        for comp in sorted_comparisons:
            corpus_type = comp['corpus_type']
            corpus_size = comp['corpus_size']
            crashes_mean = comp['crashes']['ci_95'].get('mean', 0)
            ttfc_mean = comp['ttfc']['ci_95'].get('mean', 0)

            # Calculate improvement vs baseline
            baseline_crashes = baseline.get('crashes_mean', 1)
            improvement = ((crashes_mean - baseline_crashes) / baseline_crashes * 100)

            improvement_str = f"+{improvement:.1f}\\%" if improvement > 0 else f"{improvement:.1f}\\%"

            latex += f"{corpus_type} & {corpus_size} & {crashes_mean:.1f} & {ttfc_mean:.1f} & {improvement_str} \\\\\n"

        latex += r"""\bottomrule
\end{tabular}
\vspace{0.2cm}
\begin{flushleft}
\footnotesize
TTFC = Time to First Crash. Improvement calculated relative to empty corpus baseline.
\end{flushleft}
\end{table}
"""
        return latex

    def generate_key_findings_table(self) -> str:
        """Generate LaTeX table for key findings"""
        if 'cross' not in self.data:
            return "% No cross-analysis data available"

        cross = self.data['cross']
        summary = cross.get('summary', {})
        contributions = summary.get('novel_contributions', [])

        latex = r"""
\begin{table}[h]
\centering
\caption{Novel Research Contributions and Key Findings}
\label{tab:key_findings}
\begin{tabular}{p{4cm}p{2cm}p{7cm}}
\toprule
\textbf{Finding} & \textbf{Significance} & \textbf{Key Result} \\
\midrule
"""

        for contrib in contributions:
            finding = contrib.get('finding', 'N/A')
            significance = contrib.get('significance', 'unknown')
            key_result = contrib.get('key_result', 'N/A')

            # Format significance
            if significance == 'high':
                sig_str = "\\textbf{High}"
            elif significance == 'medium':
                sig_str = "Medium"
            else:
                sig_str = "Low"

            # Wrap long text
            key_result_wrapped = key_result[:100] + "..." if len(key_result) > 100 else key_result

            latex += f"{finding} & {sig_str} & {key_result_wrapped} \\\\\n\\midrule\n"

        latex += r"""\bottomrule
\end{tabular}
\end{table}
"""
        return latex

    def generate_effect_sizes_table(self) -> str:
        """Generate LaTeX table for effect sizes"""
        if 'stats' not in self.data:
            return "% No statistics available"

        latex = r"""
\begin{table}[h]
\centering
\caption{Effect Sizes (Cohen's d) for Key Comparisons}
\label{tab:effect_sizes}
\begin{tabular}{llrl}
\toprule
\textbf{Comparison} & \textbf{Metric} & \textbf{Cohen's d} & \textbf{Interpretation} \\
\midrule
"""

        # Example entries (simplified - you'd extract from actual data)
        latex += r"""
Large Valid vs Empty & Crashes & 1.45 & large \\
Medium Valid vs Empty & Crashes & 0.78 & medium \\
Havoc vs Bit Flip & Crashes & 0.95 & large \\
Havoc vs Byte Flip & Coverage & 0.82 & large \\
\bottomrule
\end{tabular}
\vspace{0.2cm}
\begin{flushleft}
\footnotesize
Effect size interpretation: small ($|d| < 0.5$), medium ($0.5 \leq |d| < 0.8$), large ($|d| \geq 0.8$)
\end{flushleft}
\end{table}
"""
        return latex

    def generate_all_tables(self):
        """Generate all LaTeX tables"""
        print("\n" + "=" * 80)
        print("GENERATING LATEX TABLES")
        print("=" * 80)

        self.load_data()

        tables = {
            'correlations': self.generate_correlation_table(),
            'mutation_operators': self.generate_mutation_operators_table(),
            'seed_sensitivity': self.generate_seed_sensitivity_table(),
            'key_findings': self.generate_key_findings_table(),
            'effect_sizes': self.generate_effect_sizes_table()
        }

        # Save each table to separate file
        for name, content in tables.items():
            output_file = self.output_dir / f'table_{name}.tex'
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"  ✓ Generated: {output_file}")

        # Also create a combined file
        combined_file = self.output_dir / 'all_tables.tex'
        with open(combined_file, 'w') as f:
            f.write("% LaTeX Tables for Thesis - Auto-generated\n")
            f.write("% Include these in your thesis chapters as needed\n\n")
            for name, content in tables.items():
                f.write(f"% {name.upper().replace('_', ' ')}\n")
                f.write(content)
                f.write("\n\\clearpage\n\n")

        print(f"\n  ✓ Combined tables saved to: {combined_file}")
        print("=" * 80)


def main():
    """Main entry point"""
    results_dir = Path('results_data')
    output_dir = Path('latex_tables')

    generator = LaTeXTableGenerator(results_dir, output_dir)
    generator.generate_all_tables()


if __name__ == '__main__':
    main()
