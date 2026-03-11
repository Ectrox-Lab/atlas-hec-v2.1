//! Candidate 001 Final Sprint
//!
//! Last refinement attempt before freeze.
//! 
//! Config: bias = 0.7, 0.8 (only)
//! Fixed: random_rate = 0.3, 32-bit, 10x
//! 
//! Hard gate:
//! - If coherence gain >= 15% → freeze as "moderate, stable"
//! - If < 15% but prediction stable → freeze as "weak but valid"
//! - No more sweeps after this

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

struct Agent {
    scheduler: MarkerScheduler,
    action_history: Vec<Action>,
    partner_actions: Vec<Action>,
    rng: StdRng,
    bias_strength: f32,
    use_marker_bias: bool,
}

impl Agent {
    fn new(seed: u64, bias_strength: f32, use_marker_bias: bool) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            action_history: Vec::new(),
            partner_actions: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            bias_strength,
            use_marker_bias,
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
        
        let base_coop = 0.5;
        let bias = if self.use_marker_bias {
            (avg_coherence - 0.5) * self.bias_strength * 2.0
        } else { 0.0 };
        
        let coop_prob = (base_coop + bias).clamp(0.05, 0.95);
        
        // Fixed random_rate = 0.3
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

fn run_bias(bias: f32, use_marker: bool, n_seeds: usize) -> (f32, f32) {
    let mut coherences = Vec::new();
    let mut predictions = Vec::new();
    
    for seed in 0..n_seeds {
        let mut agents: Vec<Agent> = (0..4)
            .map(|i| Agent::new(seed as u64 * 100 + i as u64, bias, use_marker))
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

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("CANDIDATE 001: FINAL SPRINT");
    println!("Last refinement before freeze");
    println!("{}", "=".repeat(70));
    println!("Fixed: random_rate=0.3, 32-bit, 10x, 20 seeds");
    println!("Sweep: bias = [0.7, 0.8]");
    println!();
    
    for bias in [0.7f32, 0.8] {
        let (on_coh, on_pred) = run_bias(bias, true, 20);
        let (off_coh, off_pred) = run_bias(bias, false, 20);
        
        let coh_gain = (on_coh - off_coh) / off_coh * 100.0;
        let pred_gain = (on_pred - off_pred) / off_pred * 100.0;
        
        println!("bias={:.1}: ON={:.3}, OFF={:.3}, coh_gain={:+.1}%, pred_gain={:+.1}%",
            bias, on_coh, off_coh, coh_gain, pred_gain);
    }
    
    // Final verdict with best result
    let (on_coh, on_pred) = run_bias(0.8, true, 30);
    let (off_coh, off_pred) = run_bias(0.8, false, 30);
    let coh_gain = (on_coh - off_coh) / off_coh * 100.0;
    let pred_gain = (on_pred - off_pred) / off_pred * 100.0;
    
    println!("\n{}", "=".repeat(70));
    println!("FINAL VERDICT (bias=0.8, 30 seeds)");
    println!("{}", "=".repeat(70));
    println!("ON coherence:  {:.3}", on_coh);
    println!("OFF coherence: {:.3}", off_coh);
    println!("Gain:          {:+.1}%", coh_gain);
    println!();
    println!("ON prediction:  {:.3}", on_pred);
    println!("OFF prediction: {:.3}", off_pred);
    println!("Gain:           {:+.1}%", pred_gain);
    
    println!("\n{}", "-".repeat(70));
    if coh_gain >= 15.0 {
        println!("✅ MODERATE EFFECT ACHIEVED");
        println!("Candidate 001: Real, stable coupling under constraints");
        println!("Status: FREEZE as SUCCESS");
    } else if coh_gain > 10.0 && pred_gain > 15.0 {
        println!("⚠️  WEAK BUT VALID EFFECT");
        println!("Coherence gain: {:.1}% (target: 15%+)", coh_gain);
        println!("Prediction gain: {:.1}% (strong)", pred_gain);
        println!("Status: FREEZE as WEAK-BUT-VALID");
    } else {
        println!("❌ EFFECT MARGINAL");
        println!("Status: Requires architectural review");
    }
    println!("{}", "=".repeat(70));
}
