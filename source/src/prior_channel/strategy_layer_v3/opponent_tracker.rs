//! Online Opponent Belief Update
//!
//! Tracks opponent behavior in real-time using Bayesian-like updating.
//! Key improvement over v2: maintains belief distribution, not just point estimate.

use crate::prior_channel::Marker;

/// Belief state about opponent type
#[derive(Clone, Debug)]
pub struct BeliefState {
    /// Probability opponent is cooperative (0-1)
    pub p_cooperative: f32,
    /// Probability opponent is exploitative (0-1)
    pub p_exploitative: f32,
    /// Probability opponent is random/baseline (0-1)
    pub p_random: f32,
    /// Confidence in belief (entropy-based)
    pub confidence: f32,
    /// Last update timestamp
    pub last_update: usize,
}

impl BeliefState {
    pub fn new() -> Self {
        Self {
            p_cooperative: 0.33,
            p_exploitative: 0.33,
            p_random: 0.34,
            confidence: 0.0,
            last_update: 0,
        }
    }
    
    /// Get most likely opponent type
    pub fn most_likely(&self) -> OpponentType {
        if self.p_cooperative > self.p_exploitative && self.p_cooperative > self.p_random {
            OpponentType::Cooperative
        } else if self.p_exploitative > self.p_random {
            OpponentType::Exploitative
        } else {
            OpponentType::Random
        }
    }
    
    /// Check if belief is confident enough to act on
    pub fn is_confident(&self, threshold: f32) -> bool {
        self.confidence >= threshold
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OpponentType {
    Cooperative,
    Exploitative,
    Random,
}

/// Online opponent tracker with sliding window
pub struct OpponentTracker {
    /// History of observed opponent actions (C=0, D=1)
    action_history: Vec<f32>,
    /// History of opponent markers
    marker_history: Vec<Marker>,
    /// Current belief state
    belief: BeliefState,
    /// Window size for online updates
    window_size: usize,
    /// Current round
    current_round: usize,
}

impl OpponentTracker {
    pub fn new(window_size: usize) -> Self {
        Self {
            action_history: Vec::new(),
            marker_history: Vec::new(),
            belief: BeliefState::new(),
            window_size,
            current_round: 0,
        }
    }
    
    /// Observe opponent action and update belief
    pub fn observe(&mut self, opponent_action: f32, marker: Marker) {
        self.action_history.push(opponent_action);
        self.marker_history.push(marker);
        self.current_round += 1;
        
        // Maintain sliding window
        if self.action_history.len() > self.window_size {
            self.action_history.remove(0);
            self.marker_history.remove(0);
        }
        
        // Update belief
        self.belief = update_belief(&self.action_history, &self.marker_history, &self.belief);
        self.belief.last_update = self.current_round;
    }
    
    /// Get current belief
    pub fn belief(&self) -> &BeliefState {
        &self.belief
    }
    
    /// Detect sudden shift in opponent behavior
    pub fn detect_shift(&self, recent_window: usize) -> Option<ShiftType> {
        if self.action_history.len() < recent_window * 2 {
            return None;
        }
        
        let old_start = self.action_history.len() - recent_window * 2;
        let old_end = self.action_history.len() - recent_window;
        let recent_start = self.action_history.len() - recent_window;
        
        let old_coop_rate = 1.0 - self.action_history[old_start..old_end].iter().sum::<f32>() 
            / recent_window as f32;
        let recent_coop_rate = 1.0 - self.action_history[recent_start..].iter().sum::<f32>() 
            / recent_window as f32;
        
        let shift_magnitude = (recent_coop_rate - old_coop_rate).abs();
        
        if shift_magnitude > 0.3 {
            if recent_coop_rate > old_coop_rate {
                Some(ShiftType::ToCooperation)
            } else {
                Some(ShiftType::ToDefection)
            }
        } else {
            None
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ShiftType {
    ToCooperation,
    ToDefection,
}

/// Bayesian-like belief update
pub fn update_belief(
    actions: &[f32],
    markers: &[Marker],
    prior: &BeliefState,
) -> BeliefState {
    if actions.len() < 5 {
        return prior.clone();
    }
    
    // Compute recent statistics
    let recent_actions = &actions[actions.len().saturating_sub(20)..];
    let coop_rate = 1.0 - recent_actions.iter().sum::<f32>() / recent_actions.len() as f32;
    
    let recent_markers = &markers[markers.len().saturating_sub(20)..];
    let avg_coherence = recent_markers.iter()
        .map(|m| m.coherence() as f32 / 255.0)
        .sum::<f32>() / recent_markers.len() as f32;
    
    // Likelihood of observations given each opponent type
    // Cooperative: high coop rate, high coherence
    let likelihood_coop = coop_rate * avg_coherence;
    
    // Exploitative: low coop rate (exploits), variable coherence
    let likelihood_exploit = (1.0 - coop_rate) * (1.0 - (avg_coherence - 0.5).abs() * 2.0);
    
    // Random: coop rate ~0.5, low coherence
    let likelihood_random = (1.0 - (coop_rate - 0.5).abs() * 2.0) * (1.0 - avg_coherence);
    
    // Normalize likelihoods
    let total = likelihood_coop + likelihood_exploit + likelihood_random;
    let (l_coop, l_exploit, l_random) = if total > 0.0 {
        (likelihood_coop / total, likelihood_exploit / total, likelihood_random / total)
    } else {
        (0.33, 0.33, 0.34)
    };
    
    // Bayes update with prior
    let belief_coop = prior.p_cooperative * l_coop;
    let belief_exploit = prior.p_exploitative * l_exploit;
    let belief_random = prior.p_random * l_random;
    
    // Normalize
    let total_belief = belief_coop + belief_exploit + belief_random;
    let (p_coop, p_exploit, p_random) = if total_belief > 0.0 {
        (belief_coop / total_belief, belief_exploit / total_belief, belief_random / total_belief)
    } else {
        (0.33, 0.33, 0.34)
    };
    
    // Compute confidence (inverse entropy)
    let entropy = -(p_coop * p_coop.ln() + p_exploit * p_exploit.ln() + p_random * p_random.ln());
    let max_entropy = 1.0986; // ln(3)
    let confidence = 1.0 - (entropy / max_entropy);
    
    BeliefState {
        p_cooperative: p_coop,
        p_exploitative: p_exploit,
        p_random: p_random,
        confidence: confidence.max(0.0),
        last_update: prior.last_update,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn belief_initially_uniform() {
        let belief = BeliefState::new();
        assert!(belief.p_cooperative > 0.3 && belief.p_cooperative < 0.4);
        assert!(belief.confidence < 0.1);
    }
    
    #[test]
    fn detect_cooperative_opponent() {
        let mut tracker = OpponentTracker::new(50);
        
        // Simulate cooperative opponent (mostly C, high coherence)
        for i in 0..30 {
            let marker = Marker::new(1, 180 + (i % 10) as u8, 0, 0);
            tracker.observe(0.0, marker); // C = 0
        }
        
        assert_eq!(tracker.belief().most_likely(), OpponentType::Cooperative);
    }
    
    #[test]
    fn detect_shift_in_behavior() {
        let mut tracker = OpponentTracker::new(50);
        
        // First: cooperative behavior
        for _ in 0..20 {
            tracker.observe(0.0, Marker::new(1, 180, 0, 0));
        }
        
        // Then: sudden shift to exploitative
        for _ in 0..10 {
            tracker.observe(1.0, Marker::new(1, 100, 0, 0));
        }
        
        let shift = tracker.detect_shift(10);
        assert_eq!(shift, Some(ShiftType::ToDefection));
    }
}
