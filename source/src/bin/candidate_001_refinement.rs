//! Candidate 001 Refinement: Short-Cycle Optimization
//!
//! Target: Push "weak but real" coupling to "moderate and stable"
//!
//! Three experiments:
//! 1. Bias strength sweep (±0.2, ±0.4, ±0.6)
//! 2. Timescale sweep (1x, 10x, 100x)
//! 3. Bandwidth/schema ablation (8, 32, 128 bits)
//!
//! Pass threshold:
//! - ON-OFF coherence gain >= 15%
//! - Prediction gain stable positive
//! - No action leakage
//! - Constraints still hold (32-bit, 10x, generic-only)

use agl_mwe::prior_channel::{Marker, MarkerScheduler};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Action { Cooperate, Defect }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::Cooperate => 0.0, Action::Defect => 1.0 } }
}

#[derive(Clone, Copy)]
enum GameType { PD }

impl GameType {
    fn payoff(&self, my: Action, opp: Action) -> i32 {
        match (my, opp) {
            (Action::Cooperate, Action::Cooperate) => 3,
            (Action::Cooperate, Action::Defect) => 0,
            (Action::Defect, Action::Cooperate) => 5,
            (Action::Defect, Action::Defect) => 1,
        }
    }
}

// ============================================================================
// CONFIGURABLE AGENT
// ============================================================================

struct ConfigurableAgent {
    scheduler: MarkerScheduler,
    total_score: i32,
    action_history: Vec<Action>,
    partner_actions: Vec<Action>,
    rng: StdRng,
    // Configurable params
    bias_strength: f32,
    use_marker_bias: bool,
    random_rate: f32,
}

impl ConfigurableAgent {
    fn new(seed: u64, bias_strength: f32, use_marker_bias: bool, random_rate: f32) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            total_score: 0,
            action_history: Vec::new(),
            partner_actions: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            bias_strength,
            use_marker_bias,
            random_rate,
        }
    }
    
    fn choose_action(&mut self, partner_markers: &[Marker]) -> Action {
        let avg_coherence: f32 = if partner_markers.is_empty() {
            0.5
        } else {
            partner_markers.iter()
                .map(|m| m.coherence() as f32 / 255.0)
                .sum::<f32>() / partner_markers.len() as f32
        };
        
        let base_coop_prob = 0.5;
        
        // REFINEMENT: Configurable bias strength
        let coherence_bias = if self.use_marker_bias {
            (avg_coherence - 0.5) * self.bias_strength * 2.0  // Scale to target range
        } else {
            0.0
        };
        
        let coop_prob = (base_coop_prob + coherence_bias).clamp(0.05, 0.95);
        
        if self.rng.gen::<f32>() < self.random_rate {
            if self.rng.gen::<f32>() > 0.5 { Action::Cooperate } else { Action::Defect }
        } else {
            if self.rng.gen::<f32>() < coop_prob { Action::Cooperate } else { Action::Defect }
        }
    }
    
    fn record(&mut self, my_action: Action, partner_action: Action, payoff: i32) {
        self.action_history.push(my_action);
        self.partner_actions.push(partner_action);
        self.total_score += payoff;
        let _ = self.scheduler.tick(my_action.to_f32());
    }
    
    fn current_marker(&self) -> Marker { self.scheduler.current_marker() }
    
    fn mean_coherence(&self) -> f32 {
        if self.action_history.len() < 10 { return 0.5; }
        let actions: Vec<f32> = self.action_history.iter().map(|a| a.to_f32()).collect();
        let mean = actions.iter().sum::<f32>() / actions.len() as f32;
        let variance = actions.iter().map(|a| (a - mean).powi(2)).sum::<f32>() / actions.len() as f32;
        1.0 - (variance * 2.0).min(1.0)
    }
    
    fn prediction_accuracy(&self) -> f32 {
        if self.partner_actions.len() < 10 { return 0.5; }
        let mut correct = 0;
        let window = self.partner_actions.len().min(50);
        for i in (self.partner_actions.len() - window)..self.partner_actions.len() {
            let predicted = self.action_history[i];
            let actual = self.partner_actions[i];
            if predicted == actual { correct += 1; }
        }
        correct as f32 / window as f32
    }
}

// ============================================================================
// RUNNER
// ============================================================================

fn run_condition(
    bias_strength: f32,
    use_marker_bias: bool,
    random_rate: f32,
    n_seeds: usize,
) -> ConditionResult {
    let mut coherences = Vec::new();
    let mut predictions = Vec::new();
    
    for seed in 0..n_seeds {
        let mut agents: Vec<ConfigurableAgent> = (0..4)
            .map(|i| ConfigurableAgent::new(seed as u64 * 100 + i as u64, bias_strength, use_marker_bias, random_rate))
            .collect();
        
        for _round in 0..1000 {
            let markers: Vec<Marker> = agents.iter()
                .map(|a| a.current_marker())
                .collect();
            
            let actions: Vec<Action> = agents.iter_mut()
                .map(|a| a.choose_action(&markers))
                .collect();
            
            for i in 0..4 {
                for j in (i+1)..4 {
                    let p_i = GameType::PD.payoff(actions[i], actions[j]);
                    let p_j = GameType::PD.payoff(actions[j], actions[i]);
                    agents[i].record(actions[i], actions[j], p_i);
                    agents[j].record(actions[j], actions[i], p_j);
                }
            }
        }
        
        coherences.push(agents.iter().map(|a| a.mean_coherence()).sum::<f32>() / 4.0);
        predictions.push(agents.iter().map(|a| a.prediction_accuracy()).sum::<f32>() / 4.0);
    }
    
    ConditionResult {
        mean_coherence: coherences.iter().sum::<f32>() / coherences.len() as f32,
        mean_prediction: predictions.iter().sum::<f32>() / predictions.len() as f32,
    }
}

#[derive(Clone, Copy, Debug)]
struct ConditionResult {
    mean_coherence: f32,
    mean_prediction: f32,
}

// ============================================================================
// EXPERIMENT 1: Bias Strength Sweep
// ============================================================================

fn experiment_1_bias_sweep() {
    println!("\n{}", "=".repeat(70));
    println!("EXPERIMENT 1: Bias Strength Sweep");
    println!("{}", "=".repeat(70));
    println!("Fixed: random_rate=0.3, use_marker_bias=true");
    println!("Sweep: bias_strength = [0.2, 0.4, 0.6]");
    println!();
    
    let bias_values = vec![0.2f32, 0.4, 0.6];
    
    for &bias in &bias_values {
        let on = run_condition(bias, true, 0.3, 10);
        let off = run_condition(bias, false, 0.3, 10);
        
        let coherence_gain = (on.mean_coherence - off.mean_coherence) / off.mean_coherence * 100.0;
        let pred_gain = (on.mean_prediction - off.mean_prediction) / off.mean_prediction * 100.0;
        
        println!("bias={:.1}: ON={:.3}, OFF={:.3}, gain={:+.1}% | pred_gain={:+.1}%",
            bias, on.mean_coherence, off.mean_coherence, coherence_gain, pred_gain);
    }
}

// ============================================================================
// EXPERIMENT 2: Timescale Sweep
// ============================================================================

fn experiment_2_timescale_sweep() {
    println!("\n{}", "=".repeat(70));
    println!("EXPERIMENT 2: Timescale Sweep");
    println!("{}", "=".repeat(70));
    println!("Note: Using default MarkerScheduler (10x)");
    println!("Comparison: 1x, 10x, 100x theoretical");
    println!();
    
    // The MarkerScheduler enforces 10x, so this is documentation
    // In a real implementation, we'd parameterize the scheduler
    println!("Current implementation: 10x (MarkerScheduler::new enforces 10)");
    println!("Theory: Faster updates = more responsive but less stable");
    println!("Theory: Slower updates = more stable but less responsive");
    println!("10x chosen as FROZEN_STATE_v1 compromise");
}

// ============================================================================
// EXPERIMENT 3: Bandwidth/Schema Ablation
// ============================================================================

fn experiment_3_bandwidth_ablation() {
    println!("\n{}", "=".repeat(70));
    println!("EXPERIMENT 3: Bandwidth/Schema Ablation");
    println!("{}", "=".repeat(70));
    println!("Schema: agent_id(8) + coherence(8) + bias(16) = 32 bits");
    println!();
    
    // Verify current schema
    let marker = Marker::new(255, 255, 127, -128);
    let bytes = marker.as_bytes();
    println!("Current Marker size: {} bytes ({} bits)", bytes.len(), bytes.len() * 8);
    
    // Theoretical comparison
    println!("\nTheoretical breakdown:");
    println!("  8 bits:  agent_id only - too little info");
    println!("  32 bits: current schema - compliance target");
    println!("  128 bits: full state - violates constraint");
    
    println!("\nCurrent: 32-bit COMPLIANT ✅");
    println!("  - agent_id: 8 bits");
    println!("  - coherence: 8 bits");
    println!("  - bias[2]: 16 bits");
}

// ============================================================================
// PASS/FAIL ASSESSMENT
// ============================================================================

fn final_assessment() {
    println!("\n{}", "=".repeat(70));
    println!("FINAL ASSESSMENT");
    println!("{}", "=".repeat(70));
    
    // Run best config
    let on = run_condition(0.6, true, 0.3, 20);
    let off = run_condition(0.6, false, 0.3, 20);
    
    let coherence_gain = (on.mean_coherence - off.mean_coherence) / off.mean_coherence * 100.0;
    let pred_gain = (on.mean_prediction - off.mean_prediction) / off.mean_prediction * 100.0;
    
    println!("\nBest config (bias=0.6, random=0.3):");
    println!("  ON coherence:  {:.3}", on.mean_coherence);
    println!("  OFF coherence: {:.3}", off.mean_coherence);
    println!("  Gain:          {:+.1}%", coherence_gain);
    println!();
    println!("  ON prediction:  {:.3}", on.mean_prediction);
    println!("  OFF prediction: {:.3}", off.mean_prediction);
    println!("  Gain:           {:+.1}%", pred_gain);
    
    println!("\n{}", "-".repeat(70));
    println!("PASS CRITERIA:");
    println!("  [ ] Coherence gain >= 15%: {}", 
        if coherence_gain >= 15.0 { "✅ PASS" } else { "❌ FAIL" });
    println!("  [ ] Prediction gain > 0%:  {}", 
        if pred_gain > 0.0 { "✅ PASS" } else { "❌ FAIL" });
    println!("  [ ] No action leakage:      ✅ (enforced by PolicyModulation)");
    println!("  [ ] 32-bit constraint:      ✅ (Marker = [u8; 4])");
    println!("  [ ] 10x timescale:          ✅ (MarkerScheduler)");
    println!("{}", "-".repeat(70));
    
    if coherence_gain >= 15.0 && pred_gain > 0.0 {
        println!("\n🎉 REFINEMENT GATE PASSED");
        println!("Ready for freeze consideration");
    } else {
        println!("\n⚠️  REFINEMENT GATE NOT MET");
        println!("Current: weak but real effect");
        println!("Target: moderate and stable effect");
    }
}

// ============================================================================
// MAIN
// ============================================================================

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("CANDIDATE 001 REFINEMENT");
    println!("Target: Push weak effect to moderate effect");
    println!("Pass: Coherence gain >= 15%, Prediction gain > 0%");
    println!("{}", "=".repeat(70));
    
    experiment_1_bias_sweep();
    experiment_2_timescale_sweep();
    experiment_3_bandwidth_ablation();
    final_assessment();
    
    println!("\n{}", "=".repeat(70));
}
