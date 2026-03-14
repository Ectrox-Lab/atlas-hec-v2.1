#!/usr/bin/env python3
"""
L4 Method Family B: Contract Composition Generator

Generates candidates by composing from verified contracts.
Different from Family A: explicit composition, not implicit bias.
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

from contracts import Contract, CONTRACT_DB, get_contract, list_contracts


@dataclass
class Candidate:
    """Family B candidate with explicit contract composition"""
    id: str
    contracts: List[str]              # Which contracts this candidate satisfies
    config: Dict                      # P/T/M/D parameters
    contract_coverage: float          # contracts_satisfied / total_contracts
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "contracts": self.contracts,
            "contract_coverage": self.contract_coverage,
            "pressure": self.config["pressure"],
            "perturbation": self.config["perturbation"],
            "memory": self.config["memory"],
            "delegation": self.config["delegation"],
            "trust_decay": self.config["trust_decay"],
            "trust_recovery": self.config["trust_recovery"],
            "family_id": f"F_P{self.config['pressure']}T{self.config['perturbation']}M{self.config['memory']}",
            "generation_mode": "family_b_contract_composition",
            "contract_based": True
        }


class ContractSynthesizer:
    """
    Synthesize candidate configurations from contract requirements.
    
    Instead of biasing toward "stable families", we:
    1. Select contracts to satisfy
    2. Synthesize parameters that satisfy contract input conditions
    3. Verify output guarantees through Task-2 simulation
    """
    
    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.all_contracts = list_contracts()
    
    def synthesize_for_contract(self, contract: Contract) -> Dict:
        """
        Synthesize candidate config that satisfies contract input conditions.
        """
        config = {
            "pressure": 2,
            "perturbation": 3,
            "memory": 3,
            "delegation": 1,
            "trust_decay": 0.1,
            "trust_recovery": 0.05
        }
        
        # Apply contract-specific synthesis rules
        if contract.name == "StrictHandoff":
            config["delegation"] = 1  # D1 required
            config["perturbation"] = 4  # T4 required
            config["trust_decay"] = self.random.uniform(0.05, 0.10)
            
        elif contract.name == "AdaptiveRecovery":
            config["memory"] = self.random.choice([3, 4])  # M3+ required
            config["trust_recovery"] = self.random.uniform(0.05, 0.10)
            config["trust_decay"] = self.random.uniform(0.08, 0.12)
            
        elif contract.name == "PressureThrottle":
            config["pressure"] = self.random.choice([2, 3])  # P2-3 required
            config["perturbation"] = self.random.choice([3, 4])
            config["memory"] = self.random.choice([3, 4])
        
        return config
    
    def merge_configs(self, configs: List[Dict]) -> Dict:
        """
        Merge multiple contract-specific configs into one.
        Handle conflicts by taking the more restrictive value.
        """
        if not configs:
            return {}
        
        merged = configs[0].copy()
        
        for config in configs[1:]:
            # Pressure: prefer moderate (2-3)
            if config["pressure"] <= 3:
                merged["pressure"] = config["pressure"]
            
            # Triage: prefer higher (4)
            if config["perturbation"] >= 4:
                merged["perturbation"] = config["perturbation"]
            
            # Memory: prefer higher (3-4)
            if config["memory"] >= 3:
                merged["memory"] = config["memory"]
            
            # Delegation: prefer 1 (strict)
            if config["delegation"] == 1:
                merged["delegation"] = config["delegation"]
            
            # Trust params: average
            merged["trust_decay"] = (merged["trust_decay"] + config["trust_decay"]) / 2
            merged["trust_recovery"] = (merged["trust_recovery"] + config["trust_recovery"]) / 2
        
        return merged
    
    def generate_candidate(self, idx: int, target_contracts: List[str] = None) -> Candidate:
        """
        Generate one candidate by contract composition.
        
        If target_contracts specified, try to satisfy those.
        Otherwise, random contract selection.
        """
        if target_contracts is None:
            # Randomly select 2-3 contracts
            num_contracts = self.random.choice([2, 3])
            target_contracts = self.random.sample(self.all_contracts, 
                                                  min(num_contracts, len(self.all_contracts)))
        
        # Synthesize config for each contract
        configs = []
        for contract_name in target_contracts:
            contract = get_contract(contract_name)
            config = self.synthesize_for_contract(contract)
            configs.append(config)
        
        # Merge configs
        final_config = self.merge_configs(configs)
        
        # Calculate coverage (for now, assume all target contracts satisfied)
        # In real evaluation, this will be verified on Task-2
        coverage = 1.0  # Will be updated after verification
        
        return Candidate(
            id=f"FB{idx:04d}_" + "_".join(target_contracts),
            contracts=target_contracts,
            config=final_config,
            contract_coverage=coverage
        )
    
    def generate_batch(self, count: int, strategy: str = "composition") -> List[Candidate]:
        """
        Generate batch of candidates.
        
        Strategies:
        - "composition": Random contract composition (default)
        - "strict_handoff": All candidates must satisfy StrictHandoff
        - "recovery_focus": All candidates must satisfy AdaptiveRecovery
        - "pressure_aware": All candidates must satisfy PressureThrottle
        - "full_stack": All candidates satisfy all 3 contracts
        """
        candidates = []
        
        for i in range(count):
            if strategy == "composition":
                # Random composition
                target = None
            elif strategy == "strict_handoff":
                target = ["StrictHandoff"] + self.random.sample(
                    ["AdaptiveRecovery", "PressureThrottle"], 1)
            elif strategy == "recovery_focus":
                target = ["AdaptiveRecovery"] + self.random.sample(
                    ["StrictHandoff", "PressureThrottle"], 1)
            elif strategy == "pressure_aware":
                target = ["PressureThrottle"] + self.random.sample(
                    ["StrictHandoff", "AdaptiveRecovery"], 1)
            elif strategy == "full_stack":
                target = ["StrictHandoff", "AdaptiveRecovery", "PressureThrottle"]
            else:
                target = None
            
            candidate = self.generate_candidate(i, target_contracts=target)
            candidates.append(candidate)
        
        return candidates


def save_candidates(candidates: List[Candidate], output_dir: Path):
    """Save candidates to disk"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for candidate in candidates:
        with open(output_dir / f"{candidate.id}.json", 'w') as f:
            json.dump(candidate.to_dict(), f, indent=2)
    
    # Save summary
    summary = {
        "count": len(candidates),
        "contract_distribution": {},
        "avg_coverage": sum(c.contract_coverage for c in candidates) / len(candidates)
    }
    
    for c in candidates:
        for contract in c.contracts:
            summary["contract_distribution"][contract] = \
                summary["contract_distribution"].get(contract, 0) + 1
    
    with open(output_dir / "generation_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"[SAVE] {len(candidates)} candidates to {output_dir}")
    print(f"[SUMMARY] Avg coverage: {summary['avg_coverage']:.2f}")
    print(f"[DISTRIBUTION] {summary['contract_distribution']}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--strategy", type=str, default="composition",
                        choices=["composition", "strict_handoff", "recovery_focus", 
                                "pressure_aware", "full_stack"])
    parser.add_argument("--seed", type=int, default=8000)
    args = parser.parse_args()
    
    print("=" * 70)
    print("FAMILY B CONTRACT GENERATOR")
    print("=" * 70)
    print(f"Count: {args.count}")
    print(f"Strategy: {args.strategy}")
    print(f"Seed: {args.seed}")
    print()
    
    # Generate
    synthesizer = ContractSynthesizer(seed=args.seed)
    candidates = synthesizer.generate_batch(args.count, strategy=args.strategy)
    
    # Save
    save_candidates(candidates, Path(args.output))
    
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
