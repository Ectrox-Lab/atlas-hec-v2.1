//! Prior Sampling Functions
//!
//! FROZEN_STATE_v1: Generic prior sampling only
//! DELETED: Content-based sampling, archive lookup, retrieval

use super::{PriorChannel, PriorSample, PRIOR_SAMPLE_PROB};

/// Sample from prior channel (generic, not content-based)
/// 
/// Replaces: sample_from_archive
/// DELETED: All content-based sampling logic
pub fn sample_prior(
    channel: &mut PriorChannel,
    rng: &mut impl rand::Rng,
) -> Option<PriorSample> {
    // Check if we should sample (p=0.01 locked)
    if channel.should_sample(rng) {
        // Generate generic prior (NO content lookup)
        Some(channel.generate_prior())
    } else {
        None
    }
}

/// Sample with explicit probability override
/// 
/// For testing only - production uses locked p=0.01
pub fn sample_prior_with_prob(
    channel: &mut PriorChannel,
    probability: f64,
    rng: &mut impl rand::Rng,
) -> Option<PriorSample> {
    if rng.gen::<f64>() < probability {
        channel.prior_sample_attempts += 1;
        channel.prior_sample_successes += 1;
        Some(channel.generate_prior())
    } else {
        channel.prior_sample_attempts += 1;
        None
    }
}

/// Batch sampling for efficiency
pub fn sample_prior_batch(
    channel: &mut PriorChannel,
    n: usize,
    rng: &mut impl rand::Rng,
) -> Vec<PriorSample> {
    (0..n)
        .filter_map(|_| sample_prior(channel, rng))
        .collect()
}

/// DELETED FUNCTIONS (from old Archive):
/// - sample_by_content_relevance
/// - retrieve_historical_pattern  
/// - find_ancestral_strategy
/// - compress_and_sample
/// All content-based sampling REMOVED per FROZEN_STATE_v1

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    #[test]
    fn test_generic_sampling() {
        let mut channel = PriorChannel::new_locked();
        let mut rng = StdRng::seed_from_u64(42);
        
        // Sample 100 times
        let mut samples = 0;
        for _ in 0..100 {
            if let Some(_) = sample_prior(&mut channel, &mut rng) {
                samples += 1;
            }
        }
        
        // With p=0.01, expect ~1 sample in 100
        assert!(samples <= 5, "Too many samples - check probability");
    }
    
    #[test]
    fn test_batch_sampling() {
        let mut channel = PriorChannel::new_locked();
        let mut rng = StdRng::seed_from_u64(42);
        
        let batch = sample_prior_batch(&mut channel, 1000, &mut rng);
        
        // Should get ~10 samples
        assert!(batch.len() >= 5 && batch.len() <= 20);
        
        // All samples should be generic (no content)
        for sample in batch {
            assert_eq!(sample.alpha, 0.5);
            assert_eq!(sample.distribution_mean, 0.0);
        }
    }
}
