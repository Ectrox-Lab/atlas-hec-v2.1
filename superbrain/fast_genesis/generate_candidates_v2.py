#!/usr/bin/env python3
"""
generate_candidates_v2.py - L4-v2 Implementation
Fast Genesis with Mechanism-Level Inheritance + Anti-Leakage Bias

L4-v2 Requirements:
1. Support v2 inheritance package (mechanism-level fields)
2. Anti-leakage penalty (adjustable, not hardcoded)
3. CLI params logged in manifest/generation_log
4. Observable distribution shift when anti-leakage enabled
"""

import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Candidate:
    """Candidate configuration"""
    id: str
    pressure: int
    perturbation: int
    memory: int
    delegation: int
    recovery_threshold: float
    trust_update_rate: float
    trust_decay: float
    trust_recovery: float
    migration_threshold: float
    family_id: str
    generation_mode: str
    anti_leakage_penalty: float = 0.0  # NEW: penalty applied
    mechanism_score: float = 0.0  # NEW: mechanism match score
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FamilyRegistryHelper:
    """Helper to calculate family IDs and distances"""
    
    @staticmethod
    def get_family_id(config: Dict) -> str:
        """Extract family ID from config (P/T/M only, ignore D)"""
        p = config.get("pressure", config.get("P", 2))
        t = config.get("perturbation", config.get("T", 3))
        m = config.get("memory", config.get("M", 3))
        return f"F_P{p}T{t}M{m}"
    
    @staticmethod
    def get_core_signature(config: Dict) -> Dict:
        """Get core signature {P, T, M}"""
        return {
            "P": config.get("pressure", config.get("P", 2)),
            "T": config.get("perturbation", config.get("T", 3)),
            "M": config.get("memory", config.get("M", 3))
        }
    
    @staticmethod
    def family_distance(family1: str, family2: str) -> int:
        """Calculate distance between two families"""
        try:
            # Parse F_PxTyMz format
            def parse(fam):
                fam = fam.replace("F_P", "").replace("T", "|").replace("M", "|")
                parts = fam.split("|")
                return int(parts[0]), int(parts[1]), int(parts[2])
            
            p1, t1, m1 = parse(family1)
            p2, t2, m2 = parse(family2)
            
            return abs(p1 - p2) + abs(t1 - t2) + abs(m1 - m2)
        except:
            return 999  # Large distance on error


class InheritancePackageLoaderV2:
    """Load v2 inheritance package (mechanism-level)"""
    
    def __init__(self, package_path: Optional[str]):
        self.package_path = package_path
        self.package_data = None
        self.is_v2 = False
        
        # v2 specific fields
        self.stable_mechanisms = {}
        self.blocked_motifs = []
        self.route_constraints = {}
        self.family_mechanism_map = {}
        self.anti_expansion_hints = {}
        self.generator_priors = {}
        
        if package_path:
            self._load()
    
    def _load(self):
        """Load inheritance package from disk"""
        try:
            with open(self.package_path) as f:
                self.package_data = json.load(f)
            
            # Check if v2 package
            version = self.package_data.get("package_version", "")
            self.is_v2 = "mechanism" in version or "stable_mechanisms" in self.package_data
            
            if self.is_v2:
                # Load v2 fields
                self.stable_mechanisms = self.package_data.get("stable_mechanisms", {})
                self.blocked_motifs = self.package_data.get("blocked_motifs", [])
                self.route_constraints = self.package_data.get("route_constraints", {})
                self.family_mechanism_map = self.package_data.get("family_mechanism_map", {})
                self.anti_expansion_hints = self.package_data.get("anti_expansion_hints", {})
                self.generator_priors = self.package_data.get("generator_priors", {})
                
                print(f"[INHERITANCE-V2] Loaded mechanism-level package: {self.package_path}")
                print(f"[INHERITANCE-V2] Delegation patterns: {len(self.stable_mechanisms.get('delegation_patterns', []))}")
                print(f"[INHERITANCE-V2] Blocked motifs: {len(self.blocked_motifs)}")
                print(f"[INHERITANCE-V2] Route constraints: {list(self.route_constraints.keys())}")
            else:
                # v1 fallback
                self.generator_priors = self.package_data.get("generator_priors", {})
                print(f"[INHERITANCE-V1] Loaded legacy package: {self.package_path}")
            
        except Exception as e:
            print(f"[WARNING] Failed to load inheritance package: {e}")
            self.package_data = None
    
    def is_loaded(self) -> bool:
        return self.package_data is not None
    
    def get_stable_families(self) -> List[str]:
        """Get list of stable families from mechanism map"""
        return list(self.family_mechanism_map.keys())


class AntiLeakageBias:
    """
    Anti-leakage bias calculator (L4-v2)
    
    Penalizes candidates that:
    1. Are too far from known stable families
    2. Use untested parameter ranges (P1, P4, T2, T5, etc.)
    3. Introduce novel motifs without historical support
    """
    
    def __init__(self, inheritance_loader: InheritancePackageLoaderV2, config: Dict):
        self.inheritance = inheritance_loader
        self.strength = config.get("strength", 0.0)
        self.max_family_distance = config.get("max_family_distance", 1)
        self.prefer_stable_paths = config.get("prefer_stable_paths", True)
        self.penalize_expansion = config.get("penalize_expansion", True)
        
        # Cache stable families
        self.stable_families = inheritance_loader.get_stable_families() if inheritance_loader.is_loaded() else []
        self.family_helper = FamilyRegistryHelper()
    
    def calculate_penalty(self, candidate: Dict) -> Tuple[float, Dict]:
        """
        Calculate anti-leakage penalty for a candidate
        
        Returns:
            (penalty_score, log_dict)
        """
        if self.strength == 0.0 or not self.inheritance.is_loaded():
            return 0.0, {"applied": False}
        
        penalty = 0.0
        reasons = []
        
        family = candidate.get("family_id", "")
        p = candidate.get("pressure", 2)
        t = candidate.get("perturbation", 3)
        m = candidate.get("memory", 3)
        
        # 1. Family distance penalty
        if self.stable_families:
            min_dist = min(
                self.family_helper.family_distance(family, sf)
                for sf in self.stable_families
            )
            
            if min_dist > self.max_family_distance:
                dist_penalty = self.strength * (min_dist - self.max_family_distance) * 0.2
                penalty += dist_penalty
                reasons.append(f"family_distance:{min_dist}(>{self.max_family_distance})")
        
        # 2. Parameter range penalty (from route_constraints)
        constraints = self.inheritance.route_constraints
        
        if constraints:
            p_range = constraints.get("pressure_range", {}).get("optimal", [2, 3])
            t_range = constraints.get("triage_range", {}).get("optimal", [3, 4])
            
            if p not in p_range:
                penalty += self.strength * 0.15
                reasons.append(f"pressure:{p} not in {p_range}")
            
            if t not in t_range:
                penalty += self.strength * 0.10
                reasons.append(f"triage:{t} not in {t_range}")
        
        # 3. Anti-expansion hints penalty
        hints = self.inheritance.anti_expansion_hints
        if hints and self.penalize_expansion:
            untested_p = hints.get("untested_pressure", [])
            untested_t = hints.get("untested_triage", [])
            penalty_per_step = hints.get("penalty_per_step", 0.15)
            
            if p in untested_p:
                penalty += penalty_per_step * self.strength
                reasons.append(f"untested_pressure:{p}")
            
            if t in untested_t:
                penalty += penalty_per_step * self.strength
                reasons.append(f"untested_triage:{t}")
        
        # Cap penalty
        penalty = min(penalty, 0.8)
        
        log = {
            "applied": True,
            "penalty": round(penalty, 4),
            "strength": self.strength,
            "reasons": reasons,
            "family": family,
            "min_family_distance": min_dist if self.stable_families else None
        }
        
        return penalty, log


class CandidateGeneratorV2:
    """L4-v2 Candidate generator with mechanism bias + anti-leakage"""
    
    BASELINE_RANGES = {
        "pressure": [2, 3],
        "perturbation": [3, 4],
        "memory": [2, 3, 4],
        "delegation": [1],
        "recovery_threshold": [0.5, 2.0],
        "trust_update_rate": [0.8, 1.2],
        "trust_decay": [0.0, 0.2],
        "trust_recovery": [0.0, 0.1],
        "migration_threshold": [0.1, 0.5]
    }
    
    def __init__(
        self,
        inheritance_loader: Optional[InheritancePackageLoaderV2] = None,
        bias_strength: float = 0.0,
        anti_leakage_config: Optional[Dict] = None,
        seed: int = 42
    ):
        self.inheritance = inheritance_loader
        self.bias_strength = bias_strength
        self.seed = seed
        self.random = random.Random(seed)
        self.family_helper = FamilyRegistryHelper()
        
        # Initialize anti-leakage bias
        if anti_leakage_config and inheritance_loader:
            self.anti_leakage = AntiLeakageBias(inheritance_loader, anti_leakage_config)
        else:
            self.anti_leakage = None
        
        # Tracking
        self.generation_log = []
        self.family_counts = {}
        self.anti_leakage_stats = {"applied": 0, "total_penalty": 0.0}
    
    def _calculate_mechanism_score(self, family_id: str) -> float:
        """Score based on match to stable mechanisms (v2)"""
        if not self.inheritance or not self.inheritance.is_v2:
            return 0.5  # Neutral for v1 packages
        
        # Check if family is in mechanism map
        fam_map = self.inheritance.family_mechanism_map
        if family_id in fam_map:
            return fam_map[family_id].get("stability_score", 0.8)
        
        # Check distance to stable families
        stable_fams = self.inheritance.get_stable_families()
        if stable_fams:
            min_dist = min(
                self.family_helper.family_distance(family_id, sf)
                for sf in stable_fams
            )
            # Score decays with distance
            return max(0.1, 0.8 - min_dist * 0.2)
        
        return 0.3  # Unknown family
    
    def generate_single(self, idx: int) -> Candidate:
        """Generate a single candidate with v2 scoring"""
        
        # Select core parameters
        p = self.random.choice(self.BASELINE_RANGES["pressure"])
        t = self.random.choice(self.BASELINE_RANGES["perturbation"])
        m = self.random.choice(self.BASELINE_RANGES["memory"])
        d = 1
        
        # Bias toward stable mechanisms if v2
        if self.inheritance and self.inheritance.is_v2 and self.bias_strength > 0:
            if self.random.random() < self.bias_strength:
                # Pick from stable families
                stable = self.inheritance.get_stable_families()
                if stable:
                    target_fam = self.random.choice(stable)
                    try:
                        sig = self.inheritance.family_mechanism_map[target_fam]["route_signature"]
                        p = max(1, min(4, sig.get("P", p) + self.random.choice([-1, 0, 0, 0, 1])))
                        t = max(1, min(5, sig.get("T", t) + self.random.choice([-1, 0, 0, 0, 1])))
                        m = max(1, min(5, sig.get("M", m) + self.random.choice([-1, 0, 0, 0, 1])))
                    except:
                        pass
        
        family_id = f"F_P{p}T{t}M{m}"
        
        # Calculate mechanism score
        mech_score = self._calculate_mechanism_score(family_id)
        
        # Create candidate
        trust_decay = self.random.uniform(*self.BASELINE_RANGES["trust_decay"])
        trust_recovery = self.random.uniform(*self.BASELINE_RANGES["trust_recovery"])
        
        candidate = Candidate(
            id=f"C{idx:04d}_{family_id}",
            pressure=p,
            perturbation=t,
            memory=m,
            delegation=d,
            recovery_threshold=round(self.random.uniform(0.5, 2.0), 4),
            trust_update_rate=round(self.random.uniform(0.8, 1.2), 4),
            trust_decay=round(trust_decay, 4),
            trust_recovery=round(trust_recovery, 4),
            migration_threshold=round(self.random.uniform(0.1, 0.5), 4),
            family_id=family_id,
            generation_mode="mechanism_biased_v2" if (self.inheritance and self.inheritance.is_v2) else "uniform_exploration",
            mechanism_score=round(mech_score, 4)
        )
        
        # Apply anti-leakage penalty
        if self.anti_leakage:
            penalty, log = self.anti_leakage.calculate_penalty(candidate.to_dict())
            candidate.anti_leakage_penalty = round(penalty, 4)
            
            if log["applied"]:
                self.anti_leakage_stats["applied"] += 1
                self.anti_leakage_stats["total_penalty"] += penalty
        
        # Log generation
        self.generation_log.append({
            "idx": idx,
            "family_id": family_id,
            "core_signature": {"P": p, "T": t, "M": m},
            "mechanism_score": round(mech_score, 4),
            "anti_leakage_penalty": round(candidate.anti_leakage_penalty, 4),
            "anti_leakage_reasons": log.get("reasons", []) if self.anti_leakage else []
        })
        
        self.family_counts[family_id] = self.family_counts.get(family_id, 0) + 1
        
        return candidate
    
    def generate_batch(self, count: int) -> List[Candidate]:
        """Generate batch with optional anti-leakage filtering"""
        candidates = []
        attempts = 0
        max_attempts = count * 3  # Allow extra attempts if anti-leakage is strong
        
        while len(candidates) < count and attempts < max_attempts:
            candidate = self.generate_single(attempts)
            
            # If anti-leakage is strong, probabilistically reject high-penalty candidates
            if self.anti_leakage and self.anti_leakage.strength > 0:
                # Acceptance probability: 1 - penalty
                if self.random.random() < (1 - candidate.anti_leakage_penalty):
                    candidates.append(candidate)
            else:
                candidates.append(candidate)
            
            attempts += 1
        
        # Fill remaining with low-penalty candidates if needed
        while len(candidates) < count:
            candidate = self.generate_single(attempts)
            if candidate.anti_leakage_penalty < 0.3:  # Prefer low penalty
                candidates.append(candidate)
            attempts += 1
        
        return candidates[:count]
    
    def get_family_distribution(self) -> Dict:
        """Get distribution with anti-leakage stats"""
        total = sum(self.family_counts.values())
        if total == 0:
            return {}
        
        return {
            family: {
                "count": count,
                "percentage": round(count / total * 100, 2)
            }
            for family, count in sorted(
                self.family_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate candidates for Fast Genesis (L4-v2)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
L4-v2 - Mechanism-Level Inheritance + Anti-Leakage:
  --inheritance-package PATH      Load v2 mechanism-level package
  --bias-strength FLOAT           Mechanism bias strength (default: 0.6)
  --anti-leakage-strength FLOAT   Anti-leakage penalty (default: 0.4)
  --max-family-distance INT       Max allowed family distance (default: 1)
  --prefer-stable-paths           Prefer stable mechanism paths
  --penalize-unjustified-expansion  Penalize novel structural expansion

Examples:
  # Round A: Pure exploration
  python generate_candidates_v2.py --count 50 --output round_a/

  # Round B: Mechanism bias + anti-leakage
  python generate_candidates_v2.py --count 50 \\
      --inheritance-package task1_inheritance_package_v2.json \\
      --bias-strength 0.6 \\
      --anti-leakage-strength 0.4 \\
      --max-family-distance 1 \\
      --prefer-stable-paths \\
      --penalize-unjustified-expansion \\
      --output round_b/

  # Ablation: Zero bias
  python generate_candidates_v2.py --count 50 \\
      --inheritance-package task1_inheritance_package_v2.json \\
      --bias-strength 0.0 \\
      --anti-leakage-strength 0.0 \\
      --output round_ablation/
"""
    )
    
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--task-family", type=str, default="task1")
    parser.add_argument("--inheritance-package", type=str, default=None)
    parser.add_argument("--bias-strength", type=float, default=0.6)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--seed", type=int, default=42)
    
    # L4-v2 NEW: Anti-leakage parameters
    parser.add_argument("--anti-leakage-strength", type=float, default=0.0,
                        help="Anti-leakage penalty strength 0.0-1.0 (default: 0.0)")
    parser.add_argument("--max-family-distance", type=int, default=1,
                        help="Maximum allowed distance from stable families (default: 1)")
    parser.add_argument("--prefer-stable-paths", action="store_true",
                        help="Prefer candidates from stable mechanism paths")
    parser.add_argument("--penalize-unjustified-expansion", action="store_true",
                        help="Penalize novel structural expansion")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("FAST GENESIS V2 - L4-v2 Candidate Generation")
    print("=" * 70)
    print(f"Task Family: {args.task_family}")
    print(f"Count: {args.count}")
    print(f"Seed: {args.seed}")
    print(f"Output: {args.output}")
    
    # Load inheritance
    inheritance_loader = None
    if args.inheritance_package:
        print(f"\n[INHERITANCE] Loading: {args.inheritance_package}")
        inheritance_loader = InheritancePackageLoaderV2(args.inheritance_package)
        print(f"[INHERITANCE] Loaded: {inheritance_loader.is_loaded()}")
        print(f"[INHERITANCE] Is v2: {inheritance_loader.is_v2}")
        print(f"[INHERITANCE] Mechanism bias: {args.bias_strength}")
    else:
        print("\n[MODE] Uniform exploration (no inheritance)")
        args.bias_strength = 0.0
    
    # Configure anti-leakage
    anti_leakage_config = {
        "strength": args.anti_leakage_strength,
        "max_family_distance": args.max_family_distance,
        "prefer_stable_paths": args.prefer_stable_paths,
        "penalize_expansion": args.penalize_unjustified_expansion
    }
    
    if args.anti_leakage_strength > 0:
        print(f"\n[ANTI-LEAKAGE] Enabled")
        print(f"[ANTI-LEAKAGE] Strength: {args.anti_leakage_strength}")
        print(f"[ANTI-LEAKAGE] Max family distance: {args.max_family_distance}")
        print(f"[ANTI-LEAKAGE] Prefer stable paths: {args.prefer_stable_paths}")
        print(f"[ANTI-LEAKAGE] Penalize expansion: {args.penalize_unjustified_expansion}")
    
    # Create generator
    generator = CandidateGeneratorV2(
        inheritance_loader=inheritance_loader,
        bias_strength=args.bias_strength,
        anti_leakage_config=anti_leakage_config if args.anti_leakage_strength > 0 else None,
        seed=args.seed
    )
    
    # Generate
    print(f"\n[GENERATION] Generating {args.count} candidates...")
    candidates = generator.generate_batch(args.count)
    
    # Create output
    output_path = Path(args.output)
    candidates_dir = output_path / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    
    # Save candidates
    for candidate in candidates:
        with open(candidates_dir / f"{candidate.id}.json", 'w') as f:
            json.dump(candidate.to_dict(), f, indent=2)
    
    # Generate manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "generation_config": {
            "count": args.count,
            "task_family": args.task_family,
            "seed": args.seed,
            "bias_strength": args.bias_strength,
            "anti_leakage_strength": args.anti_leakage_strength,
            "max_family_distance": args.max_family_distance,
            "prefer_stable_paths": args.prefer_stable_paths,
            "penalize_unjustified_expansion": args.penalize_unjustified_expansion
        },
        "inheritance_metadata": {
            "package_loaded": inheritance_loader.is_loaded() if inheritance_loader else False,
            "package_is_v2": inheritance_loader.is_v2 if inheritance_loader else False,
            "package_path": args.inheritance_package
        },
        "anti_leakage_stats": generator.anti_leakage_stats if generator.anti_leakage else {"applied": 0},
        "output_files": {
            "manifest": "manifest.json",
            "family_distribution": "family_distribution.json",
            "generation_log": "generation_log.json",
            "candidates_dir": "candidates/"
        }
    }
    
    with open(output_path / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Family distribution
    family_dist = generator.get_family_distribution()
    with open(output_path / "family_distribution.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_candidates": args.count,
            "family_distribution": family_dist
        }, f, indent=2)
    
    # Generation log
    with open(output_path / "generation_log.json", 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation_log": generator.generation_log
        }, f, indent=2)
    
    # Summary
    print("\n" + "=" * 70)
    print("GENERATION SUMMARY")
    print("=" * 70)
    print(f"Total candidates: {args.count}")
    print(f"Unique families: {len(family_dist)}")
    print(f"\nTop families:")
    for fam, data in list(family_dist.items())[:5]:
        print(f"  {fam}: {data['count']} ({data['percentage']}%)")
    
    if generator.anti_leakage and generator.anti_leakage_stats["applied"] > 0:
        print(f"\nAnti-leakage applied: {generator.anti_leakage_stats['applied']} candidates")
        print(f"Total penalty: {generator.anti_leakage_stats['total_penalty']:.4f}")
        
        # Count penalties by reason
        penalties_by_reason = {}
        for log in generator.generation_log:
            for reason in log.get("anti_leakage_reasons", []):
                penalties_by_reason[reason] = penalties_by_reason.get(reason, 0) + 1
        
        if penalties_by_reason:
            print("Penalty reasons:")
            for reason, count in sorted(penalties_by_reason.items(), key=lambda x: x[1], reverse=True):
                print(f"  {reason}: {count}")
    
    print(f"\nMode: {candidates[0].generation_mode if candidates else 'unknown'}")
    print("=" * 70)
    print("✓ L4-v2 Candidate Generation Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
