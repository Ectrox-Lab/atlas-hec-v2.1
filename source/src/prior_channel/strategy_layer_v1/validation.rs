//! Score-First Validation
//!
//! PRIMARY GATE: Score improvement
//! SECONDARY: Mechanism preservation (>= 90%)

use crate::prior_channel::Marker;

/// Validation metrics for a single run
#[derive(Clone, Debug)]
pub struct RunMetrics {
    pub score: f32,
    pub coherence: f32,
    pub prediction: f32,
}

/// Aggregated results for a condition
#[derive(Clone, Debug)]
pub struct ConditionResult {
    pub avg_score: f32,
    pub avg_coherence: f32,
    pub avg_prediction: f32,
}

/// Full validation result for a game
#[derive(Clone, Debug)]
pub struct GameValidation {
    pub game_name: &'static str,
    pub on: ConditionResult,
    pub off: ConditionResult,
    pub baseline: ConditionResult,
}

impl GameValidation {
    /// PRIMARY: ON score > OFF score?
    pub fn on_beats_off(&self) -> bool {
        self.on.avg_score > self.off.avg_score
    }
    
    /// PRIMARY: ON score > Baseline?
    pub fn on_beats_baseline(&self) -> bool {
        self.on.avg_score > self.baseline.avg_score
    }
    
    /// Score-first full pass
    pub fn score_first_pass(&self) -> bool {
        self.on_beats_off() && self.on_beats_baseline()
    }
    
    /// SECONDARY: Coherence preserved (>= 90% of OFF)?
    pub fn coherence_preserved(&self) -> bool {
        if self.off.avg_coherence <= 0.0 {
            return true;  // Edge case
        }
        let ratio = self.on.avg_coherence / self.off.avg_coherence;
        ratio >= 0.90
    }
    
    /// SECONDARY: Prediction maintained (> OFF)?
    pub fn prediction_maintained(&self) -> bool {
        self.on.avg_prediction > self.off.avg_prediction
    }
    
    /// Full validation pass
    pub fn full_pass(&self) -> bool {
        self.score_first_pass() 
            && self.coherence_preserved() 
            && self.prediction_maintained()
    }
    
    /// Partial pass (score wins but mechanism degraded)
    pub fn partial_pass(&self) -> bool {
        self.score_first_pass() 
            && (!self.coherence_preserved() || !self.prediction_maintained())
    }
}

/// Batch validation across games
#[derive(Clone, Debug)]
pub struct BatchValidation {
    pub games: Vec<GameValidation>,
}

impl BatchValidation {
    /// Count games where ON > OFF
    pub fn on_beats_off_count(&self) -> usize {
        self.games.iter().filter(|g| g.on_beats_off()).count()
    }
    
    /// Count games where ON > Baseline
    pub fn on_beats_baseline_count(&self) -> usize {
        self.games.iter().filter(|g| g.on_beats_baseline()).count()
    }
    
    /// Count full passes
    pub fn full_pass_count(&self) -> usize {
        self.games.iter().filter(|g| g.full_pass()).count()
    }
    
    /// Check minimum thresholds:
    /// - At least 2/3 games: ON > OFF
    /// - At least 1/3 games: ON > Baseline
    /// - All games: mechanism preserved
    pub fn meets_minimum_thresholds(&self) -> bool {
        let n = self.games.len();
        let on_beats_off = self.on_beats_off_count();
        let on_beats_base = self.on_beats_baseline_count();
        let all_preserve = self.games.iter().all(|g| g.coherence_preserved());
        
        on_beats_off >= (n * 2 / 3) &&      // 2/3 ON > OFF
        on_beats_base >= (n * 1 / 3) &&     // 1/3 ON > Baseline
        all_preserve                         // All preserve mechanism
    }
    
    /// Overall assessment
    pub fn assessment(&self) -> Assessment {
        let n = self.games.len();
        let on_wins = self.on_beats_off_count();
        let base_wins = self.on_beats_baseline_count();
        let full = self.full_pass_count();
        
        if full == n {
            Assessment::FullSuccess
        } else if self.meets_minimum_thresholds() {
            Assessment::MinimumThreshold
        } else if on_wins > n / 2 {
            Assessment::MixedProgress
        } else {
            Assessment::NeedsWork
        }
    }
    
    /// Print report
    pub fn print_report(&self) {
        println!("\n{}", "=".repeat(70));
        println!("SCORE-FIRST VALIDATION REPORT");
        println!("{}", "=".repeat(70));
        
        for game in &self.games {
            println!("\n[{}]", game.game_name);
            println!("  Score:      ON={:.1} OFF={:.1} Base={:.1}",
                game.on.avg_score, game.off.avg_score, game.baseline.avg_score);
            println!("  Coherence:  ON={:.3} OFF={:.3} Base={:.3}",
                game.on.avg_coherence, game.off.avg_coherence, game.baseline.avg_coherence);
            println!("  Prediction: ON={:.3} OFF={:.3} Base={:.3}",
                game.on.avg_prediction, game.off.avg_prediction, game.baseline.avg_prediction);
            
            print!("  Gate: ");
            if game.score_first_pass() {
                print!("✅ Score-FIRST ");
            } else {
                print!("❌ Score-FAIL ");
            }
            if game.coherence_preserved() {
                print!("✅ Coherence ");
            } else {
                print!("⚠️  Coherence ");
            }
            if game.prediction_maintained() {
                println!("✅ Prediction");
            } else {
                println!("⚠️  Prediction");
            }
        }
        
        let n = self.games.len();
        println!("\n{}", "-".repeat(70));
        println!("Summary ({} games):", n);
        println!("  ON > OFF:     {}/{} games", self.on_beats_off_count(), n);
        println!("  ON > Base:    {}/{} games", self.on_beats_baseline_count(), n);
        println!("  Full pass:    {}/{} games", self.full_pass_count(), n);
        
        println!("\nThresholds:");
        let meets = self.meets_minimum_thresholds();
        println!("  2/3 ON > OFF:    {}", 
            if self.on_beats_off_count() >= (n*2/3) { "✅" } else { "❌" });
        println!("  1/3 ON > Base:   {}",
            if self.on_beats_baseline_count() >= (n*1/3) { "✅" } else { "❌" });
        println!("  All preserve:    {}",
            if self.games.iter().all(|g| g.coherence_preserved()) { "✅" } else { "❌" });
        
        println!("\n{}", "=".repeat(70));
        match self.assessment() {
            Assessment::FullSuccess => {
                println!("✅ FULL SUCCESS");
                println!("Strategy Layer v1 achieves task benefits with mechanism preserved");
            }
            Assessment::MinimumThreshold => {
                println!("✅ MINIMUM THRESHOLD MET");
                println!("Continue refinement toward full success");
            }
            Assessment::MixedProgress => {
                println!("⚠️  MIXED PROGRESS");
                println!("Some games show improvement, continue work");
            }
            Assessment::NeedsWork => {
                println!("❌ NEEDS WORK");
                println!("Strategy requires significant revision");
            }
        }
        println!("{}", "=".repeat(70));
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Assessment {
    FullSuccess,      // All games pass
    MinimumThreshold, // Meets 2/3 + 1/3 thresholds
    MixedProgress,    // Some progress but not thresholds
    NeedsWork,        // Little improvement
}

#[cfg(test)]
mod tests {
    use super::*;
    
    fn make_result(score: f32, coherence: f32, prediction: f32) -> ConditionResult {
        ConditionResult {
            avg_score: score,
            avg_coherence: coherence,
            avg_prediction: prediction,
        }
    }
    
    #[test]
    fn full_pass_check() {
        let game = GameValidation {
            game_name: "Test",
            on: make_result(100.0, 0.6, 0.7),
            off: make_result(80.0, 0.58, 0.6),
            baseline: make_result(70.0, 0.5, 0.5),
        };
        
        assert!(game.full_pass());
        assert!(game.score_first_pass());
        assert!(game.coherence_preserved());
        assert!(game.prediction_maintained());
    }
    
    #[test]
    fn score_fail() {
        let game = GameValidation {
            game_name: "Test",
            on: make_result(50.0, 0.6, 0.7),  // Score worse
            off: make_result(80.0, 0.58, 0.6),
            baseline: make_result(70.0, 0.5, 0.5),
        };
        
        assert!(!game.score_first_pass());
        assert!(!game.full_pass());
    }
    
    #[test]
    fn thresholds_3_games() {
        // 3 games: need 2 ON>OFF, 1 ON>Base
        let batch = BatchValidation {
            games: vec![
                GameValidation {
                    game_name: "G1",
                    on: make_result(100.0, 0.6, 0.7),
                    off: make_result(80.0, 0.58, 0.6),
                    baseline: make_result(70.0, 0.5, 0.5),
                },
                GameValidation {
                    game_name: "G2",
                    on: make_result(100.0, 0.6, 0.7),
                    off: make_result(80.0, 0.58, 0.6),
                    baseline: make_result(110.0, 0.5, 0.5),  // ON not > Base
                },
                GameValidation {
                    game_name: "G3",
                    on: make_result(70.0, 0.6, 0.7),  // ON not > OFF
                    off: make_result(80.0, 0.58, 0.6),
                    baseline: make_result(60.0, 0.5, 0.5),
                },
            ],
        };
        
        assert_eq!(batch.on_beats_off_count(), 2);  // 2/3
        assert_eq!(batch.on_beats_baseline_count(), 2);  // 2/3 > 1/3
        assert!(batch.meets_minimum_thresholds());
    }
}
