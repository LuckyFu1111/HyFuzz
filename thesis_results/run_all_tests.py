#!/usr/bin/env python3
"""
Master Test Runner
Run all thesis tests in sequence
"""

import asyncio
import sys
from pathlib import Path
import time

# Add test directories to path
sys.path.insert(0, str(Path(__file__).parent))

from modbus_tests.test_modbus_validity import ModbusValidityTester
from modbus_tests.test_modbus_fuzzing import ModbusFuzzingTester
from coap_tests.test_coap_validity import CoAPValidityTester
from coap_tests.test_coap_fuzzing import CoAPFuzzingTester
from baseline_comparisons.compare_baselines import BaselineComparer


async def run_all_tests():
    """Run complete thesis test suite"""
    start_time = time.time()

    print("=" * 80)
    print(" " * 20 + "THESIS RESULTS TEST SUITE")
    print(" " * 25 + "Complete Run")
    print("=" * 80)
    print()

    results_dir = Path(__file__).parent / "results_data"

    # Test 1: Modbus Validity
    print("\n" + "=" * 80)
    print("TEST 1/5: MODBUS VALIDITY AND STATE PROGRESS")
    print("=" * 80)
    modbus_validity_tester = ModbusValidityTester(results_dir / "modbus_validity")
    await modbus_validity_tester.run_all_tests(num_trials=1000)

    # Test 2: Modbus Fuzzing
    print("\n" + "=" * 80)
    print("TEST 2/5: MODBUS FUZZING CAMPAIGNS")
    print("=" * 80)
    modbus_fuzzing_tester = ModbusFuzzingTester(results_dir / "modbus_fuzzing")
    await modbus_fuzzing_tester.run_all_tests()

    # Test 3: CoAP Validity
    print("\n" + "=" * 80)
    print("TEST 3/5: CoAP VALIDITY AND STATE PROGRESS")
    print("=" * 80)
    coap_validity_tester = CoAPValidityTester(results_dir / "coap_validity")
    await coap_validity_tester.run_all_tests(num_trials=1000)

    # Test 4: CoAP Fuzzing
    print("\n" + "=" * 80)
    print("TEST 4/5: CoAP FUZZING CAMPAIGNS (DTLS COMPARISON)")
    print("=" * 80)
    coap_fuzzing_tester = CoAPFuzzingTester(results_dir / "coap_fuzzing")
    await coap_fuzzing_tester.run_all_tests()

    # Test 5: Baseline Comparison
    print("\n" + "=" * 80)
    print("TEST 5/5: BASELINE FUZZER COMPARISON")
    print("=" * 80)
    baseline_comparer = BaselineComparer(results_dir / "baseline_comparison")
    await baseline_comparer.run_all_comparisons()

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(" " * 25 + "ALL TESTS COMPLETED")
    print("=" * 80)
    print(f"\nTotal runtime: {elapsed/60:.1f} minutes")
    print(f"Results saved to: {results_dir}")
    print("\nNext steps:")
    print("  1. Run analysis: python3 analysis_scripts/analyze_results.py")
    print("  2. Generate plots: python3 analysis_scripts/plot_results.py")
    print("=" * 80)


def main():
    """Main entry point"""
    print("\nStarting complete thesis test suite...")
    print("This will take approximately 15-20 minutes.\n")

    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during test execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
