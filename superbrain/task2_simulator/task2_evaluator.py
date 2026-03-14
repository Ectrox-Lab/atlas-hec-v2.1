#!/usr/bin/env python3
"""
Task-2 Evaluator for L4-v3

Evaluates candidates on multi-stage pipeline simulator.
"""

import json
import random
import sys
import argparse
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from pipeline_simulator import run_pipeline_simulation


def load_candidates(candidates_dir: Path) -> List[Dict]:
    """Load candidate JSONs"""
    candidates = []
    for cand_file in sorted(candidates_dir.glob("C*.json")):
        with open(cand_file) as f:
            candidates.append(json.load(f))
    return candidates


def stratified_sample(candidates: List[Dict], n: int = 20, seed: int = 42) -> List[Dict]:
    """Stratified sampling by family"""
    random.seed(seed)
    
    # Group by family
    by_family = {}
    for c in candidates:
        fam = c.get('family_id', 'unknown')
        by_family.setdefault(fam, []).append(c)
    
    # Sample proportionally
    sampled = []
    total = len(candidates)
    
    for fam, fam_cands in by_family.items():
        target = max(1, round(n * len(fam_cands) / total))
        sampled.extend(random.sample(fam_cands, min(target, len(fam_cands))))
    
    # Fill to n if needed
    while len(sampled) < n:
        remaining = [c for c in candidates if c not in sampled]
        if remaining:
            sampled.append(random.choice(remaining))
        else:
            break
    
    return sampled[:n]


def evaluate_candidate(candidate: Dict, seed: int = 42) -> Dict:
    """Evaluate single candidate on Task-2"""
    # Extract parameters
    pressure = candidate.get('pressure', 2)
    triage = candidate.get('perturbation', 3)  # Triage = perturbation
    memory = candidate.get('memory', 3)
    delegation = candidate.get('delegation', 1)
    trust_decay = candidate.get('trust_decay', 0.1)
    trust_recovery = candidate.get('trust_recovery', 0.05)
    
    # Run Task-2 simulation
    metrics = run_pipeline_simulation(
        num_tasks=200,
        pressure=pressure,
        triage=triage,
        memory=memory,
        delegation=delegation,
        trust_decay=trust_decay,
        trust_recovery=trust_recovery,
        seed=seed
    )
    
    # Approval criteria (more lenient than Task-1)
    # Completion > 70% (baseline is 93.5%)
    approved = metrics['pipeline_completion_rate'] >= 0.70
    
    return {
        'candidate_id': candidate.get('id', 'unknown'),
        'family_id': candidate.get('family_id', 'unknown'),
        'core_signature': {
            'P': pressure,
            'T': triage,
            'M': memory
        },
        'approved': approved,
        'completion_rate': metrics['pipeline_completion_rate'],
        'throughput': metrics['stage_throughput'],
        'failover_success': metrics['failover_success_rate'],
        'is_stable_family': candidate.get('family_id', '') in ['F_P3T4M4', 'F_P2T4M3', 'F_P3T4M3', 'F_P2T3M2'],
        'is_f_p3t4m4': candidate.get('family_id', '') == 'F_P3T4M4',
        'is_leakage_family': pressure in [1, 4] or triage in [2, 5] or memory in [1, 5],
        'mechanism_score': candidate.get('mechanism_score', 0.5),
        'anti_leakage_penalty': candidate.get('anti_leakage_penalty', 0.0)
    }


def evaluate_round(candidates: List[Dict], round_name: str, sample_size: int = 20) -> Dict:
    """Evaluate a full round"""
    print(f"[EVAL] {round_name}: {len(candidates)} candidates loaded")
    
    # Sample
    sampled = stratified_sample(candidates, n=sample_size)
    print(f"[EVAL] {round_name}: Sampled {len(sampled)} candidates")
    
    # Evaluate
    results = []
    for i, cand in enumerate(sampled):
        result = evaluate_candidate(cand, seed=5000 + i)
        results.append(result)
        if (i + 1) % 5 == 0:
            print(f"  {i+1}/{len(sampled)} evaluated")
    
    # Calculate metrics
    total = len(results)
    approved = sum(1 for r in results if r['approved'])
    approved_candidates = [r for r in results if r['approved']]
    
    summary = {
        'round': round_name,
        'total_evaluated': total,
        'approved_count': approved,
        'approve_rate': round(approved / total * 100, 2) if total > 0 else 0.0,
        'avg_completion': round(sum(r['completion_rate'] for r in results) / total * 100, 2) if total > 0 else 0.0,
        'reuse_rate': round(sum(1 for r in approved_candidates if r['is_stable_family']) / approved * 100, 2) if approved > 0 else 0.0,
        'f_p3t4m4_share': round(sum(1 for r in approved_candidates if r['is_f_p3t4m4']) / approved * 100, 2) if approved > 0 else 0.0,
        'leakage': round(sum(1 for r in approved_candidates if r['is_leakage_family']) / approved * 100, 2) if approved > 0 else 0.0,
        'candidates': results
    }
    
    print(f"\n[RESULT] {round_name}:")
    print(f"  Approve rate: {summary['approve_rate']}%")
    print(f"  Reuse rate: {summary['reuse_rate']}%")
    print(f"  Leakage: {summary['leakage']}%")
    
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--sample-size", type=int, default=20)
    parser.add_argument("--baseline-completion", type=float, default=0.935)
    args = parser.parse_args()
    
    candidates_dir = Path(args.candidates)
    output_dir = Path(args.output)
    
    print("=" * 70)
    print("TASK-2 EVALUATOR (L4-v3)")
    print("=" * 70)
    print(f"Candidates: {candidates_dir}")
    print(f"Output: {output_dir}")
    print(f"Baseline completion: {args.baseline_completion:.1%}")
    print("")
    
    # Load and evaluate
    candidates = load_candidates(candidates_dir)
    round_name = candidates_dir.parent.name  # Extract round name from path
    
    summary = evaluate_round(candidates, round_name, args.sample_size)
    
    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "effectiveness.json", 'w') as f:
        json.dump({
            'round': summary['round'],
            'approve_rate': summary['approve_rate'],
            'approved_count': summary['approved_count'],
            'total_evaluated': summary['total_evaluated'],
            'avg_completion': summary['avg_completion']
        }, f, indent=2)
    
    with open(output_dir / "compositionality.json", 'w') as f:
        json.dump({
            'round': summary['round'],
            'reuse_rate': summary['reuse_rate'],
            'f_p3t4m4_share': summary['f_p3t4m4_share'],
            'leakage': summary['leakage']
        }, f, indent=2)
    
    with open(output_dir / "detailed_results.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[SAVE] Results: {output_dir}")


if __name__ == "__main__":
    main()
