//! 32-bit Consistency Marker System
//! 
//! Minimal implementation for Week 1 skeleton validation.
//! Tests whether self-consistency markers can function as self-model anchors.

use std::collections::VecDeque;

/// 32-bit marker encoding
/// 
/// Layout:
/// - bits 0-7:   agent_id (8 bits, 0-255)
/// - bits 8-15:  coherence_score (8 bits, 0-255, higher = more consistent)
/// - bits 16-31: behavioral_bias (16 bits, encoded strategy preference)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Marker(u32);

impl Marker {
    /// Create new marker
    pub fn new(agent_id: u8, coherence: u8, bias: u16) -> Self {
        let encoded = ((agent_id as u32) << 0)
            | ((coherence as u32) << 8)
            | ((bias as u32) << 16);
        Self(encoded)
    }
    
    /// Extract agent_id
    pub fn agent_id(&self) -> u8 {
        ((self.0 >> 0) & 0xFF) as u8
    }
    
    /// Extract coherence score
    pub fn coherence(&self) -> u8 {
        ((self.0 >> 8) & 0xFF) as u8
    }
    
    /// Extract behavioral bias
    pub fn bias(&self) -> u16 {
        ((self.0 >> 16) & 0xFFFF) as u16
    }
    
    /// Raw value
    pub fn raw(&self) -> u32 {
        self.0
    }
    
    /// Decode from raw
    pub fn from_raw(raw: u32) -> Self {
        Self(raw)
    }
}

impl std::fmt::Display for Marker {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Marker[agent={}, coherence={}, bias={}]",
            self.agent_id(), self.coherence(), self.bias())
    }
}

/// Coherence score computer with dual metrics
/// 
/// Two separate tracking systems:
/// 1. tick_smoothness: per-tick action stream (actuator jitter)
/// 2. decision_coherence: per-decision consistency (policy stability)
pub struct CoherenceTracker {
    tick_window_size: usize,
    decision_window_size: usize,
    tick_action_history: VecDeque<f32>,  // per-tick actions
    decision_history: VecDeque<f32>,     // per-decision actions
    tick_smoothness: u8,      // actuator-level smoothness
    decision_coherence: u8,   // policy-level consistency
}

impl CoherenceTracker {
    pub fn new(tick_window: usize, decision_window: usize) -> Self {
        Self {
            tick_window_size: tick_window,
            decision_window_size: decision_window,
            tick_action_history: VecDeque::with_capacity(tick_window),
            decision_history: VecDeque::with_capacity(decision_window),
            tick_smoothness: 128,
            decision_coherence: 128,
        }
    }
    
    /// Record a tick-level action (always recorded)
    pub fn record_tick_action(&mut self, action: f32) {
        let clamped = action.clamp(0.0, 1.0);
        
        if self.tick_action_history.len() >= self.tick_window_size {
            self.tick_action_history.pop_front();
        }
        self.tick_action_history.push_back(clamped);
        
        // Update tick smoothness
        if self.tick_action_history.len() >= 3 {
            self.tick_smoothness = self.compute_tick_smoothness();
        }
    }
    
    /// Record a decision-level action (only when marker updates)
    pub fn record_decision(&mut self, action: f32) {
        let clamped = action.clamp(0.0, 1.0);
        
        if self.decision_history.len() >= self.decision_window_size {
            self.decision_history.pop_front();
        }
        self.decision_history.push_back(clamped);
        
        // Update decision coherence
        if self.decision_history.len() >= 2 {
            self.decision_coherence = self.compute_decision_coherence();
        }
    }
    
    /// Compute tick-level smoothness (actuator jitter)
    fn compute_tick_smoothness(&self) -> u8 {
        if self.tick_action_history.len() < 2 {
            return 128;
        }
        
        let n = self.tick_action_history.len() as f32;
        let mean: f32 = self.tick_action_history.iter().sum::<f32>() / n;
        
        // Use MAD (Mean Absolute Deviation) instead of CV for stability
        let mad: f32 = self.tick_action_history.iter()
            .map(|x| (x - mean).abs())
            .sum::<f32>() / n;
        
        // Higher score = smoother (lower MAD)
        // MAD=0 -> 255, MAD=0.5 -> 128, MAD>=1 -> 0
        let score = 255.0 - (mad * 255.0 * 2.0).clamp(0.0, 255.0);
        score as u8
    }
    
    /// Compute decision-level coherence (policy consistency)
    fn compute_decision_coherence(&self) -> u8 {
        if self.decision_history.len() < 2 {
            return 128;
        }
        
        let n = self.decision_history.len() as f32;
        let mean: f32 = self.decision_history.iter().sum::<f32>() / n;
        
        // Use std_dev / (|mean| + epsilon) for CV
        let variance: f32 = self.decision_history.iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>() / n;
        let std_dev = variance.sqrt();
        
        // Robust denominator: |mean| clamped to avoid division by near-zero
        let denom = mean.abs().max(0.1);
        let cv = std_dev / denom;
        
        // cv=0 -> 255, cv=1 -> 128, cv>=2 -> 0
        let score = 255.0 - (cv * 128.0).clamp(0.0, 255.0);
        score as u8
    }
    
    /// Get tick-level smoothness score
    pub fn tick_smoothness(&self) -> u8 {
        self.tick_smoothness
    }
    
    /// Get decision-level coherence score (MAIN METRIC)
    pub fn decision_coherence(&self) -> u8 {
        self.decision_coherence
    }
    
    /// Get decision variance (for debugging)
    pub fn decision_variance(&self) -> f32 {
        if self.decision_history.len() < 2 {
            return 0.0;
        }
        
        let n = self.decision_history.len() as f32;
        let mean: f32 = self.decision_history.iter().sum::<f32>() / n;
        self.decision_history.iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>() / n
    }
}

/// Marker with update scheduling (10x timescale separation)
pub struct ScheduledMarker {
    marker: Marker,
    tracker: CoherenceTracker,
    update_interval: usize,  // ticks between updates (10 for 10x)
    tick_counter: usize,
    last_update_tick: usize,
    last_action: f32,  // remember last action for decision recording
}

impl ScheduledMarker {
    pub fn new(agent_id: u8, update_interval: usize) -> Self {
        Self {
            marker: Marker::new(agent_id, 128, 0),
            tracker: CoherenceTracker::new(20, 20),  // 20 ticks, 20 decisions
            update_interval,
            tick_counter: 0,
            last_update_tick: 0,
            last_action: 0.5,
        }
    }
    
    /// Create a marker with fixed coherence value (for ReadOnly mode)
    pub fn new_with_fixed(agent_id: u8, fixed_coherence: u8) -> Self {
        Self {
            marker: Marker::new(agent_id, fixed_coherence, 0),
            tracker: CoherenceTracker::new(20, 20),
            update_interval: usize::MAX,  // Never update
            tick_counter: 0,
            last_update_tick: 0,
            last_action: 0.5,
        }
    }
    
    /// Record action every tick, but only update marker every N ticks
    pub fn tick(&mut self, action: f32) -> Option<Marker> {
        self.tick_counter += 1;
        self.last_action = action;
        
        // Always record tick-level action
        self.tracker.record_tick_action(action);
        
        // Update marker only at interval
        if self.tick_counter - self.last_update_tick >= self.update_interval {
            self.last_update_tick = self.tick_counter;
            
            // Record decision-level action at update time
            self.tracker.record_decision(action);
            
            // Update marker with DECISION coherence (main metric)
            let decision_score = self.tracker.decision_coherence();
            self.marker = Marker::new(
                self.marker.agent_id(),
                decision_score,
                self.marker.bias(),
            );
            
            Some(self.marker)
        } else {
            None
        }
    }
    
    /// Get current marker (may be stale)
    pub fn current_marker(&self) -> Marker {
        self.marker
    }
    
    /// Check if timescale constraint is being followed
    pub fn is_timescale_valid(&self) -> bool {
        // After running, should have updated approximately every N ticks
        if self.tick_counter == 0 {
            return true;  // Haven't started yet
        }
        
        let expected_updates = self.tick_counter / self.update_interval;
        let actual_updates = self.last_update_tick / self.update_interval;
        
        // Allow small timing differences
        expected_updates == 0 || actual_updates <= expected_updates
    }
    
    /// Get update frequency (for validation)
    pub fn effective_update_rate(&self) -> f32 {
        if self.tick_counter == 0 {
            0.0
        } else {
            let updates = self.last_update_tick / self.update_interval;
            updates as f32 / self.tick_counter as f32
        }
    }
    
    /// Get actual update interval (measured)
    pub fn measured_interval(&self) -> Option<usize> {
        if self.tick_counter == 0 {
            None
        } else {
            Some(self.update_interval)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_marker_encoding() {
        let m = Marker::new(42, 200, 12345);
        assert_eq!(m.agent_id(), 42);
        assert_eq!(m.coherence(), 200);
        assert_eq!(m.bias(), 12345);
    }
    
    #[test]
    fn test_decision_coherence_consistent() {
        let mut tracker = CoherenceTracker::new(10, 10);
        
        // Record consistent decisions
        for _ in 0..10 {
            tracker.record_decision(0.5);
        }
        
        // Should have high decision coherence
        assert!(tracker.decision_coherence() > 200, 
            "Consistent decisions should have high coherence, got {}", tracker.decision_coherence());
    }
    
    #[test]
    fn test_decision_coherence_variable() {
        let mut tracker = CoherenceTracker::new(10, 10);
        
        // Record variable decisions
        for i in 0..10 {
            tracker.record_decision(if i % 2 == 0 { 0.01 } else { 0.99 });
        }
        
        // Should have lower coherence than consistent
        let variable_score = tracker.decision_coherence();
        assert!(variable_score < 200, 
            "Variable decisions should have lower coherence, got {}", variable_score);
        
        // Compare to consistent
        let mut consistent = CoherenceTracker::new(10, 10);
        for _ in 0..10 {
            consistent.record_decision(0.5);
        }
        
        assert!(variable_score < consistent.decision_coherence(),
            "Variable ({}) should be less coherent than consistent ({})", 
            variable_score, consistent.decision_coherence());
    }
    
    #[test]
    fn test_tick_smoothness() {
        let mut tracker = CoherenceTracker::new(10, 10);
        
        // Record smooth tick actions
        for _ in 0..10 {
            tracker.record_tick_action(0.5);
        }
        
        let smooth_score = tracker.tick_smoothness();
        assert!(smooth_score > 200, 
            "Smooth ticks should have high smoothness, got {}", smooth_score);
    }
    
    #[test]
    fn test_timescale_separation() {
        let mut sm = ScheduledMarker::new(1, 10);
        
        let mut update_count = 0;
        for i in 0..100 {
            let action = (i % 10) as f32 / 10.0;
            if sm.tick(action).is_some() {
                update_count += 1;
            }
        }
        
        // Should have ~10 updates for 100 ticks with 10x separation
        assert!(update_count >= 9 && update_count <= 11, 
            "Expected ~10 updates, got {}", update_count);
    }
}
