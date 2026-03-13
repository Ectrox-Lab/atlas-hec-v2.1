#!/usr/bin/env python3
"""
Candidate 002 Falsification Harness
====================================

Minimal falsification tests per intake memo:
1. Removing proprioceptive feedback degrades self-boundary metrics
2. Prediction loop affects identity-like state stability
3. Body-map cannot be arbitrarily perturbed without recovery
"""

import numpy as np
from soft_body_agent import SoftBodyAgent, run_minimal_experiment


class TestFalsificationConditions:
    """
    Falsification tests for Candidate 002
    
    Per intake memo:
    - Fail: Removing proprioceptive feedback does NOT degrade self-boundary metrics
    - Fail: Prediction loop does NOT affect identity-like state stability
    - Fail: Body-map can be arbitrarily perturbed without recovery
    """
    
    def test_proprioceptive_feedback_required(self):
        """
        Falsification 1: Removing proprioceptive feedback degrades metrics
        
        If this test FAILS (no degradation), the hypothesis is falsified.
        """
        print("\n" + "="*60)
        print("FALSIFICATION TEST 1: Proprioceptive Feedback Required")
        print("="*60)
        
        # Normal agent
        normal_metrics = run_minimal_experiment(steps=500)
        
        # Agent without proprioceptive feedback (random state updates)
        class BlindAgent(SoftBodyAgent):
            def sense(self, external_pressure):
                # Ignore actual proprioception - random state
                self.state.proprioceptive_state = np.random.random(self.n_nodes)
                return self.state.proprioceptive_state
        
        blind_agent = BlindAgent(n_nodes=10)
        for t in range(500):
            external_pressure = np.random.randn(10) * 0.1
            blind_agent.step(external_pressure)
        
        blind_metrics = {
            "self_boundary_accuracy": blind_agent.self_boundary_accuracy(),
            "final_prediction_error": np.mean(blind_agent.error_history[-100:]),
            "body_map_stability": blind_agent.body_map_stability(),
        }
        
        print(f"  Normal - boundary accuracy: {normal_metrics['self_boundary_accuracy']:.3f}")
        print(f"  Blind  - boundary accuracy: {blind_metrics['self_boundary_accuracy']:.3f}")
        print(f"  Normal - prediction error: {normal_metrics['final_prediction_error']:.3f}")
        print(f"  Blind  - prediction error: {blind_metrics['final_prediction_error']:.3f}")
        
        # Feedback should matter
        degradation = (
            blind_metrics['self_boundary_accuracy'] < normal_metrics['self_boundary_accuracy'] * 0.8
            or blind_metrics['final_prediction_error'] > normal_metrics['final_prediction_error'] * 2.0
        )
        
        if degradation:
            print("  ✅ PASS: Proprioceptive feedback matters (degradation detected)")
            return True
        else:
            print("  ❌ FAIL: No degradation without feedback - hypothesis falsified!")
            return False
    
    def test_prediction_loop_matters(self):
        """
        Falsification 2: Prediction loop affects state stability
        
        If this test FAILS (prediction doesn't matter), the hypothesis is falsified.
        """
        print("\n" + "="*60)
        print("FALSIFICATION TEST 2: Prediction Loop Affects Stability")
        print("="*60)
        
        # Normal agent with prediction
        normal_agent = SoftBodyAgent(n_nodes=10)
        for t in range(500):
            external_pressure = np.random.randn(10) * 0.1
            normal_agent.step(external_pressure)
        
        # Agent without prediction (random actions)
        class NoPredictionAgent(SoftBodyAgent):
            def act(self):
                return np.random.randn(self.n_nodes) * 0.1  # Random, not prediction-based
        
        nopred_agent = NoPredictionAgent(n_nodes=10)
        for t in range(500):
            external_pressure = np.random.randn(10) * 0.1
            nopred_agent.step(external_pressure)
        
        normal_stability = normal_agent.body_map_stability()
        nopred_stability = nopred_agent.body_map_stability()
        
        print(f"  Normal    - body-map stability: {normal_stability:.3f}")
        print(f"  No-pred   - body-map stability: {nopred_stability:.3f}")
        
        # Prediction should improve stability
        if nopred_stability < normal_stability * 0.8:
            print("  ✅ PASS: Prediction loop improves stability")
            return True
        else:
            print("  ❌ FAIL: Prediction doesn't matter - hypothesis falsified!")
            return False
    
    def test_body_map_recovery(self):
        """
        Falsification 3: Body-map cannot be arbitrarily perturbed without recovery
        
        If this test FAILS (no recovery), the hypothesis is falsified.
        """
        print("\n" + "="*60)
        print("FALSIFICATION TEST 3: Body-Map Recovery from Perturbation")
        print("="*60)
        
        agent = SoftBodyAgent(n_nodes=10)
        
        # Train initially
        for t in range(300):
            external_pressure = np.random.randn(10) * 0.05
            agent.step(external_pressure)
        
        baseline_error = np.mean(agent.error_history[-50:])
        print(f"  Baseline error: {baseline_error:.3f}")
        
        # Large perturbation
        large_perturbation = np.random.randn(10) * 0.5
        agent.sense(large_perturbation)
        
        # Measure recovery
        recovery_steps = 0
        max_steps = 100
        for i in range(max_steps):
            agent.step(np.random.randn(10) * 0.05)
            current_error = np.mean(np.abs(agent.state.prediction_error))
            if current_error < baseline_error * 2.0:
                recovery_steps = i + 1
                break
        
        print(f"  Recovery steps: {recovery_steps}/{max_steps}")
        
        if recovery_steps > 0 and recovery_steps < max_steps:
            print("  ✅ PASS: Body-map recovers from perturbation")
            return True
        else:
            print("  ❌ FAIL: No recovery from perturbation - hypothesis falsified!")
            return False


def run_falsification_harness():
    """Run all falsification tests"""
    print("="*60)
    print("CANDIDATE 002 FALSIFICATION HARNESS")
    print("="*60)
    print("Status: BUILD_NOW")
    print("Risk: Low")
    print("="*60)
    
    tests = TestFalsificationConditions()
    
    results = {
        "feedback_required": tests.test_proprioceptive_feedback_required(),
        "prediction_matters": tests.test_prediction_loop_matters(),
        "recovery_exists": tests.test_body_map_recovery(),
    }
    
    print("\n" + "="*60)
    print("FALSIFICATION HARNESS SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:20}: {status}")
    
    all_pass = all(results.values())
    
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL FALSIFICATION TESTS PASSED")
        print("Hypothesis NOT falsified - proceed with candidate")
    else:
        print("❌ SOME FALSIFICATION TESTS FAILED")
        print("Review failed conditions - may indicate illusion")
    print("="*60)
    
    return all_pass


if __name__ == "__main__":
    success = run_falsification_harness()
    exit(0 if success else 1)
