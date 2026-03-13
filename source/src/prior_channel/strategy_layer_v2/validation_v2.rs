//! Score-First Validation v2
//!
//! PRIMARY GATE: ON > Baseline (not just ON > OFF)
//! SECONDARY: Mechanism preservation >= 90%

/// Validation metrics for a condition
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
    /// PRIMARY v2: ON score > Baseline score?
    pub fn on_beats_baseline(&self) -> bool {
        self.on.avg_score > self.baseline.avg_score
    }
    
    /// SECONDARY: ON score > OFF score?
    pub fn on_beats_off(&self) -> bool {
        self.on.avg_score > self.off.avg_score
    }
    
    /// Score-first full pass (v2 standard)
    pub fn v2_score_first_pass(&self) -> bool {
        self.on_beats_baseline() && self.on_beats_off()
    }
    
    /// Coherence preserved (>= 90% of OFF)?
    pub fn coherence_preserved(&self) -> bool {
        if self.off.avg_coherence <= 0.0 {
            return true;
        }
        let ratio = self.on.avg_coherence / self.off.avg_coherence;
        ratio >= 0.90
    }
    
    /// Prediction maintained (> OFF)?
    pub fn prediction_maintained(&self) -> bool {
        self.on.avg_prediction > self.off.avg_prediction
    }
    
    /// Full v2 validation pass
    pub fn v2_full_pass(&self) -> bool {
        self.v2_score_first_pass() 
            && self.coherence_preserved() 
            && self.prediction_maintained()
    }
}

/// Batch validation across games
#[derive(Clone, Debug)]
pub struct BatchValidation {
    pub games: Vec<GameValidation>,
}

impl BatchValidation {
    /// Count games where ON > Baseline (v2 primary)
    pub fn on_beats_baseline_count(&self) -> usize {
        self.games.iter().filter(|g| g.on_beats_baseline()).count()
    }
    
    /// Count games where ON > OFF
    pub fn on_beats_off_count(&self) -> usize {
        self.games.iter().filter(|g| g.on_beats_off()).count()
    }
    
    /// Count full v2 passes
    pub fn v2_full_pass_count(&self) -> usize {
        self.games.iter().filter(|g| g.v2_full_pass()).count()
    }
    
    /// Check v2 minimum thresholds:
    /// - At least 2/3 games: ON > Baseline (v2 PRIMARY)
    /// - At least 2/3 games: ON > OFF
    /// - All games: mechanism preserved
    pub fn meets_v2_minimum_thresholds(&self) -> bool {
        let n = self.games.len();
        let on_beats_base = self.on_beats_baseline_count();
        let on_beats_off = self.on_beats_off_count();
        let all_preserve = self.games.iter().all(|g| g.coherence_preserved());
        
        on_beats_base >= (n * 2 / 3) &&      // 2/3 ON > Baseline (v2 primary)
        on_beats_off >= (n * 2 / 3) &&       // 2/3 ON > OFF
        all_preserve                         // All preserve mechanism
    }
    
    /// Overall v2 assessment
    pub fn v2_assessment(&self) -> Assessment {
        let n = self.games.len();
        let base_wins = self.on_beats_baseline_count();
        let off_wins = self.on_beats_off_count();
        let full = self.v2_full_pass_count();
        
        if full == n {
            Assessment::V2FullSuccess
        } else if self.meets_v2_minimum_thresholds() {
            Assessment::V2MinimumThreshold
        } else if base_wins >= n / 2 && off_wins >= n / 2 {
            Assessment::V2MixedProgress
        } else {
            Assessment::V2NeedsWork
        }
    }
    
    /// Print v2 report
    pub fn print_v2_report(&self) {
        println!("\n{}", "=".repeat(70));
        println!("STRATEGY LAYER v2 - BASELINE-FIRST VALIDATION REPORT");
        println!("Primary Gate: ON > Baseline | Secondary: ON > OFF");
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
            if game.on_beats_baseline() {
                print!("✅ ON>Base ");
            } else {
                print!("❌ ON<Base ");
            }
            if game.on_beats_off() {
                print!("✅ ON>OFF ");
            } else {
                print!("❌ ON<OFF ");
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
        println!("  ON > Baseline: {}/{} games (Target: 2/3)", 
            self.on_beats_baseline_count(), n);
        println!("  ON > OFF:      {}/{} games (Target: 2/3)", 
            self.on_beats_off_count(), n);
        println!("  Full v2 pass:  {}/{} games", self.v2_full_pass_count(), n);
        
        println!("\nThresholds:");
        println!("  2/3 ON > Baseline: {}", 
            if self.on_beats_baseline_count() >= (n*2/3) { "✅" } else { "❌" });
        println!("  2/3 ON > OFF:      {}", 
            if self.on_beats_off_count() >= (n*2/3) { "✅" } else { "❌" });
        println!("  All preserve:      {}",
            if self.games.iter().all(|g| g.coherence_preserved()) { "✅" } else { "❌" });
        
        println!("\n{}", "=".repeat(70));
        match self.v2_assessment() {
            Assessment::V2FullSuccess => {
                println!("✅ V2 FULL SUCCESS");
                println!("Strategy Layer v2 achieves ON > Baseline with mechanism preserved");
            }
            Assessment::V2MinimumThreshold => {
                println!("✅ V2 MINIMUM THRESHOLD MET");
                println!("ON > Baseline in 2/3 games, continue refinement");
            }
            Assessment::V2MixedProgress => {
                println!("⚠️  V2 MIXED PROGRESS");
                println!("Some progress toward Baseline, continue work");
            }
            Assessment::V2NeedsWork => {
                println!("❌ V2 NEEDS WORK");
                println!("Strategy requires significant revision to beat Baseline");
            }
            _ => {}
        }
        println!("{}", "=".repeat(70));
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Assessment {
    V2FullSuccess,      // All games pass ON > Baseline
    V2MinimumThreshold, // Meets 2/3 Baseline + 2/3 OFF thresholds
    V2MixedProgress,    // Some progress
    V2NeedsWork,        // Little improvement
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
    fn v2_baseline_is_primary() {
        let game = GameValidation {
            game_name: "Test",
            on: make_result(100.0, 0.6, 0.7),  // Good score
            off: make_result(80.0, 0.58, 0.6),
            baseline: make_result(90.0, 0.5, 0.5),  // ON > Base but not great
        };
        
        assert!(game.on_beats_baseline());  // Primary v2 gate
        assert!(game.on_beats_off());
        assert!(game.v2_score_first_pass());
    }
    
    #[test]
    fn v2_fails_if_below_baseline() {
        let game = GameValidation {
            game_name: "Test",
            on: make_result(80.0, 0.6, 0.7),  // ON < Base
            off: make_result(70.0, 0.58, 0.6),
            baseline: make_result(90.0, 0.5, 0.5),
        };
        
        assert!(!game.on_beats_baseline());  // Primary v2 gate fails
        assert!(!game.v2_score_first_pass());
    }
    
    #[test]
    fn v2_thresholds_require_baseline() {
        // Need 2/3 ON > Baseline for v2 minimum threshold
        let batch = BatchValidation {
            games: vec![
                GameValidation {
                    game_name: "G1",
                    on: make_result(100.0, 0.6, 0.7),
                    off: make_result(80.0, 0.58, 0.6),
                    baseline: make_result(90.0, 0.5, 0.5),  // ON > Base
                },
                GameValidation {
                    game_name: "G2",
                    on: make_result(100.0, 0.6, 0.7),
                    off: make_result(80.0, 0.58, 0.6),
                    baseline: make_result(90.0, 0.5, 0.5),  // ON > Base
                },
                GameValidation {
                    game_name: "G3",
                    on: make_result(80.0, 0.6, 0.7),
                    off: make_result(70.0, 0.58, 0.6),
                    baseline: make_result(90.0, 0.5, 0.5),  // ON < Base
                },
            ],
        };
        
        assert_eq!(batch.on_beats_baseline_count(), 2);  // 2/3
        assert_eq!(batch.on_beats_off_count(), 3);       // 3/3
        assert!(batch.meets_v2_minimum_thresholds());
    }
}
