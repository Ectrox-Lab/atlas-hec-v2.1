//! Game-Aware Policy Table (Explicit Rules)
//!
//! Different strategies per game type.
//! Target: ON score > OFF for at least 2/3 games.

use crate::prior_channel::Marker;
use super::opponent_model::{OpponentModel, opponent_bias};

/// Game type for strategy selection
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameType {
    PD,        // Prisoner's Dilemma
    StagHunt,  // Stag Hunt
    Chicken,   // Chicken
}

/// Game-aware policy configuration
#[derive(Clone, Debug)]
pub struct GamePolicy {
    pub game: GameType,
    pub use_opponent_model: bool,
}

impl GamePolicy {
    pub fn new(game: GameType) -> Self {
        Self {
            game,
            use_opponent_model: true,
        }
    }
}

/// EXPLICIT POLICY TABLE (v1)
/// 
/// Returns cooperation probability adjustment based on game type.
/// 
/// PD:       Defensive - avoid exploitation
/// StagHunt: Cooperative - seek mutual benefit
/// Chicken:  Risk-avoiding - prevent mutual disaster
pub fn game_bias(game: GameType, coherence: f32) -> f32 {
    match game {
        // PD: Exploit OFF's cooperative tendency
        // OFF: coop = 0.5 + (c-0.5)*1.6
        // When c=0.7, OFF coop=82%; when c=0.6, OFF coop=66%
        // Strategy: defect to exploit, only cooperate at very high c
        GameType::PD => {
            if coherence > 0.80 {
                // Very high coherence -> mutual CC = 3 each, best stable outcome
                (coherence - 0.5) * 0.8
            } else if coherence > 0.50 {
                // Medium coherence -> OFF cooperates, we DEFECT to exploit
                // Temptation payoff (5) > Reward payoff (3)
                -0.25  // Strong defection bias
            } else {
                // Low coherence -> chaos, defect is safer
                (coherence - 0.5) * 0.3 - 0.15
            }
        }
        
        // Stag Hunt: Coordination game
        // Mutual CC = 4, Mutual DD = 2, Sucker = 0
        // Key: match or exceed OFF's cooperation when coherence is high
        GameType::StagHunt => {
            if coherence > 0.55 {
                // High coherence -> strong coordination for mutual stag
                // Need to be MORE cooperative than OFF
                (coherence - 0.5) * 2.0 + 0.05  // Base +0.05 bias
            } else {
                // Low coherence -> rabbit hunt (safer)
                (coherence - 0.5) * 0.5 - 0.05
            }
        }
        
        // Chicken: Avoid mutual defection (-10)!
        // Strategy: be MORE cooperative than OFF to avoid crashes
        GameType::Chicken => {
            if coherence > 0.60 {
                // High coherence -> moderate cooperation
                (coherence - 0.5) * 0.8
            } else {
                // Low coherence -> increase cooperation to avoid -10
                // Better to get 0 or -1 than -10
                (coherence - 0.5) * 0.4 + 0.15  // Strong coop bias
            }
        }
    }
}

/// Compute final cooperation probability
/// 
/// Combines: base + game_bias + opponent_bias
pub fn coop_probability(
    policy: &GamePolicy,
    markers: &[Marker],
    opponent: Option<OpponentModel>,
) -> f32 {
    let base = 0.5;
    
    // Coherence signal from markers
    let coherence = if markers.is_empty() {
        0.5
    } else {
        markers.iter()
            .map(|m| m.coherence() as f32 / 255.0)
            .sum::<f32>() / markers.len() as f32
    };
    
    // Game-specific bias
    let game_adj = game_bias(policy.game, coherence);
    
    // Opponent-model bias
    let opp_adj = if policy.use_opponent_model {
        opponent.map(opponent_bias).unwrap_or(0.0)
    } else {
        0.0
    };
    
    // Combine and clamp
    (base + game_adj + opp_adj).clamp(0.05, 0.95)
}

/// Policy description for logging
pub fn policy_description(game: GameType) -> &'static str {
    match game {
        GameType::PD => "Defensive - avoid exploitation",
        GameType::StagHunt => "Cooperative - seek mutual benefit",
        GameType::Chicken => "Risk-avoiding - prevent mutual disaster",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn stag_most_cooperative() {
        let coherence = 0.8;
        let b_stag = game_bias(GameType::StagHunt, coherence);
        let b_pd = game_bias(GameType::PD, coherence);
        let b_chicken = game_bias(GameType::Chicken, coherence);
        
        assert!(b_stag > b_pd, "Stag should be more cooperative than PD");
        assert!(b_stag > b_chicken, "Stag should be more cooperative than Chicken");
    }
    
    #[test]
    fn chicken_risk_avoiding() {
        // Chicken: avoid mutual defection (-10)
        // Low coherence -> cooperate more to avoid crashes
        let coherence_low = 0.3;
        let b_low = game_bias(GameType::Chicken, coherence_low);
        
        // At low coherence, should bias toward cooperation
        assert!(b_low > -0.1, "Chicken should avoid strong defection at low coherence");
    }
    
    #[test]
    fn pd_defensive() {
        // PD: exploit OFF's cooperation
        let coherence_low = 0.4;
        let coherence_med = 0.6;
        
        let b_low = game_bias(GameType::PD, coherence_low);
        let b_med = game_bias(GameType::PD, coherence_med);
        
        // At medium coherence, should defect to exploit
        assert!(b_med < 0.0, "PD should defect at medium coherence to exploit OFF");
        // At low coherence, also defect (safer)
        assert!(b_low < 0.0, "PD should defect at low coherence");
    }
    
    #[test]
    fn coop_probability_bounded() {
        let policy = GamePolicy::new(GameType::PD);
        let markers = vec![Marker::new(1, 255, 0, 0)];
        
        let p = coop_probability(&policy, &markers, None);
        assert!(p >= 0.05 && p <= 0.95);
    }
}
