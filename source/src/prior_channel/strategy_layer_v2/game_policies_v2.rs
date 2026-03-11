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

/// v2.9 Game bias with population awareness + agent diversity
///
/// KEY INSIGHT:
/// 1. Random population (Baseline): Defect to exploit
/// 2. Coordinated population (all ON): Cooperate for mutual benefit
/// 3. Chicken: needs agent diversity to avoid correlated crashes
pub fn game_bias_v2(game: GameType, coherence: f32, pop: PopulationType, agent_id: usize) -> f32 {
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
                    // v2.11 PD: Always high cooperation
                    // Remove threshold to maximize CC time
                    0.42  // Maximum sustained cooperation
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
            // v2.9: PURE MIXED STRATEGY for Chicken
            // Key insight: Chicken rewards anti-correlation
            // If all agents use same deterministic logic → crash
            // Solution: Fixed mixed strategy + agent diversity
            let base_rates = [0.45, 0.50, 0.55, 0.60];  // Different for each agent
            let base = base_rates[agent_id % 4];
            
            match pop {
                PopulationType::Random => {
                    // Against random: slightly more defection
                    base - 0.10
                }
                PopulationType::Coordinated => {
                    // Coordinated: can optimize slightly
                    if coherence > 0.50 { base + 0.05 } else { base }
                }
                PopulationType::Mixed => {
                    base  // Pure mixed
                }
            }
        }
    }
}

/// Compute final cooperation probability - v2.8
///
/// KEY FIX: Game-specific bootstrap + agent diversity for Chicken
pub fn coop_probability_v2(
    policy: &GamePolicyV2,
    markers: &[Marker],
    round: usize,
    agent_id: usize,  // NEW: for anti-correlation
) -> f32 {
    // Game-specific bootstrap parameters
    let (bootstrap_rounds, bootstrap_coop, transition_rounds) = match policy.game {
        // Chicken: Shorter bootstrap, lower cooperation to avoid crash buildup
        GameType::Chicken => (100, 0.60, 200),
        // PD: Extended bootstrap for mutual CC establishment
        GameType::PD => (400, 0.85, 250),
        // Stag: Standard
        _ => (200, 0.75, 300),
    };
    
    let transition_end = bootstrap_rounds + transition_rounds;
    
    // Phase 1: Bootstrap
    if round < bootstrap_rounds {
        return bootstrap_coop;
    }
    
    // Phase 2: Transition
    if round < transition_end {
        let t = (round - bootstrap_rounds) as f32 / transition_rounds as f32;
        
        let coherence = if markers.is_empty() { 0.5 } else {
            markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
                / markers.len() as f32
        };
        
        let pop = detect_population(markers);
        let target_prob = match (policy.game, pop) {
            // Chicken: use game_bias_v2 for target
            (GameType::Chicken, _) => {
                0.5 + game_bias_v2(policy.game, coherence, pop, agent_id)
            }
            // Others
            (_, PopulationType::Coordinated) => 0.65,
            (_, PopulationType::Random) => 0.35,
            (_, PopulationType::Mixed) => 0.5 + (coherence - 0.5) * 0.3,
        };
        
        return bootstrap_coop + (target_prob - bootstrap_coop) * t;
    }
    
    // Phase 3: Steady state
    let base = 0.5;
    let coherence = if markers.is_empty() { 0.5 } else {
        markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
            / markers.len() as f32
    };
    
    let pop = detect_population(markers);
    let game_adj = game_bias_v2(policy.game, coherence, pop, agent_id);
    
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
        
        let p = coop_probability_v2(&policy, &markers, 100, 0);
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
