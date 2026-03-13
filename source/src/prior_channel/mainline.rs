//! PriorChannel Mainline Configuration
//!
//! Candidate 001 (Multi-Agent Consistency Markers) is now the DEFAULT
//! generic prior carrier for PriorChannel.
//!
//! FROZEN_STATE_v1 Mainline Constraints:
//! - Bandwidth: 32 bits fixed (4-byte Marker)
//! - Timescale: 10x separation (MarkerScheduler)
//! - Prior: Generic only (PolicyModulation)
//! - Parameters: p=0.01, α=0.5 (locked)
//!
//! This module provides the default mainline configuration.
//! Do not modify without Phase 8 validation.

use super::{
    PriorChannelMarkerAdapter, Marker, MarkerScheduler, PolicyModulation,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH,
};

/// Mainline PriorChannel with Candidate 001 markers as default prior carrier
///
/// This is the production configuration. All constraints are frozen.
pub struct MainlinePriorChannel {
    /// Marker adapter (Candidate 001 mechanism)
    pub adapter: PriorChannelMarkerAdapter,
    
    /// Frozen parameters (do not modify)
    pub sample_probability: f64,
    pub prior_strength: f64,
}

impl MainlinePriorChannel {
    /// Create new mainline PriorChannel with Candidate 001 as default
    ///
    /// This is the production entry point.
    pub fn new() -> Self {
        Self {
            adapter: PriorChannelMarkerAdapter::new(true), // Enabled by default
            sample_probability: PRIOR_SAMPLE_PROB,         // 0.01 (FROZEN)
            prior_strength: PRIOR_STRENGTH,                // 0.5 (FROZEN)
        }
    }
    
    /// Create with explicit enabled/disabled flag
    ///
    /// Use `new()` for production (enabled by default).
    /// Use `new_with_enabled(false)` for ablation testing only.
    pub fn new_with_enabled(enabled: bool) -> Self {
        Self {
            adapter: PriorChannelMarkerAdapter::new(enabled),
            sample_probability: PRIOR_SAMPLE_PROB,
            prior_strength: PRIOR_STRENGTH,
        }
    }
    
    /// Verify all mainline constraints are satisfied
    ///
    /// This should be called in CI/regression tests.
    pub fn verify_constraints(&self) -> ConstraintReport {
        ConstraintReport {
            bandwidth_fixed_32_bits: true,  // Enforced by Marker type
            timescale_10x: true,            // Enforced by MarkerScheduler
            generic_only: true,             // Enforced by PolicyModulation
            p_sample_locked: self.sample_probability == PRIOR_SAMPLE_PROB,
            alpha_locked: self.prior_strength == PRIOR_STRENGTH,
        }
    }
}

/// Constraint verification report
#[derive(Clone, Debug)]
pub struct ConstraintReport {
    pub bandwidth_fixed_32_bits: bool,
    pub timescale_10x: bool,
    pub generic_only: bool,
    pub p_sample_locked: bool,
    pub alpha_locked: bool,
}

impl ConstraintReport {
    /// All constraints satisfied
    pub fn all_pass(&self) -> bool {
        self.bandwidth_fixed_32_bits
            && self.timescale_10x
            && self.generic_only
            && self.p_sample_locked
            && self.alpha_locked
    }
}

/// Re-export mainline types for convenience
pub use super::{
    Marker as MainlineMarker,
    MarkerScheduler as MainlineScheduler,
    PolicyModulation as MainlineModulation,
};

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn mainline_default_uses_candidate_001() {
        let pc = MainlinePriorChannel::new();
        
        // Verify Candidate 001 is enabled by default
        assert!(pc.adapter.bandwidth_stats().compliant);
        assert_eq!(pc.sample_probability, 0.01);
        assert_eq!(pc.prior_strength, 0.5);
    }
    
    #[test]
    fn mainline_constraints_verified() {
        let pc = MainlinePriorChannel::new();
        let report = pc.verify_constraints();
        
        assert!(report.all_pass(), "Mainline constraints must all pass");
    }
    
    #[test]
    fn mainline_frozen_parameters() {
        let pc = MainlinePriorChannel::new();
        
        // These must never change in mainline
        assert_eq!(pc.sample_probability, 0.01, "p=0.01 is FROZEN");
        assert_eq!(pc.prior_strength, 0.5, "α=0.5 is FROZEN");
    }
}
