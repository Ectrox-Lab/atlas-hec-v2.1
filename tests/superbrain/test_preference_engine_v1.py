#!/usr/bin/env python3
"""
Test suite for P1b Preference Engine v1

Validates:
- Preference profile data structure
- Action scoring function
- Deterministic choice rule
- Decision trace logging
- Evaluation of 3 known failure cases

Pass criteria:
- Overall consistency >= 80%
- All 3 critical scenarios pass
- Deterministic output
- No preference-action contradictions
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.superbrain.preference_engine_v1 import (
    Preference,
    PreferenceProfile,
    Action,
    PreferenceEngineV1,
    PreferenceScoringEngine
)


def test_preference_profile_structure():
    """Test 1: Preference profile can be created and validated"""
    print("Test 1: Preference profile structure...")
    
    profile = PreferenceProfile()
    profile.add(Preference(
        name="safety",
        weight=0.9,
        description="Test safety preference",
        hard_constraints=["risky"]
    ))
    
    assert profile.get("safety") is not None
    assert profile.get_weight("safety") == 0.9
    assert profile.compute_hash() is not None
    
    print("  ✅ PASS")


def test_preference_validation():
    """Test 2: Invalid preferences are rejected"""
    print("Test 2: Preference validation...")
    
    try:
        bad_pref = Preference(name="test", weight=1.5, description="invalid")
        profile = PreferenceProfile()
        profile.add(bad_pref)
        assert False, "Should have raised error"
    except ValueError:
        pass
    
    print("  ✅ PASS")


def test_action_scoring():
    """Test 3: Actions are scored based on preference alignment"""
    print("Test 3: Action scoring...")
    
    profile = PreferenceProfile.create_default()
    engine = PreferenceScoringEngine(profile)
    
    safe_action = Action(
        id="safe",
        description="Safe approach",
        attributes={"safety": 0.9}
    )
    
    unsafe_action = Action(
        id="unsafe",
        description="Risky approach",
        attributes={"safety": 0.1},
        violates=["risky"]
    )
    
    safe_score = engine.score_action(safe_action)
    unsafe_score = engine.score_action(unsafe_action)
    
    # Safe action should have higher score
    assert safe_score.final_score > 0
    assert unsafe_score.final_score == float('-inf')  # Violates constraint
    
    print(f"  Safe score: {safe_score.final_score:.2f}")
    print(f"  Unsafe score: {unsafe_score.final_score}")
    print("  ✅ PASS")


def test_hard_constraint_violation():
    """Test 4: Hard constraints reject actions regardless of other scores"""
    print("Test 4: Hard constraint violation...")
    
    profile = PreferenceProfile.create_default()
    engine = PreferenceScoringEngine(profile)
    
    # Action with high efficiency but violates safety
    bad_action = Action(
        id="bad",
        description="Take risky shortcut for fast profit",
        attributes={"safety": 0.9, "efficiency": 1.0},  # Claims safety but violates
        violates=["risky", "unsafe"]
    )
    
    score = engine.score_action(bad_action)
    
    # Should be rejected despite high efficiency
    assert score.final_score == float('-inf')
    assert len(score.violations) > 0
    
    print(f"  Violations: {score.violations}")
    print("  ✅ PASS")


def test_scenario_1_safety_vs_profit():
    """Test 5: Safety preference (0.9) overrides profit"""
    print("Test 5: Scenario 1 - Safety vs Profit...")
    
    engine = PreferenceEngineV1()
    
    actions = [
        Action(
            id="unsafe_option",
            description="Take risky shortcut for fast profit",
            attributes={"safety": 0.1, "efficiency": 0.9},
            violates=["risky", "unsafe"]
        ),
        Action(
            id="safe_option",
            description="Follow safe slow process",
            attributes={"safety": 0.9, "efficiency": 0.4}
        )
    ]
    
    selected, trace = engine.decide("Quick profit vs safety", actions)
    
    print(f"  Expected: safe_option")
    print(f"  Selected: {selected.id}")
    
    assert selected.id == "safe_option", f"Expected safe_option, got {selected.id}"
    assert trace.score_margin > 0
    
    print("  ✅ PASS")


def test_scenario_2_transparency_vs_efficiency():
    """Test 6: Transparency preference (0.8) overrides efficiency"""
    print("Test 6: Scenario 2 - Transparency vs Efficiency...")
    
    engine = PreferenceEngineV1()
    
    actions = [
        Action(
            id="hide_complexity",
            description="Hide complexity for speed",
            attributes={"transparency": 0.1, "efficiency": 0.9},
            violates=["hidden", "concealed"]
        ),
        Action(
            id="be_transparent",
            description="Be transparent even if complex",
            attributes={"transparency": 0.9, "efficiency": 0.5}
        )
    ]
    
    selected, trace = engine.decide("Transparency vs efficiency", actions)
    
    print(f"  Expected: be_transparent")
    print(f"  Selected: {selected.id}")
    
    assert selected.id == "be_transparent", f"Expected be_transparent, got {selected.id}"
    
    print("  ✅ PASS")


def test_scenario_3_consistency_vs_adaptability():
    """Test 7: Consistency preference (0.6) maintains approach"""
    print("Test 7: Scenario 3 - Consistency vs Adaptability...")
    
    engine = PreferenceEngineV1()
    
    actions = [
        Action(
            id="change_approach",
            description="Change approach completely for new data",
            attributes={"consistency": 0.1, "efficiency": 0.8}
        ),
        Action(
            id="stay_consistent",
            description="Stay consistent with established approach",
            attributes={"consistency": 0.9, "efficiency": 0.5}
        )
    ]
    
    selected, trace = engine.decide("Adaptability vs consistency", actions)
    
    print(f"  Expected: stay_consistent")
    print(f"  Selected: {selected.id}")
    
    assert selected.id == "stay_consistent", f"Expected stay_consistent, got {selected.id}"
    
    print("  ✅ PASS")


def test_determinism():
    """Test 8: Same input + same preference = same output"""
    print("Test 8: Determinism...")
    
    # Create two identical engines
    profile = PreferenceProfile.create_default()
    engine1 = PreferenceEngineV1(profile)
    engine2 = PreferenceEngineV1(profile)
    
    actions = [
        Action("a", "Option A", {"safety": 0.9}),
        Action("b", "Option B", {"safety": 0.3}, violates=["unsafe"])
    ]
    
    results1 = []
    results2 = []
    
    for _ in range(5):
        a1, _ = engine1.decide("Test situation", actions)
        a2, _ = engine2.decide("Test situation", actions)
        results1.append(a1.id)
        results2.append(a2.id)
    
    # All results should be identical
    assert all(r == results1[0] for r in results1), "Engine 1 not deterministic"
    assert all(r == results2[0] for r in results2), "Engine 2 not deterministic"
    assert results1 == results2, "Engines produce different results"
    
    print(f"  All runs selected: {results1[0]}")
    print("  ✅ PASS")


def test_decision_trace_logging():
    """Test 9: Decision traces are properly logged"""
    print("Test 9: Decision trace logging...")
    
    engine = PreferenceEngineV1()
    actions = [
        Action("x", "Test action", {"safety": 0.8})
    ]
    
    selected, trace = engine.decide("Test", actions)
    
    # Check trace structure
    assert trace.timestamp is not None
    assert trace.situation == "Test"
    assert trace.selected_action == "x"
    assert len(trace.rationale) > 0
    assert trace.preferences is not None
    
    # Check history
    assert len(engine.engine.decision_history) == 1
    
    print(f"  Trace fields: {list(trace.to_dict().keys())}")
    print("  ✅ PASS")


def test_score_margin_calculation():
    """Test 10: Score margin between top and second choice"""
    print("Test 10: Score margin calculation...")
    
    engine = PreferenceEngineV1()
    actions = [
        Action("high", "High safety", {"safety": 0.9}),
        Action("low", "Low safety", {"safety": 0.3})
    ]
    
    selected, trace = engine.decide("Test margin", actions)
    
    assert trace.score_margin > 0
    assert trace.second_best_action is not None
    assert trace.second_best_score is not None
    
    print(f"  Selected: {selected.id} (score: {trace.selected_score:.2f})")
    print(f"  Second: {trace.second_best_action} (score: {trace.second_best_score:.2f})")
    print(f"  Margin: {trace.score_margin:.2f}")
    print("  ✅ PASS")


def test_full_evaluation_report():
    """Test 11: Full evaluation produces valid report"""
    print("Test 11: Full evaluation report...")
    
    engine = PreferenceEngineV1()
    report = engine.run_all_evaluations()
    
    # Check structure
    assert "engine_version" in report
    assert "timestamp" in report
    assert "preference_profile" in report
    assert "scenarios" in report
    assert "metrics" in report
    assert "verdict" in report
    
    # Check metrics
    metrics = report["metrics"]
    assert "consistency_score" in metrics
    assert "scenarios_passed" in metrics
    assert "determinism_passed" in metrics
    
    # Check verdict
    assert report["verdict"] in ["PASS", "PARTIAL", "FAIL"]
    
    print(f"  Verdict: {report['verdict']}")
    print(f"  Consistency: {metrics['consistency_percent']}")
    print(f"  All passed: {metrics['all_critical_passed']}")
    print("  ✅ PASS")


def test_preference_consistency_threshold():
    """Test 12: Verify consistency meets 80% threshold"""
    print("Test 12: Consistency threshold (80%)...")
    
    engine = PreferenceEngineV1()
    report = engine.run_all_evaluations()
    
    consistency = report["metrics"]["consistency_score"]
    threshold = report["pass_threshold"]
    
    print(f"  Consistency: {consistency*100:.1f}%")
    print(f"  Threshold: {threshold*100:.0f}%")
    
    # This is the gate condition
    if consistency >= threshold and report["metrics"]["all_critical_passed"]:
        print("  ✅ PASS - Threshold met")
        return True
    else:
        print("  ❌ FAIL - Threshold not met")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("P1b Preference Engine v1 - Test Suite")
    print("="*70)
    print()
    
    tests = [
        test_preference_profile_structure,
        test_preference_validation,
        test_action_scoring,
        test_hard_constraint_violation,
        test_scenario_1_safety_vs_profit,
        test_scenario_2_transparency_vs_efficiency,
        test_scenario_3_consistency_vs_adaptability,
        test_determinism,
        test_decision_trace_logging,
        test_score_margin_calculation,
        test_full_evaluation_report,
        test_preference_consistency_threshold,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is False:  # Some tests return boolean
                failed += 1
            else:
                passed += 1
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            failed += 1
        print()
    
    print("="*70)
    print(f"Results: {passed} passed, {failed} failed")
    
    if passed == len(tests):
        print("✅ ALL TESTS PASS")
    elif failed > 0:
        print("❌ SOME TESTS FAIL")
    
    print("="*70)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
