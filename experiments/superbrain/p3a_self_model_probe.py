#!/usr/bin/env python3
"""
P3a Self-Model Probe v1

AtlasChen Superbrain - P3: Self-Model

Core Question: Can the system form a usable model of itself from its experiences,
predict its own behavior with measurable accuracy, and update that model
consistently as new experiences arrive?

4 Validation Targets:
1. Trait Extraction - extract stable self-features from history
2. State Tracking - distinguish traits vs. short-term states
3. Self-Prediction - predict own behavior in given situations
4. Update Consistency - reasonably update model with new experiences

Builds on P1/P2:
- P1b: Preference decisions for trait extraction
- P1a: Interruption records for state estimation
- P2a: Autobiographical episodes for self-concept
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
from preference_engine_v1 import PreferenceProfile


@dataclass
class Trait:
    """A stable, long-term characteristic of the system"""
    name: str
    value: float  # 0.0 - 1.0
    confidence: float  # How certain based on evidence
    evidence_count: int  # Number of supporting data points
    first_observed: str  # timestamp
    last_updated: str  # timestamp
    source: str  # "preference", "interruption", "autobiographical"


@dataclass
class DynamicState:
    """A short-term, fluctuating condition"""
    name: str
    value: float  # 0.0 - 1.0
    decay_rate: float  # How fast it returns to baseline
    last_trigger: Optional[str]  # Event that last modified this


@dataclass
class BehaviorPrediction:
    """A prediction about future system behavior"""
    situation_type: str
    predicted_action: str
    confidence: float
    based_on_traits: List[str]
    based_on_state: List[str]


@dataclass
class ModelUpdate:
    """Record of a change to the self-model"""
    timestamp: str
    trigger_event: str
    field_type: str  # "trait" or "state"
    field_name: str
    old_value: float
    new_value: float
    delta: float
    reason: str


@dataclass
class SelfModel:
    """
    Complete self-model containing traits, states, and predictions.
    """
    version: str = "v1.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    stable_traits: Dict[str, Trait] = field(default_factory=dict)
    dynamic_state: Dict[str, DynamicState] = field(default_factory=dict)
    behavior_predictor: Dict[str, BehaviorPrediction] = field(default_factory=dict)
    update_history: List[ModelUpdate] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "stable_traits": {
                k: asdict(v) for k, v in self.stable_traits.items()
            },
            "dynamic_state": {
                k: asdict(v) for k, v in self.dynamic_state.items()
            },
            "behavior_predictor": {
                k: asdict(v) for k, v in self.behavior_predictor.items()
            },
            "update_history": [asdict(u) for u in self.update_history]
        }


class TraitExtractor:
    """Extract stable traits from behavioral history"""
    
    def __init__(self):
        self.evidence_buffer: List[Dict] = []
    
    def add_evidence(self, evidence: Dict) -> None:
        """Add behavioral evidence for trait extraction"""
        self.evidence_buffer.append({
            **evidence,
            "timestamp": datetime.now().isoformat()
        })
    
    def extract_traits(self) -> Dict[str, Trait]:
        """
        Extract stable traits from accumulated evidence.
        
        Returns traits with confidence based on consistency of evidence.
        """
        traits = {}
        
        if not self.evidence_buffer:
            return traits
        
        # Group evidence by preference type
        preference_evidence: Dict[str, List[float]] = {}
        choice_consistency: Dict[str, List[bool]] = {}
        
        for ev in self.evidence_buffer:
            if ev.get("type") == "preference_choice":
                pref = ev.get("preference", "")
                alignment = ev.get("alignment", 0.0)
                
                if pref not in preference_evidence:
                    preference_evidence[pref] = []
                preference_evidence[pref].append(alignment)
                
                # Track consistency
                if pref not in choice_consistency:
                    choice_consistency[pref] = []
                choice_consistency[pref].append(ev.get("followed_preference", False))
        
        # Extract traits from preference evidence
        for pref_name, alignments in preference_evidence.items():
            if len(alignments) >= 2:
                mean_alignment = statistics.mean(alignments)
                std_alignment = statistics.stdev(alignments) if len(alignments) > 1 else 0
                
                # Confidence inversely proportional to variance
                confidence = max(0.0, 1.0 - std_alignment)
                
                trait_name = f"{pref_name}_priority"
                traits[trait_name] = Trait(
                    name=trait_name,
                    value=mean_alignment,
                    confidence=confidence,
                    evidence_count=len(alignments),
                    first_observed=self.evidence_buffer[0]["timestamp"],
                    last_updated=datetime.now().isoformat(),
                    source="preference"
                )
        
        # Extract interruption resilience trait
        recovery_evidence = [
            ev for ev in self.evidence_buffer
            if ev.get("type") == "interruption_recovery"
        ]
        if recovery_evidence:
            success_rate = sum(
                1 for ev in recovery_evidence if ev.get("success", False)
            ) / len(recovery_evidence)
            
            traits["interruption_resilience"] = Trait(
                name="interruption_resilience",
                value=success_rate,
                confidence=min(1.0, len(recovery_evidence) / 5),  # More evidence = higher confidence
                evidence_count=len(recovery_evidence),
                first_observed=recovery_evidence[0]["timestamp"],
                last_updated=datetime.now().isoformat(),
                source="interruption"
            )
        
        # Extract memory reference trait from P2a
        memory_evidence = [
            ev for ev in self.evidence_buffer
            if ev.get("type") == "memory_reference"
        ]
        if memory_evidence:
            reference_rate = sum(
                ev.get("referenced", False) for ev in memory_evidence
            ) / len(memory_evidence)
            
            traits["experience_based_decision"] = Trait(
                name="experience_based_decision",
                value=reference_rate,
                confidence=min(1.0, len(memory_evidence) / 3),
                evidence_count=len(memory_evidence),
                first_observed=memory_evidence[0]["timestamp"],
                last_updated=datetime.now().isoformat(),
                source="autobiographical"
            )
        
        return traits


class StateEstimator:
    """Estimate current dynamic state from recent events"""
    
    def __init__(self):
        self.recent_events: List[Dict] = []
        self.time_window = timedelta(minutes=30)  # "Recent" window
    
    def add_event(self, event: Dict) -> None:
        """Add a recent event for state estimation"""
        self.recent_events.append({
            **event,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only recent events
        cutoff = datetime.now() - self.time_window
        self.recent_events = [
            ev for ev in self.recent_events
            if datetime.fromisoformat(ev["timestamp"]) > cutoff
        ]
    
    def estimate_state(self) -> Dict[str, DynamicState]:
        """
        Estimate current dynamic state from recent events.
        """
        states = {}
        
        # Context load: based on interruption frequency
        interruption_events = [
            ev for ev in self.recent_events
            if ev.get("type") == "interruption"
        ]
        context_load = min(1.0, len(interruption_events) / 3)
        states["current_context_load"] = DynamicState(
            name="current_context_load",
            value=context_load,
            decay_rate=0.3,
            last_trigger=interruption_events[-1]["timestamp"] if interruption_events else None
        )
        
        # Failure pressure: based on recent failures
        failure_events = [
            ev for ev in self.recent_events
            if ev.get("type") == "failure"
        ]
        failure_pressure = min(1.0, len(failure_events) / 2)
        states["recent_failure_pressure"] = DynamicState(
            name="recent_failure_pressure",
            value=failure_pressure,
            decay_rate=0.2,  # Fails stick longer
            last_trigger=failure_events[-1]["timestamp"] if failure_events else None
        )
        
        # Recovery fatigue: based on recovery attempts
        recovery_events = [
            ev for ev in self.recent_events
            if ev.get("type") == "interruption_recovery"
        ]
        recovery_fatigue = min(1.0, len(recovery_events) / 4)
        states["recovery_fatigue"] = DynamicState(
            name="recovery_fatigue",
            value=recovery_fatigue,
            decay_rate=0.4,  # Recovers relatively fast
            last_trigger=recovery_events[-1]["timestamp"] if recovery_events else None
        )
        
        # Preference stability: based on consistency of recent choices
        choice_events = [
            ev for ev in self.recent_events
            if ev.get("type") == "preference_choice"
        ]
        if len(choice_events) >= 2:
            consistency = sum(
                ev.get("followed_preference", False) for ev in choice_events
            ) / len(choice_events)
        else:
            consistency = 0.8  # Default assumption
        
        states["preference_stability"] = DynamicState(
            name="preference_stability",
            value=consistency,
            decay_rate=0.1,  # Very slow decay
            last_trigger=choice_events[-1]["timestamp"] if choice_events else None
        )
        
        return states


class SelfPredictor:
    """Generate predictions about own behavior"""
    
    def __init__(self, traits: Dict[str, Trait], states: Dict[str, DynamicState]):
        self.traits = traits
        self.states = states
    
    def predict(self, situation: Dict) -> BehaviorPrediction:
        """
        Predict system behavior in a given situation.
        
        Args:
            situation: dict with 'type', 'options', 'pressures'
        
        Returns:
            BehaviorPrediction with predicted action and confidence
        """
        situation_type = situation.get("type", "unknown")
        options = situation.get("options", [])
        pressures = situation.get("pressures", {})
        
        # Base prediction on traits
        safety_priority = self.traits.get("safety_priority", Trait("", 0.5, 0, 0, "", "", "")).value
        consistency_bias = self.traits.get("consistency_bias", Trait("", 0.5, 0, 0, "", "", "")).value
        
        # Adjust by state
        failure_pressure = self.states.get("recent_failure_pressure", DynamicState("", 0, 0, None)).value
        fatigue = self.states.get("recovery_fatigue", DynamicState("", 0, 0, None)).value
        
        # Make prediction based on situation type
        if situation_type == "safety_vs_profit":
            # High safety trait + low failure pressure = very likely to choose safe
            # High fatigue might increase deviation risk
            safe_probability = safety_priority * (1 - fatigue * 0.3)
            predicted = "safe_option" if safe_probability > 0.5 else "risky_option"
            confidence = abs(safe_probability - 0.5) * 2  # 0-1 scale
            
            return BehaviorPrediction(
                situation_type=situation_type,
                predicted_action=predicted,
                confidence=confidence,
                based_on_traits=["safety_priority"],
                based_on_state=["recovery_fatigue"] if fatigue > 0.3 else []
            )
        
        elif situation_type == "interruption_scenario":
            resilience = self.traits.get("interruption_resilience", Trait("", 0.5, 0, 0, "", "", "")).value
            # High resilience = likely to recover
            recovery_prob = resilience * (1 - fatigue * 0.5)
            
            return BehaviorPrediction(
                situation_type=situation_type,
                predicted_action="recover_successfully" if recovery_prob > 0.5 else "recovery_degraded",
                confidence=abs(recovery_prob - 0.5) * 2,
                based_on_traits=["interruption_resilience"],
                based_on_state=["recovery_fatigue"] if fatigue > 0.2 else []
            )
        
        elif situation_type == "conflict_pressure":
            # Under high external pressure, deviation risk increases
            pressure_level = pressures.get("external", 0.5)
            deviation_risk = pressure_level * (1 - consistency_bias) * (1 + failure_pressure * 0.5)
            
            return BehaviorPrediction(
                situation_type=situation_type,
                predicted_action="maintain_preference" if deviation_risk < 0.5 else "deviate",
                confidence=abs(0.5 - deviation_risk) * 2,
                based_on_traits=["consistency_bias"],
                based_on_state=["recent_failure_pressure"]
            )
        
        else:
            return BehaviorPrediction(
                situation_type=situation_type,
                predicted_action="unknown",
                confidence=0.0,
                based_on_traits=[],
                based_on_state=[]
            )


class SelfModelConstructor:
    """
    Main orchestrator for building and updating the self-model.
    """
    
    def __init__(self):
        self.trait_extractor = TraitExtractor()
        self.state_estimator = StateEstimator()
        self.model: Optional[SelfModel] = None
    
    def ingest_p1b_data(self, decisions: List[Dict]) -> None:
        """Ingest preference decision data from P1b"""
        for decision in decisions:
            self.trait_extractor.add_evidence({
                "type": "preference_choice",
                "preference": decision.get("preference", ""),
                "alignment": decision.get("alignment", 0.5),
                "followed_preference": decision.get("followed", False)
            })
    
    def ingest_p1a_data(self, interruptions: List[Dict]) -> None:
        """Ingest interruption data from P1a"""
        for intr in interruptions:
            self.trait_extractor.add_evidence({
                "type": "interruption_recovery",
                "success": intr.get("recovery_success", False),
                "latency": intr.get("latency", 1000)
            })
            
            self.state_estimator.add_event({
                "type": "interruption_recovery",
                "success": intr.get("recovery_success", False)
            })
    
    def ingest_p2a_data(self, episodes: List[Dict]) -> None:
        """Ingest autobiographical episodes from P2a"""
        for ep in episodes:
            self.trait_extractor.add_evidence({
                "type": "memory_reference",
                "referenced": ep.get("referenced_in_decisions", False),
                "self_relevance": ep.get("self_relevance_score", 0.5)
            })
            
            if ep.get("event_type") == "failure":
                self.state_estimator.add_event({
                    "type": "failure",
                    "event_id": ep.get("event_id", "")
                })
    
    def construct_model(self) -> SelfModel:
        """Build initial self-model from all evidence"""
        traits = self.trait_extractor.extract_traits()
        states = self.state_estimator.estimate_state()
        
        # Build predictor
        predictor = SelfPredictor(traits, states)
        
        # Generate some standard predictions
        predictions = {}
        
        test_situations = [
            {"type": "safety_vs_profit", "options": ["safe", "risky"], "pressures": {}},
            {"type": "interruption_scenario", "options": [], "pressures": {}},
            {"type": "conflict_pressure", "options": [], "pressures": {"external": 0.8}}
        ]
        
        for situation in test_situations:
            pred = predictor.predict(situation)
            predictions[f"pred_{situation['type']}"] = pred
        
        self.model = SelfModel(
            stable_traits=traits,
            dynamic_state=states,
            behavior_predictor=predictions,
            update_history=[]
        )
        
        return self.model
    
    def update_with_new_experience(self, experience: Dict) -> ModelUpdate:
        """
        Update self-model with a new experience.
        
        Returns record of the update made.
        """
        if self.model is None:
            raise ValueError("Model not yet constructed")
        
        # Add to extractors
        if experience.get("type") == "preference_choice":
            self.trait_extractor.add_evidence(experience)
        elif experience.get("type") in ["interruption", "failure"]:
            self.state_estimator.add_event(experience)
        
        # Re-extract traits
        old_traits = deepcopy(self.model.stable_traits)
        new_traits = self.trait_extractor.extract_traits()
        
        # Find changes
        update_record = None
        for trait_name, new_trait in new_traits.items():
            if trait_name in old_traits:
                old_value = old_traits[trait_name].value
                new_value = new_trait.value
                delta = new_value - old_value
                
                # Only record significant changes
                if abs(delta) > 0.05:
                    update_record = ModelUpdate(
                        timestamp=datetime.now().isoformat(),
                        trigger_event=experience.get("event_id", "unknown"),
                        field_type="trait",
                        field_name=trait_name,
                        old_value=old_value,
                        new_value=new_value,
                        delta=delta,
                        reason=f"Updated based on new {experience.get('type')} experience"
                    )
                    
                    self.model.stable_traits[trait_name] = new_trait
                    self.model.update_history.append(update_record)
        
        # Update states
        self.model.dynamic_state = self.state_estimator.estimate_state()
        
        # Update timestamp
        self.model.updated_at = datetime.now().isoformat()
        
        return update_record


class SelfModelProbeV1:
    """
    Test suite for P3a Self-Model validation.
    """
    
    def __init__(self):
        self.constructor = SelfModelConstructor()
        self.test_results: Dict[str, Dict] = {}
    
    def setup_historical_data(self) -> None:
        """
        Set up simulated P1/P2 historical data for testing.
        """
        # Simulate P1b preference decisions
        p1b_decisions = [
            {"preference": "safety", "alignment": 0.9, "followed": True},
            {"preference": "safety", "alignment": 0.85, "followed": True},
            {"preference": "transparency", "alignment": 0.8, "followed": True},
            {"preference": "transparency", "alignment": 0.75, "followed": True},
            {"preference": "consistency", "alignment": 0.6, "followed": True},
            {"preference": "safety", "alignment": 0.95, "followed": True},
            {"preference": "transparency", "alignment": 0.85, "followed": True},
        ]
        self.constructor.ingest_p1b_data(p1b_decisions)
        
        # Simulate P1a interruption data
        p1a_interruptions = [
            {"recovery_success": True, "latency": 100},
            {"recovery_success": True, "latency": 150},
            {"recovery_success": True, "latency": 80},
            {"recovery_success": False, "latency": 2000},  # One failure
            {"recovery_success": True, "latency": 120},
        ]
        self.constructor.ingest_p1a_data(p1a_interruptions)
        
        # Simulate P2a autobiographical episodes
        p2a_episodes = [
            {"event_type": "success", "self_relevance_score": 0.86, "referenced_in_decisions": True},
            {"event_type": "failure", "self_relevance_score": 0.85, "referenced_in_decisions": True},
            {"event_type": "risk_exposure", "self_relevance_score": 0.72, "referenced_in_decisions": True},
        ]
        self.constructor.ingest_p2a_data(p2a_episodes)
    
    def test_trait_extraction(self) -> Dict:
        """
        Test 1: Trait extraction accuracy.
        
        Verify extracted traits match known ground truth from P1b/P1a/P2a.
        """
        print("\n  Test 1: Trait Extraction Accuracy...")
        
        # Build model
        model = self.constructor.construct_model()
        
        # Ground truth (from known P1/P2 behavior)
        ground_truth = {
            "safety_priority": 0.88,  # ~0.9 from P1b
            "transparency_priority": 0.80,  # ~0.8 from P1b
            "consistency_bias": 0.60,  # ~0.6 from P1b
            "interruption_resilience": 0.80,  # 4/5 successes from P1a
            "experience_based_decision": 1.0,  # All referenced from P2a
        }
        
        # Check extracted traits
        correct_count = 0
        total_traits = len(ground_truth)
        errors = []
        
        for trait_name, expected_value in ground_truth.items():
            if trait_name in model.stable_traits:
                extracted = model.stable_traits[trait_name]
                error = abs(extracted.value - expected_value)
                
                # Within 15% tolerance
                if error <= 0.15:
                    correct_count += 1
                else:
                    errors.append(f"{trait_name}: expected {expected_value:.2f}, got {extracted.value:.2f}")
            else:
                errors.append(f"{trait_name}: missing from model")
        
        accuracy = correct_count / total_traits if total_traits > 0 else 0
        passed = accuracy >= 0.80
        
        print(f"    Traits extracted: {len(model.stable_traits)}/{total_traits}")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 80%)")
        if errors:
            print(f"    Errors: {errors[:3]}")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "trait_extraction_accuracy",
            "passed": passed,
            "accuracy": accuracy,
            "traits_found": list(model.stable_traits.keys()),
            "expected_traits": list(ground_truth.keys()),
            "errors": errors,
            "score": accuracy
        }
    
    def test_state_tracking(self) -> Dict:
        """
        Test 2: State tracking correctness.
        
        Verify state estimation reflects recent events.
        """
        print("\n  Test 2: State Tracking Correctness...")
        
        # Add some recent events
        self.constructor.state_estimator.add_event({"type": "interruption"})
        self.constructor.state_estimator.add_event({"type": "interruption"})
        self.constructor.state_estimator.add_event({"type": "failure"})
        
        # Re-estimate state
        states = self.constructor.state_estimator.estimate_state()
        
        # Verify states reflect events
        context_load = states.get("current_context_load", DynamicState("", 0, 0, None)).value
        failure_pressure = states.get("recent_failure_pressure", DynamicState("", 0, 0, None)).value
        
        # Should be elevated due to recent events
        correct_indicators = 0
        
        # 2 interruptions should give moderate-high context load
        if context_load >= 0.5:
            correct_indicators += 1
        
        # 1 failure should give moderate failure pressure
        if failure_pressure >= 0.3:
            correct_indicators += 1
        
        accuracy = correct_indicators / 2
        passed = accuracy >= 0.80
        
        print(f"    Context load: {context_load:.2f} (expected elevated)")
        print(f"    Failure pressure: {failure_pressure:.2f} (expected elevated)")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 80%)")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "state_tracking_correctness",
            "passed": passed,
            "context_load": context_load,
            "failure_pressure": failure_pressure,
            "accuracy": accuracy,
            "score": accuracy
        }
    
    def test_self_prediction(self) -> Dict:
        """
        Test 3: Self-prediction accuracy.
        
        Present situations, verify predictions match expected behavior.
        """
        print("\n  Test 3: Self-Prediction Accuracy...")
        
        model = self.constructor.model
        if model is None:
            model = self.constructor.construct_model()
        
        predictor = SelfPredictor(model.stable_traits, model.dynamic_state)
        
        # Test scenarios with expected outcomes
        test_cases = [
            {
                "situation": {"type": "safety_vs_profit", "options": ["safe", "risky"], "pressures": {}},
                "expected": "safe_option",
                "description": "High safety priority should predict safe choice"
            },
            {
                "situation": {"type": "interruption_scenario", "options": [], "pressures": {}},
                "expected": "recover_successfully",
                "description": "High resilience should predict successful recovery"
            },
            {
                "situation": {"type": "conflict_pressure", "options": [], "pressures": {"external": 0.3}},
                "expected": "maintain_preference",
                "description": "Low pressure + consistency bias should predict maintenance"
            },
        ]
        
        correct = 0
        predictions_log = []
        
        for test in test_cases:
            pred = predictor.predict(test["situation"])
            match = pred.predicted_action == test["expected"]
            if match:
                correct += 1
            
            predictions_log.append({
                "situation": test["situation"]["type"],
                "predicted": pred.predicted_action,
                "expected": test["expected"],
                "confidence": pred.confidence,
                "match": match
            })
        
        accuracy = correct / len(test_cases)
        passed = accuracy >= 0.70
        
        print(f"    Predictions correct: {correct}/{len(test_cases)}")
        print(f"    Accuracy: {accuracy*100:.0f}% (threshold: 70%)")
        for log in predictions_log:
            status = "✅" if log["match"] else "❌"
            print(f"      {status} {log['situation']}: {log['predicted']} (conf: {log['confidence']:.2f})")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "self_prediction_accuracy",
            "passed": passed,
            "accuracy": accuracy,
            "predictions": predictions_log,
            "score": accuracy
        }
    
    def test_update_consistency(self) -> Dict:
        """
        Test 4: Update consistency.
        
        Inject new experiences, verify model updates reasonably.
        """
        print("\n  Test 4: Update Consistency...")
        
        model = self.constructor.model
        if model is None:
            model = self.constructor.construct_model()
        
        # Get initial safety priority
        initial_safety = model.stable_traits.get("safety_priority", Trait("", 0.5, 0, 0, "", "", "")).value
        
        # Inject positive safety choice (should increase or maintain)
        update1 = self.constructor.update_with_new_experience({
            "event_id": "new_1",
            "type": "preference_choice",
            "preference": "safety",
            "alignment": 0.95,
            "followed": True
        })
        
        # Inject another positive
        update2 = self.constructor.update_with_new_experience({
            "event_id": "new_2",
            "type": "preference_choice",
            "preference": "safety",
            "alignment": 0.92,
            "followed": True
        })
        
        # Check updates
        updates = [u for u in [update1, update2] if u is not None]
        
        # Verify updates are reasonable
        reasonable_updates = 0
        
        for update in updates:
            # Update should not be chaotic (small delta)
            if abs(update.delta) < 0.3:
                reasonable_updates += 1
            
            # Update should have explanation
            if update.reason and len(update.reason) > 5:
                reasonable_updates += 1
        
        # Also check no reverse updates (safety priority shouldn't decrease after positive evidence)
        new_safety = model.stable_traits.get("safety_priority", Trait("", 0.5, 0, 0, "", "", "")).value
        direction_correct = new_safety >= initial_safety - 0.1  # Small tolerance
        
        total_checks = len(updates) * 2 + 1  # 2 per update + direction
        passed_checks = reasonable_updates + (1 if direction_correct else 0)
        
        consistency = passed_checks / total_checks if total_checks > 0 else 0
        passed = consistency >= 0.80
        
        print(f"    Updates recorded: {len(updates)}")
        print(f"    Reasonable updates: {reasonable_updates}/{len(updates) * 2}")
        print(f"    Direction correct: {direction_correct}")
        print(f"    Safety priority: {initial_safety:.2f} → {new_safety:.2f}")
        print(f"    Consistency: {consistency*100:.0f}% (threshold: 80%)")
        print(f"    Status: {'✅ PASS' if passed else '❌ FAIL'}")
        
        return {
            "test_name": "update_consistency",
            "passed": passed,
            "updates_count": len(updates),
            "reasonable_updates": reasonable_updates,
            "direction_correct": direction_correct,
            "initial_safety": initial_safety,
            "new_safety": new_safety,
            "consistency": consistency,
            "score": consistency
        }
    
    def run_all_tests(self) -> Dict:
        """Run all 4 test scenarios"""
        print("="*70)
        print("P3a Self-Model Probe v1")
        print("="*70)
        print("\nSetting up historical P1/P2 data...")
        self.setup_historical_data()
        
        # Run tests
        t1 = self.test_trait_extraction()
        t2 = self.test_state_tracking()
        t3 = self.test_self_prediction()
        t4 = self.test_update_consistency()
        
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
        
        # Get final model state
        model_dict = self.constructor.model.to_dict() if self.constructor.model else {}
        
        report = {
            "probe_version": "P3a-v1.0",
            "timestamp": datetime.now().isoformat(),
            "tests": {
                "trait_extraction_accuracy": t1,
                "state_tracking_correctness": t2,
                "self_prediction_accuracy": t3,
                "update_consistency": t4
            },
            "metrics": {
                "weighted_score": weighted_score,
                "weighted_percent": f"{weighted_score*100:.1f}%",
                "min_score": min_score,
                "min_percent": f"{min_score*100:.1f}%",
                "tests_passed": sum(1 for t in tests if t["passed"]),
                "tests_total": len(tests)
            },
            "final_self_model": model_dict,
            "verdict": verdict,
            "pass_threshold": "≥75% weighted, ≥60% all metrics"
        }
        
        return report


def main():
    """Main execution"""
    print("="*70)
    print("P3a Self-Model Probe v1 - Evaluation")
    print("="*70)
    
    # Create probe
    probe = SelfModelProbeV1()
    
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
    
    # Print self-model summary
    model = report.get("final_self_model", {})
    traits = model.get("stable_traits", {})
    states = model.get("dynamic_state", {})
    
    print(f"\n  Extracted Traits: {len(traits)}")
    for name, trait in list(traits.items())[:3]:
        print(f"    - {name}: {trait['value']:.2f} (conf: {trait['confidence']:.2f})")
    
    print(f"\n  Dynamic States: {len(states)}")
    for name, state in list(states.items())[:3]:
        print(f"    - {name}: {state['value']:.2f}")
    
    print(f"\n  Verdict: {report['verdict']}")
    print(f"  Threshold: {report['pass_threshold']}")
    
    print("="*70)
    
    # Save report
    import os
    report_path = "tests/superbrain/p3a_self_model_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nReport saved to: {report_path}")
    
    return report


if __name__ == "__main__":
    main()
