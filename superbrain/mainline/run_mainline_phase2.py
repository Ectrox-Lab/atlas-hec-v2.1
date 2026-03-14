#!/usr/bin/env python3
"""
Mainline Phase 2 - Batch Evaluation for Sampled Candidates

Execute Mainline validator on sampled candidates from Round A/B/Ablation.
Outputs:
- mainline_effectiveness_summary.json (Table A)
- mainline_compositionality_summary.json (Table B)
- mainline_phase2_report.md

Usage:
    python run_mainline_phase2.py --round a --gpu 0
    python run_mainline_phase2.py --round b --gpu 1
    python run_mainline_phase2.py --round ablation --gpu 2
"""

import json
import argparse
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
from adaptive_fast import run_adaptive_scheduling


# Fixed parameters - DO NOT CHANGE
MAINLINE_CONFIG = {
    "num_tasks": 10000,
    "num_seeds": 10,
    "num_nodes": 6,
    "arrival_rate": 8.0
}

# Baseline reference (from task1_simulator measurements)
BASELINE = {
    'throughput': 0.0214,
    'latency': 253.9,
    'recovery_time': 289.5,
    'switching_rate': 0.0036,
    'missed_rate': 0.9088,
    'stability_cv': 0.668
}


class MainlinePhase2Evaluator:
    """Execute Mainline evaluation on sampled candidates"""
    
    def __init__(self, round_name: str, gpu_id: int):
        self.round_name = round_name
        self.gpu_id = gpu_id
        
        # Load sampled candidates
        sample_path = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/mainline_input_{round_name}/mainline_sample.json")
        with open(sample_path) as f:
            data = json.load(f)
        self.candidates = data["candidates"]
        
        # Results storage
        self.results = []
        self.approved = []
        self.held = []
        self.rejected = []
        
    def evaluate_candidate(self, candidate: Dict) -> Dict:
        """Run Mainline evaluation on single candidate"""
        cid = candidate["id"]
        family = candidate["family"]
        seed_source = candidate["seed"]
        
        print(f"\n[MAINLINE-{self.round_name}] Evaluating {cid} (family: {family})")
        
        # Extract parameters
        trust_decay = candidate.get("candidate_config", {}).get("trust_decay", 0.0)
        trust_recovery = candidate.get("candidate_config", {}).get("trust_recovery", 0.0)
        
        # Run multi-seed evaluation (10 seeds, 10k tasks each)
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
                print(f"  Seed {seed_idx} failed: {e}")
                continue
        
        if not all_results:
            return {
                "candidate_id": cid,
                "family": family,
                "seed_source": seed_source,
                "decision": "REJECT",
                "reason": "all_seeds_failed",
                "metrics": {}
            }
        
        # Aggregate metrics
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
        sw_delta = sw_mean - BASELINE['switching_rate']
        
        missed_mean = statistics.mean(missed_rates)
        missed_delta = missed_mean - BASELINE['missed_rate']
        
        # Stability
        tp_std = statistics.stdev(throughputs) if len(throughputs) > 1 else 0
        cv_tp = tp_std / tp_mean if tp_mean > 0 else float('inf')
        
        # Decision (simplified: APPROVE if throughput > 2.5%)
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
                "switching_delta": sw_delta,
                "missed_rate_mean": missed_mean,
                "missed_delta": missed_delta,
                "stability_cv": cv_tp,
                "seeds_tested": len(all_results)
            }
        }
        
        # Categorize
        if decision == "APPROVE":
            self.approved.append(result)
        elif decision == "HOLD":
            self.held.append(result)
        else:
            self.rejected.append(result)
        
        self.results.append(result)
        print(f"  Decision: {decision}, Throughput: {tp_mean:.2%} (Δ{tp_delta:+.2%})")
        
        return result
    
    def run_evaluation(self):
        """Evaluate all sampled candidates"""
        print(f"="*60)
        print(f"MAINLINE PHASE 2 - Round {self.round_name.upper()} (GPU {self.gpu_id})")
        print(f"="*60)
        print(f"Candidates: {len(self.candidates)}")
        print(f"Config: {MAINLINE_CONFIG['num_tasks']} tasks × {MAINLINE_CONFIG['num_seeds']} seeds")
        
        for i, candidate in enumerate(self.candidates):
            print(f"\nProgress: {i+1}/{len(self.candidates)}")
            self.evaluate_candidate(candidate)
        
        print(f"\n{'='*60}")
        print(f"EVALUATION COMPLETE - Round {self.round_name.upper()}")
        print(f"{'='*60}")
        print(f"APPROVE: {len(self.approved)}")
        print(f"HOLD: {len(self.held)}")
        print(f"REJECT: {len(self.rejected)}")
    
    def generate_outputs(self):
        """Generate required output files"""
        output_dir = Path(f"/home/admin/atlas-hec-v2.1-repo/benchmark_results/task1_inheritance/mainline_{self.round_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Table A: Effectiveness
        effectiveness = self._generate_effectiveness_table()
        with open(output_dir / "mainline_effectiveness_summary.json", 'w') as f:
            json.dump(effectiveness, f, indent=2)
        
        # Table B: Compositionality
        compositionality = self._generate_compositionality_table()
        with open(output_dir / "mainline_compositionality_summary.json", 'w') as f:
            json.dump(compositionality, f, indent=2)
        
        # Full results
        with open(output_dir / "mainline_full_results.json", 'w') as f:
            json.dump({
                "round": self.round_name,
                "gpu": self.gpu_id,
                "config": MAINLINE_CONFIG,
                "baseline": BASELINE,
                "results": self.results
            }, f, indent=2)
        
        return output_dir
    
    def _generate_effectiveness_table(self) -> Dict:
        """Generate Table A: Effectiveness metrics"""
        total = len(self.results)
        approved = len(self.approved)
        held = len(self.held)
        
        # Aggregate metrics for approved candidates
        if self.approved:
            tp_deltas = [r["metrics"]["throughput_delta"] for r in self.approved]
            lat_deltas = [r["metrics"]["latency_delta"] for r in self.approved]
            rec_deltas = [r["metrics"]["recovery_delta"] for r in self.approved]
            
            mean_tp_delta = statistics.mean(tp_deltas)
            mean_lat_delta = statistics.mean(lat_deltas)
            mean_rec_delta = statistics.mean(rec_deltas)
        else:
            mean_tp_delta = 0
            mean_lat_delta = 0
            mean_rec_delta = 0
        
        # Failure archetype analysis (candidates with very low throughput)
        failures = [r for r in self.results if r["metrics"].get("throughput_mean", 0) < 0.015]
        
        return {
            "round": self.round_name,
            "table": "A - Effectiveness",
            "sampled_candidates": total,
            "approve_count": approved,
            "hold_count": held,
            "reject_count": len(self.rejected),
            "approve_rate": approved / total if total > 0 else 0,
            "mean_throughput_delta": mean_tp_delta,
            "mean_latency_delta": mean_lat_delta,
            "mean_recovery_delta": mean_rec_delta,
            "failure_archetype_recurrence": len(failures),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_compositionality_table(self) -> Dict:
        """Generate Table B: Compositionality metrics"""
        # Family distribution of approved candidates
        approved_families = {}
        for r in self.approved:
            fam = r["family"]
            approved_families[fam] = approved_families.get(fam, 0) + 1
        
        total_approved = len(self.approved)
        
        # F_P3T4M4 share
        f_p3t4m4_count = approved_families.get("F_P3T4M4", 0)
        f_p3t4m4_share = f_p3t4m4_count / total_approved if total_approved > 0 else 0
        
        # Reuse rate (approved from stable families)
        stable_families = ["F_P3T4M4", "F_P2T4M3", "F_P3T4M3", "F_P3T3M2", "F_P3T3M4", "F_P2T3M4"]
        reused = sum(1 for r in self.approved if r["family"] in stable_families)
        reuse_rate = reused / total_approved if total_approved > 0 else 0
        
        # New family leakage (approved from suspicious families)
        suspicious_families = ["F_P1T3M3", "F_P4T4M3", "F_P3T5M5", "F_P2T5M4"]
        leaked = sum(1 for r in self.approved if r["family"] in suspicious_families)
        leakage_rate = leaked / total_approved if total_approved > 0 else 0
        
        # Suspicious family success rate
        suspicious_total = sum(1 for r in self.results if r["family"] in suspicious_families)
        suspicious_success_rate = leaked / suspicious_total if suspicious_total > 0 else 0
        
        # Winners from existing stable paths
        stable_path_families = ["F_P3T4M4", "F_P2T4M3", "F_P3T4M3"]
        from_stable_paths = sum(1 for r in self.approved if r["family"] in stable_path_families)
        
        return {
            "round": self.round_name,
            "table": "B - Compositionality",
            "approved_family_distribution": approved_families,
            "total_approved": total_approved,
            "f_p3t4m4_count": f_p3t4m4_count,
            "f_p3t4m4_share": f_p3t4m4_share,
            "reuse_rate": reuse_rate,
            "new_family_leakage": leakage_rate,
            "suspicious_family_success_rate": suspicious_success_rate,
            "winners_from_stable_paths": from_stable_paths,
            "winners_from_stable_paths_share": from_stable_paths / total_approved if total_approved > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", choices=["a", "b", "ablation"], required=True)
    parser.add_argument("--gpu", type=int, default=0)
    args = parser.parse_args()
    
    evaluator = MainlinePhase2Evaluator(args.round, args.gpu)
    evaluator.run_evaluation()
    output_dir = evaluator.generate_outputs()
    
    print(f"\n{'='*60}")
    print(f"OUTPUTS SAVED")
    print(f"{'='*60}")
    print(f"Directory: {output_dir}")
    print(f"  - mainline_effectiveness_summary.json (Table A)")
    print(f"  - mainline_compositionality_summary.json (Table B)")
    print(f"  - mainline_full_results.json")


if __name__ == "__main__":
    main()
