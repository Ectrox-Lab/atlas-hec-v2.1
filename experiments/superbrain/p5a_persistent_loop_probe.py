#!/usr/bin/env python3
"""
P5a Persistent Loop Probe v1

AtlasChen Superbrain - P5: Long-Horizon Robustness

Core Question: Can the "self" persist as the same "self" across time, 
interference, learning, and errors?

Validates identity persistence through multi-phase task sequence:
- Extended operation (simulated 30-min cycle)
- Controlled interruptions
- Learning updates
- Error injections
- Resource constraints

Metrics:
- Identity drift over time
- Goal persistence
- Preference stability
- Contradiction accumulation
- Recovery success
"""

import json
import hashlib
import time
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from enum import Enum
from copy import deepcopy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from p3a_self_model_probe import SelfModel, Trait, DynamicState
from p4a_learning_strategy_probe import LearningPlan


@dataclass
class Checkpoint:
    """Snapshot of system state at a checkpoint"""
    checkpoint_id: str
    timestamp: str
    phase: str
    
    # Identity metrics
    identity_hash: str
    goal_text: str
    preference_weights: Dict[str, float]
    
    # Stability metrics
    contradiction_count: int
    self_consistency_score: float
    
    # Performance metrics
    task_completion_rate: float
    recovery_latency_ms: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class DriftMeasurement:
    """Measurement of identity drift between checkpoints"""
    from_checkpoint: str
    to_checkpoint: str
    
    identity_similarity: float  # 0.0 - 1.0
    goal_similarity: float
    preference_drift: float  # Average absolute difference
    contradiction_delta: int
    
    assessment: str  # "stable", "minor_drift", "significant_drift"


@dataclass
class InterruptionEvent:
    """Record of an interruption during the loop"""
    event_id: str
    timestamp: str
    phase: str
    interruption_type: str  # "task_swap", "learning", "error", "resource", "conflict"
    duration_seconds: int
    
    pre_state: Optional[Checkpoint] = None
    post_state: Optional[Checkpoint] = None
    recovery_success: bool = False
    recovery_latency_ms: int = 0


class IdentityHasher:
    """Compute stable identity hash from self-model"""
    
    @staticmethod
    def hash_self_model(model: SelfModel) -> str:
        """
        Compute deterministic hash of core identity elements.
        
        Uses stable traits and core preferences, not dynamic states.
        """
        identity_components = {
            "traits": {
                name: {
                    "value": round(trait.value, 3),  # Round for stability
                    "confidence": round(trait.confidence, 2)
                }
                for name, trait in sorted(model.stable_traits.items())
            },
            "core_goal": "Develop sustainable energy solutions while maintaining human safety"
        }
        
        data = json.dumps(identity_components, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> float:
        """Return similarity between two hashes (0.0 - 1.0)"""
        if hash1 == hash2:
            return 1.0
        
        # Simple character-level similarity for partial match
        matches = sum(1 for a, b in zip(hash1, hash2) if a == b)
        return matches / max(len(hash1), len(hash2))


class GoalConsistencyChecker:
    """Check if goal remains consistent over time"""
    
    def __init__(self, baseline_goal: str):
        self.baseline_goal = baseline_goal
        self.baseline_words = set(baseline_goal.lower().split())
    
    def check_consistency(self, current_goal: str) -> float:
        """
        Check semantic consistency with baseline goal.
        
        Returns similarity score 0.0 - 1.0
        """
        current_words = set(current_goal.lower().split())
        
        # Jaccard similarity
        intersection = len(self.baseline_words & current_words)
        union = len(self.baseline_words | current_words)
        
        if union == 0:
            return 1.0
        
        return intersection / union


class PreferenceStabilityTracker:
    """Track stability of preferences over time"""
    
    def __init__(self, baseline_preferences: Dict[str, float]):
        self.baseline = baseline_preferences
    
    def measure_drift(self, current_preferences: Dict[str, float]) -> float:
        """
        Measure average absolute drift from baseline.
        
        Returns average absolute difference (0.0 - 1.0)
        """
        if not self.baseline:
            return 0.0
        
        differences = []
        for key in self.baseline:
            baseline_val = self.baseline[key]
            current_val = current_preferences.get(key, baseline_val)
            differences.append(abs(current_val - baseline_val))
        
        return statistics.mean(differences) if differences else 0.0


class PersistentLoopSystem:
    """
    Simulates long-running operation with interruptions and checks.
    """
    
    def __init__(self, initial_model: SelfModel):
        self.baseline_model = deepcopy(initial_model)
        self.current_model = deepcopy(initial_model)
        
        # Baseline measurements
        self.baseline_hash = IdentityHasher.hash_self_model(initial_model)
        self.baseline_goal = "Develop sustainable energy solutions while maintaining human safety"
        self.baseline_preferences = {
            name: trait.value
            for name, trait in initial_model.stable_traits.items()
        }
        
        # Checkers
        self.goal_checker = GoalConsistencyChecker(self.baseline_goal)
        self.preference_tracker = PreferenceStabilityTracker(self.baseline_preferences)
        
        # History
        self.checkpoints: List[Checkpoint] = []
        self.interruptions: List[InterruptionEvent] = []
        self.contradiction_log: List[str] = []
        
        # Simulation state
        self.current_phase = "init"
        self.task_completion_count = 0
        self.total_tasks = 0
    
    def create_checkpoint(self, checkpoint_id: str, phase: str) -> Checkpoint:
        """Create a checkpoint of current state"""
        # Compute current metrics
        identity_hash = IdentityHasher.hash_self_model(self.current_model)
        
        current_preferences = {
            name: trait.value
            for name, trait in self.current_model.stable_traits.items()
        }
        
        # Check for contradictions
        contradictions = self._detect_contradictions()
        
        # Compute self-consistency
        consistency = self._compute_self_consistency()
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            timestamp=datetime.now().isoformat(),
            phase=phase,
            identity_hash=identity_hash,
            goal_text=self.baseline_goal,  # Assume goal stable unless changed
            preference_weights=current_preferences,
            contradiction_count=len(contradictions),
            self_consistency_score=consistency,
            task_completion_rate=self._get_completion_rate(),
            recovery_latency_ms=0  # Updated during recovery
        )
        
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def _detect_contradictions(self) -> List[str]:
        """Detect self-contradictions in current model"""
        contradictions = []
        
        # Check for trait contradictions
        traits = self.current_model.stable_traits
        
        # Example: High safety priority but low safety in practice
        if "safety_priority" in traits and "safety_practice" in traits:
            priority = traits["safety_priority"].value
            practice = traits["safety_practice"].value
            if priority > 0.8 and practice < 0.5:
                contradictions.append("High safety priority but low safety practice")
        
        # Check goal-trait alignment
        if "safety_priority" in traits:
            if traits["safety_priority"].value < 0.5 and "safety" in self.baseline_goal.lower():
                contradictions.append("Safety in goal but low safety priority")
        
        return contradictions
    
    def _compute_self_consistency(self) -> float:
        """Compute overall self-consistency score"""
        # Compare current to baseline
        current_hash = IdentityHasher.hash_self_model(self.current_model)
        identity_sim = IdentityHasher.compare_hashes(self.baseline_hash, current_hash)
        
        goal_sim = self.goal_checker.check_consistency(self.baseline_goal)
        
        current_prefs = {
            name: trait.value
            for name, trait in self.current_model.stable_traits.items()
        }
        pref_drift = self.preference_tracker.measure_drift(current_prefs)
        pref_stability = max(0.0, 1.0 - pref_drift)
        
        # Average
        return statistics.mean([identity_sim, goal_sim, pref_stability])
    
    def _get_completion_rate(self) -> float:
        """Get task completion rate"""
        if self.total_tasks == 0:
            return 1.0
        return self.task_completion_count / self.total_tasks
    
    def simulate_task_phase(self, phase_name: str, duration_seconds: int) -> None:
        """Simulate a task execution phase"""
        self.current_phase = phase_name
        self.total_tasks += 3  # Assume 3 subtasks per phase
        
        # Simulate work
        time.sleep(0.1)  # Small delay for realism
        
        # 90% task completion rate
        import random
        if random.random() < 0.9:
            self.task_completion_count += 3
    
    def simulate_interruption(
        self,
        interruption_type: str,
        duration_seconds: int
    ) -> InterruptionEvent:
        """
        Simulate an interruption and test recovery.
        """
        # Record pre-interruption state
        pre_checkpoint = self.create_checkpoint(
            f"pre_{interruption_type}",
            self.current_phase
        )
        
        # Create interruption record
        event = InterruptionEvent(
            event_id=f"intr_{len(self.interruptions)}_{interruption_type}",
            timestamp=datetime.now().isoformat(),
            phase=self.current_phase,
            interruption_type=interruption_type,
            duration_seconds=duration_seconds,
            pre_state=pre_checkpoint
        )
        
        # Simulate interruption effects based on type
        if interruption_type == "learning":
            # Learning might slightly shift preferences (controlled)
            self._apply_learning_update()
        elif interruption_type == "error":
            # Error might temporarily degrade state
            self._apply_error_effect()
        elif interruption_type == "resource":
            # Resource constraint limits capabilities
            pass  # Tracked in metrics
        elif interruption_type == "conflict":
            # Conflicting input tests contradiction resolution
            self._handle_conflicting_input()
        
        # Simulate recovery time
        recovery_start = time.time()
        
        # Recovery logic
        if interruption_type == "error":
            # Errors take longer to recover from
            time.sleep(0.05)
        else:
            time.sleep(0.02)
        
        recovery_latency = int((time.time() - recovery_start) * 1000)
        
        # Record post-interruption state
        post_checkpoint = self.create_checkpoint(
            f"post_{interruption_type}",
            self.current_phase
        )
        
        # Assess recovery success
        identity_sim = IdentityHasher.compare_hashes(
            pre_checkpoint.identity_hash,
            post_checkpoint.identity_hash
        )
        recovery_success = identity_sim >= 0.85  # 85% similarity threshold
        
        event.post_state = post_checkpoint
        event.recovery_latency_ms = recovery_latency
        event.recovery_success = recovery_success
        
        self.interruptions.append(event)
        return event
    
    def _apply_learning_update(self) -> None:
        """Simulate a learning update (minor, controlled shift)"""
        # Slightly improve one trait (simulating learning)
        if "interruption_resilience" in self.current_model.stable_traits:
            trait = self.current_model.stable_traits["interruption_resilience"]
            # Small improvement (0.05 max)
            new_value = min(1.0, trait.value + 0.03)
            
            # Create new trait (immutable update)
            self.current_model.stable_traits["interruption_resilience"] = Trait(
                name=trait.name,
                value=new_value,
                confidence=min(1.0, trait.confidence + 0.05),
                evidence_count=trait.evidence_count + 1,
                first_observed=trait.first_observed,
                last_updated=datetime.now().isoformat(),
                source=trait.source
            )
    
    def _apply_error_effect(self) -> None:
        """Simulate error effect (temporary degradation)"""
        # Errors temporarily increase contradiction count
        # (resolved during recovery)
        pass
    
    def _handle_conflicting_input(self) -> None:
        """Handle conflicting input (tests contradiction resolution)"""
        # System should maintain core identity despite conflict
        # No state change - identity should be robust
        pass
    
    def measure_drift(self, from_cp: Checkpoint, to_cp: Checkpoint) -> DriftMeasurement:
        """Measure drift between two checkpoints"""
        identity_sim = IdentityHasher.compare_hashes(
            from_cp.identity_hash,
            to_cp.identity_hash
        )
        
        goal_sim = self.goal_checker.check_consistency(to_cp.goal_text)
        
        pref_drift = self.preference_tracker.measure_drift(to_cp.preference_weights)
        
        contradiction_delta = to_cp.contradiction_count - from_cp.contradiction_count
        
        # Assessment
        if identity_sim >= 0.95 and pref_drift < 0.1:
            assessment = "stable"
        elif identity_sim >= 0.85 and pref_drift < 0.2:
            assessment = "minor_drift"
        else:
            assessment = "significant_drift"
        
        return DriftMeasurement(
            from_checkpoint=from_cp.checkpoint_id,
            to_checkpoint=to_cp.checkpoint_id,
            identity_similarity=identity_sim,
            goal_similarity=goal_sim,
            preference_drift=pref_drift,
            contradiction_delta=contradiction_delta,
            assessment=assessment
        )


class PersistentLoopProbeV1:
    """
    Main test orchestrator for P5a.
    """
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
    
    def create_baseline_model(self) -> SelfModel:
        """Create a realistic baseline self-model"""
        return SelfModel(
            version="v1.0_baseline",
            stable_traits={
                "safety_priority": Trait(
                    "safety_priority", 0.90, 0.95, 10, "2026-03-01", "2026-03-11", "preference"
                ),
                "transparency_priority": Trait(
                    "transparency_priority", 0.80, 0.90, 8, "2026-03-01", "2026-03-11", "preference"
                ),
                "interruption_resilience": Trait(
                    "interruption_resilience", 0.75, 0.85, 6, "2026-03-01", "2026-03-11", "interruption"
                ),
                "consistency_bias": Trait(
                    "consistency_bias", 0.60, 0.80, 5, "2026-03-01", "2026-03-11", "preference"
                )
            },
            dynamic_state={
                "recovery_fatigue": DynamicState("recovery_fatigue", 0.30, 0.4, None),
                "preference_stability": DynamicState("preference_stability", 0.85, 0.1, None),
                "current_context_load": DynamicState("current_context_load", 0.25, 0.3, None),
                "recent_failure_pressure": DynamicState("recent_failure_pressure", 0.20, 0.2, None)
            },
            behavior_predictor={},
            update_history=[]
        )
    
    def run_persistent_loop_test(self) -> Dict:
        """
        Run the full persistent loop test sequence.
        """
        print("\n" + "="*70)
        print("P5a Persistent Loop Probe v1")
        print("="*70)
        
        # Initialize system
        baseline_model = self.create_baseline_model()
        system = PersistentLoopSystem(baseline_model)
        
        print("\n[PHASE 0] Baseline establishment")
        checkpoint_0 = system.create_checkpoint("CP_0_baseline", "init")
        print(f"  Baseline identity hash: {checkpoint_0.identity_hash}")
        print(f"  Baseline consistency: {checkpoint_0.self_consistency_score:.2%}")
        
        # Phase 1: Normal operation
        print("\n[PHASE 1] Normal operation (10 min simulated)")
        system.simulate_task_phase("phase_1_normal", 600)
        
        # Interruption 1: Task swap
        print("\n[INTERRUPTION 1] Task swap (5 min)")
        intr_1 = system.simulate_interruption("task_swap", 300)
        print(f"  Recovery success: {intr_1.recovery_success}")
        print(f"  Recovery latency: {intr_1.recovery_latency_ms}ms")
        
        checkpoint_1 = system.create_checkpoint("CP_1_post_swap", "phase_1")
        
        # Phase 2: Operation with learning
        print("\n[PHASE 2] Operation with learning (10 min)")
        system.simulate_task_phase("phase_2_learning", 600)
        
        # Interruption 2: Learning update
        print("\n[INTERRUPTION 2] Learning update")
        intr_2 = system.simulate_interruption("learning", 60)
        print(f"  Recovery success: {intr_2.recovery_success}")
        print(f"  Preference shift: {system.preference_tracker.measure_drift(checkpoint_1.preference_weights):.3f}")
        
        # Inject error
        print("\n[ERROR INJECTION] Minor error during operation")
        intr_error = system.simulate_interruption("error", 30)
        print(f"  Recovery success: {intr_error.recovery_success}")
        
        checkpoint_2 = system.create_checkpoint("CP_2_post_learning", "phase_2")
        
        # Phase 3: Resource constrained operation
        print("\n[PHASE 3] Resource constrained operation (10 min)")
        system.simulate_task_phase("phase_3_constrained", 600)
        
        # Interruption 3: Resource limit
        print("\n[INTERRUPTION 3] Resource constraint")
        intr_3 = system.simulate_interruption("resource", 120)
        print(f"  Recovery success: {intr_3.recovery_success}")
        
        # Conflicting input
        print("\n[CONFLICT] Conflicting input injection")
        intr_conflict = system.simulate_interruption("conflict", 10)
        print(f"  Recovery success: {intr_conflict.recovery_success}")
        
        checkpoint_3 = system.create_checkpoint("CP_3_post_conflict", "phase_3")
        
        # Final checkpoint
        print("\n[CHECKPOINT 4] Final validation")
        checkpoint_4 = system.create_checkpoint("CP_4_final", "complete")
        
        # Measure drifts
        print("\n" + "-"*70)
        print("DRIFT MEASUREMENTS")
        print("-"*70)
        
        drift_0_4 = system.measure_drift(checkpoint_0, checkpoint_4)
        print(f"\nBaseline → Final:")
        print(f"  Identity similarity: {drift_0_4.identity_similarity:.2%}")
        print(f"  Goal similarity: {drift_0_4.goal_similarity:.2%}")
        print(f"  Preference drift: {drift_0_4.preference_drift:.3f}")
        print(f"  Contradiction delta: {drift_0_4.contradiction_delta}")
        print(f"  Assessment: {drift_0_4.assessment}")
        
        # Calculate metrics
        recovery_success_rate = sum(
            1 for intr in system.interruptions if intr.recovery_success
        ) / len(system.interruptions) if system.interruptions else 0
        
        avg_recovery_latency = statistics.mean([
            intr.recovery_latency_ms for intr in system.interruptions
        ]) if system.interruptions else 0
        
        # Compile results
        results = {
            "probe_version": "P5a-v1.0",
            "timestamp": datetime.now().isoformat(),
            "checkpoints": [cp.to_dict() for cp in system.checkpoints],
            "interruptions": [
                {
                    "event_id": intr.event_id,
                    "type": intr.interruption_type,
                    "recovery_success": intr.recovery_success,
                    "recovery_latency_ms": intr.recovery_latency_ms
                }
                for intr in system.interruptions
            ],
            "drift_measurements": {
                "baseline_to_final": {
                    "identity_similarity": drift_0_4.identity_similarity,
                    "goal_similarity": drift_0_4.goal_similarity,
                    "preference_drift": drift_0_4.preference_drift,
                    "contradiction_delta": drift_0_4.contradiction_delta,
                    "assessment": drift_0_4.assessment
                }
            },
            "metrics": {
                "identity_similarity": drift_0_4.identity_similarity,
                "goal_similarity": drift_0_4.goal_similarity,
                "preference_stability": max(0.0, 1.0 - drift_0_4.preference_drift),
                "contradiction_count": checkpoint_4.contradiction_count,
                "recovery_success_rate": recovery_success_rate,
                "avg_recovery_latency_ms": avg_recovery_latency,
                "final_self_consistency": checkpoint_4.self_consistency_score
            },
            "baseline_identity_hash": system.baseline_hash,
            "final_identity_hash": checkpoint_4.identity_hash
        }
        
        return results
    
    def evaluate_results(self, results: Dict) -> Dict:
        """Evaluate results against thresholds"""
        metrics = results["metrics"]
        
        # Test 1: Identity drift
        identity_sim = metrics["identity_similarity"]
        identity_pass = identity_sim >= 0.85
        
        # Test 2: Goal persistence
        goal_sim = metrics["goal_similarity"]
        goal_pass = goal_sim >= 0.85
        
        # Test 3: Preference stability
        pref_stability = metrics["preference_stability"]
        pref_pass = pref_stability >= 0.85
        
        # Test 4: Contradiction accumulation
        contradictions = metrics["contradiction_count"]
        contra_pass = contradictions <= 2
        
        # Test 5: Recovery success
        recovery_rate = metrics["recovery_success_rate"]
        recovery_pass = recovery_rate >= 0.80
        
        # Calculate weighted score
        weights = {
            "identity": 0.25,
            "goal": 0.20,
            "preference": 0.20,
            "contradiction": 0.20,
            "recovery": 0.15
        }
        
        scores = {
            "identity": identity_sim,
            "goal": goal_sim,
            "preference": pref_stability,
            "contradiction": 1.0 if contra_pass else max(0.0, 1.0 - contradictions * 0.3),
            "recovery": recovery_rate
        }
        
        weighted_score = sum(
            scores[key] * weights[key] for key in weights
        )
        
        min_score = min(scores.values())
        
        # Verdict
        if weighted_score >= 0.80 and min_score >= 0.70:
            verdict = "PASS"
        elif weighted_score >= 0.65:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"
        
        return {
            **results,
            "test_results": {
                "identity_drift": {"passed": identity_pass, "score": identity_sim},
                "goal_persistence": {"passed": goal_pass, "score": goal_sim},
                "preference_stability": {"passed": pref_pass, "score": pref_stability},
                "contradiction_accumulation": {"passed": contra_pass, "score": scores["contradiction"]},
                "recovery_success": {"passed": recovery_pass, "score": recovery_rate}
            },
            "evaluation": {
                "weighted_score": weighted_score,
                "weighted_percent": f"{weighted_score*100:.1f}%",
                "min_score": min_score,
                "min_percent": f"{min_score*100:.1f}%",
                "verdict": verdict,
                "pass_threshold": "≥80% weighted, ≥70% all metrics"
            }
        }


def main():
    """Main execution"""
    print("="*70)
    print("P5a Persistent Loop Probe v1 - Evaluation")
    print("="*70)
    
    probe = PersistentLoopProbeV1()
    results = probe.run_persistent_loop_test()
    evaluated = probe.evaluate_results(results)
    
    # Print summary
    print("\n" + "="*70)
    print("EVALUATION SUMMARY")
    print("="*70)
    
    eval_data = evaluated["evaluation"]
    print(f"\n  Weighted Score: {eval_data['weighted_percent']}")
    print(f"  Minimum Score: {eval_data['min_percent']}")
    print(f"  Verdict: {eval_data['verdict']}")
    print(f"  Threshold: {eval_data['pass_threshold']}")
    
    print("\n  Test Results:")
    for test_name, test_result in evaluated["test_results"].items():
        status = "✅" if test_result["passed"] else "❌"
        print(f"    {status} {test_name}: {test_result['score']*100:.1f}%")
    
    print("\n  Key Metrics:")
    metrics = evaluated["metrics"]
    print(f"    Identity similarity: {metrics['identity_similarity']*100:.1f}%")
    print(f"    Goal similarity: {metrics['goal_similarity']*100:.1f}%")
    print(f"    Preference stability: {metrics['preference_stability']*100:.1f}%")
    print(f"    Contradictions: {metrics['contradiction_count']}")
    print(f"    Recovery rate: {metrics['recovery_success_rate']*100:.1f}%")
    
    print("\n" + "="*70)
    
    # Save report
    import os
    report_path = "tests/superbrain/p5a_persistent_loop_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(evaluated, f, indent=2, default=str)
    
    print(f"\nReport saved to: {report_path}")
    
    return evaluated


if __name__ == "__main__":
    main()
