//! Hazard Rate Model
//! 
//! h(t) = d(extinctions)/dt
//! 
//! Used for:
//! - Extinction prediction
//! - Early warning signals
//! - Cascade dynamics detection

use std::collections::VecDeque;

/// Hazard rate tracker
pub struct HazardRateTracker {
    /// Window of extinction events (tick when death occurred)
    extinction_events: VecDeque<usize>,
    /// Window size for smoothing
    window_size: usize,
    /// Current tick
    current_tick: usize,
    /// Cumulative extinctions
    total_extinctions: usize,
}

impl HazardRateTracker {
    pub fn new(window_size: usize) -> Self {
        Self {
            extinction_events: VecDeque::with_capacity(window_size),
            window_size,
            current_tick: 0,
            total_extinctions: 0,
        }
    }
    
    /// Record a death event
    pub fn record_death(&mut self, tick: usize) {
        self.extinction_events.push_back(tick);
        self.total_extinctions += 1;
        
        // Remove old events outside window
        while let Some(&old_tick) = self.extinction_events.front() {
            if tick.saturating_sub(old_tick) > self.window_size {
                self.extinction_events.pop_front();
            } else {
                break;
            }
        }
        
        self.current_tick = tick;
    }
    
    /// Compute current hazard rate: h(t) = deaths / window_time
    pub fn hazard_rate(&self) -> f64 {
        if self.extinction_events.len() < 2 {
            return 0.0;
        }
        
        let deaths = self.extinction_events.len() as f64;
        let time_span = if let (Some(&first), Some(&last)) = 
            (self.extinction_events.front(), self.extinction_events.back()) {
            (last - first).max(1) as f64
        } else {
            1.0
        };
        
        deaths / time_span
    }
    
    /// Smoothed hazard rate (moving average)
    pub fn smoothed_hazard_rate(&self, smoothing: usize) -> f64 {
        if self.extinction_events.len() < smoothing {
            return self.hazard_rate();
        }
        
        // Simple moving average of recent deaths
        let recent_deaths: Vec<usize> = self.extinction_events.iter()
            .rev()
            .take(smoothing)
            .copied()
            .collect();
        
        if recent_deaths.len() < 2 {
            return 0.0;
        }
        
        let deaths = recent_deaths.len() as f64;
        let time_span = (recent_deaths[0] - recent_deaths[recent_deaths.len() - 1]).max(1) as f64;
        
        deaths / time_span
    }
    
    /// Detect extinction cascade (sudden increase in hazard rate)
    pub fn detect_cascade(&self, threshold_multiplier: f64) -> bool {
        if self.extinction_events.len() < 10 {
            return false;
        }
        
        let current = self.hazard_rate();
        let baseline = self.baseline_hazard_rate();
        
        baseline > 0.0 && current > baseline * threshold_multiplier
    }
    
    /// Baseline hazard rate (from earlier in window)
    fn baseline_hazard_rate(&self) -> f64 {
        let half_window = self.window_size / 2;
        let old_events: Vec<usize> = self.extinction_events.iter()
            .filter(|&&tick| self.current_tick.saturating_sub(tick) > half_window)
            .copied()
            .collect();
        
        if old_events.len() < 2 {
            return 0.001; // Small default
        }
        
        let deaths = old_events.len() as f64;
        let time_span = (old_events[old_events.len() - 1] - old_events[0]).max(1) as f64;
        
        deaths / time_span
    }
    
    /// Early warning: hazard rate increasing trend
    pub fn early_warning_signal(&self) -> f64 {
        if self.extinction_events.len() < 20 {
            return 0.0;
        }
        
        // Split window in half
        let half = self.extinction_events.len() / 2;
        let first_half: Vec<usize> = self.extinction_events.iter().take(half).copied().collect();
        let second_half: Vec<usize> = self.extinction_events.iter().skip(half).copied().collect();
        
        if first_half.len() < 2 || second_half.len() < 2 {
            return 0.0;
        }
        
        let rate_first = first_half.len() as f64 / 
            (first_half[first_half.len() - 1] - first_half[0]).max(1) as f64;
        let rate_second = second_half.len() as f64 / 
            (second_half[second_half.len() - 1] - second_half[0]).max(1) as f64;
        
        // Ratio > 1.5 indicates increasing hazard
        if rate_first > 0.0 {
            rate_second / rate_first
        } else {
            0.0
        }
    }
    
    /// Get statistics
    pub fn stats(&self) -> HazardStats {
        HazardStats {
            total_extinctions: self.total_extinctions,
            current_hazard: self.hazard_rate(),
            smoothed_hazard: self.smoothed_hazard_rate(10),
            early_warning: self.early_warning_signal(),
            cascade_detected: self.detect_cascade(2.0),
        }
    }
}

/// Hazard statistics
#[derive(Clone, Copy, Debug)]
pub struct HazardStats {
    pub total_extinctions: usize,
    pub current_hazard: f64,
    pub smoothed_hazard: f64,
    pub early_warning: f64,
    pub cascade_detected: bool,
}

impl HazardStats {
    /// Format for CSV output
    pub fn to_csv(&self) -> String {
        format!("{},{},{},{},{}",
            self.total_extinctions,
            self.current_hazard,
            self.smoothed_hazard,
            self.early_warning,
            if self.cascade_detected { "1" } else { "0" }
        )
    }
    
    pub fn csv_header() -> &'static str {
        "total_extinctions,current_hazard,smoothed_hazard,early_warning,cascade"
    }
}

/// Multi-universe hazard tracker
pub struct MultiUniverseHazard {
    trackers: Vec<HazardRateTracker>,
    extinct_universes: Vec<bool>,
}

impl MultiUniverseHazard {
    pub fn new(n_universes: usize, window_size: usize) -> Self {
        Self {
            trackers: (0..n_universes)
                .map(|_| HazardRateTracker::new(window_size))
                .collect(),
            extinct_universes: vec![false; n_universes],
        }
    }
    
    /// Record death in specific universe
    pub fn record_death(&mut self, universe_id: usize, tick: usize) {
        if let Some(tracker) = self.trackers.get_mut(universe_id) {
            tracker.record_death(tick);
        }
    }
    
    /// Mark universe as extinct
    pub fn mark_extinct(&mut self, universe_id: usize) {
        if universe_id < self.extinct_universes.len() {
            self.extinct_universes[universe_id] = true;
        }
    }
    
    /// Global hazard: average across all universes
    pub fn global_hazard(&self) -> f64 {
        let total: f64 = self.trackers.iter().map(|t| t.hazard_rate()).sum();
        total / self.trackers.len().max(1) as f64
    }
    
    /// Extinction count: how many universes extinct
    pub fn extinction_count(&self) -> usize {
        self.extinct_universes.iter().filter(|&&x| x).count()
    }
    
    /// Survival rate: fraction of universes still alive
    pub fn survival_rate(&self) -> f64 {
        let extinct = self.extinction_count();
        let total = self.extinct_universes.len();
        if total == 0 {
            return 0.0;
        }
        (total - extinct) as f64 / total as f64
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_hazard_rate() {
        let mut tracker = HazardRateTracker::new(100);
        
        // Record deaths at ticks 10, 20, 30
        tracker.record_death(10);
        tracker.record_death(20);
        tracker.record_death(30);
        
        let h = tracker.hazard_rate();
        assert!(h > 0.0);
    }
    
    #[test]
    fn test_early_warning() {
        let mut tracker = HazardRateTracker::new(200);
        
        // Low death rate initially
        for i in 0..10 {
            tracker.record_death(i * 10);
        }
        
        // High death rate later
        for i in 0..10 {
            tracker.record_death(100 + i * 2);
        }
        
        let ew = tracker.early_warning_signal();
        assert!(ew > 1.0); // Increasing trend
    }
    
    #[test]
    fn test_multi_universe() {
        let mut multi = MultiUniverseHazard::new(8, 100);
        
        // Need at least 2 deaths per universe for hazard rate
        multi.record_death(0, 10);
        multi.record_death(0, 20);
        multi.record_death(1, 15);
        multi.record_death(1, 25);
        multi.mark_extinct(2);
        
        assert_eq!(multi.extinction_count(), 1);
        assert!(multi.global_hazard() > 0.0);
    }
}
