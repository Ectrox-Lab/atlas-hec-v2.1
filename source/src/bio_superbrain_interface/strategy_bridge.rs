//! Strategy Bridge - Connecting Strategy Layer to Bio-World (Simplified v0)

use super::cell_adapter::{CellAction, NeighborhoodContext};

/// Bio-World specific decision context
pub struct BioDecisionContext {
    /// Local energy level
    pub energy: f32,
    /// Local population density
    pub density: f32,
    /// Recent payoff history
    pub payoff_history: Vec<i32>,
}

/// Strategy bridge for Bio-World integration
pub struct StrategyBridge {
    /// Current cooperation probability
    coop_prob: f32,
}

impl StrategyBridge {
    pub fn new() -> Self {
        Self {
            coop_prob: 0.5,
        }
    }
    
    /// Decide action based on Bio-World context
    pub fn decide(&mut self, context: &BioDecisionContext, _agent_id: usize) -> CellAction {
        // Bio-World specific adjustments
        let adjusted_prob = self.bio_adjust(self.coop_prob, context);
        
        // Simple decision
        if context.energy > adjusted_prob {
            CellAction::Cooperate
        } else {
            CellAction::Defect
        }
    }
    
    /// Bio-World specific probability adjustment
    fn bio_adjust(&self, base_prob: f32, context: &BioDecisionContext) -> f32 {
        let mut adjusted = base_prob;
        
        // Energy constraint: low energy → less likely to cooperate (risky)
        if context.energy < 0.3 {
            adjusted *= 0.8; // Reduce cooperation when starving
        }
        
        // Density constraint: very high density → more defection (competition)
        if context.density > 0.8 {
            adjusted *= 0.9;
        }
        
        // Payoff trend: negative recent payoffs → adapt
        if context.payoff_history.len() >= 5 {
            let recent: i32 = context.payoff_history.iter().rev().take(5).sum();
            if recent < 0 {
                adjusted *= 0.85; // Reduce cooperation if losing
            }
        }
        
        adjusted.clamp(0.05, 0.95)
    }
    
    /// Update with outcome
    pub fn update(&mut self, my_action: CellAction, payoff: i32) {
        // Simple learning: adjust based on payoff
        match my_action {
            CellAction::Cooperate => {
                if payoff > 0 {
                    self.coop_prob = (self.coop_prob + 0.05).min(0.95);
                } else {
                    self.coop_prob = (self.coop_prob - 0.05).max(0.05);
                }
            }
            CellAction::Defect => {
                if payoff > 0 {
                    self.coop_prob = (self.coop_prob - 0.05).max(0.05);
                } else {
                    self.coop_prob = (self.coop_prob + 0.05).min(0.95);
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn bridge_creation() {
        let bridge = StrategyBridge::new();
        assert_eq!(bridge.coop_prob, 0.5);
    }
    
    #[test]
    fn bio_adjust_energy() {
        let bridge = StrategyBridge::new();
        let ctx = BioDecisionContext {
            energy: 0.2,
            density: 0.5,
            payoff_history: vec![],
        };
        let adjusted = bridge.bio_adjust(0.5, &ctx);
        assert!(adjusted < 0.5);
    }
}
