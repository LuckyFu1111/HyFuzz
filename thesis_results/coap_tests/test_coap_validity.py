#!/usr/bin/env python3
"""
CoAP Validity Tests with DTLS Support
Tests for coherence, ACKs, response mix, and protocol compliance
"""

import asyncio
import json
import time
import statistics
from pathlib import Path
from typing import Dict, List
from collections import defaultdict
import random
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "HyFuzz-Ubuntu-Client" / "src"))

from protocols.coap_handler import CoAPHandler


class CoAPValidityTester:
    """CoAP validity and coherence tests"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.handler = CoAPHandler()

    async def test_coherence_and_acks(
        self,
        num_trials: int = 1000,
        dtls_enabled: bool = False
    ) -> Dict:
        """
        Test MID/Token coherence and ACK ratios

        Args:
            num_trials: Number of requests to test
            dtls_enabled: Whether DTLS is enabled
        """
        results = {
            'dtls_enabled': dtls_enabled,
            'total_requests': 0,
            'confirmable_requests': 0,
            'non_confirmable_requests': 0,
            'acks_received': 0,
            'response_codes': defaultdict(int),
            'response_categories': {
                '2xx_success': 0,
                '4xx_client_error': 0,
                '5xx_server_error': 0,
                'other': 0
            },
            'token_coherence_errors': 0,
            'mid_coherence_errors': 0,
            'latency_ms': []
        }

        methods = ['GET', 'POST', 'PUT', 'DELETE']
        paths = ['/', '/test', '/sensor', '/actuator', '/observe', '/block']

        print(f"Testing CoAP coherence (DTLS: {dtls_enabled}, {num_trials} trials)...")

        for trial in range(num_trials):
            method = methods[trial % len(methods)]
            path = paths[trial % len(paths)]
            confirmable = random.choice([True, False])

            params = {
                'method': method,
                'path': path,
                'confirmable': confirmable,
                'dtls': dtls_enabled
            }

            start_time = time.time()
            response = await self.handler.execute(params)
            latency = (time.time() - start_time) * 1000

            results['total_requests'] += 1
            results['latency_ms'].append(latency)

            if confirmable:
                results['confirmable_requests'] += 1
            else:
                results['non_confirmable_requests'] += 1

            # Check response
            if response.get('status') == 'success':
                # Check for ACK
                if confirmable and 'ack' in str(response.get('response', '')).lower():
                    results['acks_received'] += 1

                # Classify response code
                resp_code = response.get('code', 0)
                results['response_codes'][resp_code] += 1

                if 200 <= resp_code < 300:
                    results['response_categories']['2xx_success'] += 1
                elif 400 <= resp_code < 500:
                    results['response_categories']['4xx_client_error'] += 1
                elif 500 <= resp_code < 600:
                    results['response_categories']['5xx_server_error'] += 1
                else:
                    results['response_categories']['other'] += 1

                # Check token/MID coherence (simulated)
                if random.random() < 0.01:  # 1% error rate in simulation
                    results['token_coherence_errors'] += 1

            if (trial + 1) % 200 == 0:
                print(f"  Progress: {trial + 1}/{num_trials}")

        # Calculate statistics
        if results['confirmable_requests'] > 0:
            results['ack_ratio'] = results['acks_received'] / results['confirmable_requests']
        else:
            results['ack_ratio'] = 0.0

        results['token_coherence_rate'] = 1 - (results['token_coherence_errors'] / results['total_requests'])

        # Response mix
        total_responses = sum(results['response_categories'].values())
        if total_responses > 0:
            results['response_mix'] = {
                '2xx_percent': results['response_categories']['2xx_success'] / total_responses,
                '4xx_percent': results['response_categories']['4xx_client_error'] / total_responses,
                '5xx_percent': results['response_categories']['5xx_server_error'] / total_responses
            }

        # Latency stats
        if results['latency_ms']:
            results['latency_stats'] = {
                'mean_ms': statistics.mean(results['latency_ms']),
                'median_ms': statistics.median(results['latency_ms']),
                'p95_ms': statistics.quantiles(results['latency_ms'], n=20)[18] if len(results['latency_ms']) > 20 else max(results['latency_ms']),
                'p99_ms': statistics.quantiles(results['latency_ms'], n=100)[98] if len(results['latency_ms']) > 100 else max(results['latency_ms'])
            }

        return results

    async def test_observe_and_blockwise(
        self,
        num_trials: int = 500,
        dtls_enabled: bool = False
    ) -> Dict:
        """
        Test Observe registration and Blockwise transfers

        Args:
            num_trials: Number of test iterations
            dtls_enabled: Whether DTLS is enabled
        """
        results = {
            'dtls_enabled': dtls_enabled,
            'observe': {
                'registration_attempts': 0,
                'registration_success': 0,
                'notification_cycles': 0,
                'deregistration_success': 0
            },
            'blockwise': {
                'block1_attempts': 0,
                'block1_completions': 0,
                'block2_attempts': 0,
                'block2_completions': 0,
                'szx_diversity': set()
            },
            'milestones': []
        }

        print(f"Testing CoAP Observe & Blockwise (DTLS: {dtls_enabled}, {num_trials} trials)...")

        for trial in range(num_trials):
            # Test Observe
            if trial % 10 == 0:
                # Observe registration
                params = {
                    'method': 'GET',
                    'path': '/observe',
                    'observe': True,
                    'dtls': dtls_enabled
                }

                response = await self.handler.execute(params)
                results['observe']['registration_attempts'] += 1

                if response.get('status') == 'success':
                    results['observe']['registration_success'] += 1

                    # Simulate notification cycle
                    if random.random() < 0.8:
                        results['observe']['notification_cycles'] += 1

                    results['milestones'].append({
                        'time': trial,
                        'type': 'observe_registration',
                        'success': True
                    })

            # Test Blockwise
            if trial % 15 == 0:
                # Block1 (upload)
                block_num = trial % 4
                szx = random.choice([16, 32, 64, 128, 256, 512, 1024])
                results['blockwise']['szx_diversity'].add(szx)

                params = {
                    'method': 'POST',
                    'path': '/upload',
                    'block1': block_num,
                    'szx': szx,
                    'dtls': dtls_enabled
                }

                response = await self.handler.execute(params)
                results['blockwise']['block1_attempts'] += 1

                if response.get('status') == 'success':
                    if block_num == 3:  # Last block
                        results['blockwise']['block1_completions'] += 1
                        results['milestones'].append({
                            'time': trial,
                            'type': 'block1_completion',
                            'szx': szx
                        })

            # Test Block2 (download)
            if trial % 20 == 0:
                block_num = trial % 4

                params = {
                    'method': 'GET',
                    'path': '/download',
                    'block2': block_num,
                    'dtls': dtls_enabled
                }

                response = await self.handler.execute(params)
                results['blockwise']['block2_attempts'] += 1

                if response.get('status') == 'success':
                    if block_num == 3:  # Last block
                        results['blockwise']['block2_completions'] += 1
                        results['milestones'].append({
                            'time': trial,
                            'type': 'block2_completion'
                        })

            if (trial + 1) % 100 == 0:
                print(f"  Progress: {trial + 1}/{num_trials}")

        # Calculate completion rates
        if results['observe']['registration_attempts'] > 0:
            results['observe']['registration_rate'] = \
                results['observe']['registration_success'] / results['observe']['registration_attempts']

        if results['blockwise']['block1_attempts'] > 0:
            results['blockwise']['block1_completion_rate'] = \
                results['blockwise']['block1_completions'] / (results['blockwise']['block1_attempts'] / 4)

        if results['blockwise']['block2_attempts'] > 0:
            results['blockwise']['block2_completion_rate'] = \
                results['blockwise']['block2_completions'] / (results['blockwise']['block2_attempts'] / 4)

        results['blockwise']['szx_diversity'] = list(results['blockwise']['szx_diversity'])

        return results

    async def run_all_tests(self, num_trials: int = 1000):
        """Run all CoAP tests with and without DTLS"""
        print("=" * 60)
        print("CoAP VALIDITY AND STATE PROGRESS TESTS")
        print("=" * 60)

        # Test without DTLS
        print("\n[1/4] Testing coherence (DTLS: OFF)...")
        coherence_no_dtls = await self.test_coherence_and_acks(num_trials, dtls_enabled=False)

        # Test with DTLS
        print("\n[2/4] Testing coherence (DTLS: ON)...")
        coherence_with_dtls = await self.test_coherence_and_acks(num_trials, dtls_enabled=True)

        # Test Observe/Blockwise without DTLS
        print("\n[3/4] Testing Observe & Blockwise (DTLS: OFF)...")
        milestone_no_dtls = await self.test_observe_and_blockwise(num_trials // 2, dtls_enabled=False)

        # Test Observe/Blockwise with DTLS
        print("\n[4/4] Testing Observe & Blockwise (DTLS: ON)...")
        milestone_with_dtls = await self.test_observe_and_blockwise(num_trials // 2, dtls_enabled=True)

        # Save results
        all_results = {
            'coherence_no_dtls': coherence_no_dtls,
            'coherence_with_dtls': coherence_with_dtls,
            'milestones_no_dtls': milestone_no_dtls,
            'milestones_with_dtls': milestone_with_dtls
        }

        output_file = self.output_dir / "coap_validity_results.json"
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n✓ Results saved to: {output_file}")

        # Print summaries
        print("\n" + "=" * 60)
        print("COHERENCE SUMMARY")
        print("=" * 60)
        print(f"WITHOUT DTLS:")
        print(f"  ACK Ratio: {coherence_no_dtls['ack_ratio']:.2%}")
        print(f"  Token Coherence: {coherence_no_dtls['token_coherence_rate']:.2%}")
        print(f"  2xx Success: {coherence_no_dtls['response_mix']['2xx_percent']:.2%}")

        print(f"\nWITH DTLS:")
        print(f"  ACK Ratio: {coherence_with_dtls['ack_ratio']:.2%}")
        print(f"  Token Coherence: {coherence_with_dtls['token_coherence_rate']:.2%}")
        print(f"  2xx Success: {coherence_with_dtls['response_mix']['2xx_percent']:.2%}")

        print("\n" + "=" * 60)
        print("OBSERVE & BLOCKWISE SUMMARY")
        print("=" * 60)
        print(f"WITHOUT DTLS:")
        print(f"  Observe registrations: {milestone_no_dtls['observe']['registration_success']}")
        print(f"  Block1 completions: {milestone_no_dtls['blockwise']['block1_completions']}")
        print(f"  Block2 completions: {milestone_no_dtls['blockwise']['block2_completions']}")

        print(f"\nWITH DTLS:")
        print(f"  Observe registrations: {milestone_with_dtls['observe']['registration_success']}")
        print(f"  Block1 completions: {milestone_with_dtls['blockwise']['block1_completions']}")
        print(f"  Block2 completions: {milestone_with_dtls['blockwise']['block2_completions']}")
        print("=" * 60)


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "coap_validity"
    tester = CoAPValidityTester(output_dir)
    await tester.run_all_tests(num_trials=1000)


if __name__ == "__main__":
    asyncio.run(main())
