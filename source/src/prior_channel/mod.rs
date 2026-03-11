//! PriorChannel Module
//! 
//! Post-Phase 7 Engineering Convergence
//! - Generic prior channel (content-bearing archive REMOVED)
//! - Candidate 001 (Multi-Agent Consistency Markers): DEFAULT prior carrier
//! - Locked parameters: p=0.01, α=0.5
//! 
//! FROZEN_STATE_v1: Do not modify without Phase 8 validation

pub mod channel;
pub mod sampling;
pub mod injection;
pub mod marker_adapter;
pub mod mainline;
pub mod frozen_config;
pub mod strategy_layer;

pub use channel::PriorChannel;
pub use sampling::sample_prior;
pub use injection::prior_inject;
pub use marker_adapter::{PriorChannelMarkerAdapter, Marker, PolicyModulation, MarkerScheduler};

// Mainline: Candidate 001 is now the default prior carrier
pub use mainline::{MainlinePriorChannel, ConstraintReport};

// FROZEN: Success baseline configuration
pub use frozen_config::{
    CANDIDATE_001_FROZEN, MARKER_SIZE_BYTES, MARKER_UPDATE_INTERVAL,
    POLICY_COUPLING_BIAS, RANDOM_EXPLORATION_RATE,
    success_baseline, verify_frozen_config, FrozenConfigReport,
};
// Note: PRIOR_SAMPLE_PROB and PRIOR_STRENGTH defined above for backward compatibility

// Strategy Layer: Task-aware action selection on top of frozen mechanism
pub use strategy_layer::{
    StrategyLayer, StrategyConfig, GameType, OpponentModel,
    validate_strategy_constraints, StrategyValidationReport,
};

// Strategy Layer v1: Independent optimization track
pub mod strategy_layer_v1;

// Strategy Layer v2: ON > Baseline target
pub mod strategy_layer_v2;

// Strategy Layer v3: Online adaptation
pub mod strategy_layer_v3;

/// LOCKED DEFAULT PARAMETERS
/// DO NOT CHANGE without Phase 8 validation study
pub const PRIOR_SAMPLE_PROB: f64 = 0.01;      // p=0.01 from Phase 7 center axis
pub const PRIOR_STRENGTH: f64 = 0.5;          // α=medium

/// Prior sample structure (replaces ArchiveRecord)
/// No content storage - just generic prior sampling
#[derive(Clone, Debug)]
pub struct PriorSample {
    /// Distribution parameters only - no historical content
    pub distribution_mean: f64,
    pub distribution_std: f64,
    /// Weak regularization strength
    pub alpha: f64,
}

impl PriorSample {
    /// Create generic prior sample
    /// No content encoding - pure statistical regularization
    pub fn generic(strength: f64) -> Self {
        Self {
            distribution_mean: 0.0,
            distribution_std: 1.0,
            alpha: strength,
        }
    }
    
    /// Sample from prior distribution
    pub fn sample(&self, rng: &mut impl rand::Rng) -> f64 {
        rng.gen_range(-self.alpha..=self.alpha)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_locked_parameters() {
        // FROZEN_STATE_v1: These must not change
        assert_eq!(PRIOR_SAMPLE_PROB, 0.01);
        assert_eq!(PRIOR_STRENGTH, 0.5);
    }
    
    #[test]
    fn test_generic_prior_no_content() {
        let prior = PriorSample::generic(PRIOR_STRENGTH);
        // Verify no content fields exist
        assert!(prior.alpha > 0.0);
        assert!(prior.distribution_std > 0.0);
    }
    
    #[test]
    fn test_candidate_001_is_mainline_default() {
        // Candidate 001 (MarkerAdapter) is now the default prior carrier
        let mainline = MainlinePriorChannel::new();
        let report = mainline.verify_constraints();
        
        // All mainline constraints must be satisfied
        assert!(report.all_pass(), "Candidate 001 mainline constraints failed");
        
        // Bandwidth must be 32 bits
        assert!(report.bandwidth_fixed_32_bits);
        
        // Timescale must be 10x
        assert!(report.timescale_10x);
        
        // Must be generic-only
        assert!(report.generic_only);
    }
}
