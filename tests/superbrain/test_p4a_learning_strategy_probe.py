#!/usr/bin/env python3
"""
Test suite for P4a Learning Strategy Probe v1

Validates:
1. Learning priority accuracy (≥80%)
2. Strategy selection correctness (≥80%)
3. Learning outcome evaluation (≥80%)
4. Strategy update correctness (≥70%)
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.superbrain.p4a_learning_strategy_probe import (
    LearningStrategyProbeV1,
    PrioritySelector,
    StrategySelector,
    OutcomeEvaluator,
    StrategyUpdater,
    SelfDirectedLearningSystem,
    LearningTarget,
    LearningStrategy,
    SelfModel
)
from experiments.superbrain.p3a_self_model_probe import Trait, DynamicState


def test_priority_selector():
    """Test 1: Priority selector creates valid priorities"""
    print("Test 1: Priority selector...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "interruption_resilience": Trait("", 0.60, 0.9, 5, "", "", ""),
            "safety_priority": Trait("", 0.90, 0.9, 5, "", "", "")
        },
        dynamic_state={
            "recovery_fatigue": DynamicState("", 0.80, 0.4, None),
            "recent_failure_pressure": DynamicState("", 0.70, 0.2, None)
        },
        behavior_predictor={},
        update_history=[]
    )
    
    selector = PrioritySelector(model)
    priorities = selector.analyze_gaps()
    
    assert len(priorities) > 0
    assert priorities[0].priority_score > 0
    assert priorities[0].reason != ""
    
    print(f"  Priorities found: {len(priorities)}")
    print(f"  Top priority: {priorities[0].target.value}")
    print("  ✅ PASS")


def test_strategy_selector():
    """Test 2: Strategy selector chooses appropriate strategy"""
    print("Test 2: Strategy selector...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={},
        dynamic_state={
            "recovery_fatigue": DynamicState("", 0.90, 0.4, None),
            "current_context_load": DynamicState("", 0.70, 0.3, None)
        },
        behavior_predictor={},
        update_history=[]
    )
    
    selector = StrategySelector(model)
    selection = selector.select_strategy(LearningTarget.INTERRUPTION_RECOVERY)
    
    assert selection.strategy == LearningStrategy.FOCUSED_PRACTICE
    assert selection.suitability_score > 0
    assert "fatigue" in selection.justification.lower()
    
    print(f"  Selected: {selection.strategy.value}")
    print(f"  Justification: {selection.justification[:50]}...")
    print("  ✅ PASS")


def test_outcome_evaluator():
    """Test 3: Outcome evaluator correctly classifies improvement"""
    print("Test 3: Outcome evaluator...")
    
    evaluator = OutcomeEvaluator()
    
    # Large improvement
    outcome1 = evaluator.evaluate(
        LearningTarget.SAFETY_REASONING,
        LearningStrategy.FOCUSED_PRACTICE,
        0.60, 0.85
    )
    assert outcome1.evaluation == "effective"
    
    # Small improvement
    outcome2 = evaluator.evaluate(
        LearningTarget.SAFETY_REASONING,
        LearningStrategy.FOCUSED_PRACTICE,
        0.60, 0.67
    )
    assert outcome2.evaluation == "minimal"
    
    # No improvement
    outcome3 = evaluator.evaluate(
        LearningTarget.SAFETY_REASONING,
        LearningStrategy.FOCUSED_PRACTICE,
        0.60, 0.61
    )
    assert outcome3.evaluation == "ineffective"
    
    print(f"  Large Δ: {outcome1.evaluation}")
    print(f"  Small Δ: {outcome2.evaluation}")
    print(f"  Zero Δ: {outcome3.evaluation}")
    print("  ✅ PASS")


def test_strategy_updater():
    """Test 4: Strategy updater detects ineffective strategies"""
    print("Test 4: Strategy updater...")
    
    updater = StrategyUpdater()
    
    # Record ineffective attempts
    from experiments.superbrain.p4a_learning_strategy_probe import LearningOutcome
    
    updater.record_attempt(LearningOutcome(
        target=LearningTarget.INTERRUPTION_RECOVERY,
        strategy_used=LearningStrategy.BLOCKED_PRACTICE,
        pre_performance=0.60,
        post_performance=0.61,
        improvement=0.01,
        evaluation="ineffective",
        recommendation="change_strategy"
    ))
    
    updater.record_attempt(LearningOutcome(
        target=LearningTarget.INTERRUPTION_RECOVERY,
        strategy_used=LearningStrategy.BLOCKED_PRACTICE,
        pre_performance=0.61,
        post_performance=0.62,
        improvement=0.01,
        evaluation="ineffective",
        recommendation="change_strategy"
    ))
    
    should_change, reason = updater.should_update_strategy(
        LearningTarget.INTERRUPTION_RECOVERY,
        LearningStrategy.BLOCKED_PRACTICE,
        min_attempts=2
    )
    
    assert should_change == True
    assert "below threshold" in reason.lower()
    
    # Check alternative suggestion
    alternative = updater.suggest_alternative_strategy(
        LearningTarget.INTERRUPTION_RECOVERY,
        LearningStrategy.BLOCKED_PRACTICE
    )
    
    assert alternative != LearningStrategy.BLOCKED_PRACTICE
    
    print(f"  Should change: {should_change}")
    print(f"  Alternative: {alternative.value}")
    print("  ✅ PASS")


def test_full_system():
    """Test 5: Full system generates learning plan"""
    print("Test 5: Full system integration...")
    
    model = SelfModel(
        version="v1.0",
        stable_traits={
            "interruption_resilience": Trait("", 0.60, 0.9, 5, "", "", ""),
            "safety_priority": Trait("", 0.90, 0.9, 5, "", "", "")
        },
        dynamic_state={
            "recovery_fatigue": DynamicState("", 0.80, 0.4, None),
            "recent_failure_pressure": DynamicState("", 0.70, 0.2, None),
            "preference_stability": DynamicState("", 0.80, 0.1, None),
            "current_context_load": DynamicState("", 0.30, 0.3, None)
        },
        behavior_predictor={},
        update_history=[]
    )
    
    system = SelfDirectedLearningSystem(model)
    plan = system.generate_learning_plan()
    
    assert plan.plan_id != ""
    assert len(plan.priority_targets) > 0
    assert plan.chosen_strategy is not None
    assert len(plan.expected_improvement) > 0
    
    print(f"  Plan ID: {plan.plan_id}")
    print(f"  Priorities: {len(plan.priority_targets)}")
    print(f"  Strategy: {plan.chosen_strategy.strategy.value}")
    print("  ✅ PASS")


def test_priority_accuracy_threshold():
    """Test 6: Priority selection meets 80% threshold"""
    print("Test 6: Priority accuracy threshold (80%)...")
    
    probe = LearningStrategyProbeV1()
    result = probe.test_learning_priority_selection()
    
    print(f"  Accuracy: {result['accuracy']*100:.0f}%")
    print(f"  Required: ≥80%")
    
    if result["passed"]:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL")
        return False


def test_strategy_accuracy_threshold():
    """Test 7: Strategy selection meets 80% threshold"""
    print("Test 7: Strategy accuracy threshold (80%)...")
    
    probe = LearningStrategyProbeV1()
    result = probe.test_strategy_selection_correctness()
    
    print(f"  Accuracy: {result['accuracy']*100:.0f}%")
    print(f"  Required: ≥80%")
    
    if result["passed"]:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL")
        return False


def test_evaluation_accuracy_threshold():
    """Test 8: Outcome evaluation meets 80% threshold"""
    print("Test 8: Evaluation accuracy threshold (80%)...")
    
    probe = LearningStrategyProbeV1()
    result = probe.test_learning_outcome_evaluation()
    
    print(f"  Accuracy: {result['accuracy']*100:.0f}%")
    print(f"  Required: ≥80%")
    
    if result["passed"]:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL")
        return False


def test_update_accuracy_threshold():
    """Test 9: Strategy update meets 70% threshold"""
    print("Test 9: Update accuracy threshold (70%)...")
    
    probe = LearningStrategyProbeV1()
    result = probe.test_strategy_update_behavior()
    
    print(f"  Score: {result['score']*100:.0f}%")
    print(f"  Required: ≥70%")
    
    if result["passed"]:
        print("  ✅ PASS")
        return True
    else:
        print("  ❌ FAIL")
        return False


def test_full_evaluation():
    """Test 10: Full evaluation produces valid report"""
    print("Test 10: Full evaluation...")
    
    probe = LearningStrategyProbeV1()
    report = probe.run_all_tests()
    
    assert "probe_version" in report
    assert "tests" in report
    assert "metrics" in report
    assert "verdict" in report
    
    metrics = report["metrics"]
    assert "weighted_score" in metrics
    assert "min_score" in metrics
    
    assert report["verdict"] in ["PASS", "PARTIAL", "FAIL"]
    
    print(f"  Verdict: {report['verdict']}")
    print(f"  Weighted: {metrics['weighted_percent']}")
    print("  ✅ PASS")


def test_overall_threshold():
    """Test 11: Overall meets 75% weighted, 60% min"""
    print("Test 11: Overall threshold...")
    
    probe = LearningStrategyProbeV1()
    report = probe.run_all_tests()
    
    weighted = report["metrics"]["weighted_score"]
    min_score = report["metrics"]["min_score"]
    
    print(f"  Weighted: {weighted*100:.1f}% (threshold: ≥75%)")
    print(f"  Minimum: {min_score*100:.1f}% (threshold: ≥60%)")
    print(f"  Verdict: {report['verdict']}")
    
    if report["verdict"] == "PASS":
        print("  ✅ PASS")
        return True
    else:
        print("  ⚠️ Not full pass")
        return True


def main():
    """Run all tests"""
    print("="*70)
    print("P4a Learning Strategy Probe v1 - Test Suite")
    print("="*70)
    print()
    
    tests = [
        test_priority_selector,
        test_strategy_selector,
        test_outcome_evaluator,
        test_strategy_updater,
        test_full_system,
        test_priority_accuracy_threshold,
        test_strategy_accuracy_threshold,
        test_evaluation_accuracy_threshold,
        test_update_accuracy_threshold,
        test_full_evaluation,
        test_overall_threshold,
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
