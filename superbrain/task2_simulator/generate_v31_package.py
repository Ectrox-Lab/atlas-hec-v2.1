#!/usr/bin/env python3
"""
Generate Task-2 v3.1 Mechanism Package

Refined from family-level to route motif-level semantics.
Based on analysis of L4-v3 winners and stable patterns.
"""

import json
from pathlib import Path

def generate_v31_package():
    """Generate refined mechanism package with route motif-level semantics"""
    
    package = {
        "package_type": "task2_pipeline_orchestration",
        "package_version": "3.1-route-motif",
        "timestamp": "2026-03-14T18:00:00+08:00",
        "refinement_notes": "Upgraded from family-level to route motif-level based on L4-v3 learnings",
        
        "stable_route_motifs": [
            {
                "motif_id": "high_triage_strict_handoff",
                "description": "High triage with strict delegation for predictable stage handoffs",
                "signature": {
                    "triage": {"value": 4, "weight": 1.0},
                    "delegation": {"value": 1, "weight": 0.8},
                    "trust_decay": {"range": [0.05, 0.10], "optimal": 0.08, "weight": 0.6},
                    "trust_recovery": {"range": [0.04, 0.08], "optimal": 0.06, "weight": 0.6}
                },
                "success_rate": 0.90,
                "context": "stage_coordination",
                "associated_families": ["F_P2T4M4", "F_P3T4M4", "F_P2T4M3"],
                "mechanism_score": 0.92
            },
            {
                "motif_id": "moderate_pressure_recovery",
                "description": "Moderate pressure with memory-enabled recovery sequences",
                "signature": {
                    "pressure": {"value": 2, "weight": 0.7},
                    "memory": {"value": 3, "weight": 0.9},
                    "trust_recovery": {"range": [0.05, 0.10], "optimal": 0.07, "weight": 0.8}
                },
                "success_rate": 0.88,
                "context": "failure_recovery",
                "associated_families": ["F_P2T3M3", "F_P2T4M3"],
                "mechanism_score": 0.85
            },
            {
                "motif_id": "adaptive_pressure_migration",
                "description": "Higher pressure with adaptive migration capability",
                "signature": {
                    "pressure": {"value": 3, "weight": 0.6},
                    "triage": {"value": 4, "weight": 0.8},
                    "delegation": {"value": [1, 2], "optimal": 1, "weight": 0.5},
                    "trust_decay": {"range": [0.06, 0.12], "optimal": 0.09, "weight": 0.5}
                },
                "success_rate": 0.82,
                "context": "high_load_adaptation",
                "associated_families": ["F_P3T4M4", "F_P3T4M3"],
                "mechanism_score": 0.88
            },
            {
                "motif_id": "balanced_trust_management",
                "description": "Balanced trust decay/recovery for stable operation",
                "signature": {
                    "trust_decay": {"range": [0.07, 0.11], "optimal": 0.09, "weight": 1.0},
                    "trust_recovery": {"range": [0.05, 0.07], "optimal": 0.06, "weight": 1.0},
                    "memory": {"value": [3, 4], "optimal": 3, "weight": 0.5}
                },
                "success_rate": 0.85,
                "context": "general_stability",
                "associated_families": ["F_P2T3M3", "F_P2T4M3", "F_P3T3M3"],
                "mechanism_score": 0.80
            }
        ],
        
        "route_geometry": {
            "high_value_subspaces": [
                {
                    "name": "T4_corridor",
                    "dimensions": ["triage"],
                    "optimal_value": 4,
                    "tolerance": 0,
                    "confidence": 0.90,
                    "rationale": "L4-v3 showed T4 consistently in high performers"
                },
                {
                    "name": "P2_stability_zone",
                    "dimensions": ["pressure", "memory"],
                    "optimal": {"pressure": 2, "memory": [3, 4]},
                    "tolerance": {"pressure": 0.5, "memory": 0.5},
                    "confidence": 0.85,
                    "rationale": "P2 with M3-4 shows consistent stability"
                },
                {
                    "name": "P3_performance_zone",
                    "dimensions": ["pressure", "triage", "memory"],
                    "optimal": {"pressure": 3, "triage": 4, "memory": 4},
                    "tolerance": {"pressure": 0, "triage": 0, "memory": 0.5},
                    "confidence": 0.80,
                    "rationale": "P3T4M4 bundle - higher performance with T4M4"
                }
            ],
            "avoid_regions": [
                {
                    "name": "low_triage_zone",
                    "condition": "triage <= 2",
                    "risk": "poor_scheduling",
                    "severity": "high"
                },
                {
                    "name": "extreme_pressure",
                    "condition": "pressure >= 4 OR pressure <= 1",
                    "risk": "cascade_or_underutilization",
                    "severity": "high"
                },
                {
                    "name": "insufficient_memory",
                    "condition": "memory <= 2 AND pressure >= 3",
                    "risk": "recovery_failure",
                    "severity": "medium"
                }
            ]
        },
        
        "mechanism_scoring": {
            "method": "weighted_motif_match",
            "weights": {
                "high_triage_strict_handoff": 1.2,
                "moderate_pressure_recovery": 1.0,
                "adaptive_pressure_migration": 0.9,
                "balanced_trust_management": 0.8
            },
            "thresholds": {
                "strong_match": 0.75,
                "moderate_match": 0.50,
                "weak_match": 0.25
            }
        },
        
        "anti_leakage": {
            "enabled": True,
            "strength": 0.2,
            "max_family_distance": 1,
            "description": "Fixed at 0.2 - verified as effective guardrail in L4-v3",
            "penalty_structure": {
                "route_geometry_violation": 0.15,
                "no_motif_match": 0.10,
                "extreme_parameters": 0.20
            }
        },
        
        "generator_priors": {
            "description": "Prior weights for candidate generation",
            "triage_prior": {
                "value": 4,
                "weight": 1.5,
                "reason": "T4 showed consistent advantage in L4-v3"
            },
            "pressure_range": {
                "preferred": [2, 3],
                "weight": 1.0
            },
            "memory_range": {
                "preferred": [3, 4],
                "weight": 1.2
            },
            "delegation": {
                "value": 1,
                "weight": 1.0
            }
        },
        
        "validation_notes": {
            "from_l4_v3": {
                "approve_rate": "100% - clean signal",
                "reuse_rate": "45% - improvement over 40% baseline",
                "mechanism_effect": "+5pp - confirmed directional",
                "leakage": "0% - guardrail effective"
            },
            "v3_1_improvements": [
                "Finer motif-level semantics (vs family-level)",
                "Explicit route geometry definitions",
                "Weighted mechanism scoring",
                "Target: amplify reuse from 45% to 55%+"
            ]
        }
    }
    
    return package


def save_package(output_path: Path = None):
    """Save v3.1 package to disk"""
    package = generate_v31_package()
    
    if output_path is None:
        output_path = Path("/tmp/task2_inheritance_package_v3_1.json")
    
    with open(output_path, 'w') as f:
        json.dump(package, f, indent=2)
    
    print(f"[SAVE] Task-2 v3.1 mechanism package: {output_path}")
    print(f"[INFO] Version: {package['package_version']}")
    print(f"[INFO] Stable motifs: {len(package['stable_route_motifs'])}")
    print(f"[INFO] High-value subspaces: {len(package['route_geometry']['high_value_subspaces'])}")
    
    return output_path


if __name__ == "__main__":
    save_package()
