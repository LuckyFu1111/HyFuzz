#!/usr/bin/env python3
"""
Automated Crash Triage
Automatically deduplicate, classify, and prioritize crashes
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict
from enum import Enum


class CrashSeverity(Enum):
    """Crash severity levels"""
    CRITICAL = "critical"  # Memory corruption, code execution
    HIGH = "high"  # Denial of service, assertion failures
    MEDIUM = "medium"  # Unexpected behavior, resource leaks
    LOW = "low"  # Minor issues, edge cases
    INFO = "info"  # Informational, not a real crash


class ExploitabilityRating(Enum):
    """Exploitability assessment"""
    EXPLOITABLE = "exploitable"
    PROBABLY_EXPLOITABLE = "probably_exploitable"
    PROBABLY_NOT_EXPLOITABLE = "probably_not_exploitable"
    NOT_EXPLOITABLE = "not_exploitable"
    UNKNOWN = "unknown"


class CrashTriageAutomation:
    """Automated crash triage system"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def triage_crashes(self, crash_data: List[Dict]) -> Dict:
        """
        Perform automated triage on crash data

        Args:
            crash_data: List of crash dictionaries with crash info
        """

        print("=" * 70)
        print("AUTOMATED CRASH TRIAGE")
        print("=" * 70)
        print(f"\nProcessing {len(crash_data)} crash reports...")

        results = {
            'triage_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_crashes': len(crash_data),
            'unique_crashes': 0,
            'crash_groups': [],
            'severity_distribution': defaultdict(int),
            'exploitability_distribution': defaultdict(int),
            'priority_queue': []
        }

        # Step 1: Deduplication
        print("\n1. Deduplicating crashes...")
        unique_crashes, duplicates = self._deduplicate_crashes(crash_data)
        results['unique_crashes'] = len(unique_crashes)
        results['duplicates'] = len(duplicates)

        print(f"   Found {len(unique_crashes)} unique crashes ({len(duplicates)} duplicates)")

        # Step 2: Clustering
        print("\n2. Clustering similar crashes...")
        crash_groups = self._cluster_crashes(unique_crashes)
        results['crash_groups'] = crash_groups

        print(f"   Identified {len(crash_groups)} crash groups")

        # Step 3: Severity classification
        print("\n3. Classifying crash severity...")
        for group in crash_groups:
            severity = self._classify_severity(group)
            group['severity'] = severity.value
            results['severity_distribution'][severity.value] += len(group['crashes'])

        # Step 4: Exploitability assessment
        print("\n4. Assessing exploitability...")
        for group in crash_groups:
            exploitability = self._assess_exploitability(group)
            group['exploitability'] = exploitability.value
            results['exploitability_distribution'][exploitability.value] += len(group['crashes'])

        # Step 5: Priority scoring
        print("\n5. Calculating priority scores...")
        for group in crash_groups:
            priority_score = self._calculate_priority_score(group)
            group['priority_score'] = priority_score

        # Sort by priority
        results['crash_groups'].sort(key=lambda g: g['priority_score'], reverse=True)

        # Create priority queue (top 20)
        results['priority_queue'] = [
            {
                'group_id': g['group_id'],
                'severity': g['severity'],
                'exploitability': g['exploitability'],
                'priority_score': g['priority_score'],
                'crash_count': len(g['crashes']),
                'root_cause': g['root_cause']
            }
            for g in results['crash_groups'][:20]
        ]

        # Save results
        output_file = self.output_dir / "crash_triage_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n{'=' * 70}")
        print(f"✓ Triage results saved to: {output_file}")
        print(f"{'=' * 70}")

        self._print_triage_summary(results)

        return results

    def _deduplicate_crashes(self, crashes: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """
        Deduplicate crashes based on crash signature

        Returns:
            (unique_crashes, duplicates)
        """

        seen_signatures = {}
        unique = []
        duplicates = []

        for crash in crashes:
            # Generate crash signature
            signature = self._generate_crash_signature(crash)
            crash['signature'] = signature

            if signature not in seen_signatures:
                seen_signatures[signature] = crash
                unique.append(crash)
            else:
                duplicates.append(crash)

        return unique, duplicates

    def _generate_crash_signature(self, crash: Dict) -> str:
        """Generate unique crash signature"""

        # Extract key crash characteristics
        crash_type = crash.get('type', 'unknown')
        function_code = crash.get('function_code', 0)
        error_message = crash.get('error', '')
        stack_trace = crash.get('stack_trace', '')

        # Create signature from key fields
        sig_string = f"{crash_type}_{function_code}_{error_message[:50]}"

        # Include stack trace hash if available
        if stack_trace:
            stack_hash = hashlib.md5(stack_trace.encode()).hexdigest()[:8]
            sig_string += f"_{stack_hash}"

        return sig_string

    def _cluster_crashes(self, crashes: List[Dict]) -> List[Dict]:
        """Cluster similar crashes into groups"""

        groups = []
        grouped_crashes = set()

        for i, crash in enumerate(crashes):
            if i in grouped_crashes:
                continue

            # Start new group
            group = {
                'group_id': f"group_{len(groups)}",
                'crashes': [crash],
                'representative_crash': crash,
                'root_cause': self._identify_root_cause(crash)
            }

            # Find similar crashes
            for j, other_crash in enumerate(crashes[i+1:], start=i+1):
                if j in grouped_crashes:
                    continue

                if self._are_crashes_similar(crash, other_crash):
                    group['crashes'].append(other_crash)
                    grouped_crashes.add(j)

            groups.append(group)

        return groups

    def _are_crashes_similar(self, crash1: Dict, crash2: Dict) -> bool:
        """Determine if two crashes are similar"""

        # Same crash type
        if crash1.get('type') != crash2.get('type'):
            return False

        # Similar function codes (within 2)
        fc1 = crash1.get('function_code', 0)
        fc2 = crash2.get('function_code', 0)
        if abs(fc1 - fc2) > 2:
            return False

        # Similar error messages (simple substring matching)
        err1 = crash1.get('error', '').lower()
        err2 = crash2.get('error', '').lower()

        if err1 and err2:
            # Check for common substrings
            words1 = set(err1.split())
            words2 = set(err2.split())
            common_words = words1 & words2

            if len(common_words) / max(len(words1), len(words2)) > 0.5:
                return True

        return False

    def _identify_root_cause(self, crash: Dict) -> str:
        """Identify crash root cause"""

        crash_type = crash.get('type', 'unknown')
        error = crash.get('error', '').lower()

        if 'buffer' in error or 'overflow' in error:
            return "Buffer Overflow"
        elif 'null' in error or 'dereference' in error:
            return "Null Pointer Dereference"
        elif 'division' in error or 'divide by zero' in error:
            return "Division by Zero"
        elif 'assertion' in error or 'assert' in error:
            return "Assertion Failure"
        elif 'timeout' in error:
            return "Timeout"
        elif 'memory' in error or 'allocation' in error:
            return "Memory Error"
        elif 'invalid' in error:
            return "Invalid Input"
        elif crash_type == 'hang':
            return "Infinite Loop / Hang"
        elif crash_type == 'exception':
            return "Unhandled Exception"
        else:
            return "Unknown"

    def _classify_severity(self, group: Dict) -> CrashSeverity:
        """Classify crash severity"""

        root_cause = group['root_cause']
        crash = group['representative_crash']

        # Critical severity
        if root_cause in ["Buffer Overflow", "Use After Free", "Double Free"]:
            return CrashSeverity.CRITICAL

        # High severity
        if root_cause in ["Null Pointer Dereference", "Memory Error", "Assertion Failure"]:
            return CrashSeverity.HIGH

        # Medium severity
        if root_cause in ["Division by Zero", "Invalid Input", "Unhandled Exception"]:
            return CrashSeverity.MEDIUM

        # Low severity
        if root_cause in ["Timeout", "Infinite Loop / Hang"]:
            return CrashSeverity.LOW

        return CrashSeverity.INFO

    def _assess_exploitability(self, group: Dict) -> ExploitabilityRating:
        """Assess crash exploitability"""

        root_cause = group['root_cause']
        severity = group.get('severity', 'info')

        # Exploitable
        if root_cause in ["Buffer Overflow", "Format String"]:
            return ExploitabilityRating.EXPLOITABLE

        # Probably exploitable
        if root_cause in ["Use After Free", "Double Free", "Integer Overflow"]:
            return ExploitabilityRating.PROBABLY_EXPLOITABLE

        # Probably not exploitable
        if root_cause in ["Null Pointer Dereference", "Assertion Failure"]:
            return ExploitabilityRating.PROBABLY_NOT_EXPLOITABLE

        # Not exploitable
        if root_cause in ["Timeout", "Division by Zero", "Invalid Input"]:
            return ExploitabilityRating.NOT_EXPLOITABLE

        return ExploitabilityRating.UNKNOWN

    def _calculate_priority_score(self, group: Dict) -> float:
        """Calculate priority score (0-100)"""

        score = 0.0

        # Severity weight (40 points)
        severity_scores = {
            'critical': 40,
            'high': 30,
            'medium': 20,
            'low': 10,
            'info': 5
        }
        score += severity_scores.get(group.get('severity', 'info'), 5)

        # Exploitability weight (30 points)
        exploit_scores = {
            'exploitable': 30,
            'probably_exploitable': 25,
            'probably_not_exploitable': 15,
            'not_exploitable': 5,
            'unknown': 10
        }
        score += exploit_scores.get(group.get('exploitability', 'unknown'), 10)

        # Frequency weight (20 points)
        crash_count = len(group['crashes'])
        if crash_count >= 100:
            score += 20
        elif crash_count >= 50:
            score += 15
        elif crash_count >= 10:
            score += 10
        elif crash_count >= 5:
            score += 5
        else:
            score += 2

        # Reproducibility weight (10 points)
        # Assume all are reproducible in simulation
        score += 10

        return min(100, score)

    def _print_triage_summary(self, results: Dict):
        """Print triage summary"""

        print("\n" + "=" * 70)
        print("CRASH TRIAGE SUMMARY")
        print("=" * 70)

        print(f"\nTotal Crashes: {results['total_crashes']}")
        print(f"Unique Crashes: {results['unique_crashes']}")
        print(f"Duplicates Removed: {results['duplicates']}")
        print(f"Crash Groups: {len(results['crash_groups'])}")

        print(f"\nSeverity Distribution:")
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = results['severity_distribution'].get(severity, 0)
            if count > 0:
                print(f"  {severity.capitalize()}: {count} crashes")

        print(f"\nExploitability Distribution:")
        for exploit in ['exploitable', 'probably_exploitable', 'probably_not_exploitable', 'not_exploitable']:
            count = results['exploitability_distribution'].get(exploit, 0)
            if count > 0:
                print(f"  {exploit.replace('_', ' ').title()}: {count} crashes")

        print(f"\nTop Priority Crashes:")
        print(f"{'Rank':<6} {'Severity':<12} {'Exploitability':<25} {'Score':<10} {'Root Cause':<25}")
        print("-" * 80)

        for i, item in enumerate(results['priority_queue'][:10], 1):
            print(f"{i:<6} {item['severity'].upper():<12} "
                  f"{item['exploitability'].replace('_', ' ').title():<25} "
                  f"{item['priority_score']:<10.1f} {item['root_cause']:<25}")

        print("\n" + "=" * 70)


def generate_sample_crashes(num_crashes: int = 100) -> List[Dict]:
    """Generate sample crash data for testing"""

    import random

    crash_types = ['exception', 'segfault', 'assertion', 'hang', 'timeout']
    errors = [
        'buffer overflow detected',
        'null pointer dereference',
        'assertion failed: x > 0',
        'division by zero',
        'invalid memory access',
        'timeout after 10 seconds',
        'unhandled exception',
        'stack overflow',
    ]

    crashes = []

    for i in range(num_crashes):
        crash = {
            'id': f"crash_{i}",
            'type': random.choice(crash_types),
            'function_code': random.randint(1, 16),
            'error': random.choice(errors),
            'stack_trace': f"frame0->frame1->frame2->crash_site_{random.randint(0, 10)}",
            'timestamp': time.time() - random.randint(0, 3600)
        }
        crashes.append(crash)

    return crashes


async def main():
    output_dir = Path(__file__).parent.parent / "results_data" / "crash_triage"

    triage = CrashTriageAutomation(output_dir)

    # Generate and triage sample crashes
    print("Generating sample crash data...")
    crashes = generate_sample_crashes(150)

    triage.triage_crashes(crashes)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
