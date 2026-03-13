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
        """8 universes, 300 ticks"""
        print(f"[BRIDGE] Shadow eval for {candidate['id']}")
        
        # Simulate shadow run
        results = {
            "candidate_id": candidate["id"],
            "stage": "shadow",
            "universes": 8,
            "ticks": 300,
            "drift": random.uniform(0.18, 0.28),  # Simulated
            "accuracy": random.uniform(0.78, 0.82),
            "critical_events": 0
        }
        
        # Pass criteria
        baseline_drift = 0.25  # P2T3M1D1 baseline
        if results["drift"] <= baseline_drift + 0.02:
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"
            
        return results
        
    def dry_run_evaluation(self, candidate: Dict) -> Dict:
        """16 universes, 1000 ticks"""
        print(f"[BRIDGE] Dry run for {candidate['id']}")
        
        # Simulate dry run
        results = {
            "candidate_id": candidate["id"],
            "stage": "dry_run",
            "universes": 16,
            "repeats": 16,
            "ticks": 1000,
            "drift_mean": random.uniform(0.19, 0.24),
            "accuracy_mean": random.uniform(0.79, 0.81),
            "variance_cv": random.uniform(0.10, 0.14)
        }
        
        # Pass criteria vs CONFIG_3 (0.212 drift)
        config3_drift = 0.212
        if results["drift_mean"] <= config3_drift:
            results["status"] = "PASS"
            results["tier"] = "B"
        elif results["drift_mean"] <= config3_drift + 0.02:
            results["status"] = "MARGINAL"
            results["tier"] = "C+"
        else:
            results["status"] = "FAIL"
            
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
