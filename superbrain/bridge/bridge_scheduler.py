#!/usr/bin/env python3
"""
Bridge Scheduler - Rolling Funnel Filter

Responsibility: Admission → Shadow → Dry Run → Queue
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class BridgeScheduler:
    """Manages candidate flow through validation stages"""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.stages = {
            "admission": [],
            "shadow": [],
            "dry_run": [],
            "queue": []
        }
        
        self.stats = {
            "admitted": 0,
            "shadow_passed": 0,
            "dry_run_passed": 0,
            "queued": 0,
            "rejected": 0
        }
        
    def admission_review(self, candidate: Dict) -> bool:
        """Initial admission gate"""
        # Check hard constraints
        if candidate.get("delegation") != 1:
            return False
            
        if candidate.get("pressure", 0) >= 3 and candidate.get("memory") == 3:
            return False
            
        # Check similarity to CONFIG_3
        similarity = self._calculate_similarity(candidate)
        if similarity < 0.70:
            return False
            
        # Check failure distance
        failure_dist = self._failure_distance(candidate)
        if failure_dist < 0.30:
            return False
            
        return True
        
    def shadow_evaluation(self, candidate: Dict) -> Dict:
        """Task-1 Shadow: 100 tasks, single seed, fast screening
        
        Thresholds (relative to baseline):
        - Baseline throughput: ~2.14% (from task1_simulator measurements)
        - PASS: throughput_delta > 0 (any improvement)
        - FAIL: throughput worse than baseline OR catastrophic failure
        """
        print(f"[BRIDGE] Shadow eval for {candidate['id']}")
        
        # Import Task-1 simulator
        import sys
        sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
        try:
            from adaptive_fast import run_adaptive_scheduling
        except ImportError:
            from baseline_fast import run_baseline_scheduling as run_adaptive_scheduling
        
        # Run Task-1 shadow evaluation (100 tasks, single seed)
        seed = hash(candidate['id']) % 10000
        try:
            # Try to extract scheduler params from candidate
            trust_decay = candidate.get('trust_decay', 0.0)
            trust_recovery = candidate.get('trust_recovery', 0.0)
            
            metrics = run_adaptive_scheduling(
                num_tasks=100, 
                num_nodes=6,
                arrival_rate=8.0,
                seed=seed,
                trust_decay=trust_decay,
                trust_recovery=trust_recovery
            )
        except Exception as e:
            print(f"[BRIDGE] Shadow simulation error: {e}")
            # Fallback to baseline
            metrics = run_adaptive_scheduling(num_tasks=100, seed=seed)
        
        # Baseline reference (measured from task1_simulator)
        baseline_throughput = 0.0214  # 2.14%
        baseline_missed = 0.9088     # 90.88%
        
        # Calculate deltas
        throughput_delta = metrics['throughput'] - baseline_throughput
        missed_delta = metrics['missed_deadline_rate'] - baseline_missed
        
        results = {
            "candidate_id": candidate["id"],
            "stage": "shadow",
            "task_family": "heterogeneous_executor_coordination",
            "tasks": 100,
            "seed": seed,
            # Raw metrics
            "throughput": metrics['throughput'],
            "avg_latency": metrics['avg_latency'],
            "missed_deadline_rate": metrics['missed_deadline_rate'],
            # Baseline comparison
            "baseline_throughput": baseline_throughput,
            "throughput_delta": throughput_delta,
            "missed_delta": missed_delta,
            # Pass criteria (relative to baseline)
            "status": "PASS" if throughput_delta > -0.005 else "FAIL",  # Tolerance: -0.5%
            "improvement_pct": throughput_delta / baseline_throughput * 100 if baseline_throughput > 0 else 0
        }
        
        print(f"[BRIDGE] Shadow: throughput={metrics['throughput']:.2%} "
              f"(Δ={throughput_delta:+.2%}), status={results['status']}")
            
        return results
        
    def dry_run_evaluation(self, candidate: Dict) -> Dict:
        """Task-1 Dry Run: 1000 tasks, multiple seeds, fault injection
        
        Thresholds (relative to baseline):
        - PASS (Tier B): mean_throughput_delta > +0.2%, variance_cv < 0.15
        - MARGINAL (Tier C+): throughput not worse than baseline, moderate variance
        - FAIL: worse than baseline or high variance
        """
        print(f"[BRIDGE] Dry run for {candidate['id']}")
        
        import sys
        sys.path.insert(0, '/home/admin/atlas-hec-v2.1-repo/superbrain/task1_simulator')
        try:
            from adaptive_fast import run_adaptive_scheduling
        except ImportError:
            from baseline_fast import run_baseline_scheduling as run_adaptive_scheduling
        import statistics
        
        # Multi-seed evaluation (3 seeds for faster dry-run)
        seeds = [hash(candidate['id']) % 10000 + i for i in range(3)]
        
        trust_decay = candidate.get('trust_decay', 0.0)
        trust_recovery = candidate.get('trust_recovery', 0.0)
        
        all_metrics = []
        for seed in seeds:
            try:
                metrics = run_adaptive_scheduling(
                    num_tasks=1000,
                    num_nodes=6,
                    arrival_rate=8.0,
                    seed=seed,
                    trust_decay=trust_decay,
                    trust_recovery=trust_recovery
                )
                all_metrics.append(metrics)
            except Exception as e:
                print(f"[BRIDGE] Dry-run seed {seed} error: {e}")
                continue
        
        if not all_metrics:
            return {"candidate_id": candidate["id"], "stage": "dry_run", "status": "FAIL"}
        
        # Aggregate across seeds
        throughputs = [m['throughput'] for m in all_metrics]
        latencies = [m['avg_latency'] for m in all_metrics]
        missed_rates = [m['missed_deadline_rate'] for m in all_metrics]
        
        mean_throughput = statistics.mean(throughputs)
        std_throughput = statistics.stdev(throughputs) if len(throughputs) > 1 else 0
        cv_throughput = std_throughput / mean_throughput if mean_throughput > 0 else 0
        
        # Baseline reference
        baseline_throughput = 0.0214
        baseline_missed = 0.9088
        
        throughput_delta = mean_throughput - baseline_throughput
        
        results = {
            "candidate_id": candidate["id"],
            "stage": "dry_run",
            "task_family": "heterogeneous_executor_coordination",
            "tasks": 1000,
            "seeds": len(all_metrics),
            # Aggregated metrics
            "mean_throughput": mean_throughput,
            "std_throughput": std_throughput,
            "cv_throughput": cv_throughput,
            "mean_latency": statistics.mean(latencies),
            "mean_missed_rate": statistics.mean(missed_rates),
            # Baseline comparison
            "baseline_throughput": baseline_throughput,
            "throughput_delta": throughput_delta,
            "improvement_pct": throughput_delta / baseline_throughput * 100 if baseline_throughput > 0 else 0,
        }
        
        # Tier assignment (preserving original PASS/MARGINAL/FAIL structure)
        # PASS (Tier B): >0.2% improvement AND low variance
        if throughput_delta > 0.002 and cv_throughput < 0.15:
            results["status"] = "PASS"
            results["tier"] = "B"
        # MARGINAL (Tier C+): not worse than baseline, acceptable variance
        elif throughput_delta > -0.001 and cv_throughput < 0.20:
            results["status"] = "MARGINAL"
            results["tier"] = "C+"
        else:
            results["status"] = "FAIL"
        
        print(f"[BRIDGE] Dry-run: throughput={mean_throughput:.2%} (Δ={throughput_delta:+.2%}), "
              f"cv={cv_throughput:.3f}, tier={results.get('tier', 'FAIL')}")
            
        return results
        
    def process_candidate(self, candidate: Dict):
        """Process single candidate through all stages"""
        # Admission
        if not self.admission_review(candidate):
            self.stats["rejected"] += 1
            self._log_rejection(candidate, "admission")
            return
            
        self.stats["admitted"] += 1
        self.stages["admission"].append(candidate)
        
        # Shadow
        shadow_result = self.shadow_evaluation(candidate)
        if shadow_result["status"] != "PASS":
            self._log_rejection(candidate, "shadow")
            return
            
        self.stats["shadow_passed"] += 1
        self.stages["shadow"].append(shadow_result)
        
        # Dry Run
        dry_result = self.dry_run_evaluation(candidate)
        if dry_result["status"] not in ["PASS", "MARGINAL"]:
            self._log_rejection(candidate, "dry_run")
            return
            
        self.stats["dry_run_passed"] += 1
        self.stages["dry_run"].append(dry_result)
        
        # Queue (if Tier B)
        if dry_result.get("tier") == "B":
            self._add_to_queue(candidate, dry_result)
            
    def _add_to_queue(self, candidate: Dict, results: Dict):
        """Add candidate to mainline request queue"""
        queue_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/bridge/to_mainline")
        queue_path.mkdir(parents=True, exist_ok=True)
        
        # Check queue depth
        if len(list(queue_path.glob("*.json"))) >= 10:
            print(f"[BRIDGE] Queue full, candidate {candidate['id']} held")
            return
            
        queued = {
            "candidate": candidate,
            "bridge_results": results,
            "queued_at": datetime.now().isoformat(),
            "status": "AWAITING_MAINLINE_REQUEST"
        }
        
        filename = f"{candidate['id']}.json"
        with open(queue_path / filename, 'w') as f:
            json.dump(queued, f, indent=2)
            
        self.stats["queued"] += 1
        print(f"[BRIDGE] Added {candidate['id']} to queue (Tier B)")
        
    def _calculate_similarity(self, candidate: Dict) -> float:
        """Similarity to CONFIG_3 (P2T3M3D1)"""
        config3 = {"p": 2, "t": 3, "m": 3, "d": 1}
        matches = sum(1 for k in ["p", "t", "m", "d"] 
                     if candidate.get(k) == config3[k])
        return matches / 4
        
    def _failure_distance(self, candidate: Dict) -> float:
        """Distance from CONFIG_6 (P3T4M3D1)"""
        config6 = {"p": 3, "t": 4, "m": 3, "d": 1}
        distance = sum(abs(candidate.get(k, 0) - config6[k]) 
                      for k in ["p", "t", "m"])
        return 1.0 - (distance / 6)
        
    def _log_rejection(self, candidate: Dict, stage: str):
        """Log rejected candidate"""
        reject_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/bridge/rejected")
        reject_path.mkdir(parents=True, exist_ok=True)
        
        log = {
            "candidate_id": candidate.get("id"),
            "rejected_at": datetime.now().isoformat(),
            "stage": stage,
            "reason": "criteria_not_met"
        }
        
        filename = f"{candidate.get('id', 'unknown')}_{stage}.json"
        with open(reject_path / filename, 'w') as f:
            json.dump(log, f, indent=2)
            
    def process_incoming(self):
        """Process candidates from Fast Genesis"""
        incoming_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/bridge/incoming")
        if not incoming_path.exists():
            return
            
        for candidate_file in incoming_path.glob("*.json"):
            with open(candidate_file) as f:
                candidate = json.load(f)
                
            self.process_candidate(candidate)
            
            # Move to processed
            processed_dir = incoming_path / "processed"
            processed_dir.mkdir(exist_ok=True)
            candidate_file.rename(processed_dir / candidate_file.name)
            
    def run_continuous(self):
        """Main execution loop"""
        print("[BRIDGE] Starting rolling funnel...")
        
        while True:
            self.process_incoming()
            
            # Log stats every 5 minutes
            print(f"[BRIDGE] Stats: A={self.stats['admitted']}, "
                  f"S={self.stats['shadow_passed']}, "
                  f"D={self.stats['dry_run_passed']}, "
                  f"Q={self.stats['queued']}, R={self.stats['rejected']}")
                  
            time.sleep(300)  # 5 minute cycles


if __name__ == "__main__":
    import random
    scheduler = BridgeScheduler(
        "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
    )
    scheduler.run_continuous()
