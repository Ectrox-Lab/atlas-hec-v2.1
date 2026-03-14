#!/usr/bin/env python3
"""
Task-1 Validator Calibration

Determine if low approve rate is due to:
A) Task-1 validator being too harsh, OR
B) Candidate quality not reaching Mainline threshold

Test with 3 batches:
- Batch A: Known stable families (F_P3T4M4, etc.)
- Batch B: Hand-crafted high-quality candidates
- Batch C: L4-v2 winners (Round B approved)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from baseline_fast import measure_baseline
from adaptive_fast import run_adaptive_scheduling


@dataclass
class CalibrationResult:
    batch_name: str
    candidate_id: str
    family_id: str
    throughput: float
    latency: float
    missed_rate: float
    approved: bool


def create_batch_a_stable_families() -> List[Dict]:
    """Batch A: Known stable families with optimal parameters"""
    candidates = []
    
    stable_configs = [
        # F_P3T4M4 - the golden family
        {"pressure": 3, "perturbation": 4, "memory": 4, "family": "F_P3T4M4",
         "trust_decay": 0.1, "trust_recovery": 0.05, "priority": "high"},
        {"pressure": 3, "perturbation": 4, "memory": 4, "family": "F_P3T4M4",
         "trust_decay": 0.08, "trust_recovery": 0.06, "priority": "high"},
        {"pressure": 3, "perturbation": 4, "memory": 4, "family": "F_P3T4M4",
         "trust_decay": 0.12, "trust_recovery": 0.04, "priority": "medium"},
        
        # F_P2T4M3 - stable alternative
        {"pressure": 2, "perturbation": 4, "memory": 3, "family": "F_P2T4M3",
         "trust_decay": 0.1, "trust_recovery": 0.05, "priority": "medium"},
        {"pressure": 2, "perturbation": 4, "memory": 3, "family": "F_P2T4M3",
         "trust_decay": 0.09, "trust_recovery": 0.055, "priority": "medium"},
        
        # F_P3T4M3 - another stable
        {"pressure": 3, "perturbation": 4, "memory": 3, "family": "F_P3T4M3",
         "trust_decay": 0.1, "trust_recovery": 0.05, "priority": "medium"},
        
        # F_P2T3M2 - low memory stable
        {"pressure": 2, "perturbation": 3, "memory": 2, "family": "F_P2T3M2",
         "trust_decay": 0.1, "trust_recovery": 0.05, "priority": "low"},
    ]
    
    for i, cfg in enumerate(stable_configs):
        candidates.append({
            "id": f"BATCH_A_{i:02d}_{cfg['family']}",
            "family_id": cfg["family"],
            "pressure": cfg["pressure"],
            "perturbation": cfg["perturbation"],
            "memory": cfg["memory"],
            "delegation": 1,
            "trust_decay": cfg["trust_decay"],
            "trust_recovery": cfg["trust_recovery"],
            "recovery_threshold": 1.0,
            "trust_update_rate": 1.0,
            "migration_threshold": 0.3,
            "batch": "A",
            "priority": cfg["priority"],
            "source": "known_stable"
        })
    
    return candidates


def create_batch_b_handcrafted() -> List[Dict]:
    """Batch B: Hand-crafted high-quality candidates"""
    candidates = []
    
    # Based on L4-v1/L4-v2 observations, craft optimized configs
    handcrafted = [
        # Optimized F_P3T4M4 variants
        {"pressure": 3, "perturbation": 4, "memory": 4, "family": "F_P3T4M4",
         "trust_decay": 0.05, "trust_recovery": 0.08,  # Lower decay, higher recovery
         "recovery_threshold": 0.8, "migration_threshold": 0.2,
         "rationale": "aggressive_recovery"},
        
        {"pressure": 3, "perturbation": 4, "memory": 4, "family": "F_P3T4M4",
         "trust_decay": 0.15, "trust_recovery": 0.03,  # Conservative
         "recovery_threshold": 1.5, "migration_threshold": 0.4,
         "rationale": "conservative_trust"},
        
        # Balanced P2T4M4 (not in stable list but might work)
        {"pressure": 2, "perturbation": 4, "memory": 4, "family": "F_P2T4M4",
         "trust_decay": 0.1, "trust_recovery": 0.05,
         "recovery_threshold": 1.0, "migration_threshold": 0.3,
         "rationale": "balanced_load"},
        
        # P3T3M4 (moderate pressure)
        {"pressure": 3, "perturbation": 3, "memory": 4, "family": "F_P3T3M4",
         "trust_decay": 0.1, "trust_recovery": 0.05,
         "recovery_threshold": 1.0, "migration_threshold": 0.3,
         "rationale": "moderate_triage"},
        
        # P2T3M4
        {"pressure": 2, "perturbation": 3, "memory": 4, "family": "F_P2T3M4",
         "trust_decay": 0.1, "trust_recovery": 0.05,
         "recovery_threshold": 1.0, "migration_threshold": 0.3,
         "rationale": "low_pressure_safe"},
    ]
    
    for i, cfg in enumerate(handcrafted):
        candidates.append({
            "id": f"BATCH_B_{i:02d}_{cfg['family']}",
            "family_id": cfg["family"],
            "pressure": cfg["pressure"],
            "perturbation": cfg["perturbation"],
            "memory": cfg["memory"],
            "delegation": 1,
            "trust_decay": cfg["trust_decay"],
            "trust_recovery": cfg["trust_recovery"],
            "recovery_threshold": cfg["recovery_threshold"],
            "trust_update_rate": 1.0,
            "migration_threshold": cfg["migration_threshold"],
            "batch": "B",
            "rationale": cfg["rationale"],
            "source": "handcrafted"
        })
    
    return candidates


def load_batch_c_l4v2_winners(results_dir: Path) -> List[Dict]:
    """Batch C: L4-v2 winners (Round B approved candidates)"""
    winners = []
    
    detailed_file = results_dir / "mainline_detailed_results.json"
    if not detailed_file.exists():
        print(f"[WARN] {detailed_file} not found, Batch C empty")
        return winners
    
    with open(detailed_file) as f:
        data = json.load(f)
    
    for result in data.get("candidates", []):
        if result.get("approved") and result.get("round_name") == "Round B":
            winners.append({
                "id": f"BATCH_C_{result['candidate_id']}",
                "family_id": result["family_id"],
                "pressure": result["core_signature"]["P"],
                "perturbation": result["core_signature"]["T"],
                "memory": result["core_signature"]["M"],
                "delegation": 1,
                "trust_decay": result.get("trust_decay", 0.1),
                "trust_recovery": result.get("trust_recovery", 0.05),
                "batch": "C",
                "source": "l4v2_winner",
                "original_approval": True
            })
    
    return winners[:10]  # Limit to top 10


def evaluate_candidate(candidate: Dict, seed: int = 42) -> CalibrationResult:
    """Evaluate single candidate"""
    trust_decay = candidate.get("trust_decay", 0.1)
    trust_recovery = candidate.get("trust_recovery", 0.05)
    
    try:
        metrics = run_adaptive_scheduling(
            num_tasks=500,
            num_nodes=4,
            arrival_rate=8.0,
            seed=seed,
            trust_decay=trust_decay,
            trust_recovery=trust_recovery
        )
        
        throughput = metrics.get("throughput", 0.0)
        latency = metrics.get("avg_latency", 999.0)
        missed_rate = metrics.get("missed_deadline_rate", 1.0)
        
    except Exception as e:
        print(f"[WARN] Evaluation failed for {candidate['id']}: {e}")
        throughput = 0.0
        latency = 999.0
        missed_rate = 1.0
    
    # Approval: throughput >= 4% and missed_rate < 95%
    approved = throughput >= 0.04 and missed_rate < 0.95
    
    return CalibrationResult(
        batch_name=candidate.get("batch", "unknown"),
        candidate_id=candidate["id"],
        family_id=candidate.get("family_id", "unknown"),
        throughput=round(throughput, 4),
        latency=round(latency, 2),
        missed_rate=round(missed_rate, 4),
        approved=approved
    )


def run_calibration(output_dir: Path):
    """Run full calibration"""
    print("=" * 70)
    print("TASK-1 VALIDATOR CALIBRATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("")
    
    # Prepare batches
    print("[SETUP] Preparing calibration batches...")
    batch_a = create_batch_a_stable_families()
    batch_b = create_batch_b_handcrafted()
    batch_c = load_batch_c_l4v2_winners(output_dir)
    
    print(f"  Batch A (Known stable): {len(batch_a)} candidates")
    print(f"  Batch B (Handcrafted): {len(batch_b)} candidates")
    print(f"  Batch C (L4-v2 winners): {len(batch_c)} candidates")
    print("")
    
    # Evaluate all
    all_results = []
    
    for batch_name, batch in [("A", batch_a), ("B", batch_b), ("C", batch_c)]:
        if not batch:
            continue
            
        print(f"[EVAL] Batch {batch_name}: {len(batch)} candidates")
        for i, candidate in enumerate(batch):
            result = evaluate_candidate(candidate, seed=1000 + i)
            all_results.append(result)
            
            status = "✓" if result.approved else "✗"
            print(f"  {status} {result.candidate_id}: {result.throughput*100:.1f}% throughput, "
                  f"{result.missed_rate*100:.1f}% missed, {'APPROVED' if result.approved else 'REJECTED'}")
        
        # Batch summary
        batch_results = [r for r in all_results if r.batch_name == batch_name]
        approved = sum(1 for r in batch_results if r.approved)
        rate = approved / len(batch_results) if batch_results else 0
        print(f"[BATCH {batch_name}] {approved}/{len(batch_results)} approved ({rate*100:.1f}%)")
        print("")
    
    # Generate report
    generate_calibration_report(all_results, output_dir)
    
    return all_results


def generate_calibration_report(results: List[CalibrationResult], output_dir: Path):
    """Generate calibration report"""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    
    # Summary by batch
    summary = {}
    for batch in ["A", "B", "C"]:
        batch_results = [r for r in results if r.batch_name == batch]
        if not batch_results:
            continue
            
        approved = sum(1 for r in batch_results if r.approved)
        summary[batch] = {
            "total": len(batch_results),
            "approved": approved,
            "approve_rate": round(approved / len(batch_results) * 100, 2),
            "avg_throughput": round(sum(r.throughput for r in batch_results) / len(batch_results) * 100, 2),
            "avg_missed_rate": round(sum(r.missed_rate for r in batch_results) / len(batch_results) * 100, 2)
        }
    
    # Save JSON
    with open(output_dir / "validator_calibration_summary.json", 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": summary,
            "results": [asdict(r) for r in results]
        }, f, indent=2)
    
    # Generate Markdown
    lines = [
        "# Task-1 Validator Calibration Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Purpose",
        "",
        "Determine if low L4-v2 approve rate is due to:",
        "- A) Task-1 validator being too harsh, OR",
        "- B) Candidate quality not reaching threshold",
        "",
        "## Test Batches",
        "",
        "| Batch | Description | Candidates |",
        "|-------|-------------|------------|",
        "| A | Known stable families (F_P3T4M4, etc.) | 7 |",
        "| B | Hand-crafted high-quality candidates | 5 |",
        "| C | L4-v2 Round B winners | Variable |",
        "",
        "## Results",
        "",
    ]
    
    for batch, data in summary.items():
        lines.extend([
            f"### Batch {batch}",
            "",
            f"- Total evaluated: {data['total']}",
            f"- Approved: {data['approved']}",
            f"- Approve rate: **{data['approve_rate']}%**",
            f"- Avg throughput: {data['avg_throughput']}%",
            f"- Avg missed rate: {data['avg_missed_rate']}%",
            "",
        ])
    
    # Conclusion
    lines.extend([
        "## Conclusion",
        "",
    ])
    
    batch_a_rate = summary.get("A", {}).get("approve_rate", 0)
    batch_b_rate = summary.get("B", {}).get("approve_rate", 0)
    
    if batch_a_rate >= 50 or batch_b_rate >= 50:
        lines.extend([
            "**Verdict**: ✅ KNOWN GOOD CANDIDATES CAN PASS",
            "",
            "If Batch A or B shows high approve rate (≥50%), then:",
            "- Task-1 validator is NOT too harsh",
            "- The issue is L4-v2 candidate quality, not task difficulty",
            "- **Action**: Tune generation parameters (bias strength, etc.)",
        ])
    else:
        lines.extend([
            "**Verdict**: ❌ TASK-1 IS VERY DIFFICULT",
            "",
            "If even Batch A/B shows low approve rate (<50%), then:",
            "- Task-1 validator IS very harsh",
            "- Low L4-v2 approve rate is due to task difficulty, not mechanism failure",
            "- **Action**: Relax targets OR change task family",
        ])
    
    lines.extend([
        "",
        "---",
        "",
        "*Generated by task1_validator_calibration.py*",
    ])
    
    with open(output_dir / "validator_calibration_report.md", 'w') as f:
        f.write('\n'.join(lines))
    
    print("=" * 70)
    print("CALIBRATION COMPLETE")
    print("=" * 70)
    print(f"Summary: {output_dir / 'validator_calibration_summary.json'}")
    print(f"Report: {output_dir / 'validator_calibration_report.md'}")
    print("")
    
    # Quick verdict
    print("QUICK VERDICT:")
    if batch_a_rate >= 50 or batch_b_rate >= 50:
        print("✅ Known good candidates CAN pass")
        print("   → Issue: Generation quality")
        print("   → Action: Tune parameters")
    else:
        print("❌ Task-1 is very difficult")
        print("   → Issue: Task difficulty")
        print("   → Action: Relax targets or change task")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=str, default="/tmp/atlas_l4v2_results",
                        help="Output directory for calibration results")
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    run_calibration(output_dir)


if __name__ == "__main__":
    main()
