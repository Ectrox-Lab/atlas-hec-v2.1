//! Strategy Layer v1 - Mixed Population Test
//!
//! Tests ON agents vs OFF agents in direct competition.
//! 2 ON + 2 OFF agents, measure relative performance.

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    strategy_layer_v1::{
        GamePolicy, GameType,
        opponent_model::classify_opponent,
        game_policies::coop_probability,
        validation::{RunMetrics, ConditionResult},
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

enum AgentType { On, Off }

struct Agent {
    scheduler: MarkerScheduler,
    score: i32,
    actions: Vec<Action>,
    partners: Vec<Action>,
    rng: StdRng,
    agent_type: AgentType,
    game: GameType,
}

impl Agent {
    fn new(seed: u64, agent_type: AgentType, game: GameType) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            score: 0,
            actions: Vec::new(),
            partners: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            agent_type,
            game,
        }
    }
    
    fn act(&mut self, markers: &[Marker]) -> Action {
        match self.agent_type {
            AgentType::Off => {
                // OFF: simple coherence coupling
                let coherence = if markers.is_empty() { 0.5 } else {
                    markers.iter().map(|m| m.coherence() as f32 / 255.0).sum::<f32>() 
                        / markers.len() as f32
                };
                let bias = (coherence - 0.5) * 1.6;
                let coop_prob = (0.5 + bias).clamp(0.05, 0.95);
                
                if self.rng.gen::<f32>() < RANDOM_EXPLORATION_RATE {
                    if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
                } else {
                    if self.rng.gen::<f32>() < coop_prob { Action::C } else { Action::D }
                }
            }
            
            AgentType::On => {
                // ON: Strategy Layer v1
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

fn run_mixed_game(game: GameType, rounds: usize, seeds: usize) -> (ConditionResult, ConditionResult) {
    let mut on_scores = Vec::new();
    let mut off_scores = Vec::new();
    let mut on_coherences = Vec::new();
    let mut off_coherences = Vec::new();
    let mut on_predictions = Vec::new();
    let mut off_predictions = Vec::new();
    
    for seed in 0..seeds {
        // 2 ON + 2 OFF agents
        let mut agents: Vec<Agent> = vec![
            Agent::new(seed as u64 * 1000 + 0, AgentType::On, game),
            Agent::new(seed as u64 * 1000 + 1, AgentType::On, game),
            Agent::new(seed as u64 * 1000 + 2, AgentType::Off, game),
            Agent::new(seed as u64 * 1000 + 3, AgentType::Off, game),
        ];
        
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
        
        // Separate ON and OFF results
        let on_agents: Vec<&Agent> = agents.iter().filter(|a| matches!(a.agent_type, AgentType::On)).collect();
        let off_agents: Vec<&Agent> = agents.iter().filter(|a| matches!(a.agent_type, AgentType::Off)).collect();
        
        on_scores.push(on_agents.iter().map(|a| a.score).sum::<i32>() as f32 / 2.0);
        off_scores.push(off_agents.iter().map(|a| a.score).sum::<i32>() as f32 / 2.0);
        on_coherences.push(on_agents.iter().map(|a| a.coherence()).sum::<f32>() / 2.0);
        off_coherences.push(off_agents.iter().map(|a| a.coherence()).sum::<f32>() / 2.0);
        on_predictions.push(on_agents.iter().map(|a| a.prediction()).sum::<f32>() / 2.0);
        off_predictions.push(off_agents.iter().map(|a| a.prediction()).sum::<f32>() / 2.0);
    }
    
    let on_result = ConditionResult {
        avg_score: on_scores.iter().sum::<f32>() / on_scores.len() as f32,
        avg_coherence: on_coherences.iter().sum::<f32>() / on_coherences.len() as f32,
        avg_prediction: on_predictions.iter().sum::<f32>() / on_predictions.len() as f32,
    };
    
    let off_result = ConditionResult {
        avg_score: off_scores.iter().sum::<f32>() / off_scores.len() as f32,
        avg_coherence: off_coherences.iter().sum::<f32>() / off_coherences.len() as f32,
        avg_prediction: off_predictions.iter().sum::<f32>() / off_predictions.len() as f32,
    };
    
    (on_result, off_result)
}

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("STRATEGY LAYER v1 - MIXED POPULATION TEST (2 ON vs 2 OFF)");
    println!("Direct competition: ON agents vs OFF agents");
    println!("{}", "=".repeat(70));
    
    let rounds = 1000;
    let seeds = 30;
    
    let games = vec![
        (GameType::PD, "PD"),
        (GameType::StagHunt, "Stag"),
        (GameType::Chicken, "Chicken"),
    ];
    
    let mut on_wins = 0;
    let mut total = 0;
    
    for (game, name) in &games {
        let (on, off) = run_mixed_game(*game, rounds, seeds);
        
        println!("\n[{}]", name);
        println!("  Score:      ON={:.1} OFF={:.1} Δ={:+.1}", 
            on.avg_score, off.avg_score, on.avg_score - off.avg_score);
        println!("  Coherence:  ON={:.3} OFF={:.3}", 
            on.avg_coherence, off.avg_coherence);
        println!("  Prediction: ON={:.3} OFF={:.3}", 
            on.avg_prediction, off.avg_prediction);
        
        if on.avg_score > off.avg_score {
            println!("  Result: ✅ ON WINS");
            on_wins += 1;
        } else {
            println!("  Result: ❌ OFF WINS");
        }
        total += 1;
    }
    
    println!("\n{}", "-".repeat(70));
    println!("Summary: ON wins {}/{} games", on_wins, total);
    if on_wins >= 2 {
        println!("✅ MINIMUM THRESHOLD MET (2/3 games ON > OFF)");
    } else {
        println!("❌ NEEDS WORK");
    }
    println!("{}", "=".repeat(70));
}
