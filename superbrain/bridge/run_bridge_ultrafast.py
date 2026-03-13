#!/usr/bin/env python3
"""
Bridge Ultra-Fast Evaluation - Shadow-Only for Quick Screening

Skip Dry Run, use Shadow only (50 tasks) for rapid pass rate assessment.

Outputs:
- bridge_uf_summary.json
- bridge_uf_by_seed.json  
- bridge_uf_by_family.json
- bridge_uf_passed_candidates.json (for Phase 2 Mainline)
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/bridge')

from bridge_scheduler import BridgeScheduler


def run_ultrafast_bridge(round_name: str, gpu_id: int = 0):
    """Run ultra-fast Bridge evaluation (Shadow only)"""
    
    round_map = {"a": "round_a", "b": "round_b", "ablation": "round_ablation"}
    input_dir = f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/{round_map[round_name]}"
    
    scheduler = BridgeScheduler(
        "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
    )
    
    # Load candidates
    candidates = []
    input_path = Path(input_dir)
    for seed_dir in input_path.glob("seed_*"):
        seed = int(seed_dir.name.replace("seed_", ""))
        candidates_dir = seed_dir / "candidates"
        if candidates_dir.exists():
            for cf in candidates_dir.glob("C*.json"):
                with open(cf) as f:
                    c = json.load(f)
                    c['_source_seed'] = seed
                    candidates.append(c)
    
    print(f"[Bridge-UF-{round_name}] Evaluating {len(candidates)} candidates (Shadow only)...")
    
    results = []
    passed_candidates = []
    
    for i, c in enumerate(candidates):
        if i % 25 == 0:
            print(f"[Bridge-UF-{round_name}] {i}/{len(candidates)}")
        
        # Admission
        if not scheduler.admission_review(c):
            results.append({
                "id": c["id"], "seed": c['_source_seed'], "family": c.get("family_id"),
                "status": "REJECTED", "stage": "admission"
            })
            continue
        
        # Shadow only (fast)
        shadow = scheduler.shadow_evaluation(c)
        
        result = {
            "id": c["id"],
            "seed": c['_source_seed'],
            "family": c.get("family_id"),
            "status": shadow["status"],
            "throughput": shadow.get("throughput"),
            "throughput_delta": shadow.get("throughput_delta"),
            "improvement_pct": shadow.get("improvement_pct")
        }
        results.append(result)
        
        if shadow["status"] == "PASS":
            passed_candidates.append({
                "candidate": c,
                "bridge_result": shadow
            })
    
    # Analysis
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    rejected = sum(1 for r in results if r["status"] == "REJECTED")
    
    # By seed
    by_seed = {}
    for seed in [1000, 1001, 1002]:
        seed_results = [r for r in results if r["seed"] == seed]
        seed_passed = sum(1 for r in seed_results if r["status"] == "PASS")
        by_seed[str(seed)] = {
            "total": len(seed_results),
            "passed": seed_passed,
            "pass_rate": seed_passed / len(seed_results) if seed_results else 0
        }
    
    # By family
    families = set(r["family"] for r in results if r["family"])
    by_family = {}
    for fam in sorted(families):
        fam_results = [r for r in results if r["family"] == fam]
        fam_passed = sum(1 for r in fam_results if r["status"] == "PASS")
        by_family[fam] = {
            "total": len(fam_results),
            "passed": fam_passed,
            "pass_rate": fam_passed / len(fam_results) if fam_results else 0
        }
    
    # Save outputs
    output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/bridge_uf_{round_name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Summary
    summary = {
        "round": round_name,
        "gpu": gpu_id,
        "mode": "ultrafast_shadow_only",
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "rejected": rejected,
            "pass_rate": passed / total if total else 0
        },
        "by_seed": by_seed,
        "by_family": by_family
    }
    
    with open(output_dir / "bridge_uf_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    with open(output_dir / "bridge_uf_by_seed.json", 'w') as f:
        json.dump({"round": round_name, "by_seed": by_seed}, f, indent=2)
    
    with open(output_dir / "bridge_uf_by_family.json", 'w') as f:
        json.dump({"round": round_name, "by_family": by_family}, f, indent=2)
    
    with open(output_dir / "bridge_uf_passed_candidates.json", 'w') as f:
        json.dump({
            "round": round_name,
            "passed_count": len(passed_candidates),
            "candidates": passed_candidates
        }, f, indent=2)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"BRIDGE ULTRA-FAST - Round {round_name.upper()}")
    print(f"{'='*50}")
    print(f"Total: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Rejected: {rejected}")
    print(f"\nBy Seed:")
    for seed, data in by_seed.items():
        print(f"  Seed {seed}: {data['passed']}/{data['total']} ({data['pass_rate']*100:.1f}%)")
    print(f"\nOutput: {output_dir}")
    
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=["a", "b", "ablation"], required=True)
    parser.add_argument("--gpu", type=int, default=0)
    args = parser.parse_args()
    
    run_ultrafast_bridge(args.round, args.gpu)


if __name__ == "__main__":
    main()
