#!/usr/bin/env python3
"""
generate_candidates.py - S1 Implementation
Fast Genesis Candidate Generation with Inheritance Package Support

S1 Completion Criteria:
1. CLI interface with --inheritance-package, --bias-strength
2. No package = identical behavior to baseline (Round A purity)
3. Manifest records inheritance metadata
4. Observable distribution shift in output files
5. Bias as toggleable layer, not hardcoded
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
    
    def to_dict(self) -> Dict:
        return asdict(self)


class FamilyRegistryHelper:
    """Helper to calculate family IDs from candidate configs"""
    
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


class InheritancePackageLoader:
    """Load and parse inheritance package"""
    
    def __init__(self, package_path: Optional[str]):
        self.package_path = package_path
        self.package_data = None
        self.approved_families = []
        self.blocked_patterns = []
        self.generator_priors = {}
        
        if package_path:
            self._load()
    
    def _load(self):
        """Load inheritance package from disk"""
        try:
            with open(self.package_path) as f:
                self.package_data = json.load(f)
            
            # Extract approved families from generator_priors or delegation patterns
            self.generator_priors = self.package_data.get("generator_priors", {})
            
            # Known good families based on trust_decay_range etc.
            # F_P3T4M4 is the dominant converged family from E-EVO-003
            self.approved_families = ["F_P3T4M4", "F_P2T3M3", "F_P3T4M3"]
            
            # Blocked patterns from avoid_switching_patterns
            self.blocked_patterns = self.package_data.get("avoid_switching_patterns", [])
            
            print(f"[INHERITANCE] Loaded package: {self.package_path}")
            print(f"[INHERITANCE] Generator priors: {self.generator_priors}")
            
        except Exception as e:
            print(f"[WARNING] Failed to load inheritance package: {e}")
            self.package_data = None
    
    def is_loaded(self) -> bool:
        return self.package_data is not None
    
    def get_bias_ranges(self) -> Dict:
        """Get biased parameter ranges for candidate generation"""
        if not self.generator_priors:
            return {}
        
        return {
            "trust_decay": self.generator_priors.get("trust_decay_range", [0.0, 0.2]),
            "trust_recovery": self.generator_priors.get("trust_recovery_range", [0.0, 0.1]),
            "migration_threshold": self.generator_priors.get("migration_threshold_range", [0.1, 0.5])
        }


class CandidateGenerator:
    """Main candidate generator with optional inheritance bias"""
    
    # Baseline default ranges (Round A behavior - frozen)
    BASELINE_RANGES = {
        "pressure": [2, 3],           # P2 or P3
        "perturbation": [3, 4],       # T3 or T4
        "memory": [2, 3, 4],          # M2, M3, M4
        "delegation": [1],            # D1 locked (mandatory constraint)
        "recovery_threshold": [0.5, 2.0],
        "trust_update_rate": [0.8, 1.2],
        "trust_decay": [0.0, 0.2],    # Uniform exploration
        "trust_recovery": [0.0, 0.1],
        "migration_threshold": [0.1, 0.5]
    }
    
    def __init__(
        self,
        inheritance_loader: Optional[InheritancePackageLoader] = None,
        bias_strength: float = 0.0,
        seed: int = 42
    ):
        self.inheritance = inheritance_loader
        self.bias_strength = bias_strength  # 0.0 = pure exploration, 0.7 = biased
        self.seed = seed
        self.random = random.Random(seed)
        self.family_helper = FamilyRegistryHelper()
        
        # Generation tracking for observable output
        self.generation_log = []
        self.family_counts = {}
        
    def _get_param_range(self, param: str) -> List:
        """Get parameter range, potentially biased by inheritance"""
        baseline = self.BASELINE_RANGES.get(param, [0, 1])
        
        # If no inheritance or bias_strength=0, use baseline
        if not self.inheritance or not self.inheritance.is_loaded() or self.bias_strength == 0.0:
            return baseline
        
        # Get inheritance-biased ranges
        bias_ranges = self.inheritance.get_bias_ranges()
        
        if param in bias_ranges:
            # Interpolate between baseline and biased based on bias_strength
            biased = bias_ranges[param]
            return [
                baseline[0] + self.bias_strength * (biased[0] - baseline[0]),
                baseline[1] + self.bias_strength * (biased[1] - baseline[1])
            ]
        
        return baseline
    
    def _select_pressure_triage_memory(self) -> Tuple[int, int, int]:
        """Select P, T, M with optional bias toward approved families"""
        
        # Check if we should bias toward approved families
        if (self.inheritance and self.inheritance.is_loaded() and 
            self.bias_strength > 0.0 and self.random.random() < self.bias_strength):
            
            # Bias toward known good families (e.g., F_P3T4M4)
            approved = self.inheritance.approved_families
            if approved:
                # Parse family ID like "F_P3T4M4" -> (3, 4, 4)
                family = self.random.choice(approved)
                try:
                    parts = family.replace("F_P", "").replace("T", "|").replace("M", "|").split("|")
                    if len(parts) >= 3:
                        p = int(parts[0])
                        t = int(parts[1])
                        m = int(parts[2])
                        
                        # Add small random variation (±1) to maintain diversity
                        p = max(1, min(4, p + self.random.choice([-1, 0, 0, 0, 1])))
                        t = max(1, min(5, t + self.random.choice([-1, 0, 0, 0, 1])))
                        m = max(1, min(5, m + self.random.choice([-1, 0, 0, 0, 1])))
                        
                        return p, t, m
                except (ValueError, IndexError):
                    pass  # Fall through to baseline
        
        # Baseline: uniform exploration
        p = self.random.choice(self.BASELINE_RANGES["pressure"])
        t = self.random.choice(self.BASELINE_RANGES["perturbation"])
        m = self.random.choice(self.BASELINE_RANGES["memory"])
        
        return p, t, m
    
    def generate_single(self, idx: int) -> Candidate:
        """Generate a single candidate"""
        
        # Select core parameters
        p, t, m = self._select_pressure_triage_memory()
        d = 1  # D1 always locked
        
        # Get potentially biased ranges
        trust_decay_range = self._get_param_range("trust_decay")
        trust_recovery_range = self._get_param_range("trust_recovery")
        migration_range = self._get_param_range("migration_threshold")
        
        # Generate parameters
        trust_decay = self.random.uniform(*trust_decay_range)
        trust_recovery = self.random.uniform(*trust_recovery_range)
        migration_threshold = self.random.uniform(*migration_range)
        
        recovery_threshold = self.random.uniform(*self.BASELINE_RANGES["recovery_threshold"])
        trust_update_rate = self.random.uniform(*self.BASELINE_RANGES["trust_update_rate"])
        
        # Calculate family ID
        family_id = f"F_P{p}T{t}M{m}"
        
        # Track generation
        mode = "inheritance_biased" if (self.inheritance and self.inheritance.is_loaded() and self.bias_strength > 0) else "uniform_exploration"
        
        candidate = Candidate(
            id=f"C{idx:04d}_{family_id}",
            pressure=p,
            perturbation=t,
            memory=m,
            delegation=d,
            recovery_threshold=round(recovery_threshold, 4),
            trust_update_rate=round(trust_update_rate, 4),
            trust_decay=round(trust_decay, 4),
            trust_recovery=round(trust_recovery, 4),
            migration_threshold=round(migration_threshold, 4),
            family_id=family_id,
            generation_mode=mode
        )
        
        # Log generation
        self.generation_log.append({
            "idx": idx,
            "family_id": family_id,
            "core_signature": {"P": p, "T": t, "M": m},
            "bias_applied": mode == "inheritance_biased",
            "trust_decay": round(trust_decay, 4),
            "trust_recovery": round(trust_recovery, 4)
        })
        
        # Update family counts
        self.family_counts[family_id] = self.family_counts.get(family_id, 0) + 1
        
        return candidate
    
    def generate_batch(self, count: int) -> List[Candidate]:
        """Generate a batch of candidates"""
        candidates = []
        
        for i in range(count):
            candidate = self.generate_single(i)
            candidates.append(candidate)
        
        return candidates
    
    def get_family_distribution(self) -> Dict:
        """Get distribution of families in generated batch"""
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


def generate_manifest(
    args,
    inheritance_loader: Optional[InheritancePackageLoader],
    candidate_count: int
) -> Dict:
    """Generate manifest.json"""
    
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "generation_config": {
            "count": candidate_count,
            "task_family": args.task_family,
            "seed": args.seed,
            "bias_strength": args.bias_strength if inheritance_loader and inheritance_loader.is_loaded() else 0.0
        },
        "inheritance_metadata": {
            "inheritance_package_loaded": inheritance_loader.is_loaded() if inheritance_loader else False,
            "inheritance_package_version": inheritance_loader.package_data.get("version") if inheritance_loader and inheritance_loader.is_loaded() else None,
            "bias_source": args.inheritance_package if args.inheritance_package else None,
            "approved_family_hint": inheritance_loader.approved_families if inheritance_loader and inheritance_loader.is_loaded() else [],
            "blocked_signature_hint": inheritance_loader.blocked_patterns if inheritance_loader and inheritance_loader.is_loaded() else [],
            "generation_mode": "inheritance_biased" if (inheritance_loader and inheritance_loader.is_loaded() and args.bias_strength > 0) else "uniform_exploration"
        },
        "output_files": {
            "manifest": "manifest.json",
            "family_distribution": "family_distribution.json",
            "generation_log": "generation_log.json",
            "candidates_dir": "candidates/"
        }
    }
    
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Generate candidates for Fast Genesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
S1 Implementation - Inheritance Package Support:
  --inheritance-package PATH    Load inheritance package to bias generation
  --bias-strength FLOAT         Bias strength 0.0-1.0 (default: 0.7)

Examples:
  # Round A: Pure exploration (no inheritance)
  python generate_candidates.py --count 50 --output round_a/

  # Round B: With inheritance bias
  python generate_candidates.py --count 50 \\
      --inheritance-package task1_inheritance_package.json \\
      --bias-strength 0.7 \\
      --output round_b/

  # Ablation: Load package but disable bias
  python generate_candidates.py --count 50 \\
      --inheritance-package task1_inheritance_package.json \\
      --bias-strength 0.0 \\
      --output round_ablation/
"""
    )
    
    parser.add_argument("--count", type=int, default=50,
                        help="Number of candidates to generate (default: 50)")
    parser.add_argument("--task-family", type=str, default="task1",
                        help="Task family identifier (default: task1)")
    parser.add_argument("--inheritance-package", type=str, default=None,
                        help="Path to inheritance package JSON (optional)")
    parser.add_argument("--bias-strength", type=float, default=0.7,
                        help="Inheritance bias strength 0.0-1.0 (default: 0.7)")
    parser.add_argument("--output", type=str, required=True,
                        help="Output directory for candidates")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("FAST GENESIS - Candidate Generation (S1)")
    print("=" * 60)
    print(f"Task Family: {args.task_family}")
    print(f"Count: {args.count}")
    print(f"Seed: {args.seed}")
    print(f"Output: {args.output}")
    
    # Load inheritance package if provided
    inheritance_loader = None
    if args.inheritance_package:
        print(f"\n[INHERITANCE] Loading package: {args.inheritance_package}")
        inheritance_loader = InheritancePackageLoader(args.inheritance_package)
        print(f"[INHERITANCE] Package loaded: {inheritance_loader.is_loaded()}")
        print(f"[INHERITANCE] Bias strength: {args.bias_strength}")
        
        if inheritance_loader.is_loaded():
            print(f"[INHERITANCE] Approved families: {inheritance_loader.approved_families}")
            print(f"[INHERITANCE] Generator priors: {inheritance_loader.get_bias_ranges()}")
    else:
        print("\n[MODE] Uniform exploration (no inheritance)")
        args.bias_strength = 0.0  # Force zero bias if no package
    
    # Create generator
    generator = CandidateGenerator(
        inheritance_loader=inheritance_loader,
        bias_strength=args.bias_strength,
        seed=args.seed
    )
    
    # Generate candidates
    print(f"\n[GENERATION] Generating {args.count} candidates...")
    candidates = generator.generate_batch(args.count)
    
    # Create output directories
    output_path = Path(args.output)
    candidates_dir = output_path / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual candidates
    print(f"[GENERATION] Saving candidates to {candidates_dir}...")
    for candidate in candidates:
        candidate_file = candidates_dir / f"{candidate.id}.json"
        with open(candidate_file, 'w') as f:
            json.dump(candidate.to_dict(), f, indent=2)
    
    # Generate and save manifest
    manifest = generate_manifest(args, inheritance_loader, args.count)
    manifest_path = output_path / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"[OUTPUT] Manifest: {manifest_path}")
    
    # Generate and save family distribution
    family_distribution = generator.get_family_distribution()
    family_dist_path = output_path / "family_distribution.json"
    with open(family_dist_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_candidates": args.count,
            "family_distribution": family_distribution,
            "approved_family_percentage": sum(
                f["percentage"] for f_id, f in family_distribution.items()
                if inheritance_loader and f_id in inheritance_loader.approved_families
            ) if inheritance_loader else 0.0
        }, f, indent=2)
    print(f"[OUTPUT] Family Distribution: {family_dist_path}")
    
    # Save generation log
    generation_log_path = output_path / "generation_log.json"
    with open(generation_log_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "generation_log": generator.generation_log
        }, f, indent=2)
    print(f"[OUTPUT] Generation Log: {generation_log_path}")
    
    # Summary
    print("\n" + "=" * 60)
    print("GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total candidates: {args.count}")
    print(f"Unique families: {len(family_distribution)}")
    print(f"\nTop families:")
    for family_id, data in list(family_distribution.items())[:5]:
        marker = " ✓" if inheritance_loader and family_id in inheritance_loader.approved_families else ""
        print(f"  {family_id}: {data['count']} ({data['percentage']}%)" + marker)
    
    if inheritance_loader and inheritance_loader.is_loaded():
        approved_pct = sum(
            f["percentage"] for f_id, f in family_distribution.items()
            if f_id in inheritance_loader.approved_families
        )
        print(f"\nApproved family coverage: {approved_pct:.1f}%")
    
    print(f"\nGeneration mode: {manifest['inheritance_metadata']['generation_mode']}")
    print("=" * 60)
    print("✓ S1 Candidate Generation Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
