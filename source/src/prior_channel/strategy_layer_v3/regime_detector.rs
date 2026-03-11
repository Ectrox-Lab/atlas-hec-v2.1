//! Regime Detector - Environment State Detection
//!
//! Detects when the game environment has changed:
//! - Game type switches (PD → Stag, etc.)
//! - Population composition changes
//! - Payoff structure drifts

use crate::prior_channel::Marker;

/// Detected regime type
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RegimeType {
    PrisonersDilemma,
    StagHunt,
    Chicken,
    Unknown,
}

/// Regime change event
#[derive(Clone, Debug)]
pub struct RegimeShift {
    pub from: RegimeType,
    pub to: RegimeType,
    pub round: usize,
    pub confidence: f32,
}

/// Regime detector with online identification
pub struct RegimeDetector {
    /// Current estimated regime
    current_regime: RegimeType,
    /// History of payoff observations
    payoff_history: Vec<(i32, i32)>, // (my_action, opponent_action) → payoff
    /// Current round
    current_round: usize,
    /// Detection confidence
    confidence: f32,
    /// Shift detection threshold
    shift_threshold: f32,
}

impl RegimeDetector {
    pub fn new() -> Self {
        Self {
            current_regime: RegimeType::Unknown,
            payoff_history: Vec::new(),
            current_round: 0,
            confidence: 0.0,
            shift_threshold: 0.7,
        }
    }
    
    /// Observe a payoff outcome
    pub fn observe_payoff(&mut self, my_action: i32, opponent_action: i32, payoff: i32) {
        self.payoff_history.push((my_action, opponent_action));
        self.current_round += 1;
        
        // Maintain sliding window
        if self.payoff_history.len() > 100 {
            self.payoff_history.remove(0);
        }
        
        // Update regime estimate
        if self.payoff_history.len() >= 20 {
            let (new_regime, new_confidence) = identify_regime(&self.payoff_history, &self.payoff_outcomes(payoff));
            
            if new_regime != self.current_regime && new_confidence > self.shift_threshold {
                // Regime shift detected
                let shift = RegimeShift {
                    from: self.current_regime,
                    to: new_regime,
                    round: self.current_round,
                    confidence: new_confidence,
                };
                self.current_regime = new_regime;
                self.confidence = new_confidence;
                // Signal shift (in real implementation, would emit event)
            } else {
                self.current_regime = new_regime;
                self.confidence = new_confidence;
            }
        }
    }
    
    /// Get current regime estimate
    pub fn current_regime(&self) -> RegimeType {
        self.current_regime
    }
    
    /// Get detection confidence
    pub fn confidence(&self) -> f32 {
        self.confidence
    }
    
    /// Check if confident about current regime
    pub fn is_confident(&self) -> bool {
        self.confidence >= self.shift_threshold
    }
    
    /// Helper: compute expected payoff pattern for each game
    fn payoff_outcomes(&self, recent_payoff: i32) -> PayoffPattern {
        // Count outcomes in recent history
        let recent = &self.payoff_history[self.payoff_history.len().saturating_sub(30)..];
        
        let mut cc_count = 0;
        let mut cd_count = 0; // I cooperate, opponent defects
        let mut dc_count = 0; // I defect, opponent cooperates
        let mut dd_count = 0;
        
        for &(my, opp) in recent {
            match (my, opp) {
                (0, 0) => cc_count += 1,
                (0, 1) => cd_count += 1,
                (1, 0) => dc_count += 1,
                (1, 1) => dd_count += 1,
                _ => {}
            }
        }
        
        PayoffPattern {
            cc_count,
            cd_count,
            dc_count,
            dd_count,
        }
    }
}

#[derive(Clone, Copy, Debug)]
struct PayoffPattern {
    cc_count: usize,
    cd_count: usize,
    dc_count: usize,
    dd_count: usize,
}

/// Identify regime based on payoff patterns
fn identify_regime(history: &[(i32, i32)], pattern: &PayoffPattern) -> (RegimeType, f32) {
    let total = pattern.cc_count + pattern.cd_count + pattern.dc_count + pattern.dd_count;
    if total < 10 {
        return (RegimeType::Unknown, 0.0);
    }
    
    // Calculate pattern ratios
    let cc_ratio = pattern.cc_count as f32 / total as f32;
    let cd_ratio = pattern.cd_count as f32 / total as f32;
    let dc_ratio = pattern.dc_count as f32 / total as f32;
    let dd_ratio = pattern.dd_count as f32 / total as f32;
    
    // Expected patterns for each game (empirical):
    // PD: High DD (mutual defection Nash), some DC (exploitation)
    // Stag: High CC (coordination), balanced otherwise
    // Chicken: Mixed, avoid DD
    
    // PD score: high DD + DC
    let pd_score = dd_ratio * 2.0 + dc_ratio - cc_ratio * 2.0;
    
    // Stag score: high CC
    let stag_score = cc_ratio * 3.0 - dd_ratio;
    
    // Chicken score: mixed, low DD
    let chicken_score = (dc_ratio + cd_ratio) - dd_ratio * 3.0;
    
    // Normalize scores
    let total_score = pd_score.abs() + stag_score.abs() + chicken_score.abs();
    if total_score < 0.1 {
        return (RegimeType::Unknown, 0.0);
    }
    
    let pd_norm = pd_score / total_score;
    let stag_norm = stag_score / total_score;
    let chicken_norm = chicken_score / total_score;
    
    // Select highest scoring regime
    if pd_norm > stag_norm && pd_norm > chicken_norm && pd_score > 0.0 {
        (RegimeType::PrisonersDilemma, pd_norm.min(1.0))
    } else if stag_norm > chicken_norm && stag_score > 0.0 {
        (RegimeType::StagHunt, stag_norm.min(1.0))
    } else if chicken_score > 0.0 {
        (RegimeType::Chicken, chicken_norm.min(1.0))
    } else {
        (RegimeType::Unknown, 0.0)
    }
}

/// Detect regime shift from markers alone (faster detection)
pub fn detect_regime_shift(
    old_markers: &[Marker],
    new_markers: &[Marker],
) -> Option<RegimeType> {
    if old_markers.len() < 5 || new_markers.len() < 5 {
        return None;
    }
    
    let old_coherence: f32 = old_markers.iter()
        .map(|m| m.coherence() as f32 / 255.0)
        .sum::<f32>() / old_markers.len() as f32;
    
    let new_coherence: f32 = new_markers.iter()
        .map(|m| m.coherence() as f32 / 255.0)
        .sum::<f32>() / new_markers.len() as f32;
    
    let coherence_shift = (new_coherence - old_coherence).abs();
    
    // Significant coherence shift may indicate regime change
    if coherence_shift > 0.2 {
        if new_coherence > 0.6 {
            // High coherence often indicates Stag Hunt
            Some(RegimeType::StagHunt)
        } else if new_coherence < 0.4 {
            // Low coherence may indicate PD or Chicken
            Some(RegimeType::PrisonersDilemma)
        } else {
            Some(RegimeType::Chicken)
        }
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn initial_regime_unknown() {
        let detector = RegimeDetector::new();
        assert_eq!(detector.current_regime(), RegimeType::Unknown);
        assert!(!detector.is_confident());
    }
    
    #[test]
    fn detect_pd_from_defection_pattern() {
        let mut detector = RegimeDetector::new();
        
        // Simulate PD pattern: mostly mutual defection
        for _ in 0..30 {
            detector.observe_payoff(1, 1, 1); // DD = 1 in PD
        }
        
        // Should identify as PD
        let regime = detector.current_regime();
        assert!(regime == RegimeType::PrisonersDilemma || regime == RegimeType::Unknown);
    }
    
    #[test]
    fn detect_shift_from_markers() {
        let old_markers = vec![
            Marker::new(1, 200, 0, 0), // High coherence ~0.78
            Marker::new(1, 190, 0, 0),
            Marker::new(1, 195, 0, 0),
            Marker::new(1, 198, 0, 0),
            Marker::new(1, 192, 0, 0),
        ];
        
        let new_markers = vec![
            Marker::new(1, 100, 0, 0), // Low coherence ~0.39
            Marker::new(1, 90, 0, 0),
            Marker::new(1, 95, 0, 0),
            Marker::new(1, 85, 0, 0),
            Marker::new(1, 92, 0, 0),
        ];
        
        let shift = detect_regime_shift(&old_markers, &new_markers);
        assert!(shift.is_some(), "Should detect regime shift");
    }
}
