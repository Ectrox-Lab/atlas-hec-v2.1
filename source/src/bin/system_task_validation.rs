//! System-Level Task Validation
//!
//! Validates that Candidate 001 as mainline default improves task performance.
//!
//! Three conditions: ON / OFF / Baseline
//! Three games: PD / Stag Hunt / Chicken
//! Metrics: task score, coherence, prediction, stability, overhead
//!
//! Pass: ON > OFF and ON > Baseline for all games

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    frozen_config::{POLICY_COUPLING_BIAS, RANDOM_EXPLORATION_RATE},
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;
use std::time::Instant;

#[derive(Clone, Copy, Debug)]
enum Game { PD, StagHunt, Chicken }

impl Game {
    fn payoff(&self, my: Action, opp: Action) -> i32 {
        match self {
            Game::PD => match (my, opp) {
                (Action::C, Action::C) => 3,
                (Action::C, Action::D) => 0,
                (Action::D, Action::C) => 5,
                (Action::D, Action::D) => 1,
            },
            Game::StagHunt => match (my, opp) {
                (Action::C, Action::C) => 4,
                (Action::C, Action::D) => 0,
                (Action::D, Action::C) => 2,
                (Action::D, Action::D) => 2,
            },
            Game::Chicken => match (my, opp) {
                (Action::C, Action::C) => 0,
                (Action::C, Action::D) => -1,
                (Action::D, Action::C) => 1,
                (Action::D, Action::D) => -10,
            },
        }
    }
}

#[derive(Clone, Copy, PartialEq, Debug)]
enum Action { C, D }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::C => 0.0, Action::D => 1.0 } }
}

#[derive(Clone, Copy)]
struct Config {
    use_markers: bool,
    use_coupling: bool,
}

struct Agent {
    scheduler: MarkerScheduler,
    total_score: i32,
    actions: Vec<Action>,
    partners: Vec<Action>,
    rng: StdRng,
    config: Config,
}

impl Agent {
    fn new(seed: u64, config: Config) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            total_score: 0,
            actions: Vec::new(),
            partners: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            config,
        }
    }
    
    fn act(&mut self, partner_markers: &[Marker]) -> Action {
        if !self.config.use_markers {
            return if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D };
        }
        
        let coherence: f32 = if partner_markers.is_empty() { 0.5 } else {
            partner_markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
                / partner_markers.len() as f32
        };
        
        let bias = if self.config.use_coupling {
            (coherence - 0.5) * POLICY_COUPLING_BIAS * 2.0
        } else { 0.0 };
        
        let coop_prob = (0.5 + bias).clamp(0.05, 0.95);
        
        if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
            if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
        } else {
            if self.rng.gen::<f32>() < coop_prob { Action::C } else { Action::D }
        }
    }
    
    fn record(&mut self, my: Action, partner: Action, payoff: i32) {
        self.actions.push(my);
        self.partners.push(partner);
        self.total_score += payoff;
        let _ = self.scheduler.tick(my.to_f32());
    }
    
    fn marker(&self) -> Marker { self.scheduler.current_marker() }
    
    fn coherence(&self) -> f32 {
        if self.actions.len() < 10 { return 0.5; }
        let vals: Vec<f32> = self.actions.iter().map(|a| a.to_f32()).collect();
        let mean = vals.iter().sum::<f32>() / vals.len() as f32;
        let var = vals.iter().map(|v| (v - mean).powi(2)).sum::<f32>() / vals.len() as f32;
        1.0 - (var * 2.0).min(1.0)
    }
    
    fn prediction(&self) -> f32 {
        if self.partners.len() < 10 { return 0.5; }
        let mut correct = 0;
        let w = self.partners.len().min(50);
        for i in (self.partners.len() - w)..self.partners.len() {
            if self.actions[i] == self.partners[i] { correct += 1; }
        }
        correct as f32 / w as f32
    }
    
    fn stability(&self) -> f32 {
        if self.actions.len() < 20 { return 0.0; }
        let half = self.actions.len() / 2;
        let first: f32 = self.actions[..half].iter().map(|a| a.to_f32()).sum::<f32>() / half as f32;
        let second: f32 = self.actions[half..].iter().map(|a| a.to_f32()).sum::<f32>() / (self.actions.len() - half) as f32;
        1.0 - (first - second).abs()
    }
}

struct Arena {
    agents: Vec<Agent>,
    game: Game,
}

impl Arena {
    fn new(n: usize, game: Game, seed: u64, config: Config) -> Self {
        Self {
            agents: (0..n).map(|i| Agent::new(seed + i as u64, config)).collect(),
            game,
        }
    }
    
    fn run(&mut self, rounds: usize) -> (Metrics, u64) {
        let start = Instant::now();
        
        for _ in 0..rounds {
            let markers: Vec<Marker> = self.agents.iter().map(|a| a.marker()).collect();
            let acts: Vec<Action> = self.agents.iter_mut()
                .map(|a| a.act(&markers)).collect();
            
            for i in 0..self.agents.len() {
                for j in (i+1)..self.agents.len() {
                    let pi = self.game.payoff(acts[i], acts[j]);
                    let pj = self.game.payoff(acts[j], acts[i]);
                    self.agents[i].record(acts[i], acts[j], pi);
                    self.agents[j].record(acts[j], acts[i], pj);
                }
            }
        }
        
        let overhead = start.elapsed().as_micros() as u64;
        
        let metrics = Metrics {
            score: self.agents.iter().map(|a| a.total_score).sum::<i32>() / self.agents.len() as i32,
            coherence: self.agents.iter().map(|a| a.coherence()).sum::<f32>() / self.agents.len() as f32,
            prediction: self.agents.iter().map(|a| a.prediction()).sum::<f32>() / self.agents.len() as f32,
            stability: self.agents.iter().map(|a| a.stability()).sum::<f32>() / self.agents.len() as f32,
        };
        
        (metrics, overhead)
    }
}

#[derive(Clone, Copy, Debug)]
struct Metrics {
    score: i32,
    coherence: f32,
    prediction: f32,
    stability: f32,
}

fn run_condition(game: Game, rounds: usize, seeds: usize, config: Config) -> Aggregated {
    let mut scores = Vec::new();
    let mut coherences = Vec::new();
    let mut predictions = Vec::new();
    let mut stabilities = Vec::new();
    let mut overheads = Vec::new();
    
    for seed in 0..seeds {
        let (m, o) = Arena::new(4, game, seed as u64 * 1000, config).run(rounds);
        scores.push(m.score);
        coherences.push(m.coherence);
        predictions.push(m.prediction);
        stabilities.push(m.stability);
        overheads.push(o);
    }
    
    Aggregated {
        score: scores.iter().sum::<i32>() as f32 / scores.len() as f32,
        coherence: coherences.iter().sum::<f32>() / coherences.len() as f32,
        prediction: predictions.iter().sum::<f32>() / predictions.len() as f32,
        stability: stabilities.iter().sum::<f32>() / stabilities.len() as f32,
        overhead: overheads.iter().sum::<u64>() / overheads.len() as u64,
    }
}

#[derive(Clone, Debug)]
struct Aggregated {
    score: f32,
    coherence: f32,
    prediction: f32,
    stability: f32,
    overhead: u64,
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("SYSTEM-LEVEL TASK VALIDATION");
    println!("Candidate 001 as Mainline Default");
    println!("{}", "=".repeat(70));
    
    let rounds = 1000;
    let seeds = 30;
    
    println!("\nConfig: {} rounds × {} seeds", rounds, seeds);
    println!("Games: PD, Stag Hunt, Chicken");
    println!("Conditions: ON (mainline) / OFF / Baseline");
    
    let games = vec![(Game::PD, "PD"), (Game::StagHunt, "Stag"), (Game::Chicken, "Chicken")];
    
    println!("\n{}", "-".repeat(70));
    println!("{:<10} {:>10} {:>10} {:>10} {:>10} {:>12}", 
        "Game", "Score", "Coherence", "Pred", "Stability", "Overhead(μs)");
    println!("{}", "-".repeat(70));
    
    let mut all_pass = true;
    
    for (game, name) in &games {
        let on = run_condition(*game, rounds, seeds, Config { use_markers: true, use_coupling: true });
        let off = run_condition(*game, rounds, seeds, Config { use_markers: true, use_coupling: false });
        let base = run_condition(*game, rounds, seeds, Config { use_markers: false, use_coupling: false });
        
        println!("\n[{} - ON]   {:>10.1} {:>10.3} {:>10.3} {:>10.3} {:>12}",
            name, on.score, on.coherence, on.prediction, on.stability, on.overhead);
        println!("[{} - OFF]  {:>10.1} {:>10.3} {:>10.3} {:>10.3} {:>12}",
            name, off.score, off.coherence, off.prediction, off.stability, off.overhead);
        println!("[{} - Base] {:>10.1} {:>10.3} {:>10.3} {:>10.3} {:>12}",
            name, base.score, base.coherence, base.prediction, base.stability, base.overhead);
        
        let score_win = on.score > off.score && on.score > base.score;
        let pred_positive = on.prediction > off.prediction;
        
        print!("  Validation: ");
        if score_win && pred_positive {
            println!("✅ PASS (ON wins)");
        } else if on.score > off.score || on.score > base.score {
            println!("⚠️  PARTIAL (ON mixed)");
            all_pass = false;
        } else {
            println!("❌ FAIL (ON not best)");
            all_pass = false;
        }
    }
    
    println!("\n{}", "=".repeat(70));
    if all_pass {
        println!("✅ SYSTEM VALIDATION PASSED");
        println!("Candidate 001: Task-beneficial mainline substrate");
        println!("Status: PRODUCTION READY");
    } else {
        println!("⚠️  SYSTEM VALIDATION PARTIAL");
        println!("Some tasks show ON benefit, not all");
        println!("Status: REVIEW REQUIRED");
    }
    println!("{}", "=".repeat(70));
}
