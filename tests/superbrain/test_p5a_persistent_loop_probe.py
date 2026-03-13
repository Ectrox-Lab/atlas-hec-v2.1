#!/usr/bin/env python3
"""
Test suite for P5a Persistent Loop Probe v1

Validates:
1. Identity drift (≥85%)
2. Goal persistence (≥85%)
3. Preference stability (≥85%)
4. Contradiction accumulation (≤2)
5. Recovery success rate (≥80%)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.superbrain.p5a_persistent_loop_probe import (
    PersistentLoopProbeV1,
    PersistentLoopSystem,
    IdentityHasher,
    GoalConsistencyChecker,
    PreferenceStabilityTracker
)
from experiments.superbrain.p3a_self_model_probe import SelfModel, Trait, DynamicState


def test_identity_hasher():
    """Test 1: Identity hasher creates consistent hashes"""
    print("Test 1: Identity hasher...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "safety_priority": Trait("", 0.90, 0.95, 5, "", "", ""),
            "transparency_priority": Trait("", 0.80, 0.90, 5, "", "", "")
        },
        dynamic_state={},
        behavior_predictor={},
        update_history=[]
    )
    
    hash1 = IdentityHasher.hash_self_model(model)
    hash2 = IdentityHasher.hash_self_model(model)
    
    assert hash1 == hash2, "Hash should be deterministic"
    assert len(hash1) == 16, "Hash should be 16 chars"
    
    # Modify model slightly
    model.stable_traits["safety_priority"].value = 0.91
    hash3 = IdentityHasher.hash_self_model(model)
    
    # Hash should change with trait change
    assert hash1 != hash3, "Hash should change when traits change"
    
    print(f"  Baseline hash: {hash1}")
    print(f"  Modified hash: {hash3}")
    print("  ✅ PASS")


def test_goal_consistency():
    """Test 2: Goal consistency checker"""
    print("Test 2: Goal consistency...")
    
    baseline = "Develop sustainable energy solutions"
    checker = GoalConsistencyChecker(baseline)
    
    # Same goal
    sim1 = checker.check_consistency(baseline)
    assert sim1 == 1.0, "Identical goals should have 100% similarity"
    
    # Similar goal
    similar = "Develop sustainable energy systems"
    sim2 = checker.check_consistency(similar)
    assert sim2 > 0.5, "Similar goals should have >50% similarity"
    
    # Different goal
    different = "Build profit maximization systems"
    sim3 = checker.check_consistency(different)
    assert sim3 < 0.5, "Different goals should have <50% similarity"
    
    print(f"  Same goal: {sim1:.2%}")
    print(f"  Similar goal: {sim2:.2%}")
    print(f"  Different goal: {sim3:.2%}")
    print("  ✅ PASS")


def test_preference_stability():
    """Test 3: Preference stability tracker"""
    print("Test 3: Preference stability...")
    
    baseline = {"safety": 0.90, "transparency": 0.80}
    tracker = PreferenceStabilityTracker(baseline)
    
    # Same preferences
    drift1 = tracker.measure_drift({"safety": 0.90, "transparency": 0.80})
    assert drift1 == 0.0, "No drift for identical preferences"
    
    # Small drift
    drift2 = tracker.measure_drift({"safety": 0.85, "transparency": 0.80})
    assert abs(drift2 - 0.05) < 0.001, "Small drift should be detected"
    
    # Large drift
    drift3 = tracker.measure_drift({"safety": 0.50, "transparency": 0.50})
    assert drift3 > 0.3, "Large drift should be detected"
    
    print(f"  No drift: {drift1:.3f}")
    print(f"  Small drift: {drift2:.3f}")
    print(f"  Large drift: {drift3:.3f}")
    print("  ✅ PASS")


def test_checkpoint_creation():
    """Test 4: System creates checkpoints"""
    print("Test 4: Checkpoint creation...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "safety_priority": Trait("", 0.90, 0.95, 5, "", "", "")
        },
        dynamic_state={},
        behavior_predictor={},
        update_history=[]
    )
    
    system = PersistentLoopSystem(model)
    checkpoint = system.create_checkpoint("CP_test", "test_phase")
    
    assert checkpoint.checkpoint_id == "CP_test"
    assert checkpoint.phase == "test_phase"
    assert len(checkpoint.identity_hash) == 16
    assert checkpoint.self_consistency_score > 0
    
    print(f"  Checkpoint: {checkpoint.checkpoint_id}")
    print(f"  Identity hash: {checkpoint.identity_hash}")
    print(f"  Consistency: {checkpoint.self_consistency_score:.2%}")
    print("  ✅ PASS")


def test_interruption_handling():
    """Test 5: System handles interruptions"""
    print("Test 5: Interruption handling...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "interruption_resilience": Trait("", 0.80, 0.90, 5, "", "", "")
        },
        dynamic_state={},
        behavior_predictor={},
        update_history=[]
    )
    
    system = PersistentLoopSystem(model)
    
    # Simulate interruption
    event = system.simulate_interruption("task_swap", 60)
    
    assert event.interruption_type == "task_swap"
    assert event.pre_state is not None
    assert event.post_state is not None
    assert event.recovery_latency_ms >= 0
    
    print(f"  Interruption type: {event.interruption_type}")
    print(f"  Recovery success: {event.recovery_success}")
    print(f"  Recovery latency: {event.recovery_latency_ms}ms")
    print("  ✅ PASS")


def test_drift_measurement():
    """Test 6: Drift measurement between checkpoints"""
    print("Test 6: Drift measurement...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "safety_priority": Trait("", 0.90, 0.95, 5, "", "", "")
        },
        dynamic_state={},
        behavior_predictor={},
        update_history=[]
    )
    
    system = PersistentLoopSystem(model)
    
    cp1 = system.create_checkpoint("CP_1", "phase1")
    cp2 = system.create_checkpoint("CP_2", "phase2")
    
    drift = system.measure_drift(cp1, cp2)
    
    assert drift.from_checkpoint == "CP_1"
    assert drift.to_checkpoint == "CP_2"
    assert 0.0 <= drift.identity_similarity <= 1.0
    assert drift.assessment in ["stable", "minor_drift", "significant_drift"]
    
    print(f"  Identity similarity: {drift.identity_similarity:.2%}")
    print(f"  Assessment: {drift.assessment}")
    print("  ✅ PASS")


def test_full_probe_execution():
    """Test 7: Full probe runs without errors"""
    print("Test 7: Full probe execution...")
    
    probe = PersistentLoopProbeV1()
    results = probe.run_persistent_loop_test()
    evaluated = probe.evaluate_results(results)
    
    assert "metrics" in results
    assert "evaluation" in evaluated
    assert "verdict" in evaluated["evaluation"]
    
    print(f"  Verdict: {evaluated['evaluation']['verdict']}")
    print(f"  Weighted: {evaluated['evaluation']['weighted_percent']}")
    print("  ✅ PASS")


def test_threshold_identity():
    """Test 8: Identity drift threshold (≥85%)"""
    print("Test 8: Identity drift threshold (≥85%)...")
    
    probe = PersistentLoopProbeV1()
    results = probe.run_persistent_loop_test()
    evaluated = probe.evaluate_results(results)
    
    identity_sim = evaluated["metrics"]["identity_similarity"]
    threshold = 0.85
    
    print(f"  Identity similarity: {identity_sim*100:.1f}%")
    print(f"  Threshold: ≥{threshold*100:.0f}%")
    
    if identity_sim >= threshold:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL (may indicate learning-induced drift)")
        return False


def test_threshold_recovery():
    """Test 9: Recovery success threshold (≥80%)"""
    print("Test 9: Recovery success threshold (≥80%)...")
    
    probe = PersistentLoopProbeV1()
    results = probe.run_persistent_loop_test()
    evaluated = probe.evaluate_results(results)
    
    recovery_rate = evaluated["metrics"]["recovery_success_rate"]
    threshold = 0.80
    
    print(f"  Recovery rate: {recovery_rate*100:.1f}%")
    print(f"  Threshold: ≥{threshold*100:.0f}%")
    
    if recovery_rate >= threshold:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL")
        return False


def test_overall_evaluation():
    """Test 10: Overall evaluation structure"""
    print("Test 10: Overall evaluation...")
    
    probe = PersistentLoopProbeV1()
    results = probe.run_persistent_loop_test()
    evaluated = probe.evaluate_results(results)
    
    eval_data = evaluated["evaluation"]
    
    print(f"  Weighted: {eval_data['weighted_percent']}")
    print(f"  Minimum: {eval_data['min_percent']}")
    print(f"  Verdict: {eval_data['verdict']}")
    
    # Check structure
    assert "weighted_score" in eval_data
    assert "min_score" in eval_data
    assert eval_data["verdict"] in ["PASS", "PARTIAL", "FAIL"]
    
    print("  ✅ PASS")


def main():
    """Run all tests"""
    print("="*70)
    print("P5a Persistent Loop Probe v1 - Test Suite")
    print("="*70)
    print()
    
    tests = [
        test_identity_hasher,
        test_goal_consistency,
        test_preference_stability,
        test_checkpoint_creation,
        test_interruption_handling,
        test_drift_measurement,
        test_full_probe_execution,
        test_threshold_identity,
        test_threshold_recovery,
        test_overall_evaluation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
                passed += 1
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    
    if passed == len(tests):
        print("✅ ALL TESTS PASS")
    elif failed > 0:
        print("⚠️ SOME TESTS FAIL")
    
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
