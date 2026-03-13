//! Prior Injection Functions
//!
//! FROZEN_STATE_v1: Weak regularization via generic prior
//! DELETED: Ancestral strategy injection, wisdom transfer, historical inheritance

use super::{PriorChannel, PriorSample, PRIOR_STRENGTH};

/// Inject prior into agent state (weak regularization)
/// 
/// Replaces: archive_write, inject_ancestral_strategy
/// DELETED: All content-based injection
pub fn prior_inject(
    channel: &mut PriorChannel,
    agent_state: &mut [f64],
    prior: &PriorSample,
    rng: &mut impl rand::Rng,
) {
    // Record injection
    channel.record_injection();
    
    // Apply weak regularization (α=0.5 locked)
    // This is NOT "ancestral wisdom" - just statistical bias
    for value in agent_state.iter_mut() {
        let perturbation = prior.sample(rng);
        *value += perturbation * PRIOR_STRENGTH;
    }
}

/// Probabilistic injection (respects sampling probability)
pub fn maybe_inject_prior(
    channel: &mut PriorChannel,
    agent_state: &mut [f64],
    rng: &mut impl rand::Rng,
) -> bool {
    if let Some(prior) = super::sample_prior(channel, rng) {
        prior_inject(channel, agent_state, &prior, rng);
        true
    } else {
        false
    }
}

/// Calculate injection influence statistics
pub fn calculate_influence(agent_state: &[f64], original: &[f64]) -> f64 {
    assert_eq!(agent_state.len(), original.len());
    
    if agent_state.is_empty() {
        return 0.0;
    }
    
    let total_diff: f64 = agent_state.iter()
        .zip(original.iter())
        .map(|(a, o)| (a - o).abs())
        .sum();
    
    total_diff / agent_state.len() as f64
}

/// DELETED FUNCTIONS (from old Archive):
/// - inject_ancestral_strategy
/// - transfer_historical_wisdom
/// - compress_and_inject
/// - lineage_memory_inject
/// All content-based injection REMOVED per FROZEN_STATE_v1

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    #[test]
    fn test_prior_injection() {
        let mut channel = PriorChannel::new_locked();
        let mut rng = StdRng::seed_from_u64(42);
        
        let prior = PriorSample::generic(PRIOR_STRENGTH);
        let original = vec![1.0, 2.0, 3.0];
        let mut state = original.clone();
        
        prior_inject(&mut channel, &mut state, &prior, &mut rng);
        
        // State should be perturbed
        assert_ne!(state, original);
        
        // But not drastically (weak regularization)
        let influence = calculate_influence(&state, &original);
        assert!(influence < 1.0, "Influence too strong");
        
        // Injection recorded
        assert_eq!(channel.prior_influenced_births, 1);
    }
    
    #[test]
    fn test_probabilistic_injection() {
        let mut channel = PriorChannel::new_locked();
        let mut rng = StdRng::seed_from_u64(42);
        let mut state = vec![1.0, 2.0, 3.0];
        
        // Run many times
        let mut injections = 0;
        for _ in 0..1000 {
            if maybe_inject_prior(&mut channel, &mut state, &mut rng) {
                injections += 1;
            }
        }
        
        // Should get ~10 injections (p=0.01)
        assert!(injections >= 5 && injections <= 20);
    }
}
