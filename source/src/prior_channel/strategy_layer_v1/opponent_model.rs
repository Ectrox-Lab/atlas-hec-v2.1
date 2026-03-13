//! Opponent Model - Minimal Three-Class Classification
//!
//! Uses Candidate 001's prediction signals to classify opponents.
//! Target: Convert prediction into score improvement.

use crate::prior_channel::Marker;

/// Three-class opponent model
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OpponentModel {
    Cooperative,   // High coherence, consistent -> likely to cooperate
    Exploitative,  // High variance or low coherence -> likely to defect
    Uncertain,     // In between -> unpredictable
}

/// Classify opponent based on marker history
/// 
/// Simple rule-based classification (v1 minimal)
pub fn classify_opponent(markers: &[Marker]) -> OpponentModel {
    if markers.is_empty() {
        return OpponentModel::Uncertain;
    }
    
    // Compute average coherence
    let avg_coherence = markers.iter()
        .map(|m| m.coherence() as f32 / 255.0)
        .sum::<f32>() / markers.len() as f32;
    
    // Compute variance (consistency)
    let variance = if markers.len() > 1 {
        let mean = avg_coherence;
        markers.iter()
            .map(|m| {
                let c = m.coherence() as f32 / 255.0;
                (c - mean).powi(2)
            })
            .sum::<f32>() / markers.len() as f32
    } else {
        0.0
    };
    
    // Classification rules (v1 minimal)
    if avg_coherence > 0.65 && variance < 0.03 {
        // High coherence + stable = cooperative
        OpponentModel::Cooperative
    } else if avg_coherence < 0.4 || variance > 0.08 {
        // Low coherence OR high variance = exploitative
        OpponentModel::Exploitative
    } else {
        // Middle ground = uncertain
        OpponentModel::Uncertain
    }
}

/// Get policy bias based on opponent model
/// 
/// Fixed mapping (v1 minimal):
/// - Cooperative -> increase cooperation
/// - Exploitative -> increase defection (defense)
/// - Uncertain -> no bias (explore)
pub fn opponent_bias(model: OpponentModel) -> f32 {
    match model {
        OpponentModel::Cooperative => 0.20,   // Trust more
        OpponentModel::Exploitative => -0.25, // Defend (defect more)
        OpponentModel::Uncertain => 0.0,      // No bias
    }
}

/// Quick check if opponent model classification is available
pub fn has_opponent_model(markers: &[Marker]) -> bool {
    markers.len() >= 3  // Need some history
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn classify_cooperative() {
        let markers = vec![
            Marker::new(1, 180, 0, 0),  // ~0.7 coherence
            Marker::new(1, 185, 0, 0),
            Marker::new(1, 182, 0, 0),
        ];
        assert_eq!(classify_opponent(&markers), OpponentModel::Cooperative);
    }
    
    #[test]
    fn classify_exploitative_low() {
        let markers = vec![
            Marker::new(1, 80, 0, 0),   // ~0.3 coherence
            Marker::new(1, 90, 0, 0),
            Marker::new(1, 85, 0, 0),
        ];
        assert_eq!(classify_opponent(&markers), OpponentModel::Exploitative);
    }
    
    #[test]
    fn classify_exploitative_variance() {
        let markers = vec![
            Marker::new(1, 240, 0, 0),  // Very high (~0.94)
            Marker::new(1, 30, 0, 0),   // Very low (~0.12)
            Marker::new(1, 220, 0, 0),  // High (~0.86)
        ];
        // High variance (>0.08) -> Exploitative
        assert_eq!(classify_opponent(&markers), OpponentModel::Exploitative);
    }
    
    #[test]
    fn classify_uncertain() {
        let markers = vec![
            Marker::new(1, 130, 0, 0),  // ~0.5 coherence
            Marker::new(1, 135, 0, 0),
            Marker::new(1, 128, 0, 0),
        ];
        assert_eq!(classify_opponent(&markers), OpponentModel::Uncertain);
    }
    
    #[test]
    fn bias_directions() {
        assert!(opponent_bias(OpponentModel::Cooperative) > 0.0);
        assert!(opponent_bias(OpponentModel::Exploitative) < 0.0);
        assert_eq!(opponent_bias(OpponentModel::Uncertain), 0.0);
    }
}
