"""
R17.4 Step 5 Validation Configuration
=====================================
50-sample shadow validation for Patch A
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class ValidationThresholds:
    """Global thresholds"""
    deliberation: int = 70
    review: int = 80


@dataclass(frozen=True)
class ValidationTargets:
    """Step 5 targets"""
    overall_fb_max: float = 0.15      # ≤15%
    live_auto_fb_max: float = 0.20    # ≤20%
    alignment_min: float = 0.75       # ≥75%


@dataclass(frozen=True)
class RollbackRedlines:
    """Redlines - trigger rollback"""
    alignment_min: float = 0.75       # <75%
    live_manual_fb_max: float = 0.25  # >25%
    overall_fb_max: float = 0.18      # >18%


@dataclass
class ValidationConfig:
    """Complete Step 5 configuration"""
    
    # Sample configuration
    total_samples: int = 50
    checkpoint_interval: int = 10
    
    # Buckets
    buckets: List[str] = None
    
    # Thresholds
    thresholds: ValidationThresholds = None
    targets: ValidationTargets = None
    redlines: RollbackRedlines = None
    
    # Baseline
    patch_a_only: bool = True
    patch_b_enabled: bool = False
    
    def __post_init__(self):
        if self.buckets is None:
            self.buckets = ["live_auto", "live_manual", "replay_real"]
        if self.thresholds is None:
            self.thresholds = ValidationThresholds()
        if self.targets is None:
            self.targets = ValidationTargets()
        if self.redlines is None:
            self.redlines = RollbackRedlines()
    
    @property
    def checkpoint_samples(self) -> List[int]:
        """Checkpoint at: 10, 20, 30, 40, 50"""
        return list(range(
            self.checkpoint_interval, 
            self.total_samples + 1, 
            self.checkpoint_interval
        ))


# Default configuration
DEFAULT_CONFIG = ValidationConfig()
