#!/usr/bin/env python3
"""
Quick test of Task-1 Mainline Validator
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/mainline')

from task1_mainline_validator import Task1MainlineValidator, MainlineMetrics


def test_decision_logic():
    """Test decision making with mock metrics"""
    print("Testing decision logic...")
    
    validator = Task1MainlineValidator()
    
    # Test case 1: Strong candidate (should APPROVE)
    strong = MainlineMetrics(
        candidate_id="test_strong",
        throughput_mean=0.025, throughput_std=0.001, throughput_min=0.024, throughput_max=0.026,
        throughput_delta=0.0036,
        latency_mean=230.0, latency_std=5.0, latency_delta=-23.9,
        recovery_time_mean=250.0, recovery_time_delta=-39.5,
        switching_rate_mean=0.0025, switching_delta=-0.0011,
        stability_cv=0.60, variance_cv=0.04,
        missed_deadline_rate=0.88, missed_delta=-0.0288,
        seeds_tested=10
    )
    
    decision, rationale = validator._make_decision(strong)
    print(f"  Strong candidate: {decision} - {rationale}")
    assert decision == "APPROVE", f"Expected APPROVE, got {decision}"
    
    # Test case 2: Weak candidate (should REJECT)
    weak = MainlineMetrics(
        candidate_id="test_weak",
        throughput_mean=0.018, throughput_std=0.002, throughput_min=0.015, throughput_max=0.021,
        throughput_delta=-0.0034,
        latency_mean=280.0, latency_std=10.0, latency_delta=26.1,
        recovery_time_mean=320.0, recovery_time_delta=30.5,
        switching_rate_mean=0.005, switching_delta=0.0014,
        stability_cv=0.75, variance_cv=0.11,
        missed_deadline_rate=0.95, missed_delta=0.0412,
        seeds_tested=10
    )
    
    decision, rationale = validator._make_decision(weak)
    print(f"  Weak candidate: {decision} - {rationale}")
    assert decision == "REJECT", f"Expected REJECT, got {decision}"
    
    print("✓ Decision logic tests passed")


def test_with_real_candidate():
    """Test with a real candidate from simulator"""
    print("\nTesting with real candidate (100 tasks, 3 seeds for speed)...")
    
    # Create test candidate
    candidate = {
        "id": "adaptive_test_v1",
        "trust_decay": 0.1,
        "trust_recovery": 0.05,
        "family": "F_P3T4M4"
    }
    
    validator = Task1MainlineValidator(output_dir="/tmp/test_mainline")
    
    try:
        metrics, decision, rationale = validator.evaluate_candidate(
            candidate,
            num_tasks=100,  # Small for testing
            num_seeds=3
        )
        
        print(f"  Throughput: {metrics.throughput_mean:.2%} (Δ={metrics.throughput_delta:+.2%})")
        print(f"  Latency: {metrics.latency_mean:.1f} ms (Δ={metrics.latency_delta:+.1f})")
        print(f"  Decision: {decision}")
        print(f"  Rationale: {rationale}")
        print("✓ Real candidate evaluation passed")
        
    except Exception as e:
        print(f"  ⚠ Evaluation error: {e}")
        import traceback
        traceback.print_exc()


def test_baseline_vs_adaptive():
    """Compare baseline vs adaptive through Mainline"""
    print("\nComparing baseline vs adaptive (100 tasks, 3 seeds)...")
    
    validator = Task1MainlineValidator(output_dir="/tmp/test_mainline")
    
    # Baseline candidate (no adaptation)
    baseline_candidate = {
        "id": "baseline_sjf",
        "trust_decay": 0.0,
        "trust_recovery": 0.0
    }
    
    # Adaptive candidate
    adaptive_candidate = {
        "id": "adaptive_trust",
        "trust_decay": 0.1,
        "trust_recovery": 0.05
    }
    
    results = []
    
    for name, cand in [("baseline", baseline_candidate), ("adaptive", adaptive_candidate)]:
        print(f"\n  Running {name}...")
        try:
            metrics, decision, rationale = validator.evaluate_candidate(
                cand, num_tasks=100, num_seeds=3
            )
            results.append((name, metrics, decision))
            print(f"    Throughput: {metrics.throughput_mean:.2%}")
            print(f"    Decision: {decision}")
        except Exception as e:
            print(f"    Error: {e}")
    
    if len(results) == 2:
        base_tp = results[0][1].throughput_mean
        adap_tp = results[1][1].throughput_mean
        improvement = (adap_tp - base_tp) / base_tp * 100 if base_tp > 0 else 0
        
        print(f"\n  Comparison:")
        print(f"    Baseline: {base_tp:.2%}")
        print(f"    Adaptive: {adap_tp:.2%}")
        print(f"    Improvement: {improvement:+.1f}%")
        
        if improvement > 0:
            print("✓ Adaptive shows improvement over baseline")
        else:
            print("⚠ No improvement detected")


if __name__ == "__main__":
    print("="*70)
    print("TASK-1 MAINLINE VALIDATOR TESTS")
    print("="*70)
    
    test_decision_logic()
    test_with_real_candidate()
    test_baseline_vs_adaptive()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)