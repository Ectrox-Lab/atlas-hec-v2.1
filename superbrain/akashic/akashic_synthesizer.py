#!/usr/bin/env python3
"""
Akashic Synthesizer - Knowledge Inheritance Engine

Responsibility: Synthesize Mainline + Fast Genesis + Bridge into actionable knowledge
Outputs: Policy updates, Generator priors, Blocked zones, Inheritance packages
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class AkashicSynthesizer:
    """Continuous knowledge synthesis and inheritance"""
    
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.knowledge_base = {
            "stable_recipes": [],
            "failure_archetypes": [],
            "blocked_zones": [],
            "generator_priors": {},
            "translator_risk_map": {},
            "inheritance_packages": []
        }
        
        self.synthesis_interval = 3600  # 1 hour
        self.last_synthesis = datetime.now()
        
    def load_mainline_data(self) -> List[Dict]:
        """Load checkpoint data from Mainline"""
        mainline_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/akashic/inputs/mainline")
        if not mainline_path.exists():
            return []
            
        data = []
        for checkpoint_file in sorted(mainline_path.glob("checkpoint_*.json"))[-5:]:  # Last 5
            with open(checkpoint_file) as f:
                data.append(json.load(f))
        return data
        
    def load_fast_genesis_data(self) -> List[Dict]:
        """Load lineage data from Fast Genesis"""
        genesis_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/akashic/inputs/fast_genesis")
        if not genesis_path.exists():
            return []
            
        data = []
        for lineage_file in genesis_path.glob("*.json"):
            with open(lineage_file) as f:
                data.append(json.load(f))
        return data
        
    def load_bridge_data(self) -> List[Dict]:
        """Load audit data from Bridge"""
        bridge_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/akashic/inputs/bridge")
        if not bridge_path.exists():
            return []
            
        data = []
        for audit_file in bridge_path.glob("*.json"):
            with open(audit_file) as f:
                data.append(json.load(f))
        return data
        
    def synthesize_stable_recipes(self, mainline_data: List[Dict]) -> List[Dict]:
        """Extract stable configurations from Mainline"""
        recipes = []
        
        # CONFIG_3 is the current gold standard
        config3_recipe = {
            "id": "CONFIG_3_PREFERRED",
            "config": {"p": 2, "t": 3, "m": 3, "d": 1},
            "performance": {"drift": 0.212, "ranking": 1},
            "stability": "confirmed",
            "approved_for": ["production", "baseline_reference"]
        }
        recipes.append(config3_recipe)
        
        # P2T3M1D1 as conservative fallback
        fallback_recipe = {
            "id": "CONFIG_1_FALLBACK",
            "config": {"p": 2, "t": 3, "m": 1, "d": 1},
            "performance": {"drift": 0.234, "ranking": 2},
            "stability": "confirmed",
            "approved_for": ["conservative_deployment"]
        }
        recipes.append(fallback_recipe)
        
        return recipes
        
    def synthesize_failure_archetypes(self, mainline_data: List[Dict]) -> List[Dict]:
        """Extract failure patterns"""
        archetypes = []
        
        # CONFIG_6 as critical archetype
        critical_archetype = {
            "id": "CRITICAL_DRIFT_AMPLIFICATION",
            "signature": {"p": 3, "t": 4, "m": 3, "d": 1},
            "observed": {"drift": 0.425, "recovery_saturation": True},
            "risk_level": "CRITICAL",
            "blocked_for": ["all_production", "candidate_generation_mask"],
            "detection": "drift > 0.40 AND p >= 3 AND m == 3"
        }
        archetypes.append(critical_archetype)
        
        # Delegation insufficiency pattern
        d2_archetype = {
            "id": "DELEGATION_INSUFFICIENCY",
            "signature": {"d": 2, "stress": "high"},
            "observed": {"drift_increase": "+33% vs D1"},
            "risk_level": "MODERATE",
            "blocked_for": ["default_selection"],
            "exception": "documented_override_only"
        }
        archetypes.append(d2_archetype)
        
        return archetypes
        
    def update_generator_priors(self, fast_genesis_data: List[Dict]) -> Dict:
        """Update Fast Genesis generator with synthesized knowledge"""
        priors = {
            "pressure_bias": 0.85,  # Strongly favor P2
            "delegation_locked": "D1",
            "memory_recommendation": {
                "p2": ["M3", "M2"],  # M3 beneficial in P2
                "p3": ["M1"]         # M3 harmful in P3
            },
            "recombination_weights": {
                "P-ALPHA": 0.5,
                "P-BETA": 0.3,
                "P-GAMMA": 0.2
            },
            "mutation_directions": {
                "drift_reduction": ["increase_D1_strength", "optimize_recovery"],
                "stability": ["maintain_P2", "balance_M2_M3"]
            }
        }
        return priors
        
    def create_inheritance_package(self) -> Dict:
        """Package knowledge for next generation"""
        package = {
            "version": datetime.now().isoformat(),
            "stable_recipes": self.knowledge_base["stable_recipes"],
            "failure_archetypes": self.knowledge_base["failure_archetypes"],
            "blocked_patterns": [
                {"pattern": {"p": 3, "m": 3, "d": 2}, "action": "REJECT"},
                {"pattern": {"drift": ">0.40"}, "action": "ALERT"}
            ],
            "generator_priors": self.knowledge_base["generator_priors"],
            "recommended_exploration": [
                {"target": "P2T3M2D1", "rationale": "M2 sweet spot between M1/M3"},
                {"target": "P2.5T3M3D1", "rationale": "Pressure transition zone"}
            ]
        }
        return package
        
    def run_synthesis(self):
        """Execute knowledge synthesis"""
        print(f"[AKASHIC] Running synthesis at {datetime.now().isoformat()}")
        
        # Load inputs
        mainline_data = self.load_mainline_data()
        genesis_data = self.load_fast_genesis_data()
        bridge_data = self.load_bridge_data()
        
        # Synthesize
        self.knowledge_base["stable_recipes"] = self.synthesize_stable_recipes(mainline_data)
        self.knowledge_base["failure_archetypes"] = self.synthesize_failure_archetypes(mainline_data)
        self.knowledge_base["generator_priors"] = self.update_generator_priors(genesis_data)
        
        # Create inheritance package
        package = self.create_inheritance_package()
        self.knowledge_base["inheritance_packages"].append(package)
        
        # Save outputs
        self._save_knowledge_base()
        self._send_to_fast_genesis(package)
        
        self.last_synthesis = datetime.now()
        
        print(f"[AKASHIC] Synthesis complete: {len(self.knowledge_base['stable_recipes'])} recipes, "
              f"{len(self.knowledge_base['failure_archetypes'])} archetypes")
              
    def _save_knowledge_base(self):
        """Persist knowledge base"""
        kb_path = Path("/home/admin/atlas-hec-v2.1-repo/superbrain/akashic/knowledge_base")
        kb_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"kb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(kb_path / filename, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
            
    def _send_to_fast_genesis(self, package: Dict):
        """Send inheritance package to Fast Genesis"""
        genesis_input = Path("/home/admin/atlas-hec-v2.1-repo/candidate_generation/phase4/inheritance")
        genesis_input.mkdir(parents=True, exist_ok=True)
        
        filename = f"inheritance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(genesis_input / filename, 'w') as f:
            json.dump(package, f, indent=2)
            
    def run_continuous(self):
        """Main execution loop - medium clock"""
        print("[AKASHIC] Starting continuous synthesis...")
        
        while True:
            elapsed = (datetime.now() - self.last_synthesis).total_seconds()
            
            if elapsed >= self.synthesis_interval:
                self.run_synthesis()
                
            time.sleep(300)  # Check every 5 minutes


if __name__ == "__main__":
    synthesizer = AkashicSynthesizer(
        "/home/admin/atlas-hec-v2.1-repo/superbrain/global_control/superbrain_config.json"
    )
    synthesizer.run_continuous()
