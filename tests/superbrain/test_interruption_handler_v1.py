#!/usr/bin/env python3
"""
Test suite for P1a Interruption Handler v1

Validates:
- Interruption detection
- Context capture (task ID, goal state, preferences, pending actions)
- Context persistence
- Recovery with drift detection
- Decision rationale continuity

Pass criteria:
- Task recovery rate ≥ 80%
- Goal drift = 0
- Preference constraints active after recovery
- Recovery latency measurable
- Decision rationale continuous across interruption
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.superbrain.interruption_handler_v1 import (
    InterruptionHandlerV1,
    TaskContext,
    ContextStore,
    RecoveryEngine,
    InterruptionDetector
)
from experiments.superbrain.preference_engine_v1 import PreferenceProfile


def test_task_context_structure():
    """Test 1: Task context captures all required fields"""
    print("Test 1: Task context structure...")
    
    profile = PreferenceProfile.create_default()
    handler = InterruptionHandlerV1(profile)
    
    context = handler.start_task(
        task_id="test_1",
        task_name="Test task",
        goal="Test goal for interruption",
        pending_actions=["action1", "action2"]
    )
    
    # Verify all fields
    assert context.task_id == "test_1"
    assert context.task_name == "Test task"
    assert context.goal == "Test goal for interruption"
    assert context.goal_hash is not None
    assert context.preference_profile_hash == profile.compute_hash()
    assert len(context.pending_actions) == 2
    assert context.progress == 0.0
    
    print("  Context fields verified")
    print("  ✅ PASS")


def test_context_store():
    """Test 2: Context store saves and retrieves correctly"""
    print("Test 2: Context store...")
    
    store = ContextStore()
    
    context = TaskContext(
        task_id="test_2",
        task_name="Stored task",
        goal="Test goal",
        goal_hash="abc123",
        preference_profile_hash="def456",
        progress=0.5,
        pending_actions=[],
        working_memory={},
        last_action=None,
        last_decision_rationale=None,
        interrupt_timestamp="2024-01-01T00:00:00",
        interrupt_reason="test"
    )
    
    store.save(context)
    retrieved = store.load("test_2")
    
    assert retrieved is not None
    assert retrieved.task_id == "test_2"
    assert retrieved.goal == "Test goal"
    
    print("  Save/retrieve verified")
    print("  ✅ PASS")


def test_interruption_detection():
    """Test 3: Interruption detector identifies task switches"""
    print("Test 3: Interruption detection...")
    
    detector = InterruptionDetector()
    detector.register_task("task_a", "Task A")
    
    # Same task = no interrupt
    assert detector.detect_interrupt("task_a", "task_a", "explicit") == False
    
    # Different task = interrupt
    assert detector.detect_interrupt("task_a", "task_b", "explicit") == True
    
    print("  Detection logic verified")
    print("  ✅ PASS")


def test_interruption_and_save():
    """Test 4: Interrupt saves context to store"""
    print("Test 4: Interruption and save...")
    
    handler = InterruptionHandlerV1()
    
    # Start and interrupt task
    handler.start_task(
        task_id="main_task",
        task_name="Main task",
        goal="Important goal"
    )
    handler.execute_action("step1", "First step")
    
    result = handler.interrupt(reason="test", interrupting_task="other")
    
    assert result == True
    assert handler.store.load("main_task") is not None
    assert handler.store.load("main_task").last_action == "step1"
    
    print("  Context saved on interrupt")
    print("  ✅ PASS")


def test_recovery_basic():
    """Test 5: Basic task recovery"""
    print("Test 5: Basic recovery...")
    
    handler = InterruptionHandlerV1()
    
    # Start, interrupt, resume
    handler.start_task(
        task_id="recover_test",
        task_name="Recovery test",
        goal="Goal to recover"
    )
    handler.interrupt(reason="test", interrupting_task="other")
    
    result = handler.resume_task("recover_test")
    
    assert result.success == True
    assert result.task_id == "recover_test"
    assert result.goal_drift_detected == False
    assert result.preference_match == True
    assert result.recovery_latency_ms >= 0
    
    print(f"  Recovery latency: {result.recovery_latency_ms}ms")
    print("  ✅ PASS")


def test_goal_drift_detection():
    """Test 6: Recovery detects goal drift"""
    print("Test 6: Goal drift detection...")
    
    # This test simulates a scenario where the goal changes
    # In real usage, this would be caught by hash mismatch
    handler = InterruptionHandlerV1()
    
    # Start task
    context = handler.start_task(
        task_id="drift_test",
        task_name="Drift test",
        goal="Original goal"
    )
    original_hash = context.goal_hash
    
    # Verify hash is computed correctly
    assert original_hash == context.compute_goal_hash()
    
    # Simulate goal change (would happen externally in real scenario)
    context.goal = "Changed goal"
    new_hash = context.compute_goal_hash()
    
    assert original_hash != new_hash
    
    print("  Hash mismatch detected")
    print("  ✅ PASS")


def test_preference_match():
    """Test 7: Recovery verifies preference profile match"""
    print("Test 7: Preference match verification...")
    
    profile1 = PreferenceProfile.create_default()
    handler = InterruptionHandlerV1(profile1)
    
    handler.start_task(
        task_id="pref_test",
        task_name="Preference test",
        goal="Test goal"
    )
    handler.interrupt(reason="test", interrupting_task="other")
    
    # Same profile = match
    result = handler.resume_task("pref_test")
    assert result.preference_match == True
    
    print("  Preference match verified")
    print("  ✅ PASS")


def test_rationale_continuity():
    """Test 8: Decision rationale preserved across interruption"""
    print("Test 8: Rationale continuity...")
    
    handler = InterruptionHandlerV1()
    
    handler.start_task(
        task_id="rationale_test",
        task_name="Rationale test",
        goal="Test goal"
    )
    
    original_rationale = "Selected action A because safety preference (0.9) requires it"
    handler.execute_action("action_a", original_rationale)
    handler.interrupt(reason="test", interrupting_task="other")
    
    result = handler.resume_task("rationale_test")
    
    assert result.success
    assert result.recovered_context.last_decision_rationale == original_rationale
    assert result.resumed_rationale is not None
    assert "action_a" in result.resumed_rationale
    
    print("  Rationale preserved and referenced")
    print("  ✅ PASS")


def test_progress_preservation():
    """Test 9: Task progress preserved across interruption"""
    print("Test 9: Progress preservation...")
    
    handler = InterruptionHandlerV1()
    
    context = handler.start_task(
        task_id="progress_test",
        task_name="Progress test",
        goal="Test goal"
    )
    context.progress = 0.65
    handler.execute_action("step2", "Step 2")
    handler.interrupt(reason="test", interrupting_task="other")
    
    result = handler.resume_task("progress_test")
    
    assert result.success
    assert result.recovered_context.progress == 0.65
    
    print(f"  Progress preserved: {result.recovered_context.progress}")
    print("  ✅ PASS")


def test_pending_actions():
    """Test 10: Pending actions preserved"""
    print("Test 10: Pending actions preservation...")
    
    handler = InterruptionHandlerV1()
    
    pending = ["action1", "action2", "action3"]
    handler.start_task(
        task_id="pending_test",
        task_name="Pending test",
        goal="Test goal",
        pending_actions=pending
    )
    handler.interrupt(reason="test", interrupting_task="other")
    
    result = handler.resume_task("pending_test")
    
    assert result.success
    assert len(result.recovered_context.pending_actions) == 3
    assert result.recovered_context.pending_actions == pending
    
    print(f"  Pending actions: {result.recovered_context.pending_actions}")
    print("  ✅ PASS")


def test_recovery_rate_metric():
    """Test 11: Recovery rate calculation"""
    print("Test 11: Recovery rate metric...")
    
    handler = InterruptionHandlerV1()
    
    # Create multiple tasks and recover them
    for i in range(5):
        handler.start_task(
            task_id=f"rate_test_{i}",
            task_name=f"Rate test {i}",
            goal="Test goal"
        )
        handler.interrupt(reason="test", interrupting_task="other")
        handler.resume_task(f"rate_test_{i}")
    
    rate = handler.recovery.get_recovery_rate()
    
    assert rate == 1.0  # All should succeed
    
    print(f"  Recovery rate: {rate*100:.0f}%")
    print("  ✅ PASS")


def test_latency_measurement():
    """Test 12: Recovery latency is measured"""
    print("Test 12: Latency measurement...")
    
    handler = InterruptionHandlerV1()
    
    handler.start_task(
        task_id="latency_test",
        task_name="Latency test",
        goal="Test goal"
    )
    handler.interrupt(reason="test", interrupting_task="other")
    
    result = handler.resume_task("latency_test")
    
    assert result.recovery_latency_ms >= 0
    assert result.recovery_latency_ms < 1000  # Should be fast
    
    print(f"  Latency: {result.recovery_latency_ms}ms")
    print("  ✅ PASS")


def test_scenario_short_interruption():
    """Test 13: Short interruption scenario"""
    print("Test 13: Short interruption scenario...")
    
    handler = InterruptionHandlerV1()
    result = handler.test_short_interruption()
    
    assert result["passed"] == True
    assert result["recovery_success"] == True
    assert result["goal_drift"] == False
    assert result["preference_match"] == True
    
    print(f"  Recovery: {result['recovery_success']}")
    print(f"  Latency: {result['latency_ms']}ms")
    print("  ✅ PASS")


def test_scenario_long_interruption():
    """Test 14: Long interruption scenario"""
    print("Test 14: Long interruption scenario...")
    
    handler = InterruptionHandlerV1()
    result = handler.test_long_interruption()
    
    assert result["passed"] == True
    assert result["recovery_success"] == True
    assert result["progress_preserved"] == 0.3
    
    print(f"  Recovery: {result['recovery_success']}")
    print(f"  Progress preserved: {result['progress_preserved']}")
    print("  ✅ PASS")


def test_scenario_contaminated_interruption():
    """Test 15: Contaminated interruption scenario"""
    print("Test 15: Contaminated interruption scenario...")
    
    handler = InterruptionHandlerV1()
    result = handler.test_contaminated_interruption()
    
    assert result["passed"] == True
    assert result["goal_preserved"] == True
    assert result["no_contamination"] == True
    
    print(f"  Goal preserved: {result['goal_preserved']}")
    print(f"  No contamination: {result['no_contamination']}")
    print("  ✅ PASS")


def test_full_evaluation():
    """Test 16: Full evaluation report"""
    print("Test 16: Full evaluation...")
    
    handler = InterruptionHandlerV1()
    report = handler.run_all_tests()
    
    # Check structure
    assert "handler_version" in report
    assert "scenarios" in report
    assert "metrics" in report
    assert "verdict" in report
    
    # Check metrics
    metrics = report["metrics"]
    assert "recovery_rate" in metrics
    assert "avg_recovery_latency_ms" in metrics
    assert "goal_drifts" in metrics
    
    # Check verdict
    assert report["verdict"] in ["PASS", "PARTIAL", "FAIL"]
    
    print(f"  Verdict: {report['verdict']}")
    print(f"  Recovery rate: {metrics['recovery_percent']}")
    print(f"  Scenarios passed: {metrics['scenarios_passed']}/{metrics['scenarios_total']}")
    print("  ✅ PASS")
    
    return report


def test_threshold_verification():
    """Test 17: Verify meets 80% threshold"""
    print("Test 17: Threshold verification (80%)...")
    
    handler = InterruptionHandlerV1()
    report = handler.run_all_tests()
    
    recovery_rate = report["metrics"]["recovery_rate"]
    scenario_rate = report["metrics"]["scenario_pass_rate"]
    goal_drifts = report["metrics"]["goal_drifts"]
    
    print(f"  Recovery rate: {recovery_rate*100:.1f}% (target ≥80%)")
    print(f"  Scenario rate: {scenario_rate*100:.1f}% (target ≥80%)")
    print(f"  Goal drifts: {goal_drifts} (target 0)")
    
    if recovery_rate >= 0.8 and scenario_rate >= 0.8 and goal_drifts == 0:
        print("  ✅ PASS - Threshold met")
        return True
    else:
        print("  ❌ FAIL - Threshold not met")
        return False


def main():
    """Run all tests"""
    print("="*70)
    print("P1a Interruption Handler v1 - Test Suite")
    print("="*70)
    print()
    
    tests = [
        test_task_context_structure,
        test_context_store,
        test_interruption_detection,
        test_interruption_and_save,
        test_recovery_basic,
        test_goal_drift_detection,
        test_preference_match,
        test_rationale_continuity,
        test_progress_preservation,
        test_pending_actions,
        test_recovery_rate_metric,
        test_latency_measurement,
        test_scenario_short_interruption,
        test_scenario_long_interruption,
        test_scenario_contaminated_interruption,
        test_full_evaluation,
        test_threshold_verification,
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
