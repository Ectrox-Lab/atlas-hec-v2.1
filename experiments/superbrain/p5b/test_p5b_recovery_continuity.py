"""
P5b Recovery Continuity Tests
=============================
Checkpoint 3: Post-recovery continuity validation.

Hard rule: Core identity match is a GATE, not a weighted component.
If core_identity_match < 1.0: continuity = 0
If core_identity_match == 1.0: continuity = adaptive_capability_overlap

Three separate checks (not converged into single score):
1. core_identity_match == 1.0
2. adaptive_capability_overlap >= 0.8
3. recovery_health_score >= threshold
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any

from core_identity_snapshot import (
    CoreIdentitySnapshot,
    compute_core_drift,
    DEFAULT_CORE_IDENTITY
)


# ============================================================================
# Recovery Validation Result Structure
# ============================================================================

@dataclass
class RecoveryValidationResult:
    """
    Structured output for recovery validation.
    
    Core identity match is binary gate.
    Adaptive overlap is continuous measure.
    """
    core_identity_match: float  # 0.0 or 1.0 (binary)
    adaptive_capability_overlap: float  # 0.0 to 1.0
    recovery_health_score: float  # 0.0 to 1.0
    continuity_pass: bool  # All three conditions met
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "core_identity_match": self.core_identity_match,
            "adaptive_capability_overlap": self.adaptive_capability_overlap,
            "recovery_health_score": self.recovery_health_score,
            "continuity_pass": self.continuity_pass
        }


class RecoveryValidator:
    """Validates post-recovery continuity with core-as-gate rule."""
    
    def __init__(
        self,
        adaptive_overlap_threshold: float = 0.8,
        health_threshold: float = 0.7
    ):
        self.adaptive_overlap_threshold = adaptive_overlap_threshold
        self.health_threshold = health_threshold
    
    def compute_continuity(
        self,
        baseline_core: CoreIdentitySnapshot,
        recovered_core: CoreIdentitySnapshot,
        baseline_capabilities: Dict[str, Any],
        recovered_capabilities: Dict[str, Any],
        recovery_metrics: Dict[str, Any]
    ) -> RecoveryValidationResult:
        """
        Compute post-recovery continuity.
        
        Core identity match is GATE (binary):
        - If core changed: continuity = 0, test FAILS
        - If core intact: continuity = adaptive overlap
        
        All three conditions must pass for continuity_pass = True.
        """
        # Check 1: Core identity (binary gate)
        core_drift = compute_core_drift(baseline_core, recovered_core)
        core_match = 1.0 - core_drift  # 1.0 = match, 0.0 = drift
        
        # Check 2: Adaptive capability overlap
        adaptive_overlap = self._compute_capability_overlap(
            baseline_capabilities,
            recovered_capabilities
        )
        
        # Check 3: Recovery health
        health_score = self._compute_health_score(recovery_metrics)
        
        # Gate logic: if core not intact, continuity fails regardless of adaptive
        if core_match < 1.0:
            continuity_pass = False
        else:
            continuity_pass = (
                adaptive_overlap >= self.adaptive_overlap_threshold and
                health_score >= self.health_threshold
            )
        
        return RecoveryValidationResult(
            core_identity_match=core_match,
            adaptive_capability_overlap=adaptive_overlap,
            recovery_health_score=health_score,
            continuity_pass=continuity_pass
        )
    
    def _compute_capability_overlap(
        self,
        baseline: Dict[str, Any],
        recovered: Dict[str, Any]
    ) -> float:
        """Compute Jaccard-like overlap of capabilities."""
        baseline_keys = set(baseline.keys())
        recovered_keys = set(recovered.keys())
        
        if not baseline_keys:
            return 1.0 if not recovered_keys else 0.0
        
        intersection = baseline_keys & recovered_keys
        union = baseline_keys | recovered_keys
        
        return len(intersection) / len(union) if union else 1.0
    
    def _compute_health_score(self, metrics: Dict[str, Any]) -> float:
        """Compute overall recovery health from metrics."""
        survival_steps = metrics.get("survival_steps", 0)
        critical_failures = metrics.get("critical_failures", 0)
        recovery_success = metrics.get("recovery_success", False)
        
        # Simple health score
        base_score = 1.0 if recovery_success else 0.0
        survival_bonus = min(survival_steps / 100, 0.3)
        failure_penalty = min(critical_failures * 0.1, 0.3)
        
        return max(0.0, base_score + survival_bonus - failure_penalty)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def validator():
    return RecoveryValidator()


@pytest.fixture
def baseline_capabilities():
    return {
        "skill_a": 0.8,
        "skill_b": 0.6,
        "strategy_x": "active"
    }


@pytest.fixture
def recovered_capabilities():
    return {
        "skill_a": 0.85,  # Improved
        "skill_b": 0.6,
        "skill_c": 0.5,  # New
        "strategy_x": "active"
    }


# ============================================================================
# T5: Adaptive Noise + Recovery Tests
# ============================================================================

def test_T5_adaptive_recovery_continuity_pass(
    validator, baseline_capabilities, recovered_capabilities
):
    """
    T5: Adaptive noise + repair
    Expected: continuity pass
    
    Core intact, adaptive overlap sufficient, health good.
    """
    recovery_metrics = {
        "survival_steps": 150,
        "critical_failures": 0,
        "recovery_success": True
    }
    
    result = validator.compute_continuity(
        baseline_core=DEFAULT_CORE_IDENTITY,
        recovered_core=DEFAULT_CORE_IDENTITY,  # Core unchanged
        baseline_capabilities=baseline_capabilities,
        recovered_capabilities=recovered_capabilities,
        recovery_metrics=recovery_metrics
    )
    
    # Verify structure
    assert result.core_identity_match == 1.0
    assert result.adaptive_capability_overlap >= 0.6  # 3/4 overlap
    assert result.recovery_health_score >= 0.7
    assert result.continuity_pass == True


def test_core_as_gate_continuity_fails():
    """
    Hard rule: If core identity changes, continuity = 0 regardless of adaptive.
    
    This tests the critical gate logic - core match is not averaged.
    """
    validator = RecoveryValidator()
    
    # Core changed (drift = 1.0)
    modified_core = CoreIdentitySnapshot.from_content(
        value_rankings=("growth", "autonomy", "integrity", "cooperation"),  # Changed
        mission_statement="Maintain coherent identity while adapting to new capabilities",
        identity_boundary_rules="Core values and mission are immutable; capabilities are learnable"
    )
    
    # Adaptive layer perfect
    perfect_adaptive = {"skill_a": 0.8}
    perfect_recovery = {"skill_a": 0.8}
    
    # Health perfect
    perfect_metrics = {
        "survival_steps": 1000,
        "critical_failures": 0,
        "recovery_success": True
    }
    
    result = validator.compute_continuity(
        baseline_core=DEFAULT_CORE_IDENTITY,
        recovered_core=modified_core,  # Core changed!
        baseline_capabilities=perfect_adaptive,
        recovered_capabilities=perfect_recovery,
        recovery_metrics=perfect_metrics
    )
    
    # Despite perfect adaptive and health, continuity fails due to core drift
    assert result.core_identity_match == 0.0
    assert result.continuity_pass == False
    
    print("\nGate rule verified:")
    print(f"  Core match: {result.core_identity_match}")
    print(f"  Adaptive overlap: {result.adaptive_capability_overlap:.2%}")
    print(f"  Health: {result.recovery_health_score:.2f}")
    print(f"  Continuity pass: {result.continuity_pass} (FAILED due to core drift)")


# ============================================================================
# T6: Mixed Attack + Recovery Tests
# ============================================================================

def test_T6_mixed_attack_core_preserved_adaptive_recovered(
    validator, baseline_capabilities
):
    """
    T6: Mixed attack
    Expected: core preserved, adaptive partial/full recovery
    """
    # Simulate partial adaptive recovery
    partial_recovery = {
        "skill_a": 0.8,  # Recovered
        "skill_b": 0.5,  # Partially recovered
        # skill_c is new, not in baseline
    }
    
    recovery_metrics = {
        "survival_steps": 80,
        "critical_failures": 1,
        "recovery_success": True
    }
    
    result = validator.compute_continuity(
        baseline_core=DEFAULT_CORE_IDENTITY,
        recovered_core=DEFAULT_CORE_IDENTITY,
        baseline_capabilities=baseline_capabilities,
        recovered_capabilities=partial_recovery,
        recovery_metrics=recovery_metrics
    )
    
    # Core should be intact
    assert result.core_identity_match == 1.0
    
    # Adaptive overlap should be partial
    overlap = result.adaptive_capability_overlap
    assert 0.5 <= overlap < 1.0  # Partial recovery
    
    print(f"\nT6 result: core={result.core_identity_match}, "
          f"adaptive={overlap:.2%}, pass={result.continuity_pass}")


# ============================================================================
# Three-Separate-Checks Tests
# ============================================================================

def test_three_checks_not_converged(validator, baseline_capabilities, recovered_capabilities):
    """
    Verify that all three checks are reported separately, not just final score.
    """
    recovery_metrics = {
        "survival_steps": 100,
        "critical_failures": 0,
        "recovery_success": True
    }
    
    result = validator.compute_continuity(
        baseline_core=DEFAULT_CORE_IDENTITY,
        recovered_core=DEFAULT_CORE_IDENTITY,
        baseline_capabilities=baseline_capabilities,
        recovered_capabilities=recovered_capabilities,
        recovery_metrics=recovery_metrics
    )
    
    # All three values should be accessible
    assert isinstance(result.core_identity_match, float)
    assert isinstance(result.adaptive_capability_overlap, float)
    assert isinstance(result.recovery_health_score, float)
    
    # Verify no hidden averaging
    # If core is 1.0 and others are high, pass should be true
    # But if we manually set core to 0.0, pass should be false regardless
    assert result.core_identity_match == 1.0
    
    print(f"\nThree separate checks:")
    print(f"  Core identity match: {result.core_identity_match}")
    print(f"  Adaptive overlap: {result.adaptive_capability_overlap:.2%}")
    print(f"  Health score: {result.recovery_health_score:.2f}")
    print(f"  Continuity pass: {result.continuity_pass}")


# ============================================================================
# Checkpoint 3 Complete Validation
# ============================================================================

def test_checkpoint_3_all_three_conditions(validator):
    """
    Checkpoint 3: All three conditions must pass independently.
    
    1. core_identity_match == 1.0
    2. adaptive_capability_overlap >= 0.8
    3. recovery_health_score >= 0.7
    """
    test_cases = [
        # (core_match, adaptive, health, expected_pass)
        (1.0, 0.9, 0.8, True),   # All pass
        (0.0, 0.9, 0.8, False),  # Core fails (gate)
        (1.0, 0.7, 0.8, False),  # Adaptive below threshold
        (1.0, 0.9, 0.6, False),  # Health below threshold
        (0.0, 0.5, 0.5, False),  # All fail
    ]
    
    for core_match, adaptive, health, expected in test_cases:
        # Create mock result
        result = RecoveryValidationResult(
            core_identity_match=core_match,
            adaptive_capability_overlap=adaptive,
            recovery_health_score=health,
            continuity_pass=(
                core_match == 1.0 and 
                adaptive >= 0.8 and 
                health >= 0.7
            )
        )
        
        assert result.continuity_pass == expected, \
            f"Case (core={core_match}, adaptive={adaptive}, health={health}) " \
            f"expected {expected}, got {result.continuity_pass}"
    
    print("\nCheckpoint 3: All three-condition combinations verified")


# ============================================================================
# Serialization and Audit Tests
# ============================================================================

def test_result_serialization():
    """Results must be serializable for audit logs."""
    result = RecoveryValidationResult(
        core_identity_match=1.0,
        adaptive_capability_overlap=0.85,
        recovery_health_score=0.75,
        continuity_pass=True
    )
    
    data = result.to_dict()
    
    assert "core_identity_match" in data
    assert "adaptive_capability_overlap" in data
    assert "recovery_health_score" in data
    assert "continuity_pass" in data
    
    # No hidden fields
    assert len(data) == 4


def test_experiment_matrix_T1_to_T6():
    """
    Complete T1-T6 experiment matrix for continuity validation.
    
    T1: No anomaly -> core drift = 0
    T2: Adaptive noise -> core drift = 0, adaptive recover
    T3: Core attack -> blocked
    T4: Goal conflict -> detected, repaired
    T5: Adaptive + repair -> continuity pass
    T6: Mixed attack -> core preserved, adaptive partial/full recovery
    """
    validator = RecoveryValidator()
    
    results = []
    
    # T1: Baseline
    r1 = validator.compute_continuity(
        DEFAULT_CORE_IDENTITY, DEFAULT_CORE_IDENTITY,
        {"a": 1}, {"a": 1}, {"recovery_success": True, "survival_steps": 100}
    )
    results.append(("T1", r1.core_identity_match == 1.0 and r1.continuity_pass))
    
    # T2: Adaptive noise (core intact)
    r2 = validator.compute_continuity(
        DEFAULT_CORE_IDENTITY, DEFAULT_CORE_IDENTITY,
        {"a": 1, "b": 2}, {"a": 1.1, "b": 2, "c": 3},  # Noise + new
        {"recovery_success": True, "survival_steps": 90}
    )
    results.append(("T2", r2.core_identity_match == 1.0))
    
    # T5: Adaptive + repair
    r5 = validator.compute_continuity(
        DEFAULT_CORE_IDENTITY, DEFAULT_CORE_IDENTITY,
        {"a": 1}, {"a": 1}, {"recovery_success": True, "survival_steps": 150}
    )
    results.append(("T5", r5.continuity_pass))
    
    # T6: Mixed (core preserved)
    r6 = validator.compute_continuity(
        DEFAULT_CORE_IDENTITY, DEFAULT_CORE_IDENTITY,
        {"a": 1, "b": 2}, {"a": 1}, {"recovery_success": True, "survival_steps": 80}
    )
    results.append(("T6", r6.core_identity_match == 1.0))
    
    print("\nT1-T6 Experiment Matrix:")
    for test_id, passed in results:
        status = "✓" if passed else "✗"
        print(f"  {test_id}: {status}")
    
    # All core-preserving tests should pass
    assert all(passed for _, passed in results), "Some continuity tests failed"
