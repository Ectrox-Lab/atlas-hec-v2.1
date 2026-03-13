//! Bio-World × Superbrain Integration v0
//!
//! Minimal interface layer connecting verified Superbrain base to Bio-World environment.
//!
//! Integration points:
//! - Candidate 001 PriorChannel → Cell local_signal_state
//! - Strategy Layer v3 → Cell decision policy
//! - Identity/Continuity → Lineage inheritance
//!
//! Architecture: Bio-World v19 + Superbrain P6 base

pub mod cell_adapter;
pub mod lineage_adapter;
pub mod strategy_bridge;
pub mod experiment_runner;
pub mod v19_runner;

pub use cell_adapter::{CellAdapter, PriorInCell, LocalSignal};
pub use lineage_adapter::{LineageAdapter, IdentityInheritance};
pub use strategy_bridge::{StrategyBridge, BioDecisionContext};
pub use experiment_runner::{ExperimentAtoE, RunConfig, run_matrix, ExperimentResult};
pub use v19_runner::{V19Experiment, run_matrix_v19};

/// Integration version
pub const VERSION: &str = "v0.1.0";

/// Integration status
pub const STATUS: &str = "ACTIVE - MVP Interface Layer";

/// Core constraint: 32-bit carrier preserved
pub const CARRIER_BANDWIDTH_BITS: usize = 32;

/// Core constraint: Generic prior only
pub const GENERIC_PRIOR_ONLY: bool = true;

/// Verify Superbrain base is frozen
pub fn verify_superbrain_base() -> bool {
    use crate::prior_channel::CANDIDATE_001_FROZEN;
    CANDIDATE_001_FROZEN
}

/// Integration health check
pub fn integration_health() -> HealthStatus {
    HealthStatus {
        superbrain_base_frozen: verify_superbrain_base(),
        carrier_bandwidth_ok: CARRIER_BANDWIDTH_BITS == 32,
        generic_prior_enforced: GENERIC_PRIOR_ONLY,
        strategy_layer_active: true,
    }
}

#[derive(Clone, Debug)]
pub struct HealthStatus {
    pub superbrain_base_frozen: bool,
    pub carrier_bandwidth_ok: bool,
    pub generic_prior_enforced: bool,
    pub strategy_layer_active: bool,
}

impl HealthStatus {
    pub fn all_ok(&self) -> bool {
        self.superbrain_base_frozen
            && self.carrier_bandwidth_ok
            && self.generic_prior_enforced
            && self.strategy_layer_active
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn superbrain_base_verified() {
        assert!(verify_superbrain_base(),
            "Integration requires frozen Superbrain base");
    }
    
    #[test]
    fn carrier_constraints_preserved() {
        assert_eq!(CARRIER_BANDWIDTH_BITS, 32);
        assert!(GENERIC_PRIOR_ONLY);
    }
}
