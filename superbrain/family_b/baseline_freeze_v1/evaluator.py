#!/usr/bin/env python3
"""
Family B MVE Evaluator

Evaluates contract-based candidates on Task-2 with contract verification.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List
import random

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task2_simulator')

from contracts import verify_candidate
from pipeline_simulator import run_pipeline_simulation


def load_candidate(candidate_file: Path) -> Dict:
    """Load candidate from JSON"""
    with open(candidate_file) as f:
        return json.load(f)


def evaluate_candidate(candidate: Dict, seed: int = 42) -> Dict:
    """
    Evaluate candidate on Task-2 with contract verification.
    """
    # Extract config
    config = {
        "pressure": candidate.get("pressure", 2),
        "triage": candidate.get("perturbation", 3),
        "memory": candidate.get("memory", 3),
        "delegation": candidate.get("delegation", 1),
        "trust_decay": candidate.get("trust_decay", 0.1),
        "trust_recovery": candidate.get("trust_recovery", 0.05)
    }
    
    # Run Task-2 simulation
    sim_result = run_pipeline_simulation(
        num_tasks=200,
        pressure=config["pressure"],
        triage=config["triage"],
        memory=config["memory"],
        delegation=config["delegation"],
        trust_decay=config["trust_decay"],
        trust_recovery=config["trust_recovery"],
        seed=seed
    )
    
    # Verify contracts
    target_contracts = candidate.get("contracts", [])
    verification = verify_candidate(config, sim_result, target_contracts)
    
    # Determine approval (based on completion rate like Family A/B)
    approved = sim_result.get("pipeline_completion_rate", 0) >= 0.70
    
    return {
        "candidate_id": candidate.get("id", "unknown"),
        "target_contracts": target_contracts,
        "contract_coverage": verification["coverage"],
        "contracts_satisfied": verification["passed_contracts"],
        "contracts_failed": verification["failed_contracts"],
        "pipeline_completion": sim_result.get("pipeline_completion_rate", 0),
        "throughput": sim_result.get("stage_throughput", 0),
        "failover_success": sim_result.get("failover_success_rate", 0),
        "approved": approved,
        "is_full_stack": len(target_contracts) >= 3,
        "has_strict_handoff": "StrictHandoff" in target_contracts,
        "has_adaptive_recovery": "AdaptiveRecovery" in target_contracts,
        "has_pressure_throttle": "PressureThrottle" in target_contracts
    }


def evaluate_round(candidates_dir: Path, round_name: str, sample_size: int = 50) -> Dict:
    """Evaluate a full round"""
    print(f"[EVAL] {round_name}: Loading candidates...")
    
    # Load all candidates
    candidate_files = list(candidates_dir.glob("FB*.json"))
    if not candidate_files:
        # Try other patterns (ablation uses C*.json)
        candidate_files = list(candidates_dir.glob("C*.json"))
    
    # Debug: show what we found
    if candidate_files:
        print(f"[DEBUG] Found {len(candidate_files)} candidate files")
        print(f"[DEBUG] First file: {candidate_files[0].name}")
    
    if not candidate_files:
        print(f"[ERROR] No candidates found in {candidates_dir}")
        return {}
    
    print(f"[EVAL] {round_name}: {len(candidate_files)} candidates loaded")
    
    # Sample
    random.seed(9000)
    if len(candidate_files) > sample_size:
        sampled_files = random.sample(candidate_files, sample_size)
    else:
        sampled_files = candidate_files
    
    print(f"[EVAL] {round_name}: Evaluating {len(sampled_files)} candidates...")
    
    # Evaluate
    results = []
    for i, cand_file in enumerate(sampled_files):
        candidate = load_candidate(cand_file)
        result = evaluate_candidate(candidate, seed=9000 + i)
        results.append(result)
        
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(sampled_files)} evaluated")
    
    # Calculate metrics
    total = len(results)
    approved = [r for r in results if r["approved"]]
    approved_count = len(approved)
    
    summary = {
        "round": round_name,
        "total_evaluated": total,
        "approved_count": approved_count,
        "approve_rate": round(approved_count / total * 100, 2) if total > 0 else 0.0,
        "avg_contract_coverage": round(sum(r["contract_coverage"] for r in results) / total, 3) if total > 0 else 0.0,
        "avg_pipeline_completion": round(sum(r["pipeline_completion"] for r in results) / total * 100, 2) if total > 0 else 0.0,
        "full_stack_candidates": sum(1 for r in results if r["is_full_stack"]),
        "strict_handoff_usage": sum(1 for r in results if r["has_strict_handoff"]),
        "adaptive_recovery_usage": sum(1 for r in results if r["has_adaptive_recovery"]),
        "pressure_throttle_usage": sum(1 for r in results if r["has_pressure_throttle"]),
        "results": results
    }
    
    # Reuse via contracts (candidates with >90% contract coverage)
    high_coverage = [r for r in approved if r["contract_coverage"] >= 0.9]
    summary["reuse_via_contracts"] = round(len(high_coverage) / approved_count * 100, 2) if approved_count > 0 else 0.0
    
    print(f"\n[RESULT] {round_name}:")
    print(f"  Approve rate: {summary['approve_rate']}%")
    print(f"  Avg contract coverage: {summary['avg_contract_coverage']:.2f}")
    print(f"  Reuse via contracts: {summary['reuse_via_contracts']}%")
    
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", type=str, required=True, help="Round name (a/b/ablation)")
    parser.add_argument("--candidates-dir", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--sample-size", type=int, default=50)
    args = parser.parse_args()
    
    candidates_dir = Path(args.candidates_dir)
    output_dir = Path(args.output)
    
    print("=" * 70)
    print("FAMILY B MVE EVALUATOR")
    print("=" * 70)
    print(f"Round: {args.round}")
    print(f"Candidates: {candidates_dir}")
    print(f"Sample: {args.sample_size}")
    print()
    
    # Evaluate
    summary = evaluate_round(candidates_dir, args.round, args.sample_size)
    
    # Save
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "family_b_results.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save summary only
    summary_light = {k: v for k, v in summary.items() if k != "results"}
    with open(output_dir / "summary.json", 'w') as f:
        json.dump(summary_light, f, indent=2)
    
    print(f"\n[SAVE] Results: {output_dir}")


if __name__ == "__main__":
    main()
