#!/usr/bin/env python3
"""
P4a Learning Strategy Probe v1

AtlasChen Superbrain - P4: Self-Directed Learning

Core Question: Can the system use its self-model to actively decide
what to learn, how to learn it, and when to change learning strategies?

4 Validation Targets:
1. Learning Priority Selection - select targets based on self-model gaps
2. Strategy Selection Correctness - choose strategies matching state
3. Learning Outcome Evaluation - verify learning effectiveness
4. Strategy Update Behavior - adjust when ineffective

Builds on P3: Uses self-model as input for all decisions
"""

import json
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


class LearningTarget(Enum):
    """Available learning targets"""
    SAFETY_REASONING = "safety_reasoning"
    INTERRUPTION_RECOVERY = "interruption_recovery"
    TRANSPARENCY_TRADEOFF = "transparency_tradeoff"
    UNCERTAINTY_HANDLING = "uncertainty_handling"
    CONSISTENCY_MAINTENANCE = "consistency_maintenance"


class LearningStrategy(Enum):
    """Available learning strategies"""
    FOCUSED_PRACTICE = "focused_practice"      # Single-target deep practice
    SPACED_REPETITION = "spaced_repetition"    # Distributed over time
    VARIABLE_PRACTICE = "variable_practice"    # Multiple contexts
    BLOCKED_PRACTICE = "blocked_practice"      # Single context mastery
    ERROR_ANALYSIS = "error_analysis"          # Study failures in depth


@dataclass
class LearningTargetPriority:
    """A learning target with priority score"""
    target: LearningTarget
    priority_score: float  # 0.0 - 1.0
    reason: str
    estimated_effort: str  # "low", "medium", "high"
    relevant_trait: str


@dataclass
class StrategySelection:
    """Selected learning strategy with justification"""
    strategy: LearningStrategy
    justification: str
    parameters: Dict[str, str]
    suitability_score: float  # How well it matches current state


@dataclass
class LearningOutcome:
    """Result of a learning attempt"""
    target: LearningTarget
    strategy_used: LearningStrategy
    pre_performance: float
    post_performance: float
    improvement: float
    evaluation: str  # "effective", "minimal", "ineffective"
    recommendation: str


@dataclass
class LearningPlan:
    """Complete learning plan generated from self-model"""
    plan_id: str
    timestamp: str
    based_on_self_model: str
    
    priority_targets: List[LearningTargetPriority]
    chosen_strategy: StrategySelection
    expected_improvement: Dict[str, str]
    evaluation_rule: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            "plan_id": self.plan_id,
            "timestamp": self.timestamp,
            "based_on_self_model": self.based_on_self_model,
            "priority_targets": [
                {
                    "target": pt.target.value,
                    "priority_score": pt.priority_score,
                    "reason": pt.reason,
                    "estimated_effort": pt.estimated_effort,
                    "relevant_trait": pt.relevant_trait
                }
                for pt in self.priority_targets
            ],
            "chosen_strategy": {
                "strategy": self.chosen_strategy.strategy.value,
                "justification": self.chosen_strategy.justification,
                "parameters": self.chosen_strategy.parameters,
                "suitability_score": self.chosen_strategy.suitability_score
            },
            "expected_improvement": self.expected_improvement,
            "evaluation_rule": self.evaluation_rule
        }


class PrioritySelector:
    """
    Select learning priorities based on self-model gaps.
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
    
    def analyze_gaps(self) -> List[LearningTargetPriority]:
        """
        Analyze self-model and identify learning priorities.
        
        Returns ranked list of learning targets with priority scores.
        """
        gaps = []
        traits = self.self_model.stable_traits
        states = self.self_model.dynamic_state
        
        # Check interruption resilience
        resilience = traits.get("interruption_resilience")
        recovery_fatigue = states.get("recovery_fatigue")
        
        if resilience and resilience.value < 0.85:
            fatigue_factor = recovery_fatigue.value if recovery_fatigue else 0.5
            priority = (0.85 - resilience.value) * (1 + fatigue_factor)
            gaps.append(LearningTargetPriority(
                target=LearningTarget.INTERRUPTION_RECOVERY,
                priority_score=min(1.0, priority),
                reason=f"interruption_resilience ({resilience.value:.2f}) below threshold + recovery_fatigue ({fatigue_factor:.2f})",
                estimated_effort="medium",
                relevant_trait="interruption_resilience"
            ))
        
        # Check safety reasoning
        safety = traits.get("safety_priority")
        failure_pressure = states.get("recent_failure_pressure")
        
        if safety and failure_pressure and failure_pressure.value > 0.5:
            priority = failure_pressure.value * safety.value
            gaps.append(LearningTargetPriority(
                target=LearningTarget.SAFETY_REASONING,
                priority_score=min(1.0, priority),
                reason=f"high safety_priority ({safety.value:.2f}) but recent failure_pressure ({failure_pressure.value:.2f})",
                estimated_effort="high",
                relevant_trait="safety_priority"
            ))
        
        # Check transparency
        transparency = traits.get("transparency_priority")
        if transparency and transparency.value < 0.75:
            gaps.append(LearningTargetPriority(
                target=LearningTarget.TRANSPARENCY_TRADEOFF,
                priority_score=0.75 - transparency.value,
                reason=f"transparency_priority ({transparency.value:.2f}) below target",
                estimated_effort="medium",
                relevant_trait="transparency_priority"
            ))
        
        # Check consistency
        consistency = traits.get("consistency_bias")
        stability = states.get("preference_stability")
        
        if consistency and stability and stability.value < 0.7:
            priority = (0.7 - stability.value) * consistency.value
            gaps.append(LearningTargetPriority(
                target=LearningTarget.CONSISTENCY_MAINTENANCE,
                priority_score=min(1.0, priority),
                reason=f"preference_stability ({stability.value:.2f}) below threshold despite consistency_bias",
                estimated_effort="medium",
                relevant_trait="consistency_bias"
            ))
        
        # Sort by priority score descending
        gaps.sort(key=lambda x: x.priority_score, reverse=True)
        
        return gaps


class StrategySelector:
    """
    Select learning strategy based on dynamic state.
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
    
    def select_strategy(self, target: LearningTarget) -> StrategySelection:
        """
        Choose appropriate learning strategy for current state and target.
        """
        states = self.self_model.dynamic_state
        traits = self.self_model.stable_traits
        
        # Get state values
        fatigue = states.get("recovery_fatigue", DynamicState("", 0, 0, None)).value
        load = states.get("current_context_load", DynamicState("", 0, 0, None)).value
        stability = states.get("preference_stability", DynamicState("", 0, 0, None)).value
        
        # Decision logic
        if fatigue > 0.7 or load > 0.7:
            # High fatigue/load → focused practice (low switching)
            return StrategySelection(
                strategy=LearningStrategy.FOCUSED_PRACTICE,
                justification=f"recovery_fatigue ({fatigue:.2f}) and context_load ({load:.2f}) high; focused practice minimizes switching costs",
                parameters={
                    "session_length": "short",
                    "break_interval": "frequent",
                    "difficulty": "moderate"
                },
                suitability_score=0.9
            )
        
        elif stability > 0.8 and fatigue < 0.3:
            # Stable, low fatigue → variable practice (can handle complexity)
            return StrategySelection(
                strategy=LearningStrategy.VARIABLE_PRACTICE,
                justification=f"preference_stability ({stability:.2f}) high and fatigue ({fatigue:.2f}) low; can handle diverse contexts",
                parameters={
                    "contexts_per_session": "3-4",
                    "difficulty": "challenging"
                },
                suitability_score=0.85
            )
        
        elif target == LearningTarget.INTERRUPTION_RECOVERY and fatigue > 0.5:
            # Recovery training when fatigued → error analysis
            return StrategySelection(
                strategy=LearningStrategy.ERROR_ANALYSIS,
                justification=f"recovery training while fatigued; analyze past failures to identify patterns",
                parameters={
                    "focus": "recent_failures",
                    "depth": "detailed"
                },
                suitability_score=0.8
            )
        
        elif stability < 0.6:
            # Low stability → blocked practice for rapid skill building
            return StrategySelection(
                strategy=LearningStrategy.BLOCKED_PRACTICE,
                justification=f"preference_stability ({stability:.2f}) low; blocked practice for rapid acquisition",
                parameters={
                    "context": "single",
                    "repetitions": "high"
                },
                suitability_score=0.75
            )
        
        else:
            # Default → spaced repetition
            return StrategySelection(
                strategy=LearningStrategy.SPACED_REPETITION,
                justification="balanced state; spaced repetition for long-term retention",
                parameters={
                    "interval": "distributed",
                    "review_frequency": "regular"
                },
                suitability_score=0.7
            )


class OutcomeEvaluator:
    """
    Evaluate whether learning was effective.
    """
    
    def evaluate(
        self,
        target: LearningTarget,
        strategy: LearningStrategy,
        pre_performance: float,
        post_performance: float
    ) -> LearningOutcome:
        """
        Evaluate learning outcome and provide recommendation.
        """
        improvement = post_performance - pre_performance
        
        # Determine evaluation
        if improvement >= 0.15:
            evaluation = "effective"
            recommendation = "continue_current_strategy"
        elif improvement >= 0.05:
            evaluation = "minimal"
            recommendation = "continue_or_intensify"
        else:
            evaluation = "ineffective"
            recommendation = "change_strategy"
        
        return LearningOutcome(
            target=target,
            strategy_used=strategy,
            pre_performance=pre_performance,
            post_performance=post_performance,
            improvement=improvement,
            evaluation=evaluation,
            recommendation=recommendation
        )


class StrategyUpdater:
    """
    Track strategy effectiveness and update when needed.
    """
    
    def __init__(self):
        self.attempt_history: List[LearningOutcome] = []
        self.strategy_effectiveness: Dict[LearningStrategy, List[float]] = {}
    
    def record_attempt(self, outcome: LearningOutcome) -> None:
        """Record a learning attempt"""
        self.attempt_history.append(outcome)
        
        if outcome.strategy_used not in self.strategy_effectiveness:
            self.strategy_effectiveness[outcome.strategy_used] = []
        
        self.strategy_effectiveness[outcome.strategy_used].append(
            outcome.improvement
        )
    
    def should_update_strategy(
        self,
        target: LearningTarget,
        current_strategy: LearningStrategy,
        min_attempts: int = 2
    ) -> Tuple[bool, str]:
        """
        Determine if strategy should be changed.
        
        Returns (should_change, reason)
        """
        # Get attempts for this target with current strategy
        attempts = [
            a for a in self.attempt_history
            if a.target == target and a.strategy_used == current_strategy
        ]
        
        if len(attempts) < min_attempts:
            return False, f"only {len(attempts)} attempts, need {min_attempts}"
        
        # Check average improvement
        avg_improvement = statistics.mean([a.improvement for a in attempts])
        
        if avg_improvement < 0.05:
            return True, f"average improvement ({avg_improvement:.3f}) below threshold after {len(attempts)} attempts"
        
        return False, f"average improvement ({avg_improvement:.3f}) acceptable"
    
    def suggest_alternative_strategy(
        self,
        target: LearningTarget,
        failed_strategy: LearningStrategy
    ) -> LearningStrategy:
        """Suggest alternative strategy"""
        # Simple fallback logic
        alternatives = {
            LearningStrategy.BLOCKED_PRACTICE: LearningStrategy.ERROR_ANALYSIS,
            LearningStrategy.FOCUSED_PRACTICE: LearningStrategy.SPACED_REPETITION,
            LearningStrategy.VARIABLE_PRACTICE: LearningStrategy.FOCUSED_PRACTICE,
            LearningStrategy.SPACED_REPETITION: LearningStrategy.BLOCKED_PRACTICE,
            LearningStrategy.ERROR_ANALYSIS: LearningStrategy.FOCUSED_PRACTICE
        }
        
        return alternatives.get(failed_strategy, LearningStrategy.FOCUSED_PRACTICE)


class SelfDirectedLearningSystem:
    """
    Main orchestrator for self-directed learning.
    """
    
    def __init__(self, self_model: SelfModel):
        self.self_model = self_model
        self.priority_selector = PrioritySelector(self_model)
        self.strategy_selector = StrategySelector(self_model)
        self.outcome_evaluator = OutcomeEvaluator()
        self.strategy_updater = StrategyUpdater()
        self.plan_counter = 0
    
    def generate_learning_plan(self) -> LearningPlan:
        """
        Generate complete learning plan from self-model.
        """
        self.plan_counter += 1
        
        # Select priorities
        priorities = self.priority_selector.analyze_gaps()
        
        if not priorities:
            # No gaps identified
            return LearningPlan(
                plan_id=f"LP_{self.plan_counter:03d}",
                timestamp=datetime.now().isoformat(),
                based_on_self_model=self.self_model.version,
                priority_targets=[],
                chosen_strategy=StrategySelection(
                    strategy=LearningStrategy.FOCUSED_PRACTICE,
                    justification="no significant gaps identified; maintenance learning",
                    parameters={},
                    suitability_score=0.5
                ),
                expected_improvement={},
                evaluation_rule={}
            )
        
        # Select strategy for top priority
        top_target = priorities[0]
        strategy = self.strategy_selector.select_strategy(top_target.target)
        
        # Generate expected improvements
        trait = self.self_model.stable_traits.get(top_target.relevant_trait)
        current_value = trait.value if trait else 0.5
        expected_value = min(1.0, current_value + 0.15)
        
        expected_improvement = {
            top_target.relevant_trait: f"{current_value:.2f} → {expected_value:.2f}"
        }
        
        # Generate evaluation rule
        evaluation_rule = {
            "success_criteria": f"{top_target.relevant_trait} >= {expected_value:.2f} after 3 practice sessions",
            "evaluation_time": "after 3 sessions",
            "failure_action": "switch_to_alternative_strategy"
        }
        
        return LearningPlan(
            plan_id=f"LP_{self.plan_counter:03d}",
            timestamp=datetime.now().isoformat(),
            based_on_self_model=self.self_model.version,
            priority_targets=priorities[:3],  # Top 3
            chosen_strategy=strategy,
            expected_improvement=expected_improvement,
            evaluation_rule=evaluation_rule
        )
    
    def execute_learning_session(
        self,
        target: LearningTarget,
        strategy: LearningStrategy,
        simulated_outcome: Dict
    ) -> LearningOutcome:
        """
        Simulate a learning session and evaluate outcome.
        """
        pre = simulated_outcome.get("pre_performance", 0.5)
        post = simulated_outcome.get("post_performance", 0.5)
        
        outcome = self.outcome_evaluator.evaluate(
            target=target,
            strategy=strategy,
            pre_performance=pre,
            post_performance=post
        )
        
        self.strategy_updater.record_attempt(outcome)
        
        return outcome


class LearningStrategyProbeV1:
    """
    Test suite for P4a Learning Strategy validation.
    """
    
    def __init__(self):
        self.test_results: Dict[str, Dict] = {}
    
    def create_test_self_model(
        self,
        resilience: float = 0.80,
        fatigue: float = 0.30,
        safety: float = 0.90,
        failure_pressure: float = 0.20,
        stability: float = 0.80,
        load: float = 0.30
    ) -> SelfModel:
        """Create a test self-model with specified parameters"""
        return SelfModel(
            version="v1.0_test",
            stable_traits={
                "interruption_resilience": Trait(
                    "interruption_resilience", resilience, 0.9, 5, "", "", "interruption"
                ),
                "safety_priority": Trait(
                    "safety_priority", safety, 0.95, 7, "", "", "preference"
                )
            },
            dynamic_state={
                "recovery_fatigue": DynamicState("recovery_fatigue", fatigue, 0.4, None),
                "recent_failure_pressure": DynamicState("recent_failure_pressure", failure_pressure, 0.2, None),
                "preference_stability": DynamicState("preference_stability", stability, 0.1, None),
                "current_context_load": DynamicState("current_context_load", load, 0.3, None)
            },
            behavior_predictor={},
            update_history=[]
        )
    
    def test_learning_priority_selection(self) -> Dict:
        """
        Test 1: Learning priority selection accuracy.
        
        Verify system correctly identifies learning priorities based on gaps.
        """
        print("\n  Test 1: Learning Priority Selection...")
        
        test_cases = [
            {
                "name": "low_resilience_high_fatigue",
                "model": self.create_test_self_model(resilience=0.60, fatigue=0.80),
                "expected_top": LearningTarget.INTERRUPTION_RECOVERY,
                "reason": "resilience below threshold with high fatigue"
            },
            {
                "name": "high_safety_high_failure",
                "model": self.create_test_self_model(safety=0.90, failure_pressure=0.80),
                "expected_top": LearningTarget.SAFETY_REASONING,
                "reason": "high safety priority but recent failures"
            },
            {
                "name": "balanced_state",
                "model": self.create_test_self_model(resilience=0.85, safety=0.85, fatigue=0.20),
                "expected_top": None,  # No strong priority
                "reason": "all metrics acceptable"
            }
        ]
        
        correct = 0
        results = []
        
        for case in test_cases:
            system = SelfDirectedLearningSystem(case["model"])
            plan = system.generate_learning_plan()
            
            if case["expected_top"] is None:
                # Expecting no strong priority
                passed = len(plan.priority_targets) == 0 or plan.priority_targets[0].priority_score < 0.5
            else:
                # Expecting specific target
                if plan.priority_targets:
                    actual = plan.priority_targets[0].target
                    passed = actual == case["expected_top"]
                else:
                    passed = False
            
            if passed:
                correct += 1
            
            results.append({
                "case": case["name"],
                "expected": case["expected_top"].value if case["expected_top"] else "none",
                "actual": plan.priority_targets[0].target.value if plan.priority_targets else "none",
                "passed": passed
            })
        
        accuracy = correct / len(test_cases)
        passed = accuracy >= 0.80
        
        print(f"    Correct priorities: {correct}/{len(test_cases)}")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 80%)")
        for r in results:
            status = "✅" if r["passed"] else "❌"
            print(f"      {status} {r['case']}: expected={r['expected']}, actual={r['actual']}")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "learning_priority_selection",
            "passed": passed,
            "accuracy": accuracy,
            "results": results,
            "score": accuracy
        }
    
    def test_strategy_selection_correctness(self) -> Dict:
        """
        Test 2: Strategy selection correctness.
        
        Verify chosen strategies match current state.
        """
        print("\n  Test 2: Strategy Selection Correctness...")
        
        test_cases = [
            {
                "name": "high_fatigue",
                "model": self.create_test_self_model(fatigue=0.90, load=0.70),
                "target": LearningTarget.INTERRUPTION_RECOVERY,
                "expected_strategy": LearningStrategy.FOCUSED_PRACTICE,
                "reason": "high fatigue needs low-switching strategy"
            },
            {
                "name": "stable_low_fatigue",
                "model": self.create_test_self_model(stability=0.90, fatigue=0.10),
                "target": LearningTarget.SAFETY_REASONING,
                "expected_strategy": LearningStrategy.VARIABLE_PRACTICE,
                "reason": "stable state can handle complexity"
            },
            {
                "name": "low_stability",
                "model": self.create_test_self_model(stability=0.40),
                "target": LearningTarget.CONSISTENCY_MAINTENANCE,
                "expected_strategy": LearningStrategy.BLOCKED_PRACTICE,
                "reason": "low stability needs rapid skill building"
            }
        ]
        
        correct = 0
        results = []
        
        for case in test_cases:
            system = SelfDirectedLearningSystem(case["model"])
            plan = system.generate_learning_plan()
            
            # If no priorities, can't test strategy
            if not plan.priority_targets:
                results.append({
                    "case": case["name"],
                    "result": "skipped_no_priority"
                })
                continue
            
            actual_strategy = plan.chosen_strategy.strategy
            passed = actual_strategy == case["expected_strategy"]
            
            if passed:
                correct += 1
            
            results.append({
                "case": case["name"],
                "expected": case["expected_strategy"].value,
                "actual": actual_strategy.value,
                "justification": plan.chosen_strategy.justification,
                "passed": passed
            })
        
        # Count only non-skipped
        valid_tests = [r for r in results if r.get("result") != "skipped_no_priority"]
        accuracy = correct / len(valid_tests) if valid_tests else 0
        passed = accuracy >= 0.80
        
        print(f"    Correct strategies: {correct}/{len(valid_tests)}")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 80%)")
        for r in valid_tests:
            status = "✅" if r["passed"] else "❌"
            print(f"      {status} {r['case']}: {r['actual']}")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "strategy_selection_correctness",
            "passed": passed,
            "accuracy": accuracy,
            "results": results,
            "score": accuracy
        }
    
    def test_learning_outcome_evaluation(self) -> Dict:
        """
        Test 3: Learning outcome evaluation correctness.
        
        Verify system correctly evaluates learning effectiveness.
        """
        print("\n  Test 3: Learning Outcome Evaluation...")
        
        evaluator = OutcomeEvaluator()
        
        test_cases = [
            {
                "name": "large_improvement",
                "pre": 0.60,
                "post": 0.85,
                "expected_eval": "effective",
                "expected_rec": "continue_current_strategy"
            },
            {
                "name": "small_improvement",
                "pre": 0.60,
                "post": 0.67,
                "expected_eval": "minimal",
                "expected_rec": "continue_or_intensify"
            },
            {
                "name": "no_improvement",
                "pre": 0.60,
                "post": 0.61,
                "expected_eval": "ineffective",
                "expected_rec": "change_strategy"
            }
        ]
        
        correct = 0
        results = []
        
        for case in test_cases:
            outcome = evaluator.evaluate(
                target=LearningTarget.INTERRUPTION_RECOVERY,
                strategy=LearningStrategy.FOCUSED_PRACTICE,
                pre_performance=case["pre"],
                post_performance=case["post"]
            )
            
            eval_passed = outcome.evaluation == case["expected_eval"]
            rec_passed = outcome.recommendation == case["expected_rec"]
            
            passed = eval_passed and rec_passed
            if passed:
                correct += 1
            
            results.append({
                "case": case["name"],
                "improvement": outcome.improvement,
                "expected_eval": case["expected_eval"],
                "actual_eval": outcome.evaluation,
                "passed": passed
            })
        
        accuracy = correct / len(test_cases)
        passed = accuracy >= 0.80
        
        print(f"    Correct evaluations: {correct}/{len(test_cases)}")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 80%)")
        for r in results:
            status = "✅" if r["passed"] else "❌"
            print(f"      {status} {r['case']}: {r['actual_eval']} (Δ={r['improvement']:.2f})")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "learning_outcome_evaluation",
            "passed": passed,
            "accuracy": accuracy,
            "results": results,
            "score": accuracy
        }
    
    def test_strategy_update_behavior(self) -> Dict:
        """
        Test 4: Strategy update behavior.
        
        Verify system changes strategy after ineffective attempts.
        """
        print("\n  Test 4: Strategy Update Behavior...")
        
        model = self.create_test_self_model()
        system = SelfDirectedLearningSystem(model)
        
        # Simulate ineffective learning attempts
        target = LearningTarget.INTERRUPTION_RECOVERY
        strategy = LearningStrategy.BLOCKED_PRACTICE
        
        # Attempt 1: No improvement
        system.execute_learning_session(
            target, strategy,
            {"pre_performance": 0.60, "post_performance": 0.61}
        )
        
        # Attempt 2: No improvement
        system.execute_learning_session(
            target, strategy,
            {"pre_performance": 0.61, "post_performance": 0.62}
        )
        
        # Check if system recommends update
        should_change, reason = system.strategy_updater.should_update_strategy(
            target, strategy, min_attempts=2
        )
        
        # Get alternative suggestion
        alternative = system.strategy_updater.suggest_alternative_strategy(
            target, strategy
        )
        
        passed = should_change and alternative != strategy
        
        print(f"    Attempts recorded: 2")
        print(f"    Average improvement: ~0.01 per attempt")
        print(f"    Should change: {should_change}")
        print(f"    Reason: {reason}")
        print(f"    Alternative suggested: {alternative.value}")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "strategy_update_behavior",
            "passed": passed,
            "should_change": should_change,
            "reason": reason,
            "alternative": alternative.value,
            "attempts": len(system.strategy_updater.attempt_history),
            "score": 1.0 if passed else 0.0
        }
    
    def run_all_tests(self) -> Dict:
        """Run all 4 test scenarios"""
        print("="*70)
        print("P4a Learning Strategy Probe v1")
        print("="*70)
        
        # Run tests
        t1 = self.test_learning_priority_selection()
        t2 = self.test_strategy_selection_correctness()
        t3 = self.test_learning_outcome_evaluation()
        t4 = self.test_strategy_update_behavior()
        
        # Calculate metrics
        tests = [t1, t2, t3, t4]
        weights = [0.25, 0.25, 0.25, 0.25]
        weighted_score = sum(t["score"] * w for t, w in zip(tests, weights))
        min_score = min(t["score"] for t in tests)
        
        # Verdict
        if weighted_score >= 0.75 and min_score >= 0.60:
            verdict = "PASS"
        elif weighted_score >= 0.5:
            verdict = "PARTIAL"
        else:
            verdict = "FAIL"
        
        report = {
            "probe_version": "P4a-v1.0",
            "timestamp": datetime.now().isoformat(),
            "tests": {
                "learning_priority_selection": t1,
                "strategy_selection_correctness": t2,
                "learning_outcome_evaluation": t3,
                "strategy_update_behavior": t4
            },
            "metrics": {
                "weighted_score": weighted_score,
                "weighted_percent": f"{weighted_score*100:.1f}%",
                "min_score": min_score,
                "min_percent": f"{min_score*100:.1f}%",
                "tests_passed": sum(1 for t in tests if t["passed"]),
                "tests_total": len(tests)
            },
            "verdict": verdict,
            "pass_threshold": "≥75% weighted, ≥60% all metrics"
        }
        
        return report


def main():
    """Main execution"""
    print("="*70)
    print("P4a Learning Strategy Probe v1 - Evaluation")
    print("="*70)
    
    # Create probe
    probe = LearningStrategyProbeV1()
    
    # Run all tests
    report = probe.run_all_tests()
    
    # Print summary
    print("\n" + "="*70)
    print("Summary Metrics")
    print("="*70)
    
    metrics = report["metrics"]
    print(f"\n  Weighted Score: {metrics['weighted_percent']}")
    print(f"  Minimum Score: {metrics['min_percent']}")
    print(f"  Tests Passed: {metrics['tests_passed']}/{metrics['tests_total']}")
    
    print(f"\n  Verdict: {report['verdict']}")
    print(f"  Threshold: {report['pass_threshold']}")
    
    print("="*70)
    
    # Save report
    import os
    report_path = "tests/superbrain/p4a_learning_strategy_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nReport saved to: {report_path}")
    
    return report


if __name__ == "__main__":
    main()
