#!/usr/bin/env python3
"""
Bridge Phase 1 - Batch Evaluation for Round A/B/Ablation

Execute Bridge evaluation on all candidates and generate:
- bridge_summary.json (overall stats)
- bridge_pass_by_seed.json (per-seed breakdown)
- bridge_pass_by_family.json (family distribution of passes)
- bridge_failure_archetypes.json (failure pattern analysis)

Usage:
    python run_bridge_phase1.py --round a --gpu 0
    python run_bridge_phase1.py --round b --gpu 1
    python run_bridge_phase1.py --round ablation --gpu 2
"""

import json
import argparse
import multiprocessing as mp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import sys

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/bridge')

from bridge_scheduler import BridgeScheduler


class BridgeBatchEvaluator:
    """Batch evaluator for Round A/B/Ablation"""
    
    def __init__(self, round_name: str, gpu_id: int = 0):
        self.round_name = round_name
        self.gpu_id = gpu_id
        self.scheduler = BridgeScheduler(
            "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
        )
        
        # Results storage
        self.results = {
            "round": round_name,
            "gpu": gpu_id,
            "timestamp": datetime.now().isoformat(),
            "candidates": [],
            "summary": {
                "total": 0,
                "admitted": 0,
                "shadow_passed": 0,
                "dry_run_passed": 0,
                "tier_b": 0,
                "tier_c_plus": 0,
                "rejected": 0
            },
            "by_seed": {},
            "by_family": {},
            "failure_archetypes": []
        }
        
    def load_candidates(self, input_dir: str) -> List[Dict]:
        """Load all candidates from round directory"""
        candidates = []
        input_path = Path(input_dir)
        
        # Find all candidate JSON files
        for seed_dir in input_path.glob("seed_*"):
            seed = int(seed_dir.name.replace("seed_", ""))
            candidates_dir = seed_dir / "candidates"
            
            if not candidates_dir.exists():
                continue
                
            for candidate_file in candidates_dir.glob("C*.json"):
                with open(candidate_file) as f:
                    candidate = json.load(f)
                    candidate['_source_seed'] = seed
                    candidate['_source_file'] = str(candidate_file)
                    candidates.append(candidate)
        
        print(f"[BRIDGE-{self.round_name}] Loaded {len(candidates)} candidates from {input_dir}")
        return candidates
    
    def evaluate_candidate(self, candidate: Dict) -> Dict:
        """Evaluate single candidate through full Bridge pipeline"""
        result = {
            "candidate_id": candidate["id"],
            "seed": candidate.get('_source_seed'),
            "family_id": candidate.get("family_id", "unknown"),
            "stages": {},
            "final_status": "REJECTED",
            "final_tier": None
        }
        
        # Stage 1: Admission
        if not self.scheduler.admission_review(candidate):
            result["stages"]["admission"] = {"status": "FAIL"}
            result["rejected_at"] = "admission"
            return result
        
        result["stages"]["admission"] = {"status": "PASS"}
        
        # Stage 2: Shadow (100 tasks)
        shadow_result = self.scheduler.shadow_evaluation(candidate)
        result["stages"]["shadow"] = shadow_result
        
        if shadow_result["status"] != "PASS":
            result["rejected_at"] = "shadow"
            return result
        
        # Stage 3: Dry Run (1000 tasks, 3 seeds)
        dry_result = self.scheduler.dry_run_evaluation(candidate)
        result["stages"]["dry_run"] = dry_result
        result["final_status"] = dry_result["status"]
        result["final_tier"] = dry_result.get("tier")
        
        if dry_result["status"] == "FAIL":
            result["rejected_at"] = "dry_run"
        
        return result
    
    def run_evaluation(self, candidates: List[Dict]) -> List[Dict]:
        """Run evaluation on all candidates"""
        print(f"[BRIDGE-{self.round_name}] Starting evaluation on GPU {self.gpu_id}...")
        
        results = []
        for i, candidate in enumerate(candidates):
            if i % 10 == 0:
                print(f"[BRIDGE-{self.round_name}] Progress: {i}/{len(candidates)}")
            
            result = self.evaluate_candidate(candidate)
            results.append(result)
            
            # Save intermediate results every 25 candidates
            if (i + 1) % 25 == 0:
                self._save_intermediate(results)
        
        return results
    
    def _save_intermediate(self, results: List[Dict]):
        """Save intermediate results"""
        output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/bridge_{self.round_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "_intermediate_results.json", 'w') as f:
            json.dump(results, f, indent=2)
    
    def analyze_results(self, results: List[Dict]):
        """Analyze results and populate summary"""
        # Overall summary
        self.results["summary"]["total"] = len(results)
        self.results["summary"]["admitted"] = sum(1 for r in results if r["stages"].get("admission", {}).get("status") == "PASS")
        self.results["summary"]["shadow_passed"] = sum(1 for r in results if r["stages"].get("shadow", {}).get("status") == "PASS")
        self.results["summary"]["dry_run_passed"] = sum(1 for r in results if r["final_status"] in ["PASS", "MARGINAL"])
        self.results["summary"]["tier_b"] = sum(1 for r in results if r["final_tier"] == "B")
        self.results["summary"]["tier_c_plus"] = sum(1 for r in results if r["final_tier"] == "C+")
        self.results["summary"]["rejected"] = sum(1 for r in results if r["final_status"] == "REJECTED")
        
        # By seed analysis
        seeds = set(r["seed"] for r in results)
        for seed in sorted(seeds):
            seed_results = [r for r in results if r["seed"] == seed]
            self.results["by_seed"][str(seed)] = {
                "total": len(seed_results),
                "shadow_passed": sum(1 for r in seed_results if r["stages"].get("shadow", {}).get("status") == "PASS"),
                "dry_run_passed": sum(1 for r in seed_results if r["final_status"] in ["PASS", "MARGINAL"]),
                "tier_b": sum(1 for r in seed_results if r["final_tier"] == "B"),
                "tier_c_plus": sum(1 for r in seed_results if r["final_tier"] == "C+")
            }
        
        # By family analysis
        families = set(r["family_id"] for r in results)
        for family in sorted(families):
            family_results = [r for r in results if r["family_id"] == family]
            passed = [r for r in family_results if r["final_status"] in ["PASS", "MARGINAL"]]
            
            self.results["by_family"][family] = {
                "total": len(family_results),
                "passed": len(passed),
                "pass_rate": len(passed) / len(family_results) if family_results else 0,
                "tier_b": sum(1 for r in family_results if r["final_tier"] == "B"),
                "tier_c_plus": sum(1 for r in family_results if r["final_tier"] == "C+")
            }
        
        # Failure archetype analysis
        rejected_by_stage = {}
        for r in results:
            if r["final_status"] == "REJECTED":
                stage = r.get("rejected_at", "unknown")
                rejected_by_stage[stage] = rejected_by_stage.get(stage, 0) + 1
        
        self.results["failure_archetypes"] = [
            {"stage": stage, "count": count, "percentage": count / len(results) * 100}
            for stage, count in rejected_by_stage.items()
        ]
        
        self.results["candidates"] = results
    
    def save_outputs(self):
        """Save all required output files"""
        output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/bridge_{self.round_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. bridge_summary.json
        summary = {
            "round": self.round_name,
            "gpu": self.gpu_id,
            "timestamp": self.results["timestamp"],
            "summary": self.results["summary"],
            "pass_rate": {
                "shadow": self.results["summary"]["shadow_passed"] / self.results["summary"]["total"] * 100 if self.results["summary"]["total"] > 0 else 0,
                "dry_run": self.results["summary"]["dry_run_passed"] / self.results["summary"]["total"] * 100 if self.results["summary"]["total"] > 0 else 0,
                "tier_b": self.results["summary"]["tier_b"] / self.results["summary"]["total"] * 100 if self.results["summary"]["total"] > 0 else 0
            }
        }
        with open(output_dir / "bridge_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # 2. bridge_pass_by_seed.json
        with open(output_dir / "bridge_pass_by_seed.json", 'w') as f:
            json.dump({
                "round": self.round_name,
                "by_seed": self.results["by_seed"]
            }, f, indent=2)
        
        # 3. bridge_pass_by_family.json
        with open(output_dir / "bridge_pass_by_family.json", 'w') as f:
            json.dump({
                "round": self.round_name,
                "by_family": self.results["by_family"]
            }, f, indent=2)
        
        # 4. bridge_failure_archetypes.json
        with open(output_dir / "bridge_failure_archetypes.json", 'w') as f:
            json.dump({
                "round": self.round_name,
                "failure_archetypes": self.results["failure_archetypes"]
            }, f, indent=2)
        
        # 5. Full results (for Phase 2 Mainline)
        with open(output_dir / "bridge_full_results.json", 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"[BRIDGE-{self.round_name}] Outputs saved to {output_dir}")
        return output_dir


def main():
    parser = argparse.ArgumentParser(description="Bridge Phase 1 Evaluation")
    parser.add_argument("--round", choices=["a", "b", "ablation"], required=True,
                        help="Which round to evaluate")
    parser.add_argument("--gpu", type=int, default=0,
                        help="GPU ID for execution (for logging purposes)")
    
    args = parser.parse_args()
    
    # Map round name to directory
    round_map = {
        "a": "round_a",
        "b": "round_b",
        "ablation": "round_ablation"
    }
    
    input_dir = f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/{round_map[args.round]}"
    
    print(f"=" * 60)
    print(f"BRIDGE PHASE 1 - Round {args.round.upper()} (GPU {args.gpu})")
    print(f"=" * 60)
    
    # Initialize evaluator
    evaluator = BridgeBatchEvaluator(args.round, args.gpu)
    
    # Load candidates
    candidates = evaluator.load_candidates(input_dir)
    
    if not candidates:
        print(f"[ERROR] No candidates found in {input_dir}")
        return
    
    # Run evaluation
    results = evaluator.run_evaluation(candidates)
    
    # Analyze results
    evaluator.analyze_results(results)
    
    # Save outputs
    output_dir = evaluator.save_outputs()
    
    # Print summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY - Round {args.round.upper()}")
    print(f"{'=' * 60}")
    print(f"Total candidates: {evaluator.results['summary']['total']}")
    print(f"Admitted: {evaluator.results['summary']['admitted']}")
    print(f"Shadow passed: {evaluator.results['summary']['shadow_passed']} ({evaluator.results['summary']['shadow_passed']/evaluator.results['summary']['total']*100:.1f}%)")
    print(f"Dry-run passed: {evaluator.results['summary']['dry_run_passed']} ({evaluator.results['summary']['dry_run_passed']/evaluator.results['summary']['total']*100:.1f}%)")
    print(f"Tier B (Mainline ready): {evaluator.results['summary']['tier_b']}")
    print(f"Tier C+: {evaluator.results['summary']['tier_c_plus']}")
    print(f"Rejected: {evaluator.results['summary']['rejected']}")
    print(f"\nOutput directory: {output_dir}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
