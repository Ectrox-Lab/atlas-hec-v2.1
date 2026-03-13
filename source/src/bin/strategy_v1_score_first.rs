//! Strategy Layer v1 - Score-First Validation Runner
//!
//! Primary gate: Score improvement
//! Threshold: 2/3 games ON > OFF, 1/3 games ON > Baseline

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    strategy_layer_v1::{
        GamePolicy, GameType,
        opponent_model::{classify_opponent, OpponentModel},
        game_policies::coop_probability,
        validation::{BatchValidation, GameValidation, ConditionResult, RunMetrics},
    },
    frozen_config::RANDOM_EXPLORATION_RATE,
};
use rand::{Rng, SeedableRng};
use rand::rngs::StdRng;

#[derive(Clone, Copy, PartialEq)]
enum Action { C, D }

impl Action {
    fn to_f32(&self) -> f32 { match self { Action::C => 0.0, Action::D => 1.0 } }
}

#[derive(Clone, Copy)]
enum Condition { On, Off, Base }

struct Agent {
    scheduler: MarkerScheduler,
    score: i32,
    actions: Vec<Action>,
    partners: Vec<Action>,
    rng: StdRng,
    condition: Condition,
    game: GameType,
}

impl Agent {
    fn new(seed: u64, condition: Condition, game: GameType) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            score: 0,
            actions: Vec::new(),
            partners: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            condition,
            game,
        }
    }
    
    fn act(&mut self, markers: &[Marker]) -> Action {
        match self.condition {
            Condition::Base => {
                if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
            }
            
            Condition::Off => {
                // Original coupling (coherence -> cooperation)
                let coherence = if markers.is_empty() { 0.5 } else {
                    markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
                        / markers.len() as f32
                };
                let bias = (coherence - 0.5) * 1.6;  // bias=0.8 * 2
                let coop_prob = (0.5 + bias).clamp(0.05, 0.95);
                
                if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
                    if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
                } else {
                    if self.rng.gen::<f32>() < coop_prob { Action::C } else { Action::D }
                }
            }
            
            Condition::On => {
                // Strategy Layer v1
                let policy = GamePolicy::new(self.game);
                let opp_model = classify_opponent(markers);
                let coop_prob = coop_probability(&policy, markers, Some(opp_model));
                
                if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
                    if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
                } else {
                    if self.rng.gen::<f32>() < coop_prob { Action::C } else { Action::D }
                }
            }
        }
    }
    
    fn record(&mut self, my: Action, partner: Action, payoff: i32) {
        self.actions.push(my);
        self.partners.push(partner);
        self.score += payoff;
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
}

fn payoff(game: GameType, my: Action, opp: Action) -> i32 {
    match game {
        GameType::PD => match (my, opp) {
            (Action::C, Action::C) => 3,
            (Action::C, Action::D) => 0,
            (Action::D, Action::C) => 5,
            (Action::D, Action::D) => 1,
        },
        GameType::StagHunt => match (my, opp) {
            (Action::C, Action::C) => 4,
            (Action::C, Action::D) => 0,
            (Action::D, Action::C) => 2,
            (Action::D, Action::D) => 2,
        },
        GameType::Chicken => match (my, opp) {
            (Action::C, Action::C) => 0,
            (Action::C, Action::D) => -1,
            (Action::D, Action::C) => 1,
            (Action::D, Action::D) => -10,
        },
    }
}

fn run_game(game: GameType, rounds: usize, seeds: usize, condition: Condition) -> ConditionResult {
    let mut scores = Vec::new();
    let mut coherences = Vec::new();
    let mut predictions = Vec::new();
    
    for seed in 0..seeds {
        let mut agents: Vec<Agent> = (0..4)
            .map(|i| Agent::new(seed as u64 * 1000 + i as u64, condition, game))
            .collect();
        
        for _ in 0..rounds {
            let markers: Vec<Marker> = agents.iter().map(|a| a.marker()).collect();
            let acts: Vec<Action> = agents.iter_mut()
                .map(|a| a.act(&markers)).collect();
            
            for i in 0..4 {
                for j in (i+1)..4 {
                    let pi = payoff(game, acts[i], acts[j]);
                    let pj = payoff(game, acts[j], acts[i]);
                    agents[i].record(acts[i], acts[j], pi);
                    agents[j].record(acts[j], acts[i], pj);
                }
            }
        }
        
        scores.push(agents.iter().map(|a| a.score).sum::<i32>() as f32 / 4.0);
        coherences.push(agents.iter().map(|a| a.coherence()).sum::<f32>() / 4.0);
        predictions.push(agents.iter().map(|a| a.prediction()).sum::<f32>() / 4.0);
    }
    
    ConditionResult {
        avg_score: scores.iter().sum::<f32>() / scores.len() as f32,
        avg_coherence: coherences.iter().sum::<f32>() / coherences.len() as f32,
        avg_prediction: predictions.iter().sum::<f32>() / predictions.len() as f32,
    }
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("STRATEGY LAYER v1 - SCORE-FIRST VALIDATION");
    println!("Target: ON score > OFF AND ON > Baseline");
    println!("Threshold: 2/3 games ON > OFF, 1/3 ON > Baseline");
    println!("{}", "=".repeat(70));
    
    let rounds = 1000;
    let seeds = 30;
    
    let games = vec![
        (GameType::PD, "PD"),
        (GameType::StagHunt, "Stag"),
        (GameType::Chicken, "Chicken"),
    ];
    
    let mut validations = Vec::new();
    
    for (game, name) in &games {
        let on = run_game(*game, rounds, seeds, Condition::On);
        let off = run_game(*game, rounds, seeds, Condition::Off);
        let base = run_game(*game, rounds, seeds, Condition::Base);
        
        validations.push(GameValidation {
            game_name: name,
            on,
            off,
            baseline: base,
        });
    }
    
    let batch = BatchValidation { games: validations };
    batch.print_report();
}
