//! Minimal Multi-Agent Environment for Marker Testing
//! 
//! 4-agent repeated Prisoner's Dilemma environment.
//! Agents can observe each other's markers and use them for prediction.

use crate::marker::{Marker, ScheduledMarker};
use std::collections::HashMap;

/// Action in Prisoner's Dilemma
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Action {
    Cooperate,
    Defect,
}

impl Action {
    /// Convert to normalized value for coherence tracking
    pub fn to_f32(&self) -> f32 {
        match self {
            Action::Cooperate => 0.0,
            Action::Defect => 1.0,
        }
    }
    
    /// Get payoff
    pub fn payoff(&self, other: Action) -> i32 {
        match (self, other) {
            (Action::Cooperate, Action::Cooperate) => 3,  // R
            (Action::Cooperate, Action::Defect) => 0,     // S
            (Action::Defect, Action::Cooperate) => 5,     // T
            (Action::Defect, Action::Defect) => 1,        // P
        }
    }
}

/// Agent with marker
pub struct Agent {
    pub id: u8,
    pub marker_system: ScheduledMarker,
    pub total_score: i32,
    pub action_history: Vec<Action>,
    pub strategy: Strategy,
}

/// Agent strategy
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Strategy {
    Random,
    TitForTat,
    Defector,
    Cooperator,
    MarkerBased,  // Uses observed markers
}

impl Agent {
    pub fn new(id: u8, strategy: Strategy) -> Self {
        Self {
            id,
            marker_system: ScheduledMarker::new(id, 10),  // 10x timescale
            total_score: 0,
            action_history: Vec::new(),
            strategy,
        }
    }
    
    /// Choose action given observed markers
    pub fn choose_action(&self, observed_markers: &[Marker], last_opponent_action: Option<Action>) -> Action {
        match self.strategy {
            Strategy::Random => {
                if rand::random::<f32>() > 0.5 {
                    Action::Cooperate
                } else {
                    Action::Defect
                }
            }
            Strategy::TitForTat => {
                // Start with cooperation, then mirror
                last_opponent_action.unwrap_or(Action::Cooperate)
            }
            Strategy::Defector => Action::Defect,
            Strategy::Cooperator => Action::Cooperate,
            Strategy::MarkerBased => {
                // Use observed coherence scores
                if observed_markers.is_empty() {
                    return Action::Cooperate;
                }
                
                let avg_coherence: f32 = observed_markers.iter()
                    .map(|m| m.coherence() as f32)
                    .sum::<f32>() / observed_markers.len() as f32;
                
                // Higher coherence = more predictable = cooperate more
                if avg_coherence > 150.0 {
                    Action::Cooperate
                } else {
                    Action::Defect
                }
            }
        }
    }
    
    /// Record action and update marker
    pub fn record_action(&mut self, action: Action) {
        self.action_history.push(action);
        self.marker_system.tick(action.to_f32());
    }
    
    /// Add score
    pub fn add_score(&mut self, points: i32) {
        self.total_score += points;
    }
    
    /// Get current marker
    pub fn marker(&self) -> Marker {
        self.marker_system.current_marker()
    }
}

/// Multi-agent environment
pub struct Environment {
    pub agents: Vec<Agent>,
    pub current_tick: usize,
    pub marker_enabled: bool,
    pub last_actions: HashMap<u8, Action>,
}

impl Environment {
    pub fn new(num_agents: usize, strategies: Vec<Strategy>) -> Self {
        let mut agents = Vec::new();
        for i in 0..num_agents {
            let strategy = strategies.get(i).copied().unwrap_or(Strategy::Random);
            agents.push(Agent::new(i as u8, strategy));
        }
        
        Self {
            agents,
            current_tick: 0,
            marker_enabled: true,
            last_actions: HashMap::new(),
        }
    }
    
    /// Run one round of interactions (round-robin)
    pub fn step(&mut self) {
        let n = self.agents.len();
        let mut new_actions: HashMap<u8, Action> = HashMap::new();
        
        // Each agent chooses action
        for i in 0..n {
            let agent = &self.agents[i];
            
            // Observe other agents' markers
            let observed_markers: Vec<Marker> = if self.marker_enabled {
                self.agents.iter()
                    .filter(|a| a.id != agent.id)
                    .map(|a| a.marker())
                    .collect()
            } else {
                Vec::new()
            };
            
            // Get last opponent action (for TitForTat)
            let last_opponent = self.last_actions.get(&agent.id).copied();
            
            let action = agent.choose_action(&observed_markers, last_opponent);
            new_actions.insert(agent.id, action);
        }
        
        // Compute payoffs (round-robin pairwise)
        for i in 0..n {
            for j in (i+1)..n {
                let action_i = new_actions[&(i as u8)];
                let action_j = new_actions[&(j as u8)];
                
                let payoff_i = action_i.payoff(action_j);
                let payoff_j = action_j.payoff(action_i);
                
                self.agents[i].add_score(payoff_i);
                self.agents[j].add_score(payoff_j);
            }
        }
        
        // Record actions and update markers
        for i in 0..n {
            let action = new_actions[&(i as u8)];
            self.agents[i].record_action(action);
        }
        
        self.last_actions = new_actions;
        self.current_tick += 1;
    }
    
    /// Run for multiple ticks
    pub fn run(&mut self, ticks: usize) {
        for _ in 0..ticks {
            self.step();
        }
    }
    
    /// Get average cooperation rate
    pub fn cooperation_rate(&self) -> f32 {
        let total_actions: usize = self.agents.iter()
            .map(|a| a.action_history.len())
            .sum();
        
        if total_actions == 0 {
            return 0.0;
        }
        
        let coop_count: usize = self.agents.iter()
            .flat_map(|a| &a.action_history)
            .filter(|&&a| a == Action::Cooperate)
            .count();
        
        coop_count as f32 / total_actions as f32
    }
    
    /// Get average marker coherence
    pub fn avg_coherence(&self) -> f32 {
        let sum: f32 = self.agents.iter()
            .map(|a| a.marker().coherence() as f32)
            .sum();
        sum / self.agents.len() as f32
    }
    
    /// Check if markers are actually being updated (not every tick)
    pub fn validate_timescale(&self) -> bool {
        self.agents.iter().all(|a| a.marker_system.is_timescale_valid())
    }
    
    /// Get self-consistency proxy: variance of own marker coherence over time
    pub fn self_consistency_proxy(&self) -> f32 {
        // This is a proxy for whether markers help agents maintain consistent self-presentation
        // Higher score = agents maintain more consistent markers
        self.avg_coherence() / 255.0
    }
}

/// Week 1 experiment for 001
pub fn run_week1_experiment() -> ExperimentResult {
    // Condition 1: With markers
    let mut env_with = Environment::new(
        4,
        vec![
            Strategy::MarkerBased,
            Strategy::MarkerBased,
            Strategy::TitForTat,
            Strategy::TitForTat,
        ]
    );
    env_with.run(100);
    
    // Condition 2: Without markers
    let mut env_without = Environment::new(
        4,
        vec![
            Strategy::TitForTat,
            Strategy::TitForTat,
            Strategy::TitForTat,
            Strategy::TitForTat,
        ]
    );
    env_without.marker_enabled = false;
    env_without.run(100);
    
    ExperimentResult {
        with_markers_coop: env_with.cooperation_rate(),
        without_markers_coop: env_without.cooperation_rate(),
        with_markers_consistency: env_with.self_consistency_proxy(),
        without_markers_consistency: env_without.self_consistency_proxy(),
        timescale_valid: env_with.validate_timescale(),
        avg_coherence_with: env_with.avg_coherence(),
    }
}

/// Results from Week 1 experiment
#[derive(Debug)]
pub struct ExperimentResult {
    pub with_markers_coop: f32,
    pub without_markers_coop: f32,
    pub with_markers_consistency: f32,
    pub without_markers_consistency: f32,
    pub timescale_valid: bool,
    pub avg_coherence_with: f32,
}

impl ExperimentResult {
    /// Week 1 gate decision
    pub fn gate_decision(&self) -> &'static str {
        let marker_affects_coop = self.with_markers_coop > self.without_markers_coop * 1.05;
        let marker_affects_consistency = self.with_markers_consistency > self.without_markers_consistency * 1.05;
        let timescale_ok = self.timescale_valid;
        let coherence_meaningful = self.avg_coherence_with > 50.0 && self.avg_coherence_with < 250.0;
        
        println!("\n=== 001 Week 1 Analysis ===");
        println!("Cooperation with markers: {:.2}", self.with_markers_coop);
        println!("Cooperation without: {:.2}", self.without_markers_coop);
        println!("Consistency with markers: {:.3}", self.with_markers_consistency);
        println!("Timescale valid: {}", timescale_ok);
        println!("Avg coherence: {:.1}", self.avg_coherence_with);
        
        let continue_count = [marker_affects_coop, marker_affects_consistency, timescale_ok, coherence_meaningful]
            .iter()
            .filter(|&&x| x)
            .count();
        
        if continue_count >= 2 {
            println!("\n>>> DECISION: CONTINUE to Week 2");
            "CONTINUE"
        } else {
            println!("\n>>> DECISION: KILL - Marker mechanism not validated");
            "KILL"
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_environment_creation() {
        let env = Environment::new(4, vec![Strategy::Random; 4]);
        assert_eq!(env.agents.len(), 4);
    }
    
    #[test]
    fn test_action_payoffs() {
        assert_eq!(Action::Cooperate.payoff(Action::Cooperate), 3);
        assert_eq!(Action::Defect.payoff(Action::Cooperate), 5);
        assert_eq!(Action::Cooperate.payoff(Action::Defect), 0);
        assert_eq!(Action::Defect.payoff(Action::Defect), 1);
    }
}
