#!/usr/bin/env python3
"""Generate synthetic candidate data for SR1 validation"""

import json
import random
from pathlib import Path

random.seed(42)

def uniform(a, b):
    return random.uniform(a, b)

def randint(a, b):
    return random.randint(a, b)

def choice(options):
    return random.choice(options)

def generate_candidate(candidate_id, name, archetype):
    """Generate a candidate based on archetype"""
    
    if archetype == "octopus_mainline":
        # Stable, high performance
        cwci_total = 0.82
        specialization = 0.85
        integration = 0.80
        broadcast = 0.78
        scale_retention = 0.88
        seed_variance = 0.12
        pass_rate = 0.92
        seed_spike_risk = 0.15
        
    elif archetype == "oqs_challenger":
        # Good but more experimental
        cwci_total = 0.78
        specialization = 0.75
        integration = 0.82
        broadcast = 0.70
        scale_retention = 0.72
        seed_variance = 0.28
        pass_rate = 0.78
        seed_spike_risk = 0.35
        
    elif archetype == "stable_variant":
        # Similar to mainline
        cwci_total = uniform(0.75, 0.85)
        specialization = uniform(0.75, 0.88)
        integration = uniform(0.75, 0.85)
        broadcast = uniform(0.70, 0.82)
        scale_retention = uniform(0.80, 0.90)
        seed_variance = uniform(0.10, 0.20)
        pass_rate = uniform(0.85, 0.95)
        seed_spike_risk = uniform(0.10, 0.25)
        
    elif archetype == "seed_spike":
        # High variance, unstable
        cwci_total = uniform(0.60, 0.95)
        specialization = uniform(0.50, 0.90)
        integration = uniform(0.50, 0.90)
        broadcast = uniform(0.50, 0.85)
        scale_retention = uniform(0.40, 0.65)
        seed_variance = uniform(0.45, 0.75)
        pass_rate = uniform(0.20, 0.50)
        seed_spike_risk = uniform(0.70, 0.95)
        
    elif archetype == "experimental":
        # High potential but unproven
        cwci_total = uniform(0.70, 0.88)
        specialization = uniform(0.80, 0.92)
        integration = uniform(0.60, 0.75)
        broadcast = uniform(0.55, 0.70)
        scale_retention = uniform(0.55, 0.70)
        seed_variance = uniform(0.25, 0.40)
        pass_rate = uniform(0.55, 0.75)
        seed_spike_risk = uniform(0.35, 0.55)
    
    return {
        "candidate_id": candidate_id,
        "candidate_name": name,
        "timestamp": "2026-03-12T00:00:00Z",
        "archetype": archetype,
        "cwci": {
            "total": round(cwci_total, 3),
            "specialization": round(specialization, 3),
            "integration": round(integration, 3),
            "broadcast": round(broadcast, 3),
            "min": round(cwci_total * 0.85, 3),
            "max": round(min(cwci_total * 1.05, 1.0), 3)
        },
        "hierarchy_depth": randint(2, 6),
        "autonomy_strength": round(uniform(0.6, 0.9), 3),
        "memory_style": choice(["distributed", "hybrid", "federated"]),
        "scale_retention": round(scale_retention, 3),
        "seed_variance": round(seed_variance, 3),
        "stress_coverage": round(uniform(0.5, 0.9), 3),
        "pass_rate": round(pass_rate, 3),
        "recovery_time": round(uniform(10, 60), 1),
        "energy_stability": round(uniform(0.6, 0.9), 3),
        "coordination_score": round(uniform(0.65, 0.90), 3),
        "hazard_resistance": round(uniform(0.60, 0.85), 3),
        "communication_cost": round(uniform(0.2, 0.5), 3),
        "first_failure_mode": choice(["coordination", "energy", "memory", "broadcast"]),
        "seed_spike_risk": round(seed_spike_risk, 3),
        "collapse_signature": f"sig_{candidate_id}",
        "bottleneck_type": choice(["single_point", "distributed", "cascading"])
    }

def main():
    output_dir = Path(__file__).parent / "synthetic_gate_results"
    output_dir.mkdir(exist_ok=True)
    
    candidates = [
        # Mainline
        ("octopus_01", "OctopusLike-Mainline", "octopus_mainline"),
        ("octopus_02", "OctopusLike-R4", "octopus_mainline"),
        
        # OQS Challenger
        ("oqs_01", "OQS-Challenger", "oqs_challenger"),
        ("oqs_02", "OQS-v2", "oqs_challenger"),
        
        # Stable variants
        ("stable_01", "StableVariant-A", "stable_variant"),
        ("stable_02", "StableVariant-B", "stable_variant"),
        ("stable_03", "StableVariant-C", "stable_variant"),
        
        # Seed-spike (high risk)
        ("spike_01", "SpikeCandidate-1", "seed_spike"),
        ("spike_02", "SpikeCandidate-2", "seed_spike"),
        ("spike_03", "SpikeCandidate-3", "seed_spike"),
        
        # Experimental
        ("exp_01", "Experimental-A", "experimental"),
        ("exp_02", "Experimental-B", "experimental"),
    ]
    
    for cid, name, archetype in candidates:
        data = generate_candidate(cid, name, archetype)
        with open(output_dir / f"{cid}_gate_result.json", 'w') as f:
            json.dump(data, f, indent=2)
    
    print(f"Generated {len(candidates)} synthetic candidates in {output_dir}")

if __name__ == "__main__":
    main()
