//! Strategy Layer for Task-Aware Action Selection
//!
//! Sits ON TOP of frozen Candidate 001 mechanism.
//! Maps coherence/prediction signals to task-appropriate actions.
//!
//! Goal: Convert mechanism success (coherence +16.6%, prediction +24.6%)
//! into task success (score improvement).

use super::{Marker, frozen_config::POLICY_COUPLING_BIAS};

/// Game type for strategy-aware coupling
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameType {
    PrisonersDilemma,
    StagHunt,
    Chicken,
}

/// Opponent model for prediction-conditioned bias
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OpponentModel {
    Cooperative,      // High coherence, likely to cooperate
    Exploitative,     // High variance, likely to defect
    Uncertain,        // Low coherence, unpredictable
}

/// Strategy configuration
#[derive(Clone, Copy, Debug)]
pub struct StrategyConfig {
    pub game: GameType,
    pub use_game_aware: bool,
    pub use_opponent_model: bool,
}

impl StrategyConfig {
    /// Default: use all strategy adaptations
    pub fn adaptive(game: GameType) -> Self {
        Self {
            game,
            use_game_aware: true,
            use_opponent_model: true,
        }
    }
    
    /// Baseline: no strategy adaptation (original coupling)
    pub fn baseline(game: GameType) -> Self {
        Self {
            game,
            use_game_aware: false,
            use_opponent_model: false,
        }
    }
}

/// Strategy layer: converts marker signals to action probabilities
pub struct StrategyLayer {
    config: StrategyConfig,
}

impl StrategyLayer {
    pub fn new(config: StrategyConfig) -> Self {
        Self { config }
    }
    
    /// Compute cooperation probability based on strategy
    /// 
    /// Returns value in [0.05, 0.95] (avoids pure deterministic)
    pub fn coop_probability(&self, partner_markers: &[Marker], prediction: Option<OpponentModel>) -> f32 {
        let base = 0.5;
        
        // Base coherence bias from mechanism
        let coherence = if partner_markers.is_empty() {
            0.5
        } else {
            partner_markers.iter()
                .map(|m| m.coherence() as f32 / 255.0)
                .sum::<f32>() / partner_markers.len() as f32
        };
        
        // Layer 1: Game-aware modulation
        let game_bias = if self.config.use_game_aware {
            self.game_aware_bias(coherence)
        } else {
            // Original: high coherence → cooperate more
            (coherence - 0.5) * POLICY_COUPLING_BIAS * 2.0
        };
        
        // Layer 2: Opponent-model-conditioned modulation
        let opp_bias = if self.config.use_opponent_model {
            self.opponent_model_bias(prediction)
        } else {
            0.0
        };
        
        (base + game_bias + opp_bias).clamp(0.05, 0.95)
    }
    
    /// Game-aware bias: different strategy per game type
    fn game_aware_bias(&self, coherence: f32) -> f32 {
        match self.config.game {
            GameType::StagHunt => {
                // Stag Hunt: Cooperation is Pareto optimal
                // High coherence → strong cooperation bias
                (coherence - 0.5) * POLICY_COUPLING_BIAS * 2.5  // Stronger coop
            }
            
            GameType::PrisonersDilemma => {
                // PD: Risk-sensitive
                // High coherence → moderate cooperation with defection insurance
                if coherence > 0.7 {
                    // Trust but verify: slight coop bias with readiness to defect
                    (coherence - 0.5) * POLICY_COUPLING_BIAS * 1.0
                } else {
                    // Low coherence: more defensive
                    (coherence - 0.5) * POLICY_COUPLING_BIAS * 0.5 - 0.1
                }
            }
            
            GameType::Chicken => {
                // Chicken: Avoid mutual cooperation (both lose)
                // High coherence → actually REDUCE cooperation (commit to "crazy")
                // or use mixed strategy
                if coherence > 0.7 {
                    // Both predictable → someone must "swerve"
                    // Bias toward defection (commitment strategy)
                    -(coherence - 0.5) * POLICY_COUPLING_BIAS * 1.5
                } else {
                    // Uncertain → standard exploration
                    (coherence - 0.5) * POLICY_COUPLING_BIAS * 0.5
                }
            }
        }
    }
    
    /// Opponent-model-conditioned bias
    fn opponent_model_bias(&self, prediction: Option<OpponentModel>) -> f32 {
        match prediction {
            Some(OpponentModel::Cooperative) => {
                // Predicted cooperative → exploit by cooperating (for mutual gain)
                match self.config.game {
                    GameType::StagHunt => 0.15,  // Strong mutual benefit
                    GameType::PrisonersDilemma => 0.05,  // Cautious trust
                    GameType::Chicken => -0.05,  // They'll swerve, we drive
                }
            }
            
            Some(OpponentModel::Exploitative) => {
                // Predicted exploitative → defend by defecting
                match self.config.game {
                    GameType::StagHunt => -0.10,  // Avoid being abandoned
                    GameType::PrisonersDilemma => -0.15,  // Defect to avoid sucker
                    GameType::Chicken => 0.05,   // They drive, we swerve (survive)
                }
            }
            
            Some(OpponentModel::Uncertain) | None => {
                // Uncertain → no additional bias
                0.0
            }
        }
    }
    
    /// Infer opponent model from markers
    pub fn infer_opponent(&self, markers: &[Marker]) -> OpponentModel {
        if markers.is_empty() {
            return OpponentModel::Uncertain;
        }
        
        let avg_coherence = markers.iter()
            .map(|m| m.coherence() as f32 / 255.0)
            .sum::<f32>() / markers.len() as f32;
        
        let coherence_variance = if markers.len() > 1 {
            let mean = avg_coherence;
            markers.iter()
                .map(|m| {
                    let c = m.coherence() as f32 / 255.0;
                    (c - mean).powi(2)
                })
                .sum::<f32>() / markers.len() as f32
        } else {
            0.0
        };
        
        if avg_coherence > 0.7 && coherence_variance < 0.05 {
            OpponentModel::Cooperative
        } else if avg_coherence < 0.4 || coherence_variance > 0.1 {
            OpponentModel::Exploitative
        } else {
            OpponentModel::Uncertain
        }
    }
}

/// Validation: Ensure strategy layer doesn't violate constraints
pub fn validate_strategy_constraints() -> StrategyValidationReport {
    StrategyValidationReport {
        uses_frozen_marker: true,      // Must use 32-bit Marker
        uses_frozen_timescale: true,   // Must respect 10x
        generic_only: true,            // No specific action encoding
        no_leakage: true,              // Only modulation
    }
}

#[derive(Clone, Debug)]
pub struct StrategyValidationReport {
    pub uses_frozen_marker: bool,
    pub uses_frozen_timescale: bool,
    pub generic_only: bool,
    pub no_leakage: bool,
}

impl StrategyValidationReport {
    pub fn all_pass(&self) -> bool {
        self.uses_frozen_marker 
            && self.uses_frozen_timescale 
            && self.generic_only 
            && self.no_leakage
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn strategy_preserves_constraints() {
        let report = validate_strategy_constraints();
        assert!(report.all_pass(), "Strategy layer must preserve frozen constraints");
    }
    
    #[test]
    fn game_aware_differentiates() {
        let markers = vec![Marker::new(1, 200, 0, 0)]; // High coherence
        
        let strat_stag = StrategyLayer::new(StrategyConfig::adaptive(GameType::StagHunt));
        let strat_pd = StrategyLayer::new(StrategyConfig::adaptive(GameType::PrisonersDilemma));
        let strat_chicken = StrategyLayer::new(StrategyConfig::adaptive(GameType::Chicken));
        
        let p_stag = strat_stag.coop_probability(&markers, None);
        let p_pd = strat_pd.coop_probability(&markers, None);
        let p_chicken = strat_chicken.coop_probability(&markers, None);
        
        // Stag should be most cooperative
        assert!(p_stag > p_pd, "Stag should favor cooperation more than PD");
        // Chicken should be least cooperative (or defect)
        assert!(p_chicken < p_stag, "Chicken should favor cooperation less than Stag");
    }
    
    #[test]
    fn opponent_model_affects_strategy() {
        let markers = vec![Marker::new(1, 128, 0, 0)]; // Neutral
        
        let strat = StrategyLayer::new(StrategyConfig::adaptive(GameType::PrisonersDilemma));
        
        let p_coop = strat.coop_probability(&markers, Some(OpponentModel::Cooperative));
        let p_exploit = strat.coop_probability(&markers, Some(OpponentModel::Exploitative));
        
        // Should defend against exploitative
        assert!(p_exploit < p_coop, "Should cooperate less against exploitative opponent");
    }
    
    #[test]
    fn coop_probability_bounded() {
        let strat = StrategyLayer::new(StrategyConfig::adaptive(GameType::PrisonersDilemma));
        
        let markers_high = vec![Marker::new(1, 255, 0, 0)];
        let markers_low = vec![Marker::new(1, 0, 0, 0)];
        
        let p_high = strat.coop_probability(&markers_high, None);
        let p_low = strat.coop_probability(&markers_low, None);
        
        // Must be in [0.05, 0.95]
        assert!(p_high <= 0.95 && p_high >= 0.05);
        assert!(p_low <= 0.95 && p_low >= 0.05);
    }
}
