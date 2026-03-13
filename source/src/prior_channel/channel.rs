//! PriorChannel Core Implementation
//!
//! Replaces CausalArchive with simplified generic prior channel
//! DELETED: Content storage, history, compression, retrieval
//! RETAINED: Sampling, prior generation, injection

use super::{PriorSample, PRIOR_SAMPLE_PROB, PRIOR_STRENGTH};

/// PriorChannel - Generic prior sampling channel
/// 
/// FROZEN_STATE_v1: Content-bearing archive REMOVED
/// Only generic prior sampling remains
pub struct PriorChannel {
    /// Sampling probability (LOCKED: p=0.01)
    pub sample_probability: f64,
    
    /// Prior strength (LOCKED: α=0.5)
    pub prior_strength: f64,
    
    /// Sampling statistics (no content storage)
    pub prior_sample_attempts: u64,
    pub prior_sample_successes: u64,
    pub prior_influenced_births: u64,
}

impl PriorChannel {
    /// Create new PriorChannel with LOCKED parameters
    pub fn new_locked() -> Self {
        Self {
            sample_probability: PRIOR_SAMPLE_PROB,
            prior_strength: PRIOR_STRENGTH,
            prior_sample_attempts: 0,
            prior_sample_successes: 0,
            prior_influenced_births: 0,
        }
    }
    
    /// Check if prior should be sampled (generic, not content-based)
    pub fn should_sample(&mut self, rng: &mut impl rand::Rng) -> bool {
        self.prior_sample_attempts += 1;
        let sample = rng.gen::<f64>() < self.sample_probability;
        if sample {
            self.prior_sample_successes += 1;
        }
        sample
    }
    
    /// Generate generic prior (NO content lookup)
    pub fn generate_prior(&self) -> PriorSample {
        // FROZEN: Generic prior only - no content-based retrieval
        PriorSample::generic(self.prior_strength)
    }
    
    /// Record prior-influenced birth
    pub fn record_injection(&mut self) {
        self.prior_influenced_births += 1;
    }
    
    /// Get sampling statistics
    pub fn get_stats(&self) -> SamplingStats {
        SamplingStats {
            attempts: self.prior_sample_attempts,
            successes: self.prior_sample_successes,
            injections: self.prior_influenced_births,
            success_rate: if self.prior_sample_attempts > 0 {
                self.prior_sample_successes as f64 / self.prior_sample_attempts as f64
            } else {
                0.0
            },
        }
    }
}

pub struct SamplingStats {
    pub attempts: u64,
    pub successes: u64,
    pub injections: u64,
    pub success_rate: f64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    #[test]
    fn test_locked_parameters_in_channel() {
        let channel = PriorChannel::new_locked();
        assert_eq!(channel.sample_probability, 0.01);
        assert_eq!(channel.prior_strength, 0.5);
    }
    
    #[test]
    fn test_generic_prior_generation() {
        let channel = PriorChannel::new_locked();
        let prior = channel.generate_prior();
        
        // Verify no content-based fields
        assert_eq!(prior.alpha, 0.5);
        assert_eq!(prior.distribution_mean, 0.0);
    }
    
    #[test]
    fn test_sampling_statistics() {
        let mut channel = PriorChannel::new_locked();
        let mut rng = StdRng::seed_from_u64(42);
        
        // Sample 1000 times
        for _ in 0..1000 {
            let _ = channel.should_sample(&mut rng);
        }
        
        let stats = channel.get_stats();
        assert_eq!(stats.attempts, 1000);
        // With p=0.01, expect ~10 successes
        assert!(stats.successes >= 5 && stats.successes <= 20);
    }
}
