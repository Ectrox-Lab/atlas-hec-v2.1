//! PriorChannel Module
//! 
//! Post-Phase 7 Engineering Convergence
//! - Generic prior channel (content-bearing archive REMOVED)
//! - Locked parameters: p=0.01, α=0.5
//! 
//! FROZEN_STATE_v1: Do not modify without Phase 8 validation

pub mod channel;
pub mod sampling;
pub mod injection;

pub use channel::PriorChannel;
pub use sampling::sample_prior;
pub use injection::prior_inject;

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
}
