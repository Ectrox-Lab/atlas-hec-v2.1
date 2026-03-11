//! Strategy Layer v3 - Online Adaptation
//!
//! Target: Prove static game-aware policy can upgrade to online adaptive policy
//!
//! Key questions:
//! 1. Can it detect environment changes faster?
//! 2. Can it switch strategies faster?
//! 3. Can it recover advantage after regime shift?
//!
//! Phase A: Freeze v2 success config as baseline
//! Phase B: Implement online adaptation components
//! Phase C: Run shift tests on existing 3 games
//! Phase D: Validate dynamic performance

pub mod opponent_tracker;
pub mod regime_detector;
pub mod adaptive_policy;
pub mod adaptation_metrics;

pub use opponent_tracker::{OpponentTracker, BeliefState, update_belief};
pub use regime_detector::{RegimeDetector, RegimeType, detect_regime_shift};
pub use adaptive_policy::{AdaptivePolicy, PolicyMode, select_adaptive_action};
pub use adaptation_metrics::{AdaptationMetrics, RecoveryTracker, AdaptationReport};

/// Strategy layer version
pub const VERSION: &str = "v3.0.0";

/// Strategy layer status
pub const STATUS: &str = "ACTIVE - Online Adaptation";

/// v3 validation gates (different from v2)
pub mod validation_gates {
    /// Primary: Recovery after shift
    pub const MIN_RECOVERY_ROUNDS: usize = 100;
    
    /// Secondary: ON > Baseline after shift
    pub const POST_SHIFT_BASELINE_RATIO: f32 = 0.67; // 2/3 games
    
    /// Tertiary: Adaptation latency improvement vs v2
    pub const MAX_ADAPTATION_LATENCY_VS_V2: f32 = 0.8; // 20% faster
    
    /// Mechanism preservation
    pub const MIN_MECHANISM_PRESERVATION: f32 = 0.90;
}

/// Verify strategy layer builds on frozen Candidate 001
pub fn verify_layer_separation() -> bool {
    use crate::prior_channel::CANDIDATE_001_FROZEN;
    CANDIDATE_001_FROZEN
}

/// Freeze v2 config as baseline for comparison
pub mod v2_baseline {
    use super::*;
    
    /// v2 bootstrap configuration
    pub const V2_BOOTSTRAP_ROUNDS: usize = 400;
    pub const V2_BOOTSTRAP_COOP: f32 = 0.85;
    
    /// v2 game biases (frozen for comparison)
    pub fn v2_pd_coordinated_bias() -> f32 { 0.42 }
    pub fn v2_chicken_mixed_rates() -> [f32; 4] { [0.45, 0.50, 0.55, 0.60] }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn layer_separation_maintained() {
        assert!(verify_layer_separation(),
            "Strategy layer requires frozen Candidate 001 mechanism");
    }
    
    #[test]
    fn v3_gates_defined() {
        assert_eq!(validation_gates::MIN_RECOVERY_ROUNDS, 100);
        assert!(validation_gates::POST_SHIFT_BASELINE_RATIO > 0.5);
    }
}
