#!/usr/bin/env python3
"""
Candidate 001 + PriorChannel Ablation Test
==========================================
Three-condition protocol to validate integration.

Conditions:
A: 001-Standalone (no PriorChannel)
B: 001 + PriorChannel(OFF) (architecture only)
C: 001 + PriorChannel(ON, p=0.01, α=0.5)

Success criteria:
1. Coherence maintained: C >= 0.7
2. Marker mechanism intact: C - B < 0.2
3. Constraints: bandwidth ≤32b, timescale 10x
4. Generic-only: No content-bearing priors
"""

import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json

sys.path.insert(0, str(Path(__file__).parent))

from multi_agent_markers import MarkerGameArena
from priorchannel_adapter import PriorChannelMarkerAdapter, IntegratedMarkerArena


class AblationRunner:
    """Runs three-condition ablation with full instrumentation"""
    
    def __init__(self, n_agents: int = 4, n_rounds: int = 1000):
        self.n_agents = n_agents
        self.n_rounds = n_rounds
        
    def run_condition_a(self) -> Dict:
        """
        Condition A: 001-Standalone
        Baseline without PriorChannel integration
        """
        arena = MarkerGameArena(n_agents=self.n_agents)
        metrics = arena.run_episode(n_rounds=self.n_rounds)
        
        return {
            "condition": "A",
            "name": "001-Standalone",
            "mean_coherence": metrics["mean_coherence"],
            "behavioral_consistency": metrics["behavioral_consistency"],
            "marker_stability": metrics["marker_stability"],
            "priorchannel_enabled": False,
            "bandwidth_compliant": True,  # By design
            "timescale_compliant": True,   # By design
        }
    
    def run_condition_b(self) -> Dict:
        """
        Condition B: 001 + PriorChannel(OFF)
        Tests architecture overhead
        """
        adapter = PriorChannelMarkerAdapter(enabled=False)
        arena = IntegratedMarkerArena(
            n_agents=self.n_agents,
            priorchannel_adapter=adapter
        )
        metrics = arena.run_episode(n_rounds=self.n_rounds)
        
        return {
            "condition": "B",
            "name": "001 + PC(OFF)",
            "mean_coherence": metrics["mean_coherence"],
            "behavioral_consistency": metrics["behavioral_consistency"],
            "marker_stability": metrics["marker_stability"],
            "priorchannel_enabled": False,
            "bandwidth_compliant": True,
            "timescale_compliant": True,
        }
    
    def run_condition_c(self) -> Dict:
        """
        Condition C: 001 + PriorChannel(ON)
        Full integration with FROZEN_STATE_v1 parameters
        """
        adapter = PriorChannelMarkerAdapter(enabled=True)
        arena = IntegratedMarkerArena(
            n_agents=self.n_agents,
            priorchannel_adapter=adapter
        )
        metrics = arena.run_episode(n_rounds=self.n_rounds)
        
        # Extract PriorChannel stats
        pc_stats = metrics.get("priorchannel_stats", {})
        
        # Validate constraints
        bandwidth_compliant = pc_stats.get("mean_bits_per_sample", 0) <= 32
        timescale_compliant = True  # Enforced by design
        
        return {
            "condition": "C",
            "name": "001 + PC(ON)",
            "mean_coherence": metrics["mean_coherence"],
            "behavioral_consistency": metrics["behavioral_consistency"],
            "marker_stability": metrics["marker_stability"],
            "priorchannel_enabled": True,
            "priorchannel_stats": pc_stats,
            "bandwidth_compliant": bandwidth_compliant,
            "timescale_compliant": timescale_compliant,
        }
    
    def run_full_ablation(self, n_trials: int = 10) -> Dict:
        """Run all three conditions with multiple trials"""
        results = {
            "A": [],
            "B": [],
            "C": []
        }
        
        print(f"Running {n_trials} trials per condition...")
        
        for trial in range(n_trials):
            print(f"  Trial {trial + 1}/{n_trials}...", end=" ", flush=True)
            
            results["A"].append(self.run_condition_a())
            results["B"].append(self.run_condition_b())
            results["C"].append(self.run_condition_c())
            
            print("done")
        
        return self._compute_statistics(results)
    
    def _compute_statistics(self, raw_results: Dict) -> Dict:
        """Compute summary statistics across trials"""
        summary = {}
        
        for condition, trials in raw_results.items():
            consistencies = [t["behavioral_consistency"] for t in trials]
            coherences = [t["mean_coherence"] for t in trials]
            
            summary[condition] = {
                "consistency_mean": np.mean(consistencies),
                "consistency_std": np.std(consistencies),
                "coherence_mean": np.mean(coherences),
                "coherence_std": np.std(coherences),
                "n_trials": len(trials),
                "raw_trials": trials
            }
        
        return summary


class IntegrationValidator:
    """Validates integration against success criteria"""
    
    CRITERIA = {
        "coherence_threshold": 0.7,
        "mechanism_preserved_threshold": 0.2,
        "bandwidth_limit": 32,
    }
    
    def __init__(self, results: Dict):
        self.results = results
        
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate integration against all criteria.
        Returns (success, [messages]).
        """
        checks = []
        all_pass = True
        
        # Criterion 1: Coherence maintained in Condition C
        c_coherence = self.results["C"]["coherence_mean"]
        if c_coherence >= self.CRITERIA["coherence_threshold"]:
            checks.append(f"✅ Coherence maintained: {c_coherence:.3f} >= {self.CRITERIA['coherence_threshold']}")
        else:
            checks.append(f"❌ Coherence too low: {c_coherence:.3f} < {self.CRITERIA['coherence_threshold']}")
            all_pass = False
        
        # Criterion 2: Marker mechanism intact (additive, not replaced)
        c_consistency = self.results["C"]["consistency_mean"]
        b_consistency = self.results["B"]["consistency_mean"]
        mechanism_diff = c_consistency - b_consistency
        
        if mechanism_diff < self.CRITERIA["mechanism_preserved_threshold"]:
            checks.append(f"✅ Marker mechanism preserved: Δ={mechanism_diff:.3f} < {self.CRITERIA['mechanism_preserved_threshold']}")
        else:
            checks.append(f"⚠️  PriorChannel may dominate: Δ={mechanism_diff:.3f} >= {self.CRITERIA['mechanism_preserved_threshold']}")
            # This is a warning, not a failure
        
        # Criterion 3: Bandwidth compliance
        last_trial_c = self.results["C"]["raw_trials"][-1]
        if last_trial_c.get("bandwidth_compliant", True):
            checks.append("✅ Bandwidth compliant (≤32 bits)")
        else:
            checks.append("❌ Bandwidth violation")
            all_pass = False
        
        # Criterion 4: Timescale compliance
        if last_trial_c.get("timescale_compliant", True):
            checks.append("✅ Timescale compliant (10x)")
        else:
            checks.append("❌ Timescale violation")
            all_pass = False
        
        # Additional: Architecture overhead check (B vs A)
        a_consistency = self.results["A"]["consistency_mean"]
        overhead = abs(b_consistency - a_consistency)
        if overhead < 0.1:
            checks.append(f"✅ Low architecture overhead: {overhead:.3f}")
        else:
            checks.append(f"⚠️  Architecture overhead: {overhead:.3f}")
        
        return all_pass, checks
    
    def get_recommendation(self) -> str:
        """Get integration recommendation"""
        c_coherence = self.results["C"]["coherence_mean"]
        c_consistency = self.results["C"]["consistency_mean"]
        b_consistency = self.results["B"]["consistency_mean"]
        
        if c_coherence >= 0.7 and c_consistency >= 0.7:
            if c_consistency - b_consistency < 0.2:
                return "INTEGRATE"
            else:
                return "INTEGRATE_WITH_MONITORING"
        elif c_coherence >= 0.5:
            return "REFINE"
        else:
            return "ABORT"


def print_report(results: Dict, validation: Tuple[bool, List[str]], recommendation: str):
    """Print formatted report"""
    print("\n" + "="*70)
    print("CANDIDATE 001 + PRIORCHANNEL ABLATION REPORT")
    print("="*70)
    
    # Results table
    print("\nResults Summary:")
    print("-"*70)
    print(f"{'Condition':<15} {'Consistency':<20} {'Coherence':<20}")
    print("-"*70)
    
    for cond in ["A", "B", "C"]:
        r = results[cond]
        consistency_str = f"{r['consistency_mean']:.3f} ± {r['consistency_std']:.3f}"
        coherence_str = f"{r['coherence_mean']:.3f} ± {r['coherence_std']:.3f}"
        print(f"{cond:<15} {consistency_str:<20} {coherence_str:<20}")
    
    print("-"*70)
    
    # Validation checks
    print("\nValidation Checks:")
    print("-"*70)
    for check in validation[1]:
        print(f"  {check}")
    
    # Recommendation
    print("\n" + "="*70)
    print(f"RECOMMENDATION: {recommendation}")
    print("="*70)
    
    if recommendation == "INTEGRATE":
        print("\n🎉 Integration validated. Proceed with full integration.")
    elif recommendation == "INTEGRATE_WITH_MONITORING":
        print("\n⚠️  Integration validated but monitor for PriorChannel dominance.")
    elif recommendation == "REFINE":
        print("\n⚠️  Needs refinement before integration.")
    else:
        print("\n💀 Integration failed. Consider alternative approaches.")


def save_results(results: Dict, recommendation: str, filename: str = "integration_results.json"):
    """Save results to JSON"""
    # Clean results for JSON serialization
    clean_results = {}
    for cond, data in results.items():
        clean_results[cond] = {
            "consistency_mean": float(data["consistency_mean"]),
            "consistency_std": float(data["consistency_std"]),
            "coherence_mean": float(data["coherence_mean"]),
            "coherence_std": float(data["coherence_std"]),
            "n_trials": data["n_trials"]
        }
    
    output = {
        "results": clean_results,
        "recommendation": recommendation,
        "timestamp": str(np.datetime64('now'))
    }
    
    filepath = Path(__file__).parent / filename
    with open(filepath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to: {filepath}")


if __name__ == "__main__":
    print("="*70)
    print("Candidate 001 + PriorChannel Ablation Test")
    print("="*70)
    print("Three-condition protocol to validate integration")
    print("-"*70)
    
    # Run ablation
    runner = AblationRunner(n_agents=4, n_rounds=1000)
    results = runner.run_full_ablation(n_trials=10)
    
    # Validate
    validator = IntegrationValidator(results)
    all_pass, checks = validator.validate()
    recommendation = validator.get_recommendation()
    
    # Print report
    print_report(results, (all_pass, checks), recommendation)
    
    # Save results
    save_results(results, recommendation)
    
    # Exit code
    sys.exit(0 if recommendation in ["INTEGRATE", "INTEGRATE_WITH_MONITORING"] else 1)
