//! Strategy Layer v1
//!
//! Independent optimization track on top of frozen Candidate 001.
//!
//! Goal: Convert coherence/prediction signals into task score advantages.
//! Status: ACTIVE (separate from Candidate 001 validation)

pub mod opponent_model;
pub mod game_policies;
pub mod validation;

pub use opponent_model::{OpponentModel, classify_opponent, opponent_bias, has_opponent_model};
pub use game_policies::{GameType, GamePolicy, game_bias, coop_probability, policy_description};
pub use validation::{RunMetrics, ConditionResult, GameValidation, BatchValidation, Assessment};

/// Strategy layer version
pub const VERSION: &str = "v1.0.0";

/// Strategy layer status
pub const STATUS: &str = "ACTIVE - Independent optimization";

/// Verify strategy layer builds on frozen Candidate 001
pub fn verify_layer_separation() -> bool {
    // Strategy layer must use frozen mechanism
    use crate::prior_channel::CANDIDATE_001_FROZEN;
    CANDIDATE_001_FROZEN
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn layer_separation_maintained() {
        // Strategy layer must build on frozen mechanism
        assert!(verify_layer_separation(), 
            "Strategy layer requires frozen Candidate 001 mechanism");
    }
}
