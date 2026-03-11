//! Strategy Layer v2
//!
//! Target: ON > Baseline (not just ON > OFF)
//! Priority: PD exploitation capability
//!
//! Key upgrades from v1:
//! 1. Enhanced opponent model with trend detection
//! 2. Steeper policy split (exploitative detection -> strong defection)
//! 3. Baseline-aware strategy (handle random 50/50 opponents)

pub mod opponent_model_v2;
pub mod game_policies_v2;
pub mod validation_v2;

pub use opponent_model_v2::{OpponentModelV2, classify_opponent_v2, opponent_bias_v2};
pub use game_policies_v2::{GameType, GamePolicyV2, coop_probability_v2};
pub use validation_v2::{ConditionResult, GameValidation, BatchValidation, Assessment};

/// Strategy layer version
pub const VERSION: &str = "v2.0.0";

/// Strategy layer status  
pub const STATUS: &str = "ACTIVE - Target: ON > Baseline";

/// Verify strategy layer builds on frozen Candidate 001
pub fn verify_layer_separation() -> bool {
    use crate::prior_channel::CANDIDATE_001_FROZEN;
    CANDIDATE_001_FROZEN
}

/// Target threshold for v2 success
pub const TARGET_ON_BEATS_BASELINE_RATIO: f32 = 2.0 / 3.0; // 2/3 games

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn layer_separation_maintained() {
        assert!(verify_layer_separation(), 
            "Strategy layer requires frozen Candidate 001 mechanism");
    }
    
    #[test]
    fn v2_target_defined() {
        assert_eq!(TARGET_ON_BEATS_BASELINE_RATIO, 2.0 / 3.0);
    }
}
