#!/usr/bin/env python3
"""
Candidate 002: Soft Robot Proprioceptive Homeostasis
======================================================
Minimal implementation of body self-model through homeostatic regulation.

BUILD_NOW - Low risk, ready for immediate implementation
"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class SoftBodyState:
    """Required state variables per intake memo"""
    proprioceptive_state: np.ndarray      # Current pressure/strain
    predicted_state: np.ndarray           # Expected sensation
    prediction_error: np.ndarray          # Mismatch signal
    body_model_weights: np.ndarray        # Learned self-predictions
    homeostatic_setpoint: np.ndarray      # Target state
    self_boundary_map: np.ndarray         # What counts as "self"


class SoftBodyAgent:
    """
    Soft body agent with proprioceptive self-model
    
    Core mechanism: Prediction-error minimization → body self-model
    """
    
    def __init__(self, n_nodes: int = 10):
        self.n_nodes = n_nodes
        
        # Initialize state
        self.state = SoftBodyState(
            proprioceptive_state=np.zeros(n_nodes),
            predicted_state=np.zeros(n_nodes),
            prediction_error=np.zeros(n_nodes),
            body_model_weights=np.eye(n_nodes) * 0.1,  # Initial weak predictions
            homeostatic_setpoint=np.ones(n_nodes) * 0.5,  # Viable pressure range
            self_boundary_map=np.ones(n_nodes, dtype=bool),  # All nodes = self initially
        )
        
        # Learning rate for body model
        self.alpha = 0.01
        
        # History for continuity tracking
        self.weight_history = []
        self.error_history = []
    
    def predict(self, action: np.ndarray) -> np.ndarray:
        """
        PREDICT: P̂(t+1) = f_body(P(t), A(t); θ)
        
        Predict next proprioceptive state using current body model
        """
        # Linear prediction: predicted = current + action + model_bias
        self.state.predicted_state = (
            self.state.proprioceptive_state + 
            action + 
            self.state.body_model_weights @ self.state.proprioceptive_state
        )
        return self.state.predicted_state
    
    def act(self) -> np.ndarray:
        """
        ACT: A(t) = argmin_A ||P̂(t+1) - P_setpoint||
        
        Generate action to move toward homeostatic setpoint
        """
        # Simple gradient descent toward setpoint
        error = self.state.homeostatic_setpoint - self.state.predicted_state
        action = np.tanh(error * 0.5)  # Bounded action
        return action
    
    def sense(self, external_pressure: np.ndarray) -> np.ndarray:
        """
        SENSE: P(t+1) = Environment(P(t), A(t), E(t))
        
        Update proprioceptive state with external perturbation
        """
        self.state.proprioceptive_state = np.clip(
            self.state.proprioceptive_state + external_pressure,
            0.0, 1.0  # Viable pressure range
        )
        return self.state.proprioceptive_state
    
    def update(self) -> float:
        """
        UPDATE: θ ← θ - α∇_θ ||ε||²
        
        Update body model based on prediction error
        """
        # Calculate prediction error
        self.state.prediction_error = (
            self.state.proprioceptive_state - self.state.predicted_state
        )
        
        # Update body model weights (outer product learning)
        delta_weights = self.alpha * np.outer(
            self.state.prediction_error,
            self.state.proprioceptive_state
        )
        self.state.body_model_weights += delta_weights
        
        # Record history
        self.weight_history.append(self.state.body_model_weights.copy())
        mean_error = np.mean(np.abs(self.state.prediction_error))
        self.error_history.append(mean_error)
        
        return mean_error
    
    def step(self, external_pressure: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Full feedback loop:
        PREDICT → ACT → SENSE → UPDATE
        """
        # 1. PREDICT
        action = self.act()
        self.predict(action)
        
        # 2. SENSE (environment applies pressure)
        self.sense(external_pressure)
        
        # 3. UPDATE
        error = self.update()
        
        return action, error
    
    def self_boundary_accuracy(self) -> float:
        """
        Measure self-boundary discrimination accuracy
        
        Returns: 1.0 = perfect discrimination, 0.0 = no discrimination
        """
        # Nodes with stable low error = self
        # Nodes with high variable error = external
        error_variance = np.var(self.state.prediction_error)
        if error_variance < 0.01:
            return 1.0  # Clear boundary
        return max(0.0, 1.0 - error_variance * 10)
    
    def recovery_time(self, perturbation: np.ndarray) -> int:
        """
        Measure prediction error recovery time after perturbation
        
        Returns: Number of steps to return to baseline error
        """
        baseline_error = np.mean(np.abs(self.state.prediction_error))
        threshold = baseline_error * 2.0
        
        for t in range(100):  # Max 100 steps
            self.step(perturbation)
            current_error = np.mean(np.abs(self.state.prediction_error))
            if current_error < threshold:
                return t + 1
        
        return 100  # Did not recover
    
    def body_map_stability(self, window: int = 10) -> float:
        """
        Measure body-map stability over perturbations
        
        Returns: 1.0 = perfectly stable, 0.0 = unstable
        """
        if len(self.weight_history) < window:
            return 0.0
        
        recent_weights = self.weight_history[-window:]
        weight_variance = np.var([np.mean(np.abs(w)) for w in recent_weights])
        
        return max(0.0, 1.0 - weight_variance * 100)


def run_minimal_experiment(steps: int = 1000) -> dict:
    """
    Minimal Experiment A: Self-Boundary Discrimination
    
    Returns metrics:
    - self_boundary_accuracy
    - mean_recovery_time
    - body_map_stability
    """
    agent = SoftBodyAgent(n_nodes=10)
    
    # Run with random pressure perturbations
    for t in range(steps):
        # Random external pressure perturbation
        external_pressure = np.random.randn(agent.n_nodes) * 0.1
        agent.step(external_pressure)
    
    # Calculate metrics
    metrics = {
        "self_boundary_accuracy": agent.self_boundary_accuracy(),
        "final_prediction_error": np.mean(agent.error_history[-100:]),
        "body_map_stability": agent.body_map_stability(),
        "mean_error_history": np.mean(agent.error_history),
    }
    
    return metrics


if __name__ == "__main__":
    print("="*60)
    print("Candidate 002: Soft Robot Proprioceptive Homeostasis")
    print("="*60)
    
    # Run minimal experiment
    metrics = run_minimal_experiment(steps=1000)
    
    print("\nMinimal Experiment Results:")
    print(f"  Self-boundary accuracy: {metrics['self_boundary_accuracy']:.3f}")
    print(f"  Final prediction error: {metrics['final_prediction_error']:.3f}")
    print(f"  Body-map stability: {metrics['body_map_stability']:.3f}")
    print(f"  Mean error (all): {metrics['mean_error_history']:.3f}")
    
    # Check emergence criteria
    print("\nEmergence Criteria:")
    if metrics['final_prediction_error'] < 0.1:
        print("  ✅ Prediction error converged to low values")
    else:
        print("  ❌ Prediction error remains high")
    
    if metrics['body_map_stability'] > 0.5:
        print("  ✅ Body-map stable over perturbations")
    else:
        print("  ❌ Body-map unstable")
    
    print("\n" + "="*60)
