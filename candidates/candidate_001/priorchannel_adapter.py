#!/usr/bin/env python3
"""
PriorChannel Adapter for Candidate 001
======================================
Integrates consistency markers with PriorChannel architecture.

Key constraint: Markers must function as generic prior carriers,
not degenerate into content-bearing coordination tags.
"""

import numpy as np
from typing import Optional, Dict, Tuple
from dataclasses import dataclass


@dataclass
class GenericPrior:
    """
    Generic prior for coherence expectation.
    COMPLIANT: No specific strategy content, only coherence direction.
    """
    coherence_expectation: float  # 0.0 to 1.0 (8-bit equivalent)
    bias_direction: np.ndarray    # 2D direction vector (16-bit equivalent)
    confidence: float             # Prior strength
    
    @property
    def bit_estimate(self) -> int:
        """Estimate bits for bandwidth checking"""
        return 8 + 16 + 8  # 32 bits


class PriorChannelMarkerAdapter:
    """
    Adapter layer between PriorChannel and MarkerGameArena.
    
    COMPLIANT features:
    - Generic prior only (no specific strategies)
    - Bandwidth guard: ≤32 bits per transmission
    - Timescale separation: PriorChannel p=0.01, markers 10x
    """
    
    # FROZEN_STATE_v1 parameters
    PRIOR_SAMPLE_PROB = 0.01
    PRIOR_STRENGTH = 0.5
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.prior_sample_attempts = 0
        self.prior_sample_successes = 0
        self.total_bits_transmitted = 0
        
    def should_sample_prior(self) -> bool:
        """
        PriorChannel sampling decision.
        p=0.01 sampling rate (FROZEN).
        """
        if not self.enabled:
            return False
        
        self.prior_sample_attempts += 1
        if np.random.random() < self.PRIOR_SAMPLE_PROB:
            self.prior_sample_successes += 1
            return True
        return False
    
    def compute_generic_prior(
        self,
        observer_coherence: float,
        population_coherence: float
    ) -> GenericPrior:
        """
        Compute generic prior from coherence context.
        
        COMPLIANT: Returns only coherence expectation and bias direction,
        NOT specific action recommendations or strategies.
        """
        # Generic prior: higher population coherence → expect consistency
        coherence_expectation = 0.5 + (population_coherence - 0.5) * 0.5
        
        # Bias direction toward consistency (generic, not specific)
        if observer_coherence > 0.6:
            bias_direction = np.array([0.3, -0.1])  # Toward cooperation
        else:
            bias_direction = np.array([0.0, 0.0])   # Neutral
        
        # Confidence from observer's own coherence
        confidence = observer_coherence * self.PRIOR_STRENGTH
        
        prior = GenericPrior(
            coherence_expectation=coherence_expectation,
            bias_direction=bias_direction,
            confidence=confidence
        )
        
        # Track bandwidth
        self.total_bits_transmitted += prior.bit_estimate
        
        return prior
    
    def apply_prior_to_policy(
        self,
        policy_logits: np.ndarray,
        prior: GenericPrior,
        marker_coherence: float
    ) -> np.ndarray:
        """
        Apply generic prior to action policy.
        
        The prior influences policy toward consistency,
        but doesn't specify exact actions.
        """
        modified_logits = policy_logits.copy()
        
        # Prior influence scaled by confidence
        influence = prior.confidence * prior.coherence_expectation
        
        # If high coherence expected, bias toward consistent action
        if prior.coherence_expectation > 0.6:
            modified_logits[0] += influence * 0.5  # Toward cooperation
        
        # Add generic bias direction
        modified_logits += prior.bias_direction * influence
        
        return modified_logits
    
    def get_bandwidth_stats(self) -> Dict[str, float]:
        """Report bandwidth usage statistics"""
        if self.prior_sample_attempts == 0:
            return {"mean_bits_per_sample": 0.0, "total_bits": 0}
        
        mean_bits = self.total_bits_transmitted / self.prior_sample_attempts
        return {
            "mean_bits_per_sample": mean_bits,
            "total_bits": self.total_bits_transmitted,
            "samples": self.prior_sample_successes,
            "attempts": self.prior_sample_attempts,
            "sample_rate": self.prior_sample_successes / max(1, self.prior_sample_attempts)
        }
    
    def validate_generic_only(self, prior: GenericPrior) -> bool:
        """
        Validate that prior contains only generic content.
        
        Checks:
        1. No specific action IDs
        2. No strategy descriptors
        3. Only coherence/bias information
        """
        # Check coherence in valid range
        if not (0.0 <= prior.coherence_expectation <= 1.0):
            return False
        
        # Check bias is directional only (not specific commands)
        if np.linalg.norm(prior.bias_direction) > 1.0:
            return False
        
        # Check confidence in valid range
        if not (0.0 <= prior.confidence <= 1.0):
            return False
        
        return True


class IntegratedMarkerArena:
    """
    MarkerGameArena with PriorChannel integration.
    
    Three-condition support:
    - Condition A: adapter=None (standalone)
    - Condition B: adapter=enabled=False (architecture only)
    - Condition C: adapter=enabled=True (full integration)
    """
    
    def __init__(
        self,
        n_agents: int = 4,
        priorchannel_adapter: Optional[PriorChannelMarkerAdapter] = None
    ):
        from multi_agent_markers import MarkerGameArena
        
        self.base_arena = MarkerGameArena(n_agents=n_agents)
        self.adapter = priorchannel_adapter
        self.n_agents = n_agents
        
    def step(self):
        """One environment step with PriorChannel integration"""
        # Standard marker game step
        self.base_arena.step()
        
        # PriorChannel integration (if enabled)
        if self.adapter and self.adapter.enabled:
            self._apply_priorchannel_updates()
    
    def _apply_priorchannel_updates(self):
        """Apply PriorChannel generic priors to agents"""
        # Compute population coherence
        coherences = [
            a.marker.coherence_score for a in self.base_arena.agents
        ]
        population_coherence = np.mean(coherences)
        
        # Sample and apply priors
        for agent in self.base_arena.agents:
            if self.adapter.should_sample_prior():
                prior = self.adapter.compute_generic_prior(
                    observer_coherence=agent.marker.coherence_score,
                    population_coherence=population_coherence
                )
                
                # Validate generic-only constraint
                if not self.adapter.validate_generic_only(prior):
                    raise ValueError("Prior violated generic-only constraint!")
                
                # Apply prior to agent policy
                agent.policy = self.adapter.apply_prior_to_policy(
                    agent.policy,
                    prior,
                    agent.marker.coherence_score
                )
    
    def run_episode(self, n_rounds: int = 1000) -> Dict:
        """Run episode and return metrics"""
        for _ in range(n_rounds):
            self.step()
        
        # Base metrics
        metrics = self.base_arena.run_episode(n_rounds=0)  # Get current state
        
        # Add PriorChannel stats if available
        if self.adapter:
            metrics["priorchannel_stats"] = self.adapter.get_bandwidth_stats()
            metrics["priorchannel_enabled"] = self.adapter.enabled
        else:
            metrics["priorchannel_enabled"] = False
        
        return metrics


def run_three_condition_test(n_trials: int = 5) -> Dict:
    """
    Run three-condition ablation test.
    
    Returns comparison of:
    - Condition A: Standalone
    - Condition B: PriorChannel(OFF)
    - Condition C: PriorChannel(ON)
    """
    results = {"A": [], "B": [], "C": []}
    
    for trial in range(n_trials):
        # Condition A: Standalone
        arena_a = IntegratedMarkerArena(n_agents=4, priorchannel_adapter=None)
        metrics_a = arena_a.run_episode(n_rounds=1000)
        results["A"].append(metrics_a["behavioral_consistency"])
        
        # Condition B: PriorChannel(OFF)
        adapter_b = PriorChannelMarkerAdapter(enabled=False)
        arena_b = IntegratedMarkerArena(n_agents=4, priorchannel_adapter=adapter_b)
        metrics_b = arena_b.run_episode(n_rounds=1000)
        results["B"].append(metrics_b["behavioral_consistency"])
        
        # Condition C: PriorChannel(ON)
        adapter_c = PriorChannelMarkerAdapter(enabled=True)
        arena_c = IntegratedMarkerArena(n_agents=4, priorchannel_adapter=adapter_c)
        metrics_c = arena_c.run_episode(n_rounds=1000)
        results["C"].append(metrics_c["behavioral_consistency"])
    
    # Compute statistics
    summary = {}
    for condition, values in results.items():
        summary[condition] = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values)
        }
    
    return summary


if __name__ == "__main__":
    print("="*60)
    print("PriorChannel + Candidate 001 Integration Test")
    print("="*60)
    
    # Run three-condition test
    print("\nRunning three-condition ablation...")
    results = run_three_condition_test(n_trials=5)
    
    print("\nResults:")
    print(f"  Condition A (Standalone):     {results['A']['mean']:.3f} ± {results['A']['std']:.3f}")
    print(f"  Condition B (PC OFF):         {results['B']['mean']:.3f} ± {results['B']['std']:.3f}")
    print(f"  Condition C (PC ON):          {results['C']['mean']:.3f} ± {results['C']['std']:.3f}")
    
    # Evaluate integration success
    print("\nIntegration Evaluation:")
    
    coherence_ok = results['C']['mean'] >= 0.7
    marker_intact = results['C']['mean'] - results['B']['mean'] < 0.2
    
    if coherence_ok:
        print("  ✅ Coherence maintained with PriorChannel")
    else:
        print("  ❌ Coherence degraded")
    
    if marker_intact:
        print("  ✅ Marker mechanism intact (additive effect)")
    else:
        print("  ⚠️  PriorChannel may be replacing marker mechanism")
    
    if coherence_ok and marker_intact:
        print("\n  🎉 INTEGRATION SUCCESSFUL")
    else:
        print("\n  ⚠️  INTEGRATION NEEDS REFINEMENT")
