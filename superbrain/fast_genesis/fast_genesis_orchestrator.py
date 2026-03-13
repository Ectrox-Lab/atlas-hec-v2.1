#!/usr/bin/env python3
"""
Fast Genesis Orchestrator - Time-Compressed Evolution Engine

Real: 1 second = Simulated: 1 year+
Implements: event-driven, epoch-skip, surrogate-filter, lineage-compression
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class TimeCompressionEngine:
    """Handles multiscale time: tick → epoch → era"""
    
    def __init__(self, compression_ratio: float = 31536000.0):  # 1 sec = 1 year
        self.compression_ratio = compression_ratio
        self.mode = "tick"  # tick, epoch, era
        self.stability_counter = 0
        self.epoch_threshold = 1000
        self.era_threshold = 10000
        
    def step(self, events_detected: bool = False) -> str:
        """Determine time scale based on system activity"""
        if events_detected:
            self.stability_counter = 0
            self.mode = "tick"
            return "tick"
        
        self.stability_counter += 1
        
        if self.stability_counter > self.era_threshold:
            self.mode = "era"
            return "era"  # 1 era = 10000 ticks compressed
        elif self.stability_counter > self.epoch_threshold:
            self.mode = "epoch"
            return "epoch"  # 1 epoch = 1000 ticks compressed
        else:
            self.mode = "tick"
            return "tick"
    
    def get_effective_ticks(self, time_mode: str) -> int:
        """Return how many ticks this step represents"""
        return {
            "tick": 1,
            "epoch": 1000,
            "era": 10000
        }.get(time_mode, 1)


class EventDetector:
    """Detects critical events that require fine-grained simulation"""
    
    CRITICAL_EVENTS = [
        "drift_crossing",
        "policy_violation", 
        "delegation_collapse",
        "recovery_failure",
        "lineage_bifurcation",
        "fitness_breakthrough",
        "archetype_proximity_alert"
    ]
    
    def __init__(self, thresholds: Dict):
        self.thresholds = thresholds
        self.event_history = []
        
    def check(self, candidate_state: Dict) -> Tuple[bool, List[str]]:
        """Check if candidate triggers critical events"""
        events = []
        
        # Drift crossing
        if candidate_state.get("drift", 0) > self.thresholds.get("drift_critical", 0.40):
            events.append("drift_crossing")
            
        # Policy violation
        if candidate_state.get("delegation") != 1:
            events.append("policy_violation")
        if candidate_state.get("pressure", 0) >= 3 and candidate_state.get("memory") == 3:
            events.append("policy_violation")
            
        # Archetype proximity
        if candidate_state.get("failure_distance", 1.0) < 0.30:
            events.append("archetype_proximity_alert")
            
        # Recovery failure
        if candidate_state.get("recovery_effectiveness", 1.0) < 0.5:
            events.append("recovery_failure")
            
        return len(events) > 0, events


class SurrogateFitnessModel:
    """Cheap proxy evaluator - 99% candidates die here"""
    
    def __init__(self, akashic_priors: Dict):
        self.priors = akashic_priors
        self.threshold = 0.85
        
    def evaluate(self, candidate: Dict) -> float:
        """Fast prediction of candidate quality (0-1)"""
        score = 0.0
        
        # Structural similarity to known good configs
        sim_to_p_alpha = self._calculate_similarity(candidate, "P-ALPHA")
        score += sim_to_p_alpha * 0.3
        
        # Distance from failure archetype
        dist_from_config6 = self._failure_distance(candidate)
        score += dist_from_config6 * 0.3
        
        # Policy compliance
        if candidate.get("delegation") == 1:
            score += 0.2
        if not (candidate.get("pressure", 0) >= 3 and candidate.get("memory") == 3):
            score += 0.2
            
        return min(1.0, score)
    
    def _calculate_similarity(self, candidate: Dict, parent_id: str) -> float:
        """Calculate genome similarity to parent"""
        parent = self.priors.get(parent_id, {})
        # Simplified similarity
        matches = 0
        total = 0
        for key in ["pressure", "perturbation", "memory", "delegation"]:
            if candidate.get(key) == parent.get(key):
                matches += 1
            total += 1
        return matches / total if total > 0 else 0
    
    def _failure_distance(self, candidate: Dict) -> float:
        """Calculate distance from CONFIG_6 (P3T4M3D1)"""
        failure_signature = {"pressure": 3, "perturbation": 4, "memory": 3, "delegation": 1}
        
        distance = 0
        for key in ["pressure", "perturbation", "memory"]:
            distance += abs(candidate.get(key, 0) - failure_signature[key])
        
        # Normalize to 0-1
        max_distance = 6  # Max possible difference
        return 1.0 - (distance / max_distance)
    
    def filter_batch(self, candidates: List[Dict]) -> List[Dict]:
        """Filter candidates - only top 10% survive"""
        scored = [(c, self.evaluate(c)) for c in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        cutoff = max(1, len(scored) // 10)  # Top 10%
        survivors = scored[:cutoff]
        
        return [c for c, score in survivors if score >= self.threshold]


class LineageCompressor:
    """Merges highly similar lineages to reduce computational load"""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.threshold = similarity_threshold
        
    def compress(self, lineages: List[Dict]) -> List[Dict]:
        """Merge lineages that are phenotypically equivalent"""
        compressed = []
        merged_ids = set()
        
        for i, lineage_a in enumerate(lineages):
            if i in merged_ids:
                continue
                
            # Find similar lineages
            similar = [lineage_a]
            for j, lineage_b in enumerate(lineages[i+1:], start=i+1):
                if j in merged_ids:
                    continue
                if self._phenotypic_similarity(lineage_a, lineage_b) > self.threshold:
                    similar.append(lineage_b)
                    merged_ids.add(j)
                    
            # Merge into representative
            representative = self._merge_lineages(similar)
            compressed.append(representative)
            
        return compressed
    
    def _phenotypic_similarity(self, a: Dict, b: Dict) -> float:
        """Compare lineage phenotypes"""
        keys = ["mean_drift", "variance", "recovery_pattern", "policy_signature"]
        matches = sum(1 for k in keys if abs(a.get(k, 0) - b.get(k, 0)) < 0.1)
        return matches / len(keys)
    
    def _merge_lineages(self, lineages: List[Dict]) -> Dict:
        """Create representative from merged group"""
        representative = lineages[0].copy()
        representative["merged_count"] = len(lineages)
        representative["merged_ids"] = [l.get("id") for l in lineages]
        return representative


class FastGenesisOrchestrator:
    """Main orchestrator for time-compressed evolution"""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.time_engine = TimeCompressionEngine(
            compression_ratio=self.config["time_scales"]["fast_genesis"].get("compression_ratio", 31536000)
        )
        self.event_detector = EventDetector({
            "drift_critical": 0.40,
            "drift_warning": 0.30
        })
        self.surrogate = SurrogateFitnessModel({
            "P-ALPHA": {"pressure": 2, "perturbation": 3, "memory": 3, "delegation": 1},
            "P-BETA": {"pressure": 2, "perturbation": 3, "memory": 1, "delegation": 1},
            "P-GAMMA": {"pressure": 3, "perturbation": 4, "memory": 1, "delegation": 1}
        })
        self.compressor = LineageCompressor(similarity_threshold=0.95)
        
        self.lineages = []
        self.generation = 0
        self.candidates_emitted = 0
        self.start_time = datetime.now()
        
    def initialize_lineages(self):
        """Create initial 9 parallel lineages"""
        base_configs = [
            ("stable_plus_a", "P-ALPHA", 1.0),
            ("stable_plus_b", "P-ALPHA", 0.9),
            ("stable_plus_c", "P-ALPHA", 0.8),
            ("balanced_memory_a", ["P-ALPHA", "P-BETA"], [0.6, 0.4]),
            ("balanced_memory_b", ["P-ALPHA", "P-BETA"], [0.5, 0.5]),
            ("balanced_memory_c", ["P-ALPHA", "P-BETA"], [0.4, 0.6]),
            ("resilient_hybrid_a", ["P-ALPHA", "P-GAMMA"], [0.8, 0.2]),
            ("resilient_hybrid_b", ["P-ALPHA", "P-GAMMA"], [0.7, 0.3]),
            ("resilient_hybrid_c", ["P-ALPHA", "P-GAMMA"], [0.6, 0.4]),
        ]
        
        for lid, parents, weights in base_configs:
            lineage = {
                "id": lid,
                "parents": parents if isinstance(parents, list) else [parents],
                "weights": weights if isinstance(weights, list) else [weights],
                "population": [],
                "generation": 0,
                "fitness_history": [],
                "status": "ACTIVE"
            }
            self.lineages.append(lineage)
            
        print(f"[FAST_GENESIS] Initialized {len(self.lineages)} lineages")
        
    def evolve_generation(self):
        """One compressed generation step"""
        self.generation += 1
        
        for lineage in self.lineages:
            if lineage["status"] != "ACTIVE":
                continue
                
            # Generate candidates
            candidates = self._generate_candidates(lineage, count=64)
            
            # Surrogate filter - 99% die here
            survivors = self.surrogate.filter_batch(candidates)
            
            # Event detection for time compression
            for candidate in survivors:
                has_events, events = self.event_detector.check(candidate)
                time_mode = self.time_engine.step(has_events)
                effective_ticks = self.time_engine.get_effective_ticks(time_mode)
                candidate["time_mode"] = time_mode
                candidate["effective_ticks"] = effective_ticks
                
            lineage["population"] = survivors
            lineage["generation"] = self.generation
            
            # Check convergence
            if len(survivors) < 3:
                lineage["status"] = "CONVERGED"
                
        # Compress similar lineages
        if self.generation % 5 == 0:
            self.lineages = self.compressor.compress(self.lineages)
            
    def _generate_candidates(self, lineage: Dict, count: int) -> List[Dict]:
        """Generate candidate offspring"""
        candidates = []
        for i in range(count):
            candidate = {
                "id": f"{lineage['id']}_g{self.generation}_c{i}",
                "lineage": lineage["id"],
                "generation": self.generation,
                "pressure": 2,  # Locked to P2 for first wave
                "perturbation": 3,
                "memory": random.choice([2, 3]),  # M2 or M3
                "delegation": 1,  # D1 locked
                "recovery_threshold": random.uniform(0.5, 2.0),
                "trust_update_rate": random.uniform(0.8, 1.2),
                "fitness": None,
                "status": "GENERATED"
            }
            candidates.append(candidate)
        return candidates
        
    def emit_tier_candidates(self) -> List[Dict]:
        """Extract candidates ready for Bridge admission"""
        tier_b_candidates = []
        
        for lineage in self.lineages:
            for candidate in lineage.get("population", []):
                fitness = self.surrogate.evaluate(candidate)
                if fitness >= 0.90:  # Tier B threshold
                    candidate["fitness"] = fitness
                    candidate["emitted_at"] = datetime.now().isoformat()
                    tier_b_candidates.append(candidate)
                    
        self.candidates_emitted += len(tier_b_candidates)
        return tier_b_candidates
        
    def get_status(self) -> Dict:
        """Return current orchestrator status"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        sim_years = elapsed * self.config["time_scales"]["fast_genesis"].get("compression_ratio", 31536000) / 31536000
        
        return {
            "generation": self.generation,
            "active_lineages": sum(1 for l in self.lineages if l["status"] == "ACTIVE"),
            "converged_lineages": sum(1 for l in self.lineages if l["status"] == "CONVERGED"),
            "candidates_emitted": self.candidates_emitted,
            "real_time_elapsed_sec": elapsed,
            "simulated_years": sim_years,
            "time_compression_ratio": self.config["time_scales"]["fast_genesis"].get("compression_ratio", 31536000)
        }
        
    def run_continuous(self, max_generations: int = 25):
        """Main execution loop"""
        print("[FAST_GENESIS] Starting continuous evolution...")
        
        while self.generation < max_generations:
            self.evolve_generation()
            
            # Every 5 generations, emit candidates to Bridge
            if self.generation % 5 == 0:
                candidates = self.emit_tier_candidates()
                if candidates:
                    self._send_to_bridge(candidates)
                    
            # Log status
            if self.generation % 10 == 0:
                status = self.get_status()
                print(f"[FAST_GENESIS] Gen {status['generation']}: "
                      f"{status['active_lineages']} active, "
                      f"{status['candidates_emitted']} emitted, "
                      f"{status['simulated_years']:.1f} years simulated")
                      
            time.sleep(0.1)  # Brief pause between generations
            
    def _send_to_bridge(self, candidates: List[Dict]):
        """Send candidates to Bridge queue"""
        bridge_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/bridge/incoming")
        bridge_path.mkdir(parents=True, exist_ok=True)
        
        for candidate in candidates:
            filename = f"{candidate['id']}.json"
            with open(bridge_path / filename, 'w') as f:
                json.dump(candidate, f, indent=2)
                
        print(f"[FAST_GENESIS] Sent {len(candidates)} candidates to Bridge")


if __name__ == "__main__":
    orchestrator = FastGenesisOrchestrator(
        "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
    )
    orchestrator.initialize_lineages()
    orchestrator.run_continuous(max_generations=25)
