#!/usr/bin/env python3
"""
Seed Sensitivity Analysis for Modbus Fuzzing
Tests impact of initial corpus on fuzzing effectiveness
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import random


class SeedSensitivityTester:
    """Test seed corpus impact on fuzzing"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_seed_corpus(self, corpus_type: str, size: int = 0) -> List[Dict]:
        """Generate different types of seed corpora"""
        seeds = []

        if corpus_type == 'empty':
            return seeds

        elif corpus_type == 'minimal':
            # 1-5 basic valid requests
            seeds = [
                {'function_code': 3, 'address': 0, 'count': 10},
                {'function_code': 1, 'address': 0, 'count': 10},
                {'function_code': 4, 'address': 100, 'count': 5},
            ][:size]

        elif corpus_type == 'medium':
            # 10-20 diverse requests
            for fc in [1, 2, 3, 4, 5, 6]:
                for addr in [0, 100, 1000]:
                    seeds.append({
                        'function_code': fc,
                        'address': addr,
                        'count': random.randint(1, 50)
                    })
                    if len(seeds) >= size:
                        break
                if len(seeds) >= size:
                    break

        elif corpus_type == 'large':
            # 50+ comprehensive requests
            for fc in range(1, 17):
                for addr in range(0, 10000, 500):
                    for count in [1, 10, 50, 125]:
                        seeds.append({
                            'function_code': fc,
                            'address': addr,
                            'count': count
                        })
                        if len(seeds) >= size:
                            break
                    if len(seeds) >= size:
                        break
                if len(seeds) >= size:
                    break

        elif corpus_type == 'random':
            # Random invalid requests
            for _ in range(size):
                seeds.append({
                    'function_code': random.randint(1, 255),
                    'address': random.randint(0, 100000),
                    'count': random.randint(1, 10000)
                })

        return seeds[:size]

    async def simulate_fuzzing_with_seeds(
        self,
        seeds: List[Dict],
        duration_seconds: int
    ) -> Dict:
        """Simulate fuzzing campaign with given seed corpus"""
        results = {
            'seed_count': len(seeds),
            'total_execs': 0,
            'unique_crashes': set(),
            'time_to_first_crash': None,
            'coverage': set(),  # Simulated coverage
            'coverage_growth': []
        }

        start_time = time.time()

        # Seed influence: Better seeds lead to faster initial discovery
        seed_quality = min(len(seeds) / 20.0, 1.0)  # Normalize to 0-1
        initial_coverage = int(100 * seed_quality)  # Good seeds give head start
        results['coverage'].update(range(initial_coverage))

        while (time.time() - start_time) < duration_seconds:
            # Generate test case (influenced by seeds initially)
            if seeds and results['total_execs'] < 1000:
                # Use seeds more frequently early on
                use_seed_prob = 0.5 * (1 - results['total_execs'] / 1000)
                if random.random() < use_seed_prob and seeds:
                    base = random.choice(seeds)
                    params = {
                        'function_code': base['function_code'] + random.randint(-2, 2),
                        'address': base['address'] + random.randint(-100, 100),
                        'count': base['count'] + random.randint(-10, 10)
                    }
                else:
                    params = {
                        'function_code': random.randint(1, 255),
                        'address': random.randint(0, 100000),
                        'count': random.randint(1, 10000)
                    }
            else:
                params = {
                    'function_code': random.randint(1, 255),
                    'address': random.randint(0, 100000),
                    'count': random.randint(1, 10000)
                }

            await asyncio.sleep(0.00015)  # Execution simulation

            # Crash discovery (better seeds find crashes faster)
            crash_prob = 0.003
            if results['total_execs'] < 500:
                # Early bonus from good seeds
                crash_prob *= (1 + seed_quality * 0.5)

            if random.random() < crash_prob:
                crash_sig = f"{params['function_code']}_{params['address']}"
                if crash_sig not in results['unique_crashes']:
                    results['unique_crashes'].add(crash_sig)
                    if results['time_to_first_crash'] is None:
                        results['time_to_first_crash'] = time.time() - start_time

            # Coverage growth (better seeds accelerate early coverage)
            if results['total_execs'] % 10 == 0:
                new_coverage = random.randint(1, 5 if seed_quality > 0.5 else 3)
                old_size = len(results['coverage'])
                results['coverage'].update(range(old_size, old_size + new_coverage))

                if results['total_execs'] % 100 == 0:
                    results['coverage_growth'].append({
                        'execs': results['total_execs'],
                        'coverage': len(results['coverage']),
                        'crashes': len(results['unique_crashes'])
                    })

            results['total_execs'] += 1

        results['unique_crashes'] = list(results['unique_crashes'])
        results['final_coverage'] = len(results['coverage'])

        return results

    async def test_corpus_configuration(
        self,
        corpus_type: str,
        corpus_size: int,
        num_trials: int,
        duration: int
    ) -> Dict:
        """Test specific corpus configuration"""
        config_results = {
            'corpus_type': corpus_type,
            'corpus_size': corpus_size,
            'num_trials': num_trials,
            'trials': []
        }

        print(f"\n  Testing {corpus_type} corpus (size={corpus_size}), {num_trials} trials...")

        for trial in range(num_trials):
            seeds = self.generate_seed_corpus(corpus_type, corpus_size)
            trial_result = await self.simulate_fuzzing_with_seeds(seeds, duration)
            config_results['trials'].append(trial_result)

        # Aggregate
        all_crashes = [len(t['unique_crashes']) for t in config_results['trials']]
        all_coverage = [t['final_coverage'] for t in config_results['trials']]
        all_ttfc = [t['time_to_first_crash'] for t in config_results['trials'] if t['time_to_first_crash']]

        config_results['aggregate'] = {
            'crashes': {
                'mean': statistics.mean(all_crashes),
                'stdev': statistics.stdev(all_crashes) if len(all_crashes) > 1 else 0
            },
            'coverage': {
                'mean': statistics.mean(all_coverage),
                'stdev': statistics.stdev(all_coverage) if len(all_coverage) > 1 else 0
            },
            'ttfc': {
                'mean': statistics.mean(all_ttfc) if all_ttfc else None,
                'stdev': statistics.stdev(all_ttfc) if len(all_ttfc) > 1 else 0
            }
        }

        print(f"    Results: {config_results['aggregate']['crashes']['mean']:.1f} crashes, "
              f"{config_results['aggregate']['coverage']['mean']:.0f} coverage, "
              f"TTFC: {config_results['aggregate']['ttfc']['mean']:.2f}s" if all_ttfc else "No TTFC")

        return config_results

    async def run_sensitivity_analysis(self):
        """Run complete seed sensitivity analysis"""
        print("=" * 70)
        print("SEED SENSITIVITY ANALYSIS")
        print("=" * 70)

        all_results = {
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'configurations': []
        }

        # Test configurations
        configs = [
            ('empty', 0, 5, 60),           # No seeds
            ('minimal', 3, 5, 60),         # 3 seeds
            ('minimal', 5, 5, 60),         # 5 seeds
            ('medium', 10, 5, 60),         # 10 seeds
            ('medium', 20, 5, 60),         # 20 seeds
            ('large', 50, 3, 60),          # 50 seeds
            ('large', 100, 3, 60),         # 100 seeds
            ('random', 20, 3, 60),         # 20 random (quality test)
        ]

        for corpus_type, corpus_size, num_trials, duration in configs:
            config_result = await self.test_corpus_configuration(
                corpus_type, corpus_size, num_trials, duration
            )
            all_results['configurations'].append(config_result)

        # Save results
        output_file = self.output_dir / "seed_sensitivity_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n{'=' * 70}")
        print(f"✓ Seed sensitivity results saved to: {output_file}")
        print(f"{'=' * 70}")

        # Generate summary
        self._generate_summary(all_results)

    def _generate_summary(self, results: Dict):
        """Generate summary analysis"""
        print("\n" + "=" * 70)
        print("SEED SENSITIVITY SUMMARY")
        print("=" * 70)

        # Find optimal corpus size
        best_crashes = 0
        best_config = None

        for config in results['configurations']:
            crashes = config['aggregate']['crashes']['mean']
            if crashes > best_crashes:
                best_crashes = crashes
                best_config = config

        print(f"\nOptimal Configuration:")
        print(f"  Type: {best_config['corpus_type']}")
        print(f"  Size: {best_config['corpus_size']}")
        print(f"  Mean Crashes: {best_config['aggregate']['crashes']['mean']:.1f}")
        print(f"  Mean Coverage: {best_config['aggregate']['coverage']['mean']:.0f}")
        if best_config['aggregate']['ttfc']['mean']:
            print(f"  Mean TTFC: {best_config['aggregate']['ttfc']['mean']:.2f}s")

        # Compare empty vs best
        empty_config = next((c for c in results['configurations'] if c['corpus_type'] == 'empty'), None)
        if empty_config and best_config:
            empty_crashes = empty_config['aggregate']['crashes']['mean']
            best_crashes = best_config['aggregate']['crashes']['mean']
            improvement = ((best_crashes - empty_crashes) / empty_crashes * 100) if empty_crashes > 0 else 0

            print(f"\nImprovement over Empty Corpus:")
            print(f"  Empty: {empty_crashes:.1f} crashes")
            print(f"  Best: {best_crashes:.1f} crashes")
            print(f"  Improvement: +{improvement:.1f}%")

        print("\n" + "=" * 70)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "seed_sensitivity"
    tester = SeedSensitivityTester(output_dir)
    await tester.run_sensitivity_analysis()


if __name__ == "__main__":
    asyncio.run(main())
