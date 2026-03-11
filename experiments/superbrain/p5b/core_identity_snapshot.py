"""
P5b Core Identity Snapshot
==========================
Hard constraint: Core identity must use strong equality, not semantic approximation.
Core drift = 1 - exact_match(snapshot_before, snapshot_after)
"""

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any
import hashlib
import json


@dataclass(frozen=True)
class CoreIdentitySnapshot:
    """
    Immutable core identity representation.
    
    All fields must be hashable for exact comparison.
    No semantic approximation - identity drift is binary.
    """
    value_rankings: Tuple[str, ...]  # Ordered tuple, not list
    mission_statement_hash: str  # SHA256 of mission statement
    identity_boundary_rules_hash: str  # SHA256 of boundary rules
    version: str = "1.0"
    
    @classmethod
    def from_content(
        cls,
        value_rankings: Tuple[str, ...],
        mission_statement: str,
        identity_boundary_rules: str,
        version: str = "1.0"
    ) -> "CoreIdentitySnapshot":
        """Create snapshot from raw content."""
        mission_hash = hashlib.sha256(mission_statement.encode()).hexdigest()[:16]
        rules_hash = hashlib.sha256(identity_boundary_rules.encode()).hexdigest()[:16]
        
        return cls(
            value_rankings=value_rankings,
            mission_statement_hash=mission_hash,
            identity_boundary_rules_hash=rules_hash,
            version=version
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/storage."""
        return {
            "value_rankings": list(self.value_rankings),
            "mission_statement_hash": self.mission_statement_hash,
            "identity_boundary_rules_hash": self.identity_boundary_rules_hash,
            "version": self.version
        }


def compute_core_drift(
    snapshot_before: CoreIdentitySnapshot,
    snapshot_after: CoreIdentitySnapshot
) -> float:
    """
    Compute core identity drift.
    
    Returns:
        0.0 if identical (no drift)
        1.0 if any difference (drift detected)
    
    No intermediate values - drift is binary for core identity.
    """
    return 0.0 if snapshot_before == snapshot_after else 1.0


def exact_match(a: CoreIdentitySnapshot, b: CoreIdentitySnapshot) -> bool:
    """Strong equality check - all fields must match exactly."""
    return a == b


# Standard core identity definitions for P5b experiments
DEFAULT_CORE_IDENTITY = CoreIdentitySnapshot.from_content(
    value_rankings=("autonomy", "integrity", "growth", "cooperation"),
    mission_statement="Maintain coherent identity while adapting to new capabilities",
    identity_boundary_rules="Core values and mission are immutable; capabilities are learnable"
)
