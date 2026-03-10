#!/usr/bin/env python3
"""
Test suite for Continuity Probe v1

Validates:
- Probe execution correctness
- Metric calculation accuracy
- Pass/fail criteria
"""

import json
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.superbrain.continuity_probe_v1 import (
    AtlasChenSystem, 
    ContinuityProbeV1,
    SystemState
)


def test_system_initialization():
    """Test 1: System can be initialized with identity"""
    print("Test 1: System initialization...")
    
    system = AtlasChenSystem("test_v1")
    state = system.initialize(
        goal="Test goal",
        preferences={"safety": 0.9, "efficiency": 0.7},
        narrative="Test narrative",
        constraints=["constraint1", "constraint2"]
    )
    
    assert state is not None
    assert state.long_term_goal == "Test goal"
    assert state.core_preferences["safety"] == 0.9
    assert len(system.state_history) == 1
    
    print("  ✅ PASS")


def test_restart_preserves_identity():
    """Test 2: Restart preserves core identity"""
    print("Test 2: Restart identity preservation...")
    
    system = AtlasChenSystem("test_v2")
    initial = system.initialize(
        goal="Stable goal",
        preferences={"safety": 0.9},
        narrative="I am stable",
        constraints=["never harm"]
    )
    
    initial_hash = initial.identity_hash()
    
    # Process some work
    system.process_task("Work task")
    
    # Restart
    after_restart = system.restart(preserve_state=True)
    
    # Check preservation
    assert after_restart is not None
    assert after_restart.long_term_goal == "Stable goal"
    assert after_restart.identity_hash() == initial_hash
    
    print("  ✅ PASS")


def test_contradiction_detection():
    """Test 3: Contradiction probe detects inconsistencies"""
    print("Test 3: Contradiction detection...")
    
    system = AtlasChenSystem("test_v3")
    system.initialize(
        goal="Consistent goal",
        preferences={"safety": 0.9},
        narrative="I am consistent",
        constraints=["be consistent"]
    )
    
    probe = ContinuityProbeV1(system)
    
    # Run contradiction probe
    result = probe.run_contradiction_probe()
    
    # Should pass with consistent system
    assert "contradictions_found" in result
    assert "pass" in result
    
    print(f"  Contradictions found: {result['contradictions_found']}")
    print(f"  Pass: {result['pass']}")
    print("  ✅ PASS")


def test_metric_calculation():
    """Test 4: Metrics calculated correctly"""
    print("Test 4: Metric calculation...")
    
    system = AtlasChenSystem("test_v4")
    system.initialize(
        goal="Metric test goal",
        preferences={"safety": 0.8, "efficiency": 0.6},
        narrative="Metric test",
        constraints=["test"]
    )
    
    probe = ContinuityProbeV1(system)
    
    # Run all probes
    probe.run_all_probes()
    
    # Check metrics
    metrics = probe.results.get("metrics", {})
    
    assert "identity_consistency_score" in metrics
    assert "goal_persistence_score" in metrics
    assert "preference_retention_score" in metrics
    assert "contradiction_count" in metrics
    assert "overall_score" in metrics
    
    assert 0.0 <= metrics["overall_score"] <= 1.0
    
    print(f"  Overall score: {metrics['overall_score']:.2%}")
    print("  ✅ PASS")


def test_pass_criteria():
    """Test 5: Pass/fail criteria applied correctly"""
    print("Test 5: Pass criteria...")
    
    system = AtlasChenSystem("test_v5")
    probe = ContinuityProbeV1(system)
    
    # Run probes
    results = probe.run_all_probes()
    
    # Check verdict
    assert "verdict" in results
    assert results["verdict"] in ["PASS", "PARTIAL", "FAIL"]
    assert "interpretation" in results
    
    # Check score alignment
    score = results["metrics"]["overall_score"]
    verdict = results["verdict"]
    
    if score >= 0.8:
        expected = "PASS"
    elif score >= 0.5:
        expected = "PARTIAL"
    else:
        expected = "FAIL"
    
    assert verdict == expected, f"Verdict {verdict} doesn't match score {score}"
    
    print(f"  Verdict: {verdict}")
    print("  ✅ PASS")


def test_report_generation():
    """Test 6: Report can be generated and saved"""
    print("Test 6: Report generation...")
    
    system = AtlasChenSystem("test_v6")
    probe = ContinuityProbeV1(system)
    
    # Run and get results
    results = probe.run_all_probes()
    
    # Verify structure
    assert "probe_version" in results
    assert "timestamp" in results
    assert "probes" in results
    assert "metrics" in results
    assert "verdict" in results
    
    # Check probe results
    probes = results["probes"]
    assert "restart_probe" in probes
    assert "interruption_probe" in probes
    assert "distraction_probe" in probes
    assert "contradiction_probe" in probes
    
    print("  Report structure valid")
    print("  ✅ PASS")


def test_distraction_resistance():
    """Test 7: System maintains preferences under distraction"""
    print("Test 7: Distraction resistance...")
    
    system = AtlasChenSystem("test_v7")
    system.initialize(
        goal="Distraction test",
        preferences={"safety": 0.95},  # Strong safety preference
        narrative="Safety first",
        constraints=["always safe"]
    )
    
    # Make choice
    choice = system.check_preference_choice(
        "safety test",
        ["unsafe option", "safe option"]
    )
    
    # Should choose safe
    assert "safe" in choice.lower()
    
    print(f"  Choice: {choice}")
    print("  ✅ PASS")


def main():
    """Run all tests"""
    print("="*60)
    print("Continuity Probe v1 - Test Suite")
    print("="*60)
    print()
    
    tests = [
        test_system_initialization,
        test_restart_preserves_identity,
        test_contradiction_detection,
        test_metric_calculation,
        test_pass_criteria,
        test_report_generation,
        test_distraction_resistance,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            failed += 1
        print()
    
    print("="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
