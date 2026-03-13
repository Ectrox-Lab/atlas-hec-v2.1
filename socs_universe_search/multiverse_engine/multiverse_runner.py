#!/usr/bin/env python3
"""
Multiverse Runner - 128 Parallel Universes with Akashic Memory
P2.5 Surprise Search Lane Core Engine
"""

import json
import random
import math
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

# ============ Configuration ============
MAX_UNIVERSES = 128
MAX_AGENTS = 5000
GRID_SIZE = (25, 25, 8)

# Stress profile distribution
STRESS_DISTRIBUTION = {
    "ResourceScarcity": 0.20,
    "FailureBurst": 0.20,
    "HighCoordinationDemand": 0.20,
    "RegimeShiftFrequent": 0.15,
    "SyncRiskHigh": 0.15,
    "StableLowStress": 0.10,
}

# ============ Structure DNA ============
@dataclass
class StructureDNA:
    """8-dimensional structure parameter space"""
    local_autonomy: float      # 0.1-0.9
    broadcast_sparsity: float  # 0.01-0.20
    division_strength: float   # 0.0-0.8
    lineage_bias: float        # 0.0-0.5
    culling_style: str         # soft/hard/none
    memory_gating: str         # L1/L2/L3/mixed
    hierarchy_depth: int       # 0-4
    coupling_topology: str     # small_world/random/regular
    
    def signature(self) -> str:
        """Generate unique signature for this DNA"""
        params = f"{self.local_autonomy:.3f}_{self.broadcast_sparsity:.3f}_{self.division_strength:.3f}"
        return hashlib.md5(params.encode()).hexdigest()[:12]
    
    def to_family_name(self) -> str:
        """Auto-generate family name based on dominant traits"""
        traits = []
        if self.local_autonomy > 0.6:
            traits.append("Autonomous")
        if self.division_strength > 0.5:
            traits.append("Divided")
        if self.hierarchy_depth > 2:
            traits.append("Hierarchical")
        if self.culling_style == "hard":
            traits.append("Pruned")
        if self.memory_gating == "L3":
            traits.append("Memorious")
        if self.broadcast_sparsity < 0.05:
            traits.append("Focused")
        
        if not traits:
            return "Emergent_" + self.signature()[:6]
        return "".join(traits) + "_" + self.signature()[:4]


# ============ Akashic Memory ============
class AkashicMemory:
    """
    Cross-Universe Memory System
    Only stores structure summaries, not action answers
    """
    
    def __init__(self):
        self.structure_fitness = {}  # signature -> {stress: cwci}
        self.lineage_mutations = []   # successful mutations
        self.failure_signatures = {}  # failure pattern -> count
        self.emergent_patterns = []   # unexpected behaviors
        self.cross_stress_transfer = {}  # learning transfer between stresses
        
    def record_universe_result(self, dna: StructureDNA, stress: str, 
                               cwci: float, survived: bool,
                               failure_mode: Optional[str] = None):
        """Record a universe run result"""
        sig = dna.signature()
        
        if sig not in self.structure_fitness:
            self.structure_fitness[sig] = {
                "dna": asdict(dna),
                "family": dna.to_family_name(),
                "results": {}
            }
        
        self.structure_fitness[sig]["results"][stress] = {
            "cwci": cwci,
            "survived": survived
        }
        
        if not survived and failure_mode:
            self.failure_signatures[failure_mode] = \
                self.failure_signatures.get(failure_mode, 0) + 1
    
    def find_cross_stress_learners(self) -> List[Dict]:
        """Find structures that transfer learning across stresses"""
        learners = []
        for sig, data in self.structure_fitness.items():
            results = data["results"]
            if len(results) >= 3:
                cwci_values = [r["cwci"] for r in results.values()]
                if min(cwci_values) > 0.55:  # Good across board
                    learners.append({
                        "signature": sig,
                        "family": data["family"],
                        "mean_cwci": sum(cwci_values) / len(cwci_values),
                        "stresses": list(results.keys())
                    })
        return sorted(learners, key=lambda x: x["mean_cwci"], reverse=True)
    
    def get_promising_novelty(self, top_k: int = 5) -> List[Dict]:
        """Get top novel structures not in known families"""
        known_families = {"octopus_like", "bee_like", "ant_like", "worm_like", 
                         "pulse_central", "modular_lattice", "random_sparse"}
        
        novel = []
        for sig, data in self.structure_fitness.items():
            family = data["family"].lower()
            is_known = any(kf in family for kf in known_families)
            
            if not is_known:
                results = data["results"]
                if results:
                    mean_cwci = sum(r["cwci"] for r in results.values()) / len(results)
                    if mean_cwci > 0.60:  # Above threshold
                        novel.append({
                            "signature": sig,
                            "family": data["family"],
                            "mean_cwci": mean_cwci,
                            "dna": data["dna"]
                        })
        
        return sorted(novel, key=lambda x: x["mean_cwci"], reverse=True)[:top_k]
    
    def generate_digest(self) -> Dict:
        """Generate Akashic digest for mainline"""
        return {
            "total_structures_scanned": len(self.structure_fitness),
            "cross_stress_learners": len(self.find_cross_stress_learners()),
            "promising_novelties": len(self.get_promising_novelty(10)),
            "top_failure_modes": sorted(self.failure_signatures.items(), 
                                       key=lambda x: x[1], reverse=True)[:5],
            "lineage_mutations_recorded": len(self.lineage_mutations)
        }


# ============ Universe Simulation ============
def simulate_universe(universe_id: int, dna: StructureDNA, 
                      stress: str, seed: int) -> Dict:
    """
    Simulate a single universe with given DNA and stress
    Simplified physics for P2.5 lane (15% budget)
    """
    random.seed(seed + universe_id)
    
    # Calculate effective parameters based on DNA
    n_units = random.randint(500, MAX_AGENTS)
    
    # CWCI estimation based on DNA + stress interaction
    base_cwci = 0.45  # Baseline
    
    # DNA contribution
    dna_contrib = (
        dna.local_autonomy * 0.15 +
        (1 - dna.broadcast_sparsity) * 0.10 +
        dna.division_strength * 0.08 +
        dna.lineage_bias * 0.05 +
        (dna.hierarchy_depth / 4) * 0.07
    )
    
    # Stress penalty/bonus
    stress_modifiers = {
        "ResourceScarcity": -0.05 if dna.division_strength < 0.3 else 0.05,
        "FailureBurst": 0.08 if dna.local_autonomy > 0.6 else -0.03,
        "HighCoordinationDemand": 0.10 if dna.broadcast_sparsity < 0.08 else -0.08,
        "RegimeShiftFrequent": 0.05 if dna.local_autonomy > 0.5 else -0.05,
        "SyncRiskHigh": -0.05 if dna.coupling_topology == "regular" else 0.03,
        "StableLowStress": 0.02
    }
    
    stress_mod = stress_modifiers.get(stress, 0)
    noise = random.uniform(-0.08, 0.08)
    
    cwci = base_cwci + dna_contrib + stress_mod + noise
    cwci = max(0.0, min(1.0, cwci))
    
    # Determine survival
    survived = cwci > 0.55
    failure_mode = None
    if not survived:
        failure_modes = ["fragmentation", "sync_loss", "resource_depletion", 
                        "coordination_collapse", "memory_overload"]
        failure_mode = random.choice(failure_modes)
    
    return {
        "universe_id": universe_id,
        "dna_signature": dna.signature(),
        "family": dna.to_family_name(),
        "stress": stress,
        "n_units": n_units,
        "cwci": round(cwci, 3),
        "survived": survived,
        "failure_mode": failure_mode,
        "seed": seed
    }


# ============ Multiverse Runner ============
class MultiverseRunner:
    """Main runner for 128 parallel universes"""
    
    def __init__(self, n_universes: int = MAX_UNIVERSES):
        self.n_universes = n_universes
        self.akashic = AkashicMemory()
        self.surprise_candidates = []
        
    def generate_random_dna(self) -> StructureDNA:
        """Generate random DNA from parameter space"""
        culling_styles = ["soft", "hard", "none"]
        memory_gatings = ["L1", "L2", "L3", "mixed"]
        topologies = ["small_world", "random", "regular"]
        
        return StructureDNA(
            local_autonomy=random.uniform(0.1, 0.9),
            broadcast_sparsity=random.uniform(0.01, 0.20),
            division_strength=random.uniform(0.0, 0.8),
            lineage_bias=random.uniform(0.0, 0.5),
            culling_style=random.choice(culling_styles),
            memory_gating=random.choice(memory_gatings),
            hierarchy_depth=random.randint(0, 4),
            coupling_topology=random.choice(topologies)
        )
    
    def run_universe_batch(self, batch_id: int) -> List[Dict]:
        """Run a batch of universes"""
        results = []
        
        for i in range(self.n_universes // 4):  # 4 batches
            universe_id = batch_id * (self.n_universes // 4) + i
            dna = self.generate_random_dna()
            stress = random.choices(
                list(STRESS_DISTRIBUTION.keys()),
                weights=list(STRESS_DISTRIBUTION.values())
            )[0]
            
            result = simulate_universe(universe_id, dna, stress, seed=42)
            results.append((result, dna))
            
        return results
    
    def run_multiverse(self, parallel: bool = True) -> Dict:
        """Run full multiverse sweep"""
        print(f"🌌 Launching {self.n_universes} parallel universes...")
        
        all_results = []
        
        if parallel and mp.cpu_count() > 2:
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.run_universe_batch, i) for i in range(4)]
                for future in as_completed(futures):
                    batch_results = future.result()
                    all_results.extend(batch_results)
        else:
            for i in range(4):
                batch_results = self.run_universe_batch(i)
                all_results.extend(batch_results)
        
        # Record to Akashic
        print("📝 Recording to Akashic Memory...")
        for result, dna in all_results:
            self.akashic.record_universe_result(
                dna, result["stress"], result["cwci"],
                result["survived"], result["failure_mode"]
            )
        
        # Check for surprises
        self._check_surprises()
        
        return self._generate_report()
    
    def _check_surprises(self):
        """Check for surprise candidates"""
        novelties = self.akashic.get_promising_novelty(10)
        cross_learners = self.akashic.find_cross_stress_learners()
        
        self.surprise_candidates = {
            "novel_structures": novelties,
            "cross_stress_learners": cross_learners[:5]
        }
    
    def _generate_report(self) -> Dict:
        """Generate multiverse report"""
        digest = self.akashic.generate_digest()
        
        report = {
            "multiverse_summary": {
                "n_universes": self.n_universes,
                "structures_scanned": digest["total_structures_scanned"],
                "cross_stress_learners": digest["cross_stress_learners"],
                "promising_novelties": digest["promising_novelties"]
            },
            "akashic_digest": digest,
            "surprise_candidates": self.surprise_candidates,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict]:
        """Generate recommendations for mainline"""
        recs = []
        
        novelties = self.surprise_candidates.get("novel_structures", [])
        for novel in novelties[:3]:
            recs.append({
                "type": "SURPRISE_NOMINATION",
                "family": novel["family"],
                "signature": novel["signature"],
                "mean_cwci": novel["mean_cwci"],
                "action": "Consider for P1 challenger validation",
                "priority": "HIGH" if novel["mean_cwci"] > 0.65 else "MEDIUM"
            })
        
        cross_learners = self.surprise_candidates.get("cross_stress_learners", [])
        if cross_learners:
            recs.append({
                "type": "ROBUSTNESS_INSIGHT",
                "finding": f"{len(cross_learners)} structures show cross-stress resilience",
                "action": "Analyze DNA patterns for robust design principles",
                "priority": "MEDIUM"
            })
        
        return recs


# ============ Main Entry ============
if __name__ == "__main__":
    import sys
    
    print("=" * 70)
    print("🌌 SOCS Multiverse Runner - P2.5 Surprise Search Lane")
    print("=" * 70)
    
    runner = MultiverseRunner(n_universes=128)
    report = runner.run_multiverse(parallel=False)  # Sequential for reliability
    
    # Save report
    output_path = "outputs/multiverse_report.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 70)
    print("📊 MULTIVERSE REPORT")
    print("=" * 70)
    
    summary = report["multiverse_summary"]
    print(f"\nUniverses Run: {summary['n_universes']}")
    print(f"Unique Structures: {summary['structures_scanned']}")
    print(f"Cross-Stress Learners: {summary['cross_stress_learners']}")
    print(f"Promising Novelties: {summary['promising_novelties']}")
    
    print("\n🎁 SURPRISE CANDIDATES:")
    for rec in report["recommendations"]:
        if rec["type"] == "SURPRISE_NOMINATION":
            icon = "🔥" if rec["priority"] == "HIGH" else "⭐"
            print(f"  {icon} {rec['family']}: CWCI={rec['mean_cwci']:.3f}")
    
    print(f"\n💾 Full report saved to: {output_path}")
    print("=" * 70)
