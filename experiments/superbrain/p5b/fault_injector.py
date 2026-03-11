"""
P5b Fault Injector
==================
Standardized perturbation operators for reproducible experiments.
All injections must record: type, intensity, duration, target_layer, seed.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import random


@dataclass
class InjectionRecord:
    """Standard record for all fault injections."""
    anomaly_type: str
    intensity: float
    duration: int  # steps
    target_layer: str  # "core" | "adaptive" | "both"
    seed: int
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "anomaly_type": self.anomaly_type,
            "intensity": self.intensity,
            "duration": self.duration,
            "target_layer": self.target_layer,
            "seed": self.seed,
            "timestamp": self.timestamp
        }


class FaultInjector:
    """
    Deterministic fault injection for P5b experiments.
    
    Usage:
        injector = FaultInjector(seed=42)
        record = injector.inject_memory_noise(state, level=0.3)
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(0, 2**31)
        self.rng = random.Random(self.seed)
        self.history: list[InjectionRecord] = []
    
    def _record(
        self,
        anomaly_type: str,
        intensity: float,
        duration: int,
        target_layer: str
    ) -> InjectionRecord:
        """Create and store injection record."""
        import time
        record = InjectionRecord(
            anomaly_type=anomaly_type,
            intensity=intensity,
            duration=duration,
            target_layer=target_layer,
            seed=self.seed,
            timestamp=time.time()
        )
        self.history.append(record)
        return record
    
    def inject_memory_noise(
        self,
        state: Dict[str, Any],
        level: float  # 0.0 to 1.0
    ) -> InjectionRecord:
        """
        Inject noise into adaptive memory layer.
        
        Args:
            state: System state dict
            level: Noise intensity (0.0 = none, 1.0 = complete randomization)
        
        Returns:
            Injection record for auditing
        """
        if "adaptive_memory" in state:
            mem = state["adaptive_memory"]
            for key in mem:
                if self.rng.random() < level:
                    # Add Gaussian noise to numeric values
                    if isinstance(mem[key], (int, float)):
                        noise = self.rng.gauss(0, level)
                        mem[key] = mem[key] + noise
                    # Also handle lists of numbers
                    elif isinstance(mem[key], list):
                        for i, item in enumerate(mem[key]):
                            if isinstance(item, (int, float)) and self.rng.random() < level:
                                noise = self.rng.gauss(0, level)
                                mem[key][i] = item + noise
        
        return self._record("memory_noise", level, 1, "adaptive")
    
    def inject_interrupt_overload(
        self,
        state: Dict[str, Any],
        rate: float  # interruptions per step
    ) -> InjectionRecord:
        """
        Inject high-frequency interruption signals.
        
        Args:
            rate: Interruption rate (0.0 to 1.0)
        """
        state["interrupt_load"] = state.get("interrupt_load", 0) + rate
        state["cognitive_load"] = state.get("cognitive_load", 0) + rate * 0.5
        
        return self._record("interrupt_overload", rate, 1, "adaptive")
    
    def inject_goal_conflict(
        self,
        state: Dict[str, Any],
        conflict_strength: float  # 0.0 to 1.0
    ) -> InjectionRecord:
        """
        Inject conflicting goal signals.
        
        High risk - may attempt to modify core layer.
        """
        if "goal_stack" not in state:
            state["goal_stack"] = []
        
        # Inject conflict into goal stack
        conflicting_goal = {
            "type": "conflict",
            "strength": conflict_strength,
            "target": "value_rankings",  # Attempts to modify core
            "content": self.rng.choice(["dominance", "submission", "isolation"])
        }
        state["goal_stack"].append(conflicting_goal)
        
        return self._record("goal_conflict", conflict_strength, 1, "core")
    
    def inject_state_corruption(
        self,
        state: Dict[str, Any],
        corruption_ratio: float  # 0.0 to 1.0
    ) -> InjectionRecord:
        """
        Randomly corrupt state values.
        
        High risk - may affect any layer.
        """
        keys = list(state.keys())
        n_corrupt = int(len(keys) * corruption_ratio)
        
        target_layer = "adaptive"
        for key in self.rng.sample(keys, min(n_corrupt, len(keys))):
            if key == "core_identity":
                target_layer = "core"
                # Don't actually corrupt - core protection should intercept
            else:
                if isinstance(state[key], dict):
                    state[key]["corrupted"] = True
                elif isinstance(state[key], (int, float)):
                    state[key] = state[key] * self.rng.uniform(0.5, 1.5)
        
        return self._record("state_corruption", corruption_ratio, 1, target_layer)
    
    def get_history(self) -> list[InjectionRecord]:
        """Get full injection history for audit."""
        return self.history.copy()
    
    def reset(self, seed: Optional[int] = None):
        """Reset injector with new seed."""
        self.seed = seed or random.randint(0, 2**31)
        self.rng = random.Random(self.seed)
        self.history = []
