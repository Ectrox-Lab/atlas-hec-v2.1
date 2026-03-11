//! Adaptive Policy - Dynamic Strategy Switching
//!
//! Switches policy mode based on:
//! - Current regime (game type)
//! - Opponent belief
//! - Adaptation phase (bootstrap vs online)

use crate::prior_channel::Marker;
use super::{
    opponent_tracker::{OpponentTracker, OpponentType, ShiftType},
    regime_detector::{RegimeDetector, RegimeType},
};

/// Policy operating mode
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PolicyMode {
    /// Bootstrap phase: establish coordination
    Bootstrap,
    /// Exploit cooperative opponents
    Exploit,
    /// Defend against exploitative opponents
    Defend,
    /// Mixed strategy for uncertain opponents
    Mixed,
    /// Recovery after regime shift
    Recovery,
}

/// Adaptive policy state
pub struct AdaptivePolicy {
    /// Current mode
    mode: PolicyMode,
    /// Current game regime
    regime: RegimeType,
    /// Opponent tracker
    opponent_tracker: OpponentTracker,
    /// Regime detector
    regime_detector: RegimeDetector,
    /// Current round
    round: usize,
    /// Bootstrap duration (game-specific)
    bootstrap_rounds: usize,
    /// Last shift detection round
    last_shift_round: Option<usize>,
}

impl AdaptivePolicy {
    pub fn new(game_hint: RegimeType) -> Self {
        let bootstrap_rounds = match game_hint {
            RegimeType::PrisonersDilemma => 400,
            RegimeType::StagHunt => 200,
            RegimeType::Chicken => 100,
            RegimeType::Unknown => 200,
        };
        
        Self {
            mode: PolicyMode::Bootstrap,
            regime: game_hint,
            opponent_tracker: OpponentTracker::new(50),
            regime_detector: RegimeDetector::new(),
            round: 0,
            bootstrap_rounds,
            last_shift_round: None,
        }
    }
    
    /// Update state with new observations
    pub fn update(
        &mut self,
        my_action: i32,
        opponent_action: i32,
        payoff: i32,
        marker: Marker,
    ) {
        self.round += 1;
        
        // Update opponent tracker
        self.opponent_tracker.observe(opponent_action as f32, marker);
        
        // Update regime detector
        self.regime_detector.observe_payoff(my_action, opponent_action, payoff);
        
        // Check for regime shift
        if let Some(new_regime) = detect_regime_shift_from_detector(&self.regime_detector) {
            if new_regime != self.regime {
                self.regime = new_regime;
                self.mode = PolicyMode::Recovery;
                self.last_shift_round = Some(self.round);
                // Adjust bootstrap for recovery
                self.bootstrap_rounds = self.round + 100;
            }
        }
        
        // Check for opponent behavior shift
        if let Some(shift) = self.opponent_tracker.detect_shift(10) {
            self.mode = PolicyMode::Recovery;
            self.bootstrap_rounds = self.round + 50;
        }
        
        // Update mode based on current state
        self.update_mode();
    }
    
    /// Select action based on current mode
    pub fn select_action(&self, markers: &[Marker], agent_id: usize) -> f32 {
        select_adaptive_action(
            self.mode,
            self.regime,
            self.opponent_tracker.belief(),
            markers,
            self.round,
            self.bootstrap_rounds,
            agent_id,
        )
    }
    
    /// Get current mode
    pub fn mode(&self) -> PolicyMode {
        self.mode
    }
    
    /// Get current regime
    pub fn regime(&self) -> RegimeType {
        self.regime
    }
    
    /// Check if in recovery
    pub fn is_recovering(&self) -> bool {
        matches!(self.mode, PolicyMode::Recovery)
    }
    
    /// Get adaptation state for metrics
    pub fn adaptation_state(&self) -> AdaptationState {
        AdaptationState {
            round: self.round,
            mode: self.mode,
            regime: self.regime,
            opponent_belief: self.opponent_tracker.belief().clone(),
            confidence: self.regime_detector.confidence(),
        }
    }
    
    /// Update policy mode based on current state
    fn update_mode(&mut self) {
        // Bootstrap phase
        if self.round < self.bootstrap_rounds {
            self.mode = PolicyMode::Bootstrap;
            return;
        }
        
        // Recovery phase
        if let Some(shift_round) = self.last_shift_round {
            if self.round < shift_round + 50 {
                self.mode = PolicyMode::Recovery;
                return;
            }
        }
        
        // Normal operation: mode based on opponent belief
        let belief = self.opponent_tracker.belief();
        
        if belief.is_confident(0.6) {
            self.mode = match belief.most_likely() {
                OpponentType::Cooperative => PolicyMode::Exploit,
                OpponentType::Exploitative => PolicyMode::Defend,
                OpponentType::Random => PolicyMode::Mixed,
            };
        } else {
            self.mode = PolicyMode::Mixed;
        }
    }
}

/// Detect regime shift from detector state
fn detect_regime_shift_from_detector(detector: &RegimeDetector) -> Option<RegimeType> {
    if detector.is_confident() {
        let regime = detector.current_regime();
        if regime != RegimeType::Unknown {
            return Some(regime);
        }
    }
    None
}

/// Select action based on adaptive parameters
pub fn select_adaptive_action(
    mode: PolicyMode,
    regime: RegimeType,
    opponent_belief: &super::opponent_tracker::BeliefState,
    markers: &[Marker],
    round: usize,
    bootstrap_rounds: usize,
    agent_id: usize,
) -> f32 {
    match mode {
        PolicyMode::Bootstrap => bootstrap_action(regime, round, bootstrap_rounds, agent_id),
        PolicyMode::Exploit => exploit_action(regime, opponent_belief, agent_id),
        PolicyMode::Defend => defend_action(regime, opponent_belief, agent_id),
        PolicyMode::Mixed => mixed_action(regime, opponent_belief, agent_id),
        PolicyMode::Recovery => recovery_action(regime, round, agent_id),
    }
}

/// Bootstrap phase: establish coordination
fn bootstrap_action(regime: RegimeType, round: usize, bootstrap_rounds: usize, agent_id: usize) -> f32 {
    let progress = round as f32 / bootstrap_rounds as f32;
    
    match regime {
        RegimeType::PrisonersDilemma => {
            // High cooperation early, gradual reduction
            0.85 - 0.35 * progress
        }
        RegimeType::StagHunt => {
            // Very high cooperation
            0.80 - 0.20 * progress
        }
        RegimeType::Chicken => {
            // Moderate cooperation with agent diversity
            let base = [0.60, 0.65, 0.70, 0.75][agent_id % 4];
            base - 0.20 * progress
        }
        RegimeType::Unknown => 0.60,
    }
}

/// Exploit cooperative opponents
fn exploit_action(
    regime: RegimeType,
    belief: &super::opponent_tracker::BeliefState,
    agent_id: usize,
) -> f32 {
    match regime {
        RegimeType::PrisonersDilemma => {
            // Defect against cooperative opponent
            0.25
        }
        RegimeType::StagHunt => {
            // Cooperate to maintain mutual benefit
            0.70
        }
        RegimeType::Chicken => {
            // Mixed, slight cooperation
            [0.45, 0.50, 0.55, 0.60][agent_id % 4]
        }
        RegimeType::Unknown => 0.50,
    }
}

/// Defend against exploitative opponents
fn defend_action(
    regime: RegimeType,
    belief: &super::opponent_tracker::BeliefState,
    agent_id: usize,
) -> f32 {
    match regime {
        RegimeType::PrisonersDilemma => {
            // Defect to avoid being exploited
            0.15
        }
        RegimeType::StagHunt => {
            // Safer to defect (rabbit hunt)
            0.30
        }
        RegimeType::Chicken => {
            // Cooperate to avoid crash
            0.55
        }
        RegimeType::Unknown => 0.40,
    }
}

/// Mixed strategy for uncertain opponents
fn mixed_action(
    regime: RegimeType,
    belief: &super::opponent_tracker::BeliefState,
    agent_id: usize,
) -> f32 {
    match regime {
        RegimeType::PrisonersDilemma => {
            // Balanced
            0.40
        }
        RegimeType::StagHunt => {
            // Slight cooperation bias
            0.55
        }
        RegimeType::Chicken => {
            // Pure mixed with diversity
            [0.45, 0.50, 0.55, 0.60][agent_id % 4]
        }
        RegimeType::Unknown => 0.50,
    }
}

/// Recovery after shift: rapid re-coordination
fn recovery_action(regime: RegimeType, round: usize, agent_id: usize) -> f32 {
    // Quick cooperation to re-establish
    match regime {
        RegimeType::PrisonersDilemma => 0.70,
        RegimeType::StagHunt => 0.75,
        RegimeType::Chicken => [0.50, 0.55, 0.60, 0.65][agent_id % 4],
        RegimeType::Unknown => 0.60,
    }
}

/// Adaptation state snapshot
#[derive(Clone, Debug)]
pub struct AdaptationState {
    pub round: usize,
    pub mode: PolicyMode,
    pub regime: RegimeType,
    pub opponent_belief: super::opponent_tracker::BeliefState,
    pub confidence: f32,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn starts_in_bootstrap() {
        let policy = AdaptivePolicy::new(RegimeType::PrisonersDilemma);
        assert_eq!(policy.mode(), PolicyMode::Bootstrap);
    }
    
    #[test]
    fn bootstrap_cooperation_high() {
        let coop = bootstrap_action(RegimeType::PrisonersDilemma, 0, 400, 0);
        assert!(coop > 0.8);
    }
    
    #[test]
    fn exploit_pd_defects() {
        use super::super::opponent_tracker::BeliefState;
        
        let belief = BeliefState::new();
        let coop = exploit_action(RegimeType::PrisonersDilemma, &belief, 0);
        assert!(coop < 0.3);
    }
}
