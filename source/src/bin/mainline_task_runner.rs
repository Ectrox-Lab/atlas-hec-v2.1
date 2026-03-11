//! Mainline Task Runner: End-to-End Behavior Validation
//!
//! Validates Candidate 001 as mainline default in repeated game environments.
//!
//! Three conditions:
//! - MainlinePriorChannel ON (Candidate 001 default)
//! - MainlinePriorChannel OFF (ablation)
//! - Single-agent baseline (no markers)
//!
//! Games: Prisoner's Dilemma, Stag Hunt, Chicken
//! Metrics: coherence, prediction accuracy, stability, overhead

use agl_mwe::prior_channel::{
    MainlinePriorChannel, Marker, MarkerScheduler, PolicyModulation,
    PriorChannelMarkerAdapter,
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::collections::HashMap;

// ============================================================================
// Game Definitions
// ============================================================================

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
enum GameType {
    PrisonersDilemma,
    StagHunt,
    Chicken,
}

impl GameType {
    fn payoff(&self, my_action: Action, opponent_action: Action) -> i32 {
        match self {
            GameType::PrisonersDilemma => match (my_action, opponent_action) {
                (Action::Cooperate, Action::Cooperate) => 3,  // R
                (Action::Cooperate, Action::Defect) => 0,     // S
                (Action::Defect, Action::Cooperate) => 5,     // T
                (Action::Defect, Action::Defect) => 1,        // P
            },
            GameType::StagHunt => match (my_action, opponent_action) {
                (Action::Cooperate, Action::Cooperate) => 4,  // Stag-Stag
                (Action::Cooperate, Action::Defect) => 0,     // Stag-Hare
                (Action::Defect, Action::Cooperate) => 2,     // Hare-Stag
                (Action::Defect, Action::Defect) => 2,        // Hare-Hare
            },
            GameType::Chicken => match (my_action, opponent_action) {
                (Action::Cooperate, Action::Cooperate) => 0,  // Swerve-Swerve
                (Action::Cooperate, Action::Defect) => -1,    // Swerve-Drive
                (Action::Defect, Action::Cooperate) => 1,     // Drive-Swerve
                (Action::Defect, Action::Defect) => -10,      // Drive-Drive
            },
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Action {
    Cooperate,  // C, Stag, Swerve
    Defect,     // D, Hare, Drive
}

impl Action {
    fn to_f32(&self) -> f32 {
        match self {
            Action::Cooperate => 0.0,
            Action::Defect => 1.0,
        }
    }
    
    fn from_f32(v: f32) -> Self {
        if v < 0.5 {
            Action::Cooperate
        } else {
            Action::Defect
        }
    }
}

// ============================================================================
// Agent with Candidate 001 Markers
// ============================================================================

struct MainlineAgent {
    id: u8,
    scheduler: MarkerScheduler,
    total_score: i32,
    action_history: Vec<Action>,
    partner_actions: Vec<Action>,
    coherence_history: Vec<f32>,
    rng: StdRng,
}

impl MainlineAgent {
    fn new(id: u8, seed: u64) -> Self {
        Self {
            id,
            scheduler: MarkerScheduler::new(id),
            total_score: 0,
            action_history: Vec::new(),
            partner_actions: Vec::new(),
            coherence_history: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
        }
    }
    
    /// Choose action based on observed partner markers
    fn choose_action(&mut self, partner_markers: &[Marker], _game: GameType) -> Action {
        if partner_markers.is_empty() {
            // No observation: random
            return if self.rng.gen::<f32>() > 0.5 {
                Action::Cooperate
            } else {
                Action::Defect
            };
        }
        
        // Use partner coherence to predict
        let avg_coherence: f32 = partner_markers.iter()
            .map(|m: &Marker| m.coherence() as f32 / 255.0)
            .sum::<f32>() / partner_markers.len() as f32;
        
        // High coherence partner -> more predictable -> cooperate more
        let coop_prob = 0.3 + avg_coherence * 0.5;  // 0.3 to 0.8
        
        if self.rng.gen::<f32>() < coop_prob {
            Action::Cooperate
        } else {
            Action::Defect
        }
    }
    
    /// Record outcome and update marker
    fn record(&mut self, my_action: Action, partner_action: Action, payoff: i32) {
        self.action_history.push(my_action);
        self.partner_actions.push(partner_action);
        self.total_score += payoff;
        
        // Update marker (every 10 ticks via scheduler)
        if let Some(marker) = self.scheduler.tick(my_action.to_f32()) {
            let coherence: f32 = marker.coherence() as f32 / 255.0;
            self.coherence_history.push(coherence);
        }
    }
    
    fn current_marker(&self) -> Marker {
        self.scheduler.current_marker()
    }
    
    fn mean_coherence(&self) -> f32 {
        if self.coherence_history.is_empty() {
            0.5
        } else {
            self.coherence_history.iter().sum::<f32>() / self.coherence_history.len() as f32
        }
    }
    
    /// Prediction accuracy: how often did we predict partner correctly?
    fn prediction_accuracy(&self) -> f32 {
        if self.partner_actions.len() < 10 {
            return 0.5;
        }
        
        // Simple heuristic: if we cooperated and partner had high coherence,
        // we predicted they'd cooperate
        let mut correct = 0;
        let window = self.partner_actions.len().min(50);
        
        for i in (self.partner_actions.len() - window)..self.partner_actions.len() {
            // Simple prediction: assume partner mirrors our action if coherent
            let predicted = self.action_history[i];
            let actual = self.partner_actions[i];
            
            if predicted == actual {
                correct += 1;
            }
        }
        
        correct as f32 / window as f32
    }
}

// ============================================================================
// Baseline Agent (no markers)
// ============================================================================

struct BaselineAgent {
    id: u8,
    total_score: i32,
    action_history: Vec<Action>,
    rng: StdRng,
}

impl BaselineAgent {
    fn new(id: u8, seed: u64) -> Self {
        Self {
            id,
            total_score: 0,
            action_history: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
        }
    }
    
    fn choose_action(&mut self) -> Action {
        if self.rng.gen::<f32>() > 0.5 {
            Action::Cooperate
        } else {
            Action::Defect
        }
    }
    
    fn record(&mut self, my_action: Action, _partner_action: Action, payoff: i32) {
        self.action_history.push(my_action);
        self.total_score += payoff;
    }
    
    fn mean_coherence(&self) -> f32 {
        0.5  // No coherence tracking
    }
    
    fn prediction_accuracy(&self) -> f32 {
        0.5  // No prediction
    }
}

// ============================================================================
// Arena: Multi-agent game environment
// ============================================================================

enum AgentType {
    Mainline(MainlineAgent),
    Baseline(BaselineAgent),
}

struct Arena {
    agents: Vec<AgentType>,
    use_markers: bool,
    use_priorchannel: bool,
    game: GameType,
    round: usize,
    pc_adapter: Option<PriorChannelMarkerAdapter>,
    rng: StdRng,
}

impl Arena {
    fn new(
        n_agents: usize,
        use_markers: bool,
        use_priorchannel: bool,
        game: GameType,
        seed: u64,
    ) -> Self {
        let mut agents = Vec::new();
        
        for i in 0..n_agents {
            if use_markers {
                agents.push(AgentType::Mainline(MainlineAgent::new(i as u8, seed + i as u64)));
            } else {
                agents.push(AgentType::Baseline(BaselineAgent::new(i as u8, seed + i as u64)));
            }
        }
        
        let pc_adapter = if use_priorchannel {
            Some(PriorChannelMarkerAdapter::new(true))
        } else {
            None
        };
        
        Self {
            agents,
            use_markers,
            use_priorchannel,
            game,
            round: 0,
            pc_adapter,
            rng: StdRng::seed_from_u64(seed),
        }
    }
    
    fn run_round(&mut self) {
        let n = self.agents.len();
        let mut actions: Vec<Action> = Vec::with_capacity(n);
        
        // Collect all markers first (immutable borrow)
        let all_markers: Vec<Option<Marker>> = self.agents
            .iter()
            .map(|a| match a {
                AgentType::Mainline(agent) => Some(agent.current_marker()),
                _ => None,
            })
            .collect();
        
        // Each agent chooses action
        for i in 0..n {
            let action = match &mut self.agents[i] {
                AgentType::Mainline(agent) => {
                    // Observe other agents' markers
                    let partner_markers: Vec<Marker> = all_markers
                        .iter()
                        .enumerate()
                        .filter(|(j, _)| *j != i)
                        .filter_map(|(_, m)| *m)
                        .collect();
                    
                    agent.choose_action(&partner_markers, self.game)
                }
                AgentType::Baseline(agent) => agent.choose_action(),
            };
            actions.push(action);
        }
        
        // Apply PriorChannel modulation if enabled
        if let Some(ref mut adapter) = self.pc_adapter {
            for i in 0..n {
                if let Some(marker) = all_markers[i] {
                    // Get partner markers
                    let pop_markers: Vec<Marker> = all_markers
                        .iter()
                        .enumerate()
                        .filter(|(j, _)| *j != i)
                        .filter_map(|(_, m)| *m)
                        .collect();
                    
                    let modulation = adapter.inject_prior(&marker, &pop_markers, &mut self.rng);
                    
                    // Modulate action probability
                    if modulation.confidence > 0.0 {
                        // High confidence -> more consistent
                        let current = actions[i].to_f32();
                        let modulated = current * (1.0 - modulation.confidence * 0.3);
                        actions[i] = Action::from_f32(modulated);
                    }
                }
            }
        }
        
        // Compute payoffs (round-robin pairing)
        for i in 0..n {
            for j in (i+1)..n {
                let payoff_i = self.game.payoff(actions[i], actions[j]);
                let payoff_j = self.game.payoff(actions[j], actions[i]);
                
                match &mut self.agents[i] {
                    AgentType::Mainline(a) => a.record(actions[i], actions[j], payoff_i),
                    AgentType::Baseline(a) => a.record(actions[i], actions[j], payoff_i),
                }
                match &mut self.agents[j] {
                    AgentType::Mainline(a) => a.record(actions[j], actions[i], payoff_j),
                    AgentType::Baseline(a) => a.record(actions[j], actions[i], payoff_j),
                }
            }
        }
        
        self.round += 1;
    }
    
    fn run(&mut self, n_rounds: usize) -> ArenaMetrics {
        for _ in 0..n_rounds {
            self.run_round();
        }
        
        // Compute aggregate metrics
        let coherences: Vec<f32> = self.agents.iter()
            .filter_map(|a| match a {
                AgentType::Mainline(agent) => Some(agent.mean_coherence()),
                AgentType::Baseline(_) => None,
            })
            .collect();
        
        let predictions: Vec<f32> = self.agents.iter()
            .filter_map(|a| match a {
                AgentType::Mainline(agent) => Some(agent.prediction_accuracy()),
                AgentType::Baseline(_) => None,
            })
            .collect();
        
        let total_score: i32 = self.agents.iter()
            .map(|a| match a {
                AgentType::Mainline(agent) => agent.total_score,
                AgentType::Baseline(agent) => agent.total_score,
            })
            .sum();
        
        ArenaMetrics {
            mean_coherence: if coherences.is_empty() { 0.5 } else { coherences.iter().sum::<f32>() / coherences.len() as f32 },
            coherence_stability: if coherences.len() >= 2 {
                let mean = coherences.iter().sum::<f32>() / coherences.len() as f32;
                let variance = coherences.iter().map(|c| (c - mean).powi(2)).sum::<f32>() / coherences.len() as f32;
                1.0 - variance.sqrt()
            } else { 0.0 },
            prediction_accuracy: if predictions.is_empty() { 0.5 } else { predictions.iter().sum::<f32>() / predictions.len() as f32 },
            total_score,
            bandwidth_overhead: if self.use_priorchannel {
                self.pc_adapter.as_ref().map(|a: &PriorChannelMarkerAdapter| a.bandwidth_stats().total_bits).unwrap_or(0) as f64
            } else { 0.0 },
        }
    }
}

#[derive(Clone, Debug)]
struct ArenaMetrics {
    mean_coherence: f32,
    coherence_stability: f32,
    prediction_accuracy: f32,
    total_score: i32,
    bandwidth_overhead: f64,
}

// ============================================================================
// Three-Condition Benchmark
// ============================================================================

fn run_three_condition_benchmark(
    game: GameType,
    n_agents: usize,
    n_rounds: usize,
    n_seeds: usize,
) -> BenchmarkResult {
    let mut on_results = Vec::new();
    let mut off_results = Vec::new();
    let mut baseline_results = Vec::new();
    
    for seed in 0..n_seeds {
        // Condition A: Mainline ON (Candidate 001 default)
        let mut arena_on = Arena::new(n_agents, true, true, game, seed as u64);
        on_results.push(arena_on.run(n_rounds));
        
        // Condition B: Mainline OFF (markers but no PriorChannel)
        let mut arena_off = Arena::new(n_agents, true, false, game, seed as u64);
        off_results.push(arena_off.run(n_rounds));
        
        // Condition C: Baseline (no markers)
        let mut arena_baseline = Arena::new(n_agents, false, false, game, seed as u64);
        baseline_results.push(arena_baseline.run(n_rounds));
    }
    
    BenchmarkResult {
        game,
        on: aggregate_metrics(&on_results),
        off: aggregate_metrics(&off_results),
        baseline: aggregate_metrics(&baseline_results),
    }
}

fn aggregate_metrics(results: &[ArenaMetrics]) -> AggregatedMetrics {
    let n = results.len() as f32;
    
    AggregatedMetrics {
        mean_coherence: results.iter().map(|m| m.mean_coherence).sum::<f32>() / n,
        coherence_stability: results.iter().map(|m| m.coherence_stability).sum::<f32>() / n,
        prediction_accuracy: results.iter().map(|m| m.prediction_accuracy).sum::<f32>() / n,
        total_score: (results.iter().map(|m| m.total_score).sum::<i32>() as f32 / n) as i32,
        bandwidth_overhead: results.iter().map(|m| m.bandwidth_overhead).sum::<f64>() / n as f64,
    }
}

#[derive(Clone, Debug)]
struct AggregatedMetrics {
    mean_coherence: f32,
    coherence_stability: f32,
    prediction_accuracy: f32,
    total_score: i32,
    bandwidth_overhead: f64,
}

#[derive(Clone, Debug)]
struct BenchmarkResult {
    game: GameType,
    on: AggregatedMetrics,
    off: AggregatedMetrics,
    baseline: AggregatedMetrics,
}

impl BenchmarkResult {
    fn print(&self) {
        println!("\n  Game: {:?}", self.game);
        println!("  {:-<60}", "");
        println!("  {:<25} {:>10} {:>10} {:>10}", "Metric", "ON", "OFF", "Baseline");
        println!("  {:-<60}", "");
        println!("  {:<25} {:>10.3} {:>10.3} {:>10.3}", 
            "Coherence", self.on.mean_coherence, self.off.mean_coherence, self.baseline.mean_coherence);
        println!("  {:<25} {:>10.3} {:>10.3} {:>10.3}", 
            "Stability", self.on.coherence_stability, self.off.coherence_stability, self.baseline.coherence_stability);
        println!("  {:<25} {:>10.3} {:>10.3} {:>10.3}", 
            "Prediction", self.on.prediction_accuracy, self.off.prediction_accuracy, self.baseline.prediction_accuracy);
        println!("  {:<25} {:>10} {:>10} {:>10}", 
            "Score", self.on.total_score, self.off.total_score, self.baseline.total_score);
        println!("  {:<25} {:>10.0} {:>10.0} {:>10}", 
            "Bandwidth (bits)", self.on.bandwidth_overhead, self.off.bandwidth_overhead, 0.0);
        println!("  {:-<60}", "");
        
        // Validation
        let coherence_improvement = self.on.mean_coherence - self.off.mean_coherence;
        let prediction_improvement = self.on.prediction_accuracy - self.off.prediction_accuracy;
        
        println!("  Validation:");
        if self.on.mean_coherence >= 0.7 {
            println!("    ✅ Coherence maintained (ON >= 0.7)");
        } else {
            println!("    ❌ Coherence too low: {:.3}", self.on.mean_coherence);
        }
        
        if coherence_improvement.abs() < 0.2 {
            println!("    ✅ Mechanism intact (|ON-OFF| < 0.2): {:.3}", coherence_improvement);
        } else {
            println!("    ⚠️  Large coherence diff: {:.3}", coherence_improvement);
        }
        
        if self.on.bandwidth_overhead <= 32.0 * 100.0 {  // ~100 samples * 32 bits
            println!("    ✅ Bandwidth overhead acceptable");
        }
    }
}

// ============================================================================
// Main
// ============================================================================

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("MAINLINE TASK RUNNER: Candidate 001 Behavior Validation");
    println!("{}", "=".repeat(70));
    
    let n_agents = 4;
    let n_rounds = 1000;
    let n_seeds = 10;
    
    println!("\nConfiguration:");
    println!("  Agents: {}", n_agents);
    println!("  Rounds: {}", n_rounds);
    println!("  Seeds: {}", n_seeds);
    println!("  Games: Prisoner's Dilemma, Stag Hunt, Chicken");
    
    // Run benchmarks for each game
    let games = vec![
        GameType::PrisonersDilemma,
        GameType::StagHunt,
        GameType::Chicken,
    ];
    
    for game in games {
        let result = run_three_condition_benchmark(game, n_agents, n_rounds, n_seeds);
        result.print();
    }
    
    println!("\n{}", "=".repeat(70));
    println!("Benchmark Complete");
    println!("{}", "=".repeat(70));
}
