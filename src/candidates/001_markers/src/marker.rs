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

/// Coherence score computer
/// 
/// Measures behavioral consistency over a window of actions.
/// Higher score = lower variance = more consistent.
pub struct CoherenceTracker {
    window_size: usize,
    action_history: VecDeque<f32>,  // normalized action values
    current_score: u8,
}

impl CoherenceTracker {
    pub fn new(window_size: usize) -> Self {
        Self {
            window_size,
            action_history: VecDeque::with_capacity(window_size),
            current_score: 128,  // neutral starting point
        }
    }
    
    /// Record an action and update coherence score
    /// 
    /// Action should be normalized to [0, 1] range.
    pub fn record_action(&mut self, action: f32) {
        let clamped = action.clamp(0.0, 1.0);
        
        // Add to history
        if self.action_history.len() >= self.window_size {
            self.action_history.pop_front();
        }
        self.action_history.push_back(clamped);
        
        // Compute coherence only if we have enough history
        if self.action_history.len() >= 3 {
            self.current_score = self.compute_coherence();
        }
    }
    
    /// Compute coherence score from history
    /// 
    /// Uses inverse of coefficient of variation (normalized std/mean)
    /// Returns 0-255, where 255 = perfectly consistent.
    fn compute_coherence(&self) -> u8 {
        if self.action_history.len() < 2 {
            return 128;
        }
        
        let n = self.action_history.len() as f32;
        let mean: f32 = self.action_history.iter().sum::<f32>() / n;
        
        if mean < 0.01 {
            return 128;  // Avoid division by near-zero
        }
        
        let variance: f32 = self.action_history.iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>() / n;
        let std_dev = variance.sqrt();
        
        // Coefficient of variation (lower = more consistent)
        let cv = std_dev / mean;
        
        // Convert to 0-255 score (higher = more consistent)
        // cv=0 -> 255, cv=1 -> 128, cv=2 -> 0
        let score = 255.0 - (cv * 128.0).clamp(0.0, 255.0);
        score as u8
    }
    
    /// Get current coherence score
    pub fn current_score(&self) -> u8 {
        self.current_score
    }
    
    /// Get action variance (for debugging)
    pub fn variance(&self) -> f32 {
        if self.action_history.len() < 2 {
            return 0.0;
        }
        
        let n = self.action_history.len() as f32;
        let mean: f32 = self.action_history.iter().sum::<f32>() / n;
        self.action_history.iter()
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
}

impl ScheduledMarker {
    pub fn new(agent_id: u8, update_interval: usize) -> Self {
        Self {
            marker: Marker::new(agent_id, 128, 0),
            tracker: CoherenceTracker::new(20),
            update_interval,
            tick_counter: 0,
            last_update_tick: 0,
        }
    }
    
    /// Record action every tick, but only update marker every N ticks
    pub fn tick(&mut self, action: f32) -> Option<Marker> {
        self.tick_counter += 1;
        
        // Record action for coherence computation
        self.tracker.record_action(action);
        
        // Update marker only at interval
        if self.tick_counter - self.last_update_tick >= self.update_interval {
            self.last_update_tick = self.tick_counter;
            
            // Update marker with new coherence score
            self.marker = Marker::new(
                self.marker.agent_id(),
                self.tracker.current_score(),
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
        // Should not update every tick
        self.tick_counter == 0 || self.last_update_tick < self.tick_counter
    }
    
    /// Get update frequency (for validation)
    pub fn effective_update_rate(&self) -> f32 {
        if self.tick_counter == 0 {
            0.0
        } else {
            (self.last_update_tick / self.update_interval) as f32 / self.tick_counter as f32
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
    fn test_coherence_consistent_actions() {
        let mut tracker = CoherenceTracker::new(10);
        
        // Record consistent actions
        for _ in 0..10 {
            tracker.record_action(0.5);
        }
        
        // Should have high coherence
        assert!(tracker.current_score() > 200, "Consistent actions should have high coherence");
    }
    
    #[test]
    fn test_coherence_variable_actions() {
        let mut tracker = CoherenceTracker::new(10);
        
        // Record variable actions (high variance)
        for i in 0..10 {
            tracker.record_action(if i % 2 == 0 { 0.01 } else { 0.99 });
        }
        
        // Should have lower coherence than consistent
        assert!(tracker.current_score() < 200, "Variable actions should have lower coherence");
        
        // Compare to consistent
        let mut consistent = CoherenceTracker::new(10);
        for _ in 0..10 {
            consistent.record_action(0.5);
        }
        
        assert!(tracker.current_score() < consistent.current_score(),
            "Variable should be less coherent than consistent");
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
