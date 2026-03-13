#!/usr/bin/env python3
"""
Compare Round A (control) vs Round B (treatment) for inheritance effectiveness.

Usage:
    python compare_rounds.py --round-a round_a --round-b round_b --output comparison.json
"""

import json
import sys
import statistics
from pathlib import Path
from typing import Dict, List
import argparse


def load_round_data(round_dir: str) -> Dict:
    """Load all data for a single round"""
    base = Path(round_dir)
    
    data = {
        'candidates': [],
        'bridge_results': [],
        'mainline_results': None
    }
    
    # Load candidates
    cand_file = base / 'candidates.json'
    if cand_file.exists():
        with open(cand_file) as f:
            data['candidates'] = json.load(f)
    
    # Load Bridge results
    bridge_dir = base / 'bridge_results'
    if bridge_dir.exists():
        for f in bridge_dir.glob('*.json'):
            with open(f) as fp:
                data['bridge_results'].append(json.load(fp))
    
    # Load Mainline results
    main_file = base / 'mainline_results.json'
    if main_file.exists():
        with open(main_file) as f:
            data['mainline_results'] = json.load(f)
    
    return data


def calculate_metrics(data: Dict) -> Dict:
    """Calculate key metrics for a round"""
    metrics = {
        'total_candidates': len(data['candidates']),
        'bridge_passed': 0,
        'bridge_pass_rate': 0.0,
        'mainline_approved': 0,
        'mainline_approve_rate': 0.0,
        'mean_throughput_delta': 0.0,
        'throughput_variance': 0.0,
        'failure_archetypes': []
    }
    
    # Bridge metrics
    if data['bridge_results']:
        passed = [r for r in data['bridge_results'] if r.get('status') in ['PASS', 'MARGINAL']]
        metrics['bridge_passed'] = len(passed)
        metrics['bridge_pass_rate'] = len(passed) / len(data['bridge_results'])
    
    # Mainline metrics
    if data['mainline_results']:
        summary = data['mainline_results'].get('summary', {})
        metrics['mainline_approved'] = summary.get('approved', 0)
        total = summary.get('total_evaluated', 1)
        metrics['mainline_approve_rate'] = metrics['mainline_approved'] / total if total > 0 else 0
        
        # Throughput analysis
        detailed = data['mainline_results'].get('detailed_results', [])
        if detailed:
            deltas = [r['metrics']['throughput_delta'] for r in detailed if 'metrics' in r]
            if deltas:
                metrics['mean_throughput_delta'] = statistics.mean(deltas)
                if len(deltas) > 1:
                    metrics['throughput_variance'] = statistics.variance(deltas)
            
            # Collect failure archetypes
            for r in detailed:
                if r.get('decision') == 'REJECT':
                    metrics['failure_archetypes'].append({
                        'candidate': r['candidate_id'],
                        'rationale': r.get('rationale', '')
                    })
    
    return metrics


def compare_rounds(round_a_dir: str, round_b_dir: str) -> Dict:
    """Compare two rounds and calculate improvements"""
    
    print(f"Loading Round A (control) from {round_a_dir}...")
    round_a = load_round_data(round_a_dir)
    metrics_a = calculate_metrics(round_a)
    
    print(f"Loading Round B (treatment) from {round_b_dir}...")
    round_b = load_round_data(round_b_dir)
    metrics_b = calculate_metrics(round_b)
    
    # Calculate improvements
    comparison = {
        'round_a': metrics_a,
        'round_b': metrics_b,
        'improvements': {
            'bridge_pass_rate_pp': (metrics_b['bridge_pass_rate'] - metrics_a['bridge_pass_rate']) * 100,
            'mainline_approve_rate_pp': (metrics_b['mainline_approve_rate'] - metrics_a['mainline_approve_rate']) * 100,
            'throughput_delta_change': metrics_b['mean_throughput_delta'] - metrics_a['mean_throughput_delta'],
            'variance_reduction': metrics_a['throughput_variance'] - metrics_b['throughput_variance']
        }
    }
    
    # Determine verdict
    imp = comparison['improvements']
    passes = 0
    
    if imp['bridge_pass_rate_pp'] >= 5:
        passes += 1
    if imp['mainline_approve_rate_pp'] >= 5:
        passes += 1
    if imp['throughput_delta_change'] >= 0.003:  # +0.3%
        passes += 1
    
    if passes >= 2:
        comparison['verdict'] = 'EFFECTIVE'
        comparison['confidence'] = 'high' if passes == 3 else 'medium'
    elif passes >= 1:
        comparison['verdict'] = 'PROMISING'
        comparison['confidence'] = 'low'
    else:
        comparison['verdict'] = 'INEFFECTIVE'
        comparison['confidence'] = 'high'
    
    return comparison


def generate_report(comparison: Dict) -> str:
    """Generate markdown report"""
    a = comparison['round_a']
    b = comparison['round_b']
    imp = comparison['improvements']
    
    lines = [
        "# Task-1 Inheritance Effectiveness: Comparison Report",
        "",
        f"**Verdict**: {comparison['verdict']} (confidence: {comparison['confidence']})",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Round A (Control) | Round B (Inheritance) | Improvement |",
        "|--------|-------------------|----------------------|-------------|",
        f"| Bridge Pass Rate | {a['bridge_pass_rate']:.1%} | {b['bridge_pass_rate']:.1%} | {imp['bridge_pass_rate_pp']:+.1f}pp |",
        f"| Mainline Approve Rate | {a['mainline_approve_rate']:.1%} | {b['mainline_approve_rate']:.1%} | {imp['mainline_approve_rate_pp']:+.1f}pp |",
        f"| Mean Throughput Δ | {a['mean_throughput_delta']:.3f} | {b['mean_throughput_delta']:.3f} | {imp['throughput_delta_change']:+.3f} |",
        f"| Throughput Variance | {a['throughput_variance']:.6f} | {b['throughput_variance']:.6f} | {imp['variance_reduction']:+.6f} |",
        "",
        "## Success Criteria",
        "",
        "| Criterion | Target | Achieved | Status |",
        "|-----------|--------|----------|--------|",
    ]
    
    # Check each criterion
    if imp['bridge_pass_rate_pp'] >= 10:
        lines.append(f"| Bridge +10pp | +10pp | {imp['bridge_pass_rate_pp']:+.1f}pp | ✅ |")
    elif imp['bridge_pass_rate_pp'] >= 5:
        lines.append(f"| Bridge +10pp | +10pp | {imp['bridge_pass_rate_pp']:+.1f}pp | ⚠️ Partial |")
    else:
        lines.append(f"| Bridge +10pp | +10pp | {imp['bridge_pass_rate_pp']:+.1f}pp | ❌ |")
    
    if imp['mainline_approve_rate_pp'] >= 10:
        lines.append(f"| Mainline +10pp | +10pp | {imp['mainline_approve_rate_pp']:+.1f}pp | ✅ |")
    elif imp['mainline_approve_rate_pp'] >= 5:
        lines.append(f"| Mainline +10pp | +10pp | {imp['mainline_approve_rate_pp']:+.1f}pp | ⚠️ Partial |")
    else:
        lines.append(f"| Mainline +10pp | +10pp | {imp['mainline_approve_rate_pp']:+.1f}pp | ❌ |")
    
    if imp['throughput_delta_change'] >= 0.005:
        lines.append(f"| Throughput +0.5% | >+0.5% | {imp['throughput_delta_change']:+.3f} | ✅ |")
    elif imp['throughput_delta_change'] >= 0.003:
        lines.append(f"| Throughput +0.5% | >+0.5% | {imp['throughput_delta_change']:+.3f} | ⚠️ Partial |")
    else:
        lines.append(f"| Throughput +0.5% | >+0.5% | {imp['throughput_delta_change']:+.3f} | ❌ |")
    
    lines.extend([
        "",
        "## Interpretation",
        "",
    ])
    
    if comparison['verdict'] == 'EFFECTIVE':
        lines.append("The Task-1 inheritance package **demonstrably improves** search quality.")
        lines.append("Fast Genesis should continue to use and refine this package.")
        lines.append("")
        lines.append("**Recommendation**: Productionize inheritance for Task-1.")
    elif comparison['verdict'] == 'PROMISING':
        lines.append("The inheritance package shows **some positive signals** but not conclusive.")
        lines.append("More data or refined priors may be needed.")
        lines.append("")
        lines.append("**Recommendation**: Collect more results before final decision.")
    else:
        lines.append("The inheritance package **does not significantly improve** search quality.")
        lines.append("Possible causes: poor priors, wrong parameters, or task-specific issues.")
        lines.append("")
        lines.append("**Recommendation**: Redesign inheritance extraction or try different task.")
    
    lines.extend([
        "",
        "## Raw Data",
        "",
        "```json",
        json.dumps(comparison, indent=2),
        "```"
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Compare Round A vs Round B')
    parser.add_argument('--round-a', required=True, help='Round A directory')
    parser.add_argument('--round-b', required=True, help='Round B directory')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--report', help='Output markdown report')
    
    args = parser.parse_args()
    
    comparison = compare_rounds(args.round_a, args.round_b)
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump(comparison, f, indent=2)
    print(f"✓ Comparison saved to: {args.output}")
    
    # Generate and save report
    if args.report:
        report = generate_report(comparison)
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"✓ Report saved to: {args.report}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"VERDICT: {comparison['verdict']} ({comparison['confidence']} confidence)")
    print(f"{'='*60}")
    print(f"Bridge pass rate: {comparison['improvements']['bridge_pass_rate_pp']:+.1f}pp")
    print(f"Mainline approve rate: {comparison['improvements']['mainline_approve_rate_pp']:+.1f}pp")
    print(f"Throughput delta change: {comparison['improvements']['throughput_delta_change']:+.3f}")


if __name__ == "__main__":
    main()