#!/usr/bin/env python3
"""
Mainline Phase 2 - FAST VERSION for demonstration

Reduced parameters for faster execution:
- 1000 tasks (instead of 10k)
- 3 seeds (instead of 10)

Output format identical to full version.
"""

import json
import argparse
import statistics
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from adaptive_fast import run_adaptive_scheduling


# FAST MODE parameters
MAINLINE_CONFIG = {
    "num_tasks": 1000,  # Reduced from 10000
    "num_seeds": 3,     # Reduced from 10
    "num_nodes": 6,
    "arrival_rate": 8.0
}

BASELINE = {
    'throughput': 0.0214,
    'latency': 253.9,
    'recovery_time': 289.5,
    'switching_rate': 0.0036,
    'missed_rate': 0.9088,
    'stability_cv': 0.668
}


class FastMainlineEvaluator:
    """Fast Mainline evaluation for demonstration"""
    
    def __init__(self, round_name: str, gpu_id: int):
        self.round_name = round_name
        self.gpu_id = gpu_id
        
        sample_path = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/mainline_input_{round_name}/mainline_sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        self.candidates = data["candidates"]
        
        self.results = []
        self.approved = []
        self.held = []
        self.rejected = []
    
    def evaluate_candidate(self, candidate: Dict) -> Dict:
        """Evaluate single candidate"""
        cid = candidate["id"]
        family = candidate["family"]
        seed_source = candidate["seed"]
        
        print(f"[MAINLINE-{self.round_name}] {cid} ({family})")
        
        trust_decay = candidate.get("candidate_config", {}).get("trust_decay", 0.0)
        trust_recovery = candidate.get("candidate_config", {}).get("trust_recovery", 0.0)
        
        # Run evaluation
        all_results = []
        for seed_idx in range(MAINLINE_CONFIG["num_seeds"]):
            seed = hash(cid) % 10000 + seed_idx * 1000
            try:
                result = run_adaptive_scheduling(
                    num_tasks=MAINLINE_CONFIG["num_tasks"],
                    num_nodes=MAINLINE_CONFIG["num_nodes"],
                    arrival_rate=MAINLINE_CONFIG["arrival_rate"],
                    seed=seed,
                    trust_decay=trust_decay,
                    trust_recovery=trust_recovery
                )
                all_results.append(result)
            except Exception as e:
                print(f"  Seed error: {e}")
                continue
        
        if not all_results:
            return self._make_fallback_result(cid, family, seed_source)
        
        # Aggregate
        throughputs = [r['throughput'] for r in all_results]
        latencies = [r['avg_latency'] for r in all_results]
        recovery_times = [r['recovery_time'] for r in all_results]
        switching_rates = [r['unnecessary_switches'] for r in all_results]
        missed_rates = [r['missed_deadline_rate'] for r in all_results]
        
        tp_mean = statistics.mean(throughputs)
        tp_delta = tp_mean - BASELINE['throughput']
        
        lat_mean = statistics.mean(latencies)
        lat_delta = lat_mean - BASELINE['latency']
        
        rec_mean = statistics.mean(recovery_times)
        rec_delta = rec_mean - BASELINE['recovery_time']
        
        sw_mean = statistics.mean(switching_rates)
        
        tp_std = statistics.stdev(throughputs) if len(throughputs) > 1 else 0
        cv_tp = tp_std / tp_mean if tp_mean > 0 else 0
        
        # Decision
        if tp_mean >= 0.025:
            decision = "APPROVE"
        elif tp_mean >= 0.022:
            decision = "HOLD"
        else:
            decision = "REJECT"
        
        result = {
            "candidate_id": cid,
            "family": family,
            "seed_source": seed_source,
            "decision": decision,
            "metrics": {
                "throughput_mean": tp_mean,
                "throughput_delta": tp_delta,
                "latency_mean": lat_mean,
                "latency_delta": lat_delta,
                "recovery_mean": rec_mean,
                "recovery_delta": rec_delta,
                "switching_mean": sw_mean,
                "stability_cv": cv_tp,
                "seeds_tested": len(all_results)
            }
        }
        
        if decision == "APPROVE":
            self.approved.append(result)
        elif decision == "HOLD":
            self.held.append(result)
        else:
            self.rejected.append(result)
        
        self.results.append(result)
        print(f"  -> {decision} (tp={tp_mean:.2%})")
        return result
    
    def _make_fallback_result(self, cid, family, seed_source):
        """Fallback for failed evaluation"""
        result = {
            "candidate_id": cid,
            "family": family,
            "seed_source": seed_source,
            "decision": "REJECT",
            "metrics": {"throughput_mean": 0, "throughput_delta": -0.0214}
        }
        self.rejected.append(result)
        self.results.append(result)
        return result
    
    def run_evaluation(self):
        """Run all evaluations"""
        print(f"="*60)
        print(f"MAINLINE PHASE 2 (FAST) - Round {self.round_name.upper()}")
        print(f"="*60)
        print(f"Candidates: {len(self.candidates)}")
        print(f"Config: {MAINLINE_CONFIG['num_tasks']} tasks × {MAINLINE_CONFIG['num_seeds']} seeds")
        
        for i, c in enumerate(self.candidates):
            print(f"\n[{i+1}/{len(self.candidates)}]", end=" ")
            self.evaluate_candidate(c)
        
        print(f"\n{'='*60}")
        print(f"COMPLETE - APPROVE:{len(self.approved)} HOLD:{len(self.held)} REJECT:{len(self.rejected)}")
    
    def generate_outputs(self):
        """Generate output files"""
        output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/mainline_{self.round_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Table A
        effectiveness = self._generate_effectiveness()
        with open(output_dir / "mainline_effectiveness_summary.json", 'w') as f:
            json.dump(effectiveness, f, indent=2)
        
        # Table B
        compositionality = self._generate_compositionality()
        with open(output_dir / "mainline_compositionality_summary.json", 'w') as f:
            json.dump(compositionality, f, indent=2)
        
        # Full results
        with open(output_dir / "mainline_full_results.json", 'w') as f:
            json.dump({
                "round": self.round_name,
                "mode": "FAST",
                "config": MAINLINE_CONFIG,
                "results": self.results
            }, f, indent=2)
        
        return output_dir, effectiveness, compositionality
    
    def _generate_effectiveness(self):
        """Table A"""
        total = len(self.results)
        approved = len(self.approved)
        
        if self.approved:
            tp_deltas = [r["metrics"]["throughput_delta"] for r in self.approved]
            lat_deltas = [r["metrics"]["latency_delta"] for r in self.approved]
            mean_tp = statistics.mean(tp_deltas)
            mean_lat = statistics.mean(lat_deltas)
        else:
            mean_tp = mean_lat = 0
        
        failures = [r for r in self.results if r["metrics"].get("throughput_mean", 0) < 0.015]
        
        return {
            "round": self.round_name,
            "table": "A - Effectiveness",
            "sampled_candidates": total,
            "approve_count": approved,
            "hold_count": len(self.held),
            "reject_count": len(self.rejected),
            "approve_rate": approved / total if total > 0 else 0,
            "mean_throughput_delta": mean_tp,
            "mean_latency_delta": mean_lat,
            "failure_archetype_recurrence": len(failures)
        }
    
    def _generate_compositionality(self):
        """Table B"""
        approved_families = {}
        for r in self.approved:
            fam = r["family"]
            approved_families[fam] = approved_families.get(fam, 0) + 1
        
        total = len(self.approved)
        
        # F_P3T4M4 share
        p3t4m4 = approved_families.get("F_P3T4M4", 0)
        
        # Reuse rate (stable families)
        stable = ["F_P3T4M4", "F_P2T4M3", "F_P3T4M3", "F_P3T3M2", "F_P3T3M4"]
        reused = sum(1 for r in self.approved if r["family"] in stable)
        
        # Leakage (suspicious families)
        suspicious = ["F_P1T3M3", "F_P4T4M3", "F_P3T5M5"]
        leaked = sum(1 for r in self.approved if r["family"] in suspicious)
        
        # Stable paths (P2/P3-T4)
        stable_paths = ["F_P3T4M4", "F_P2T4M3", "F_P3T4M3"]
        from_stable = sum(1 for r in self.approved if r["family"] in stable_paths)
        
        return {
            "round": self.round_name,
            "table": "B - Compositionality",
            "approved_family_distribution": approved_families,
            "total_approved": total,
            "f_p3t4m4_count": p3t4m4,
            "f_p3t4m4_share": p3t4m4 / total if total > 0 else 0,
            "reuse_rate": reused / total if total > 0 else 0,
            "new_family_leakage": leaked / total if total > 0 else 0,
            "winners_from_stable_paths": from_stable,
            "winners_from_stable_paths_share": from_stable / total if total > 0 else 0
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=["a", "b", "ablation"], required=True)
    parser.add_argument("--gpu", type=int, default=0)
    args = parser.parse_args()
    
    evaluator = FastMainlineEvaluator(args.round, args.gpu)
    evaluator.run_evaluation()
    output_dir, eff, comp = evaluator.generate_outputs()
    
    print(f"\n{'='*60}")
    print(f"OUTPUTS SAVED to {output_dir}")
    print(f"{'='*60}")
    print(f"\nTable A - Effectiveness:")
    print(f"  Approve rate: {eff['approve_rate']:.1%}")
    print(f"  Mean throughput Δ: {eff['mean_throughput_delta']:+.2%}")
    print(f"\nTable B - Compositionality:")
    print(f"  F_P3T4M4 share: {comp['f_p3t4m4_share']:.1%}")
    print(f"  Reuse rate: {comp['reuse_rate']:.1%}")
    print(f"  Leakage: {comp['new_family_leakage']:.1%}")


if __name__ == "__main__":
    main()
