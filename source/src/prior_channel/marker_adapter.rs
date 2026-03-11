//! PriorChannel Marker Adapter
//!
//! Integrates Candidate 001 (Multi-Agent Consistency Markers) with PriorChannel.
//! 
//! COMPLIANT with FROZEN_STATE_v1:
//! - Fixed 32-bit bandwidth (4 bytes)
//! - Fixed 10-tick update interval (10x timescale separation)
//! - Generic prior only (bias/modulation, not specific actions)
//! - No content-bearing signaling

use super::{PriorChannel, PRIOR_STRENGTH};

/// 4-byte marker encoding (32 bits fixed)
/// 
/// Layout:
/// - bits 0-7:   agent_id (8 bits)
/// - bits 8-15:  coherence_score (8 bits, 0-255)
/// - bits 16-31: behavioral_bias (16 bits, encoded as i8 x 2)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Marker([u8; 4]);

impl Marker {
    /// Create new marker with fixed 32-bit encoding
    pub fn new(agent_id: u8, coherence: u8, bias_x: i8, bias_y: i8) -> Self {
        let bytes = [
            agent_id,
            coherence,
            bias_x as u8,
            bias_y as u8,
        ];
        Self(bytes)
    }
    
    /// Encode from components
    pub fn encode(agent_id: u8, coherence: u8, bias: [i8; 2]) -> [u8; 4] {
        [agent_id, coherence, bias[0] as u8, bias[1] as u8]
    }
    
    /// Decode to components
    pub fn decode(&self) -> (u8, u8, [i8; 2]) {
        (
            self.0[0],                    // agent_id
            self.0[1],                    // coherence
            [self.0[2] as i8, self.0[3] as i8],  // bias
        )
    }
    
    /// Raw bytes
    pub fn as_bytes(&self) -> &[u8; 4] {
        &self.0
    }
    
    /// Extract agent_id
    pub fn agent_id(&self) -> u8 {
        self.0[0]
    }
    
    /// Extract coherence score
    pub fn coherence(&self) -> u8 {
        self.0[1]
    }
    
    /// Extract behavioral bias
    pub fn bias(&self) -> [i8; 2] {
        [self.0[2] as i8, self.0[3] as i8]
    }
}

/// Modulation output from PriorChannel integration
/// 
/// COMPLIANT: Only bias/modulation values, never specific action recommendations
#[derive(Clone, Copy, Debug)]
pub struct PolicyModulation {
    /// Coherence expectation (normalized -1 to 1)
    pub coherence_bias: f32,
    /// Directional bias for policy (generic, not action-specific)
    pub directional_bias: [f32; 2],
    /// Confidence level (0 to 1)
    pub confidence: f32,
}

impl PolicyModulation {
    /// Zero modulation (no effect)
    pub fn zero() -> Self {
        Self {
            coherence_bias: 0.0,
            directional_bias: [0.0, 0.0],
            confidence: 0.0,
        }
    }
    
    /// Apply modulation to policy logits
    /// COMPLIANT: Modulates policy distribution, doesn't replace it
    pub fn apply(&self, policy_logits: &mut [f32; 2]) {
        // Coherence bias: shift toward consistent behavior
        if self.coherence_bias > 0.0 {
            policy_logits[0] += self.coherence_bias * self.confidence;
        }
        
        // Directional bias: weak generic influence
        policy_logits[0] += self.directional_bias[0] * self.confidence * 0.5;
        policy_logits[1] += self.directional_bias[1] * self.confidence * 0.5;
    }
}

/// PriorChannel adapter for Candidate 001 markers
/// 
/// Bridges generic PriorChannel sampling with marker-based coherence tracking
pub struct PriorChannelMarkerAdapter {
    /// PriorChannel instance
    channel: PriorChannel,
    /// Whether PriorChannel is enabled
    enabled: bool,
    /// Total bits transmitted (for bandwidth guard)
    total_bits: u64,
    /// Sample count
    sample_count: u64,
}

impl PriorChannelMarkerAdapter {
    /// Create new adapter with PriorChannel
    pub fn new(enabled: bool) -> Self {
        Self {
            channel: PriorChannel::new_locked(),
            enabled,
            total_bits: 0,
            sample_count: 0,
        }
    }
    
    /// Check if prior should be sampled (p=0.01)
    pub fn should_sample(&mut self, rng: &mut impl rand::Rng) -> bool {
        if !self.enabled {
            return false;
        }
        self.channel.should_sample(rng)
    }
    
    /// Compute generic prior from marker context
    /// 
    /// COMPLIANT: Returns only coherence expectation and bias, never specific actions
    pub fn compute_modulation(
        &mut self,
        observer_coherence: u8,
        population_coherence: u8,
    ) -> PolicyModulation {
        if !self.enabled {
            return PolicyModulation::zero();
        }
        
        self.sample_count += 1;
        self.total_bits += 32; // Fixed 32-bit marker
        
        // Generic prior: higher population coherence → expect consistency
        let coherence_expectation = (population_coherence as f32 / 255.0) * 2.0 - 1.0;
        
        // Bias direction based on observer's own coherence
        let directional_bias = if observer_coherence > 150 {
            [0.3, -0.1]  // Toward cooperation/consistency
        } else {
            [0.0, 0.0]   // Neutral
        };
        
        // Confidence from observer's coherence (scaled by PriorChannel strength)
        let confidence = (observer_coherence as f32 / 255.0) * PRIOR_STRENGTH as f32;
        
        PolicyModulation {
            coherence_bias: coherence_expectation,
            directional_bias,
            confidence,
        }
    }
    
    /// Inject PriorChannel prior into marker context
    /// 
    /// Returns modulation that can be applied to policy
    pub fn inject_prior(
        &mut self,
        marker: &Marker,
        population_markers: &[Marker],
        rng: &mut impl rand::Rng,
    ) -> PolicyModulation {
        if !self.should_sample(rng) {
            return PolicyModulation::zero();
        }
        
        // Compute population coherence average
        let population_coherence = if population_markers.is_empty() {
            128
        } else {
            let sum: u32 = population_markers.iter().map(|m| m.coherence() as u32).sum();
            (sum / population_markers.len() as u32) as u8
        };
        
        let modulation = self.compute_modulation(marker.coherence(), population_coherence);
        
        self.channel.record_injection();
        modulation
    }
    
    /// Get bandwidth statistics
    pub fn bandwidth_stats(&self) -> BandwidthStats {
        BandwidthStats {
            total_bits: self.total_bits,
            sample_count: self.sample_count,
            mean_bits_per_sample: if self.sample_count > 0 {
                self.total_bits as f64 / self.sample_count as f64
            } else {
                0.0
            },
            compliant: self.total_bits == 0 || (self.total_bits / self.sample_count.max(1)) <= 32,
        }
    }
    
    /// Get PriorChannel stats
    pub fn channel_stats(&self) -> super::channel::SamplingStats {
        self.channel.get_stats()
    }
}

/// Bandwidth usage statistics
#[derive(Clone, Debug)]
pub struct BandwidthStats {
    pub total_bits: u64,
    pub sample_count: u64,
    pub mean_bits_per_sample: f64,
    pub compliant: bool,
}

/// Marker scheduler with 10x timescale separation
/// 
/// Updates marker every 10 ticks while actions happen every tick
pub struct MarkerScheduler {
    marker: Marker,
    coherence_score: u8,
    update_interval: usize,
    tick_counter: usize,
    last_update_tick: usize,
    action_history: Vec<f32>,
}

impl MarkerScheduler {
    /// Create new scheduler with fixed 10x timescale
    pub fn new(agent_id: u8) -> Self {
        Self {
            marker: Marker::new(agent_id, 128, 0, 0),
            coherence_score: 128,
            update_interval: 10,  // FROZEN: 10x timescale separation
            tick_counter: 0,
            last_update_tick: 0,
            action_history: Vec::with_capacity(20),
        }
    }
    
    /// Record action every tick, update marker every 10 ticks
    /// 
    /// Returns new marker if updated, None otherwise
    pub fn tick(&mut self, action: f32) -> Option<Marker> {
        self.tick_counter += 1;
        self.action_history.push(action.clamp(0.0, 1.0));
        
        // Keep only recent history
        if self.action_history.len() > 20 {
            self.action_history.remove(0);
        }
        
        // Update marker only at 10-tick interval
        if self.tick_counter - self.last_update_tick >= self.update_interval {
            self.last_update_tick = self.tick_counter;
            
            // Compute coherence from action variance
            let coherence = self.compute_coherence();
            self.coherence_score = coherence;
            
            self.marker = Marker::new(
                self.marker.agent_id(),
                coherence,
                self.marker.bias()[0],
                self.marker.bias()[1],
            );
            
            Some(self.marker)
        } else {
            None
        }
    }
    
    /// Compute coherence score from action history
    fn compute_coherence(&self) -> u8 {
        if self.action_history.len() < 2 {
            return 128;
        }
        
        let n = self.action_history.len() as f32;
        let mean: f32 = self.action_history.iter().sum::<f32>() / n;
        
        // Variance
        let variance: f32 = self.action_history
            .iter()
            .map(|x| (x - mean).powi(2))
            .sum::<f32>() / n;
        
        // Low variance = high coherence
        let coherence = 255.0 - (variance * 255.0 * 4.0).clamp(0.0, 255.0);
        coherence as u8
    }
    
    /// Get current marker
    pub fn current_marker(&self) -> Marker {
        self.marker
    }
    
    /// Get coherence score
    pub fn coherence(&self) -> u8 {
        self.coherence_score
    }
    
    /// Verify timescale compliance
    pub fn check_timescale(&self) -> bool {
        self.update_interval == 10
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    #[test]
    fn test_marker_encoding() {
        let m = Marker::new(42, 200, -5, 10);
        let (id, coh, bias) = m.decode();
        assert_eq!(id, 42);
        assert_eq!(coh, 200);
        assert_eq!(bias, [-5, 10]);
    }
    
    #[test]
    fn test_bandwidth_fixed_32bits() {
        let m = Marker::new(1, 128, 0, 0);
        assert_eq!(m.as_bytes().len(), 4); // Exactly 32 bits
    }
    
    #[test]
    fn test_modulation_apply() {
        let mut logits = [0.0, 0.0];
        let modulate = PolicyModulation {
            coherence_bias: 0.5,
            directional_bias: [0.2, -0.1],
            confidence: 0.8,
        };
        modulate.apply(&mut logits);
        
        // Should have modified logits
        assert!(logits[0] != 0.0);
        assert!(logits[1] != 0.0);
    }
    
    #[test]
    fn test_adapter_disabled() {
        let mut adapter = PriorChannelMarkerAdapter::new(false);
        let mut rng = StdRng::seed_from_u64(42);
        
        assert!(!adapter.should_sample(&mut rng));
        
        let m = Marker::new(1, 128, 0, 0);
        let pop = vec![];
        let modulation = adapter.inject_prior(&m, &pop, &mut rng);
        
        // Should be zero when disabled
        assert_eq!(modulation.confidence, 0.0);
    }
    
    #[test]
    fn test_adapter_enabled_sampling() {
        let mut adapter = PriorChannelMarkerAdapter::new(true);
        let mut rng = StdRng::seed_from_u64(42);
        
        // Sample many times to trigger at least one
        let mut sampled = false;
        for _ in 0..1000 {
            if adapter.should_sample(&mut rng) {
                sampled = true;
                break;
            }
        }
        assert!(sampled, "Should sample with p=0.01 over 1000 trials");
    }
    
    #[test]
    fn test_marker_scheduler_timescale() {
        let mut scheduler = MarkerScheduler::new(1);
        assert!(scheduler.check_timescale(), "Must be 10x timescale");
        
        let mut update_count = 0;
        for i in 0..100 {
            let action = (i % 10) as f32 / 10.0;
            if scheduler.tick(action).is_some() {
                update_count += 1;
            }
        }
        
        // Should have ~10 updates for 100 ticks at 10x
        assert!(update_count >= 9 && update_count <= 11, 
            "Expected ~10 updates, got {}", update_count);
    }
    
    #[test]
    fn test_generic_only_no_specific_actions() {
        let mut adapter = PriorChannelMarkerAdapter::new(true);
        let modulation = adapter.compute_modulation(200, 180);
        
        // Modulation should only have generic values
        assert!(modulation.confidence >= 0.0 && modulation.confidence <= 1.0);
        assert!(modulation.coherence_bias >= -1.0 && modulation.coherence_bias <= 1.0);
        
        // Should not encode specific actions
        // (confidence should be from coherence, not action IDs)
    }
}
