//! Policy Coupling Refinement
//!
//! Fix: Marker signal not being amplified by action policy.
//! 
//! Current problem: Policy too random (50%), marker signal drowned out.
//! Fix: Coherence-conditioned bias on action selection.

use agl_mwe::prior_channel::{
    PriorChannelMarkerAdapter, Marker, MarkerScheduler,
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Action { Cooperate, Defect }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::Cooperate => 0.0, Action::Defect => 1.0 } }
    fn from_f32(v: f32) -> Self { if v < 0.5 { Action::Cooperate } else { Action::Defect } }
}

#[derive(Clone, Copy)]
enum GameType { PD, StagHunt, Chicken }

impl GameType {
    fn payoff(&self, my: Action, opp: Action) -> i32 {
        match self {
            GameType::PD => match (my, opp) {
                (Action::Cooperate, Action::Cooperate) => 3,
                (Action::Cooperate, Action::Defect) => 0,
                (Action::Defect, Action::Cooperate) => 5,
                (Action::Defect, Action::Defect) => 1,
            },
            GameType::StagHunt => match (my, opp) {
                (Action::Cooperate, Action::Cooperate) => 4,
                (Action::Cooperate, Action::Defect) => 0,
                (Action::Defect, Action::Cooperate) => 2,
                (Action::Defect, Action::Defect) => 2,
            },
            GameType::Chicken => match (my, opp) {
                (Action::Cooperate, Action::Cooperate) => 0,
                (Action::Cooperate, Action::Defect) => -1,
                (Action::Defect, Action::Cooperate) => 1,
                (Action::Defect, Action::Defect) => -10,
            },
        }
    }
}

// ============================================================================
// REFINED AGENT: Coherence-conditioned policy
// ============================================================================

struct RefinedAgent {
    scheduler: MarkerScheduler,
    total_score: i32,
    action_history: Vec<Action>,
    partner_actions: Vec<Action>,
    rng: StdRng,
    // Policy params
    random_rate: f32,
    use_marker_bias: bool,
}

impl RefinedAgent {
    fn new(seed: u64, random_rate: f32, use_marker_bias: bool) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            total_score: 0,
            action_history: Vec::new(),
            partner_actions: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            random_rate,
            use_marker_bias,
        }
    }
    
    /// KEY REFINEMENT: Coherence-conditioned action selection
    fn choose_action(&mut self, partner_markers: &[Marker]) -> Action {
        // Compute partner coherence expectation
        let avg_coherence: f32 = if partner_markers.is_empty() {
            0.5
        } else {
            partner_markers.iter()
                .map(|m| m.coherence() as f32 / 255.0)
                .sum::<f32>() / partner_markers.len() as f32
        };
        
        // Base cooperation probability
        let base_coop_prob = 0.5;
        
        // COUPLING: High coherence → more consistent, lower randomness
        let coherence_bias = if self.use_marker_bias {
            // High coherence partners → cooperate more (expect consistency)
            (avg_coherence - 0.5) * 0.4  // -0.2 to +0.2
        } else {
            0.0
        };
        
        let coop_prob = (base_coop_prob + coherence_bias).clamp(0.1, 0.9);
        
        // Reduced randomness (swept param)
        let effective_random = self.random_rate;
        
        if self.rng.gen::<f32>() < effective_random {
            // Random exploration
            if self.rng.gen::<f32>() > 0.5 { Action::Cooperate } else { Action::Defect }
        } else {
            // Biased selection
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
        // Compute from action history variance
        if self.action_history.len() < 10 { return 0.5; }
        let actions: Vec<f32> = self.action_history.iter().map(|a| a.to_f32()).collect();
        let mean = actions.iter().sum::<f32>() / actions.len() as f32;
        let variance = actions.iter().map(|a| (a - mean).powi(2)).sum::<f32>() / actions.len() as f32;
        1.0 - (variance * 2.0).min(1.0)
    }
    
    fn prediction_accuracy(&self) -> f32 {
        if self.partner_actions.len() < 10 { return 0.5; }
        // Simple: predict partner mirrors our last action if we were consistent
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
// SWEEP EXPERIMENTS
// ============================================================================

fn run_random_rate_sweep() {
    println!("\n{}" , "=".repeat(70));
    println!("EXPERIMENT A: Random Rate Sweep");
    println!("{}", "=".repeat(70));
    println!("Fixed: use_marker_bias=true, Game=PD");
    println!("Sweep: random_rate = [0.5, 0.3, 0.1, 0.0]");
    println!();
    
    let random_rates = vec![0.5f32, 0.3, 0.1, 0.0];
    
    for &rate in &random_rates {
        let mut agents: Vec<RefinedAgent> = (0..4)
            .map(|i| RefinedAgent::new(i as u64 * 100, rate, true))
            .collect();
        
        // Run 1000 rounds
        for _round in 0..1000 {
            let markers: Vec<Marker> = agents.iter()
                .map(|a| a.current_marker())
                .collect();
            
            let actions: Vec<Action> = agents.iter_mut()
                .map(|a| a.choose_action(&markers))
                .collect();
            
            // Pairwise payoffs
            for i in 0..4 {
                for j in (i+1)..4 {
                    let p_i = GameType::PD.payoff(actions[i], actions[j]);
                    let p_j = GameType::PD.payoff(actions[j], actions[i]);
                    agents[i].record(actions[i], actions[j], p_i);
                    agents[j].record(actions[j], actions[i], p_j);
                }
            }
        }
        
        let mean_coherence: f32 = agents.iter().map(|a| a.mean_coherence()).sum::<f32>() / 4.0;
        let mean_pred: f32 = agents.iter().map(|a| a.prediction_accuracy()).sum::<f32>() / 4.0;
        let total_score: i32 = agents.iter().map(|a| a.total_score).sum();
        
        println!("random_rate={:.1}: coherence={:.3}, pred={:.3}, score={}", 
            rate, mean_coherence, mean_pred, total_score);
    }
}

fn run_coupling_ablation() {
    println!("\n{}" , "=".repeat(70));
    println!("EXPERIMENT B: Coupling Ablation");
    println!("{}", "=".repeat(70));
    println!("Fixed: random_rate=0.3, Game=PD");
    println!("Compare: use_marker_bias=false vs true");
    println!();
    
    let conditions = vec![(false, "OFF"), (true, "ON")];
    
    for &(use_bias, label) in &conditions {
        let mut agents: Vec<RefinedAgent> = (0..4)
            .map(|i| RefinedAgent::new(i as u64 * 100, 0.3, use_bias))
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
        
        let mean_coherence: f32 = agents.iter().map(|a| a.mean_coherence()).sum::<f32>() / 4.0;
        let mean_pred: f32 = agents.iter().map(|a| a.prediction_accuracy()).sum::<f32>() / 4.0;
        
        println!("{}: coherence={:.3}, pred={:.3}", label, mean_coherence, mean_pred);
    }
}

fn run_game_breakdown() {
    println!("\n{}" , "=".repeat(70));
    println!("EXPERIMENT C: Game-Specific Breakdown");
    println!("{}", "=".repeat(70));
    println!("Fixed: random_rate=0.3, use_marker_bias=true");
    println!();
    
    let games = vec![(GameType::PD, "PD"), (GameType::StagHunt, "Stag"), (GameType::Chicken, "Chicken")];
    
    for &(game, name) in &games {
        let mut agents: Vec<RefinedAgent> = (0..4)
            .map(|i| RefinedAgent::new(i as u64 * 100, 0.3, true))
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
                    let p_i = game.payoff(actions[i], actions[j]);
                    let p_j = game.payoff(actions[j], actions[i]);
                    agents[i].record(actions[i], actions[j], p_i);
                    agents[j].record(actions[j], actions[i], p_j);
                }
            }
        }
        
        let mean_coherence: f32 = agents.iter().map(|a| a.mean_coherence()).sum::<f32>() / 4.0;
        let mean_pred: f32 = agents.iter().map(|a| a.prediction_accuracy()).sum::<f32>() / 4.0;
        
        println!("{}: coherence={:.3}, pred={:.3}", name, mean_coherence, mean_pred);
    }
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("POLICY COUPLING REFINEMENT");
    println!("Goal: Make marker signal produce behavior bias");
    println!("{}", "=".repeat(70));
    
    run_random_rate_sweep();
    run_coupling_ablation();
    run_game_breakdown();
    
    println!("\n{}" , "=".repeat(70));
    println!("SUMMARY");
    println!("{}", "=".repeat(70));
    println!("Look for:");
    println!("  - Lower random_rate → higher coherence");
    println!("  - ON (use_bias=true) > OFF (use_bias=false)");
    println!("  - One game type shows stronger effect");
    println!("{}", "=".repeat(70));
}
