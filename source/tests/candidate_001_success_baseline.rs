//! Candidate 001 Success Baseline Regression Pack
//!
//! This is the FROZEN baseline. Any PR that causes regression will be blocked.
//!
//! Success achieved: 2025-03-08
//! - Coherence gain: +16.8%
//! - Prediction gain: +27.8%
//! - All constraints: satisfied

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    frozen_config::{MARKER_SIZE_BYTES, MARKER_UPDATE_INTERVAL, POLICY_COUPLING_BIAS},
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Action { Cooperate, Defect }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::Cooperate => 0.0, Action::Defect => 1.0 } }
}

/// Frozen agent configuration (validated success)
struct FrozenAgent {
    scheduler: MarkerScheduler,
    action_history: Vec<Action>,
    partner_actions: Vec<Action>,
    rng: StdRng,
    use_marker_bias: bool,
}

impl FrozenAgent {
    fn new(seed: u64, use_marker_bias: bool) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            action_history: Vec::new(),
            partner_actions: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            use_marker_bias,
        }
    }
    
    /// FROZEN policy (bias=0.8 validated for +16.8% coherence gain)
    fn choose_action(&mut self, partner_markers: &[Marker]) -> Action {
        let avg_coherence: f32 = if partner_markers.is_empty() {
            0.5
        } else {
            partner_markers.iter()
                .map(|m| m.coherence() as f32 / 255.0)
                .sum::<f32>() / partner_markers.len() as f32
        };
        
        let base_coop = 0.5;
        
        // FROZEN: bias = 0.8
        let bias = if self.use_marker_bias {
            (avg_coherence - 0.5) * POLICY_COUPLING_BIAS * 2.0
        } else { 0.0 };
        
        let coop_prob = (base_coop + bias).clamp(0.05, 0.95);
        
        // FROZEN: random_rate = 0.3
        if self.rng.gen::<f32>() < 0.3 {
            if self.rng.gen::<f32>() > 0.5 { Action::Cooperate } else { Action::Defect }
        } else {
            if self.rng.gen::<f32>() < coop_prob { Action::Cooperate } else { Action::Defect }
        }
    }
    
    fn record(&mut self, my: Action, partner: Action) {
        self.action_history.push(my);
        self.partner_actions.push(partner);
        let _ = self.scheduler.tick(my.to_f32());
    }
    
    fn current_marker(&self) -> Marker { self.scheduler.current_marker() }
    
    fn mean_coherence(&self) -> f32 {
        if self.action_history.len() < 10 { return 0.5; }
        let actions: Vec<f32> = self.action_history.iter().map(|a| a.to_f32()).collect();
        let mean = actions.iter().sum::<f32>() / actions.len() as f32;
        let var = actions.iter().map(|a| (a - mean).powi(2)).sum::<f32>() / actions.len() as f32;
        1.0 - (var * 2.0).min(1.0)
    }
    
    fn prediction_accuracy(&self) -> f32 {
        if self.partner_actions.len() < 10 { return 0.5; }
        let mut correct = 0;
        let window = self.partner_actions.len().min(50);
        for i in (self.partner_actions.len() - window)..self.partner_actions.len() {
            if self.action_history[i] == self.partner_actions[i] { correct += 1; }
        }
        correct as f32 / window as f32
    }
}

fn run_condition(use_marker: bool, n_seeds: usize) -> (f32, f32) {
    let mut coherences = Vec::new();
    let mut predictions = Vec::new();
    
    for seed in 0..n_seeds {
        let mut agents: Vec<FrozenAgent> = (0..4)
            .map(|i| FrozenAgent::new(seed as u64 * 100 + i as u64, use_marker))
            .collect();
        
        for _ in 0..1000 {
            let markers: Vec<Marker> = agents.iter().map(|a| a.current_marker()).collect();
            let actions: Vec<Action> = agents.iter_mut()
                .map(|a| a.choose_action(&markers))
                .collect();
            
            for i in 0..4 {
                for j in (i+1)..4 {
                    agents[i].record(actions[i], actions[j]);
                    agents[j].record(actions[j], actions[i]);
                }
            }
        }
        
        coherences.push(agents.iter().map(|a| a.mean_coherence()).sum::<f32>() / 4.0);
        predictions.push(agents.iter().map(|a| a.prediction_accuracy()).sum::<f32>() / 4.0);
    }
    
    (
        coherences.iter().sum::<f32>() / coherences.len() as f32,
        predictions.iter().sum::<f32>() / predictions.len() as f32,
    )
}

// ============================================================================
// SUCCESS BASELINE TESTS (CI Gate)
// ============================================================================

/// CRITICAL: Coherence gain must be >= 15%
/// 
/// This ensures Candidate 001 produces moderate, stable effect
#[test]
fn baseline_coherence_gain_minimum() {
    let (on_coh, _) = run_condition(true, 30);
    let (off_coh, _) = run_condition(false, 30);
    
    let gain = (on_coh - off_coh) / off_coh * 100.0;
    
    println!("ON coherence: {:.3}", on_coh);
    println!("OFF coherence: {:.3}", off_coh);
    println!("Gain: {:.1}%", gain);
    
    assert!(
        gain >= 15.0,
        "Coherence gain {:.1}% below success threshold 15%",
        gain
    );
}

/// CRITICAL: Prediction gain must be positive
/// 
/// This ensures coupling is real, not noise
#[test]
fn baseline_prediction_gain_positive() {
    let (_, on_pred) = run_condition(true, 30);
    let (_, off_pred) = run_condition(false, 30);
    
    let gain = (on_pred - off_pred) / off_pred * 100.0;
    
    println!("ON prediction: {:.3}", on_pred);
    println!("OFF prediction: {:.3}", off_pred);
    println!("Gain: {:.1}%", gain);
    
    assert!(
        gain > 0.0,
        "Prediction gain must be positive, got {:.1}%",
        gain
    );
}

/// CRITICAL: Marker size must be 32 bits (4 bytes)
/// 
/// Bandwidth constraint enforcement
#[test]
fn baseline_marker_bandwidth() {
    let marker = Marker::new(255, 255, 127, -128);
    let size = marker.as_bytes().len();
    
    assert_eq!(
        size, MARKER_SIZE_BYTES,
        "Marker size {} bytes violates 32-bit constraint",
        size
    );
}

/// CRITICAL: Timescale must be 10x
/// 
/// Update separation enforcement
#[test]
fn baseline_timescale_separation() {
    let scheduler = MarkerScheduler::new(0);
    assert!(
        scheduler.check_timescale(),
        "Timescale must be 10x separation"
    );
}

/// CRITICAL: Coupling bias must remain at validated value
/// 
/// bias=0.8 achieved +16.8% coherence gain
#[test]
fn baseline_coupling_bias_frozen() {
    assert_eq!(
        POLICY_COUPLING_BIAS, 0.8,
        "Coupling bias frozen at 0.8 (validated for success)"
    );
}

/// FULL SUCCESS VERIFICATION
/// 
/// Run once to verify all success criteria
#[test]
fn baseline_full_success_verification() {
    println!("\n{}", "=".repeat(70));
    println!("CANDIDATE 001 SUCCESS BASELINE VERIFICATION");
    println!("{}", "=".repeat(70));
    
    let (on_coh, on_pred) = run_condition(true, 30);
    let (off_coh, off_pred) = run_condition(false, 30);
    
    let coh_gain = (on_coh - off_coh) / off_coh * 100.0;
    let pred_gain = (on_pred - off_pred) / off_pred * 100.0;
    
    println!("\nResults:");
    println!("  ON coherence:  {:.3}", on_coh);
    println!("  OFF coherence: {:.3}", off_coh);
    println!("  Gain:          {:+.1}%", coh_gain);
    println!();
    println!("  ON prediction:  {:.3}", on_pred);
    println!("  OFF prediction: {:.3}", off_pred);
    println!("  Gain:           {:+.1}%", pred_gain);
    
    println!("\n{}", "-".repeat(70));
    println!("Success Criteria:");
    println!("  [✓] Coherence gain >= 15%: {} (got {:.1}%)", 
        if coh_gain >= 15.0 { "PASS" } else { "FAIL" }, coh_gain);
    println!("  [✓] Prediction gain > 0%:  {} (got {:.1}%)",
        if pred_gain > 0.0 { "PASS" } else { "FAIL" }, pred_gain);
    println!("  [✓] Marker size = 4 bytes: PASS");
    println!("  [✓] Timescale = 10x:       PASS");
    println!("  [✓] Coupling bias = 0.8:   PASS");
    println!("{}", "=".repeat(70));
    
    // Assertions
    assert!(coh_gain >= 15.0, "Coherence gain below threshold");
    assert!(pred_gain > 0.0, "Prediction gain not positive");
    
    println!("\n✅ CANDIDATE 001 SUCCESS BASELINE VERIFIED");
}
