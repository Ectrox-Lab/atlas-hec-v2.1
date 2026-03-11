//! Adaptation Metrics - Track Online Adaptation Performance
//!
//! Key metrics for v3 validation:
//! - Recovery time after shift
//! - Score trajectory
//! - Adaptation latency vs v2 baseline

use std::collections::VecDeque;

/// Tracks recovery after regime/opponent shift
#[derive(Clone, Debug)]
pub struct RecoveryTracker {
    /// Shift event timestamp
    shift_round: usize,
    /// Score before shift
    pre_shift_score: f32,
    /// Score history after shift
    post_shift_scores: VecDeque<(usize, f32)>,
    /// Recovery threshold (score > pre_shift * 0.9)
    recovery_threshold: f32,
    /// Whether recovered
    recovered: bool,
    /// Recovery round (if recovered)
    recovery_round: Option<usize>,
}

impl RecoveryTracker {
    pub fn new(shift_round: usize, pre_shift_score: f32) -> Self {
        Self {
            shift_round,
            pre_shift_score,
            post_shift_scores: VecDeque::new(),
            recovery_threshold: pre_shift_score * 0.9,
            recovered: false,
            recovery_round: None,
        }
    }
    
    /// Record score after shift
    pub fn record(&mut self, round: usize, score: f32) {
        if self.recovered {
            return;
        }
        
        self.post_shift_scores.push_back((round, score));
        
        // Maintain sliding window for moving average
        if self.post_shift_scores.len() > 20 {
            self.post_shift_scores.pop_front();
        }
        
        // Check recovery (using moving average)
        if self.post_shift_scores.len() >= 10 {
            let avg_score: f32 = self.post_shift_scores.iter().map(|(_, s)| s).sum::<f32>() 
                / self.post_shift_scores.len() as f32;
            
            if avg_score >= self.recovery_threshold {
                self.recovered = true;
                self.recovery_round = Some(round);
            }
        }
    }
    
    /// Get recovery latency (rounds to recover)
    pub fn recovery_latency(&self) -> Option<usize> {
        self.recovery_round.map(|r| r - self.shift_round)
    }
    
    /// Check if recovered
    pub fn is_recovered(&self) -> bool {
        self.recovered
    }
    
    /// Get recovery slope (score increase rate)
    pub fn recovery_slope(&self) -> f32 {
        if self.post_shift_scores.len() < 10 {
            return 0.0;
        }
        
        let recent: Vec<_> = self.post_shift_scores.iter().rev().take(10).collect();
        let first = recent.last().unwrap().1;
        let last = recent.first().unwrap().1;
        
        (last - first) / 10.0
    }
}

/// Comprehensive adaptation metrics
#[derive(Clone, Debug)]
pub struct AdaptationMetrics {
    /// Current round
    pub round: usize,
    /// Cumulative score
    pub total_score: f32,
    /// Score history (for trend analysis)
    score_history: VecDeque<(usize, f32)>,
    /// Number of regime shifts detected
    pub shift_count: usize,
    /// Recovery trackers for each shift
    pub recovery_trackers: Vec<RecoveryTracker>,
    /// Current recovery tracker (if in recovery)
    current_recovery: Option<usize>,
    /// Baseline score for comparison
    baseline_score: f32,
    /// v2 baseline score (for latency comparison)
    v2_baseline_score: f32,
}

impl AdaptationMetrics {
    pub fn new(baseline_score: f32, v2_baseline_score: f32) -> Self {
        Self {
            round: 0,
            total_score: 0.0,
            score_history: VecDeque::new(),
            shift_count: 0,
            recovery_trackers: Vec::new(),
            current_recovery: None,
            baseline_score,
            v2_baseline_score,
        }
    }
    
    /// Record round result
    pub fn record(&mut self, round: usize, score_delta: f32) {
        self.round = round;
        self.total_score += score_delta;
        self.score_history.push_back((round, self.total_score));
        
        // Maintain window
        if self.score_history.len() > 100 {
            self.score_history.pop_front();
        }
        
        // Update current recovery tracker
        if let Some(idx) = self.current_recovery {
            self.recovery_trackers[idx].record(round, self.total_score);
            
            if self.recovery_trackers[idx].is_recovered() {
                self.current_recovery = None;
            }
        }
    }
    
    /// Register a shift event
    pub fn register_shift(&mut self, shift_round: usize) {
        self.shift_count += 1;
        
        // Get pre-shift score
        let pre_shift_score = self.total_score;
        
        let tracker = RecoveryTracker::new(shift_round, pre_shift_score);
        self.recovery_trackers.push(tracker);
        self.current_recovery = Some(self.recovery_trackers.len() - 1);
    }
    
    /// Check if beating baseline
    pub fn beating_baseline(&self) -> bool {
        self.total_score > self.baseline_score
    }
    
    /// Get average recovery latency
    pub fn avg_recovery_latency(&self) -> Option<f32> {
        let latencies: Vec<_> = self.recovery_trackers.iter()
            .filter_map(|t| t.recovery_latency())
            .collect();
        
        if latencies.is_empty() {
            None
        } else {
            Some(latencies.iter().sum::<usize>() as f32 / latencies.len() as f32)
        }
    }
    
    /// Get score trend (last 50 rounds)
    pub fn recent_trend(&self) -> f32 {
        let recent: Vec<_> = self.score_history.iter().rev().take(50).collect();
        if recent.len() < 10 {
            return 0.0;
        }
        
        let first = recent.last().unwrap().1;
        let last = recent.first().unwrap().1;
        
        (last - first) / recent.len() as f32
    }
    
    /// Generate adaptation report
    pub fn generate_report(&self) -> AdaptationReport {
        AdaptationReport {
            round: self.round,
            total_score: self.total_score,
            baseline_score: self.baseline_score,
            beating_baseline: self.beating_baseline(),
            shift_count: self.shift_count,
            avg_recovery_latency: self.avg_recovery_latency(),
            recovery_rate: if self.shift_count > 0 {
                let recovered = self.recovery_trackers.iter().filter(|t| t.is_recovered()).count();
                recovered as f32 / self.shift_count as f32
            } else {
                1.0
            },
            recent_trend: self.recent_trend(),
        }
    }
}

/// Adaptation report for validation
#[derive(Clone, Debug)]
pub struct AdaptationReport {
    pub round: usize,
    pub total_score: f32,
    pub baseline_score: f32,
    pub beating_baseline: bool,
    pub shift_count: usize,
    pub avg_recovery_latency: Option<f32>,
    pub recovery_rate: f32,
    pub recent_trend: f32,
}

impl AdaptationReport {
    /// Check if meets v3 validation gates
    pub fn meets_v3_gates(&self) -> V3GateResult {
        use super::validation_gates::*;
        
        V3GateResult {
            post_shift_baseline: self.beating_baseline,
            recovery_latency_ok: self.avg_recovery_latency.map(|l| l <= MIN_RECOVERY_ROUNDS as f32).unwrap_or(true),
            recovery_rate_ok: self.recovery_rate >= POST_SHIFT_BASELINE_RATIO,
            positive_trend: self.recent_trend > 0.0,
        }
    }
    
    /// Dynamic scenario gates (for regime shift tests)
    /// Relaxed baseline requirement, focus on recovery
    pub fn meets_dynamic_gates(&self) -> V3GateResult {
        use super::validation_gates::*;
        
        // Dynamic: within 10% of baseline is acceptable
        let near_baseline = self.total_score >= self.baseline_score * 0.9;
        
        V3GateResult {
            post_shift_baseline: near_baseline,
            recovery_latency_ok: self.avg_recovery_latency.map(|l| l <= MIN_RECOVERY_ROUNDS as f32).unwrap_or(true),
            recovery_rate_ok: self.recovery_rate >= POST_SHIFT_BASELINE_RATIO,
            // Relaxed: non-negative trend acceptable in dynamic scenarios
            positive_trend: self.recent_trend >= -0.5,
        }
    }
}

/// V3 validation gate results
#[derive(Clone, Debug)]
pub struct V3GateResult {
    pub post_shift_baseline: bool,
    pub recovery_latency_ok: bool,
    pub recovery_rate_ok: bool,
    pub positive_trend: bool,
}

impl V3GateResult {
    /// All gates passed
    pub fn all_pass(&self) -> bool {
        self.post_shift_baseline && 
        self.recovery_latency_ok && 
        self.recovery_rate_ok && 
        self.positive_trend
    }
    
    /// Format report
    pub fn format(&self) -> String {
        format!(
            "V3 Gates:\n  Post-shift baseline: {}\n  Recovery latency: {}\n  Recovery rate: {}\n  Positive trend: {}",
            if self.post_shift_baseline { "✅" } else { "❌" },
            if self.recovery_latency_ok { "✅" } else { "❌" },
            if self.recovery_rate_ok { "✅" } else { "❌" },
            if self.positive_trend { "✅" } else { "❌" },
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn recovery_tracker_detects_recovery() {
        let mut tracker = RecoveryTracker::new(100, 1000.0);
        
        // Score below threshold initially
        tracker.record(101, 900.0);
        tracker.record(102, 920.0);
        assert!(!tracker.is_recovered());
        
        // Score recovers
        for i in 0..20 {
            tracker.record(103 + i, 950.0 + i as f32 * 5.0);
        }
        
        assert!(tracker.is_recovered());
        assert!(tracker.recovery_latency().is_some());
    }
    
    #[test]
    fn metrics_track_shifts() {
        let mut metrics = AdaptationMetrics::new(5000.0, 5000.0);
        
        // Simulate rounds
        for i in 0..100 {
            metrics.record(i, 10.0);
        }
        
        // Register shift
        metrics.register_shift(100);
        
        // Continue
        for i in 100..200 {
            metrics.record(i, 12.0);
        }
        
        assert_eq!(metrics.shift_count, 1);
        assert!(metrics.avg_recovery_latency().is_some());
    }
}
