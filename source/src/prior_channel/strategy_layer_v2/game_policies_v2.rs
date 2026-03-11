//! Game-Aware Policy Table v2
//!
//! Target: ON > Baseline
//! 
//! KEY INSIGHT v2.1:
//! In homogenous population (all ON agents), agents need to COORDINATE
//! rather than all trying to exploit each other.
//! 
//! Solution: Detect population coherence and switch to coordination mode.

use crate::prior_channel::Marker;
use super::opponent_model_v2::{classify_opponent_v2, opponent_bias_v2, is_likely_random, ClassificationResult};

/// Game type for strategy selection
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum GameType {
    PD,        // Prisoner's Dilemma
    StagHunt,  // Stag Hunt
    Chicken,   // Chicken
}

/// Population type detection
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PopulationType {
    Random,       // Baseline-like (50/50, low coherence)
    Coordinated,  // All ON agents (high population coherence)
    Mixed,        // Mix of strategies
}

/// Game policy v2 with population awareness
#[derive(Clone, Debug)]
pub struct GamePolicyV2 {
    pub game: GameType,
    pub use_opponent_model: bool,
    pub population_aware: bool,
}

impl GamePolicyV2 {
    pub fn new(game: GameType) -> Self {
        Self {
            game,
            use_opponent_model: true,
            population_aware: true,
        }
    }
}

/// Detect population type from all markers
///
/// v2.3: Relaxed thresholds for early-game coordination bootstrap
pub fn detect_population(markers: &[Marker]) -> PopulationType {
    if markers.len() < 2 {
        // Early game: assume coordinated to bootstrap cooperation
        return PopulationType::Coordinated;
    }
    
    let coherence_vals: Vec<f32> = markers.iter()
        .map(|m| m.coherence() as f32 / 255.0)
        .collect();
    
    let avg = coherence_vals.iter().sum::<f32>() / coherence_vals.len() as f32;
    let variance = coherence_vals.iter()
        .map(|&c| (c - avg).powi(2))
        .sum::<f32>() / coherence_vals.len() as f32;
    
    // Population classification (relaxed thresholds)
    if avg > 0.40 && variance < 0.05 {
        // Moderate coherence, low variance = coordinated ON population
        // RELAXED from avg > 0.55 to allow early bootstrap
        PopulationType::Coordinated
    } else if avg > 0.45 && avg < 0.55 && variance > 0.04 {
        // Around 0.5, high variance = random/baseline
        PopulationType::Random
    } else {
        PopulationType::Mixed
    }
}

/// v2.1 Game bias with population awareness
///
/// KEY INSIGHT:
/// 1. Random population (Baseline): Defect to exploit
/// 2. Coordinated population (all ON): Cooperate for mutual benefit
pub fn game_bias_v2(game: GameType, coherence: f32, pop: PopulationType) -> f32 {
    match game {
        GameType::PD => {
            match pop {
                PopulationType::Random => {
                    // Against random: DEFECT to exploit their cooperation
                    // Random gives 50% C, 50% D
                    // Defecting: 0.5*5 + 0.5*1 = 3.0 avg
                    // Cooperating: 0.5*3 + 0.5*0 = 1.5 avg
                    -0.30  // Strong defection
                }
                PopulationType::Coordinated => {
                    // Against coordinated ON agents: COOPERATE!
                    // If all agents cooperate: mutual CC = 3 each
                    // If all defect: mutual DD = 1 each
                    // Cooperation beats baseline (which gets ~2.25 vs random)
                    if coherence > 0.60 {
                        0.25  // Strong cooperation
                    } else {
                        0.10  // Moderate cooperation
                    }
                }
                PopulationType::Mixed => {
                    // Mixed population: balanced approach
                    if coherence > 0.65 {
                        0.10
                    } else {
                        -0.10
                    }
                }
            }
        }
        
        GameType::StagHunt => {
            match pop {
                PopulationType::Random => {
                    // Against random: moderate cooperation
                    // Random might coordinate accidentally
                    (coherence - 0.5) * 0.8 + 0.05
                }
                PopulationType::Coordinated => {
                    // Strong coordination for mutual stag
                    if coherence > 0.55 {
                        0.35  // Very strong cooperation
                    } else {
                        0.15
                    }
                }
                PopulationType::Mixed => {
                    if coherence > 0.60 {
                        0.20
                    } else {
                        -0.05  // Safer to rabbit hunt
                    }
                }
            }
        }
        
        GameType::Chicken => {
            match pop {
                PopulationType::Random => {
                    // Against random: cooperate to avoid -10 crash
                    // Random has 25% chance of mutual DD = -10
                    0.15  // Cooperation bias
                }
                PopulationType::Coordinated => {
                    // Coordinated: can use mixed strategy
                    if coherence > 0.65 {
                        -0.10  // Slight defection (commitment)
                    } else {
                        0.20  // Cooperate to avoid crash
                    }
                }
                PopulationType::Mixed => {
                    // Mixed: cooperate more to be safe
                    0.12
                }
            }
        }
    }
}

/// Compute final cooperation probability - v2.4
///
/// KEY FIX: Extended bootstrap with sustained cooperation
pub fn coop_probability_v2(
    policy: &GamePolicyV2,
    markers: &[Marker],
    round: usize,
) -> f32 {
    // Phase 1: Bootstrap (0-200 rounds) - Sustained high cooperation
    if round < 200 {
        return 0.75;  // 75% cooperation during bootstrap
    }
    
    // Phase 2: Transition (200-500 rounds) - Gradual adjustment
    if round < 500 {
        let t = (round - 200) as f32 / 300.0;  // 0 to 1
        
        let coherence = if markers.is_empty() { 0.5 } else {
            markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
                / markers.len() as f32
        };
        
        let pop = detect_population(markers);
        let target_prob = match pop {
            PopulationType::Coordinated => 0.65,
            PopulationType::Random => 0.35,
            PopulationType::Mixed => 0.5 + (coherence - 0.5) * 0.3,
        };
        
        // Interpolate from 0.75 to target
        return 0.75 + (target_prob - 0.75) * t;
    }
    
    // Phase 3: Steady state (>500 rounds) - Full strategy
    let base = 0.5;
    let coherence = if markers.is_empty() { 0.5 } else {
        markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
            / markers.len() as f32
    };
    
    let pop = detect_population(markers);
    let game_adj = game_bias_v2(policy.game, coherence, pop);
    
    let opp_adj = if policy.use_opponent_model && pop == PopulationType::Mixed {
        opponent_bias_v2(&classify_opponent_v2(markers))
    } else { 0.0 };
    
    (base + game_adj + opp_adj).clamp(0.05, 0.95)
}

/// Policy description for logging
pub fn policy_description(game: GameType) -> &'static str {
    match game {
        GameType::PD => "Population-aware: Defect vs random, Cooperate vs coordinated",
        GameType::StagHunt => "Coordination: Cooperate with coordinated population",
        GameType::Chicken => "Risk-avoid: Cooperate vs random, mixed vs coordinated",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn pd_defect_vs_random() {
        // Against random population in PD, should defect
        let bias = game_bias_v2(GameType::PD, 0.5, PopulationType::Random);
        assert!(bias < -0.2, "PD should defect against random population");
    }
    
    #[test]
    fn pd_cooperate_vs_coordinated() {
        // Against coordinated population in PD, should cooperate
        let bias = game_bias_v2(GameType::PD, 0.7, PopulationType::Coordinated);
        assert!(bias > 0.0, "PD should cooperate with coordinated population");
    }
    
    #[test]
    fn coop_probability_bounded() {
        let policy = GamePolicyV2::new(GameType::PD);
        let markers = vec![Marker::new(1, 255, 0, 0)];
        
        let p = coop_probability_v2(&policy, &markers, 100);
        assert!(p >= 0.05 && p <= 0.95);
    }
    
    #[test]
    fn detect_coordinated_population() {
        // All high coherence, low variance = coordinated
        let markers = vec![
            Marker::new(1, 180, 0, 0),  // ~0.7
            Marker::new(1, 182, 0, 0),
            Marker::new(1, 178, 0, 0),
            Marker::new(1, 181, 0, 0),
        ];
        
        assert_eq!(detect_population(&markers), PopulationType::Coordinated);
    }
    
    #[test]
    fn detect_random_population() {
        // Around 0.5 with high variance = random
        let markers = vec![
            Marker::new(1, 160, 0, 0),  // ~0.63
            Marker::new(1, 90, 0, 0),   // ~0.35
            Marker::new(1, 155, 0, 0),  // ~0.61
            Marker::new(1, 95, 0, 0),   // ~0.37
        ];
        
        let pop = detect_population(&markers);
        // Should be either Random or Mixed depending on thresholds
        assert!(matches!(pop, PopulationType::Random | PopulationType::Mixed));
    }
}
