#!/usr/bin/env python3
"""
Candidate 002 1D Spring Diagnostic
==================================
Quick diagnostic to isolate prediction loop signal.

Hypothesis: 2D mesh masks the prediction effect. 1D spring
will make prediction-error minimization more visible.

Test: Prediction loop affects stability
- Normal: Full prediction-error minimization
- No-pred: No prediction, only reflexive response

PASS: Normal >> No-pred (significant difference)
FAIL: Normal ≈ No-pred (prediction doesn't matter)
"""

import numpy as np
from typing import List, Tuple


class Spring1DAgent:
    """
    1D spring-mass agent with proprioceptive feedback.
    Simplified from 2D mesh to isolate prediction signal.
    """
    
    def __init__(self, k_spring: float = 1.0, mass: float = 1.0, enable_prediction: bool = True):
        self.k_spring = k_spring  # Spring constant
        self.mass = mass
        self.enable_prediction = enable_prediction
        
        # State
        self.position = 0.0
        self.velocity = 0.0
        self.target_position = 0.0  # Homeostatic setpoint
        
        # Proprioception
        self.proprioceptive_position = 0.0
        self.predicted_position = 0.0
        
        # Body model (prediction)
        self.body_model_k = k_spring  # Estimated spring constant
        self.prediction_error = 0.0
        
        # History for metrics
        self.position_history: List[float] = []
        self.prediction_error_history: List[float] = []
        
    def sense(self, true_position: float):
        """Update proprioceptive state"""
        self.proprioceptive_position = true_position
        self.position = true_position
        
    def predict(self):
        """Predict next position based on body model"""
        if self.enable_prediction:
            # Predict where we should be given spring dynamics
            force = -self.body_model_k * (self.proprioceptive_position - self.target_position)
            predicted_acceleration = force / self.mass
            self.predicted_position = (
                self.proprioceptive_position + 
                self.velocity * 0.1 +  # dt=0.1
                0.5 * predicted_acceleration * 0.01
            )
        else:
            # No prediction - just use current position
            self.predicted_position = self.proprioceptive_position
    
    def update(self, external_force: float, dt: float = 0.1):
        """
        Homeostatic regulation with prediction-error minimization.
        """
        # Compute prediction error
        self.prediction_error = (
            self.proprioceptive_position - self.predicted_position
        )
        
        # Update body model (learning)
        if self.enable_prediction:
            # Gradient descent on prediction error
            learning_rate = 0.01
            self.body_model_k += learning_rate * abs(self.prediction_error)
            self.body_model_k = np.clip(self.body_model_k, 0.1, 5.0)
        
        # Homeostatic control: minimize displacement from target
        displacement = self.position - self.target_position
        
        # Add prediction-error correction if enabled
        if self.enable_prediction:
            # Use prediction error to adjust control
            correction = -0.5 * self.prediction_error
        else:
            correction = 0.0
        
        # Spring force + external + correction
        spring_force = -self.k_spring * displacement
        total_force = spring_force + external_force + correction
        
        # Dynamics
        acceleration = total_force / self.mass
        self.velocity += acceleration * dt
        self.velocity *= 0.95  # Damping
        new_position = self.position + self.velocity * dt
        
        # Record history
        self.position_history.append(new_position)
        self.prediction_error_history.append(abs(self.prediction_error))
        
        return new_position
    
    def compute_stability(self, window: int = 50) -> float:
        """
        Compute body-map stability.
        Stable = position variance is low (stays near target).
        """
        if len(self.position_history) < window:
            return 0.0
        
        recent_positions = self.position_history[-window:]
        variance = np.var(recent_positions)
        
        # Lower variance = higher stability
        stability = np.exp(-variance * 10)
        return stability
    
    def compute_body_map_stability(self, window: int = 50) -> float:
        """
        Compute body model (k estimate) stability.
        """
        if not self.enable_prediction or len(self.prediction_error_history) < window:
            return 1.0 if not self.enable_prediction else 0.0
        
        recent_errors = self.prediction_error_history[-window:]
        mean_error = np.mean(recent_errors)
        
        # Lower error = higher body-map stability
        stability = np.exp(-mean_error * 5)
        return stability


class PerturbationEnvironment:
    """Environment that perturbs the spring agent"""
    
    def __init__(self, perturbation_std: float = 0.5):
        self.perturbation_std = perturbation_std
        
    def get_external_force(self, t: float) -> float:
        """Generate time-varying external force"""
        # Periodic + random perturbations
        periodic = 0.3 * np.sin(t * 2.0)
        random = np.random.normal(0, self.perturbation_std)
        return periodic + random


def run_diagnostic(
    n_trials: int = 5,
    n_steps: int = 500,
    perturbation_std: float = 0.5
) -> Tuple[float, float, float, float]:
    """
    Run 1D spring diagnostic.
    
    Returns: (normal_stability, normal_body_map, no_pred_stability, no_pred_body_map)
    """
    normal_stabilities = []
    normal_body_maps = []
    no_pred_stabilities = []
    no_pred_body_maps = []
    
    for trial in range(n_trials):
        env = PerturbationEnvironment(perturbation_std=perturbation_std)
        
        # Normal agent (with prediction)
        normal_agent = Spring1DAgent(enable_prediction=True)
        
        # No-prediction agent
        no_pred_agent = Spring1DAgent(enable_prediction=False)
        
        # Run simulation
        for step in range(n_steps):
            t = step * 0.1
            external_force = env.get_external_force(t)
            
            # Normal agent
            normal_agent.sense(normal_agent.position)
            normal_agent.predict()
            normal_agent.update(external_force)
            
            # No-pred agent
            no_pred_agent.sense(no_pred_agent.position)
            no_pred_agent.predict()
            no_pred_agent.update(external_force)
        
        # Compute metrics
        normal_stabilities.append(normal_agent.compute_stability())
        normal_body_maps.append(normal_agent.compute_body_map_stability())
        no_pred_stabilities.append(no_pred_agent.compute_stability())
        no_pred_body_maps.append(no_pred_agent.compute_body_map_stability())
    
    return (
        np.mean(normal_stabilities),
        np.mean(normal_body_maps),
        np.mean(no_pred_stabilities),
        np.mean(no_pred_body_maps)
    )


def main():
    print("="*60)
    print("Candidate 002: 1D Spring Diagnostic")
    print("="*60)
    print("Quick diagnostic to isolate prediction loop signal")
    print("-"*60)
    
    # Run diagnostic
    print("\nRunning 1D spring diagnostic (5 trials)...")
    normal_stab, normal_body, no_pred_stab, no_pred_body = run_diagnostic(
        n_trials=5,
        n_steps=500,
        perturbation_std=0.5
    )
    
    print("\nResults:")
    print(f"  Normal (with prediction):")
    print(f"    Position stability: {normal_stab:.3f}")
    print(f"    Body-map stability: {normal_body:.3f}")
    
    print(f"\n  No-prediction:")
    print(f"    Position stability: {no_pred_stab:.3f}")
    print(f"    Body-map stability: {no_pred_body:.3f}")
    
    # Evaluate
    print("\nDiagnostic Evaluation:")
    
    position_diff = normal_stab - no_pred_stab
    print(f"  Position stability difference: {position_diff:.3f}")
    
    if position_diff > 0.1:
        print("  ✅ Prediction improves position stability")
        position_pass = True
    else:
        print("  ❌ Prediction doesn't improve position stability")
        position_pass = False
    
    if normal_body > 0.5:
        print("  ✅ Body-map is stable with prediction")
        body_pass = True
    else:
        print("  ❌ Body-map unstable even with prediction")
        body_pass = False
    
    print("\n" + "="*60)
    if position_pass and body_pass:
        print("DIAGNOSTIC: PASS")
        print("1D spring shows prediction effect - 2D issue confirmed")
        print("Action: Refine 2D mesh or proceed with 1D")
        return True
    else:
        print("DIAGNOSTIC: FAIL")
        print("Prediction effect not visible even in 1D")
        print("Action: Candidate 002 hypothesis falsified, recommend ARCHIVE")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
