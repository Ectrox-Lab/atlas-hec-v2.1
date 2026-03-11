//! Strategy Layer v2 - Debug Homogenous Population Behavior

use agl_mwe::prior_channel::{
    Marker, MarkerScheduler,
    strategy_layer_v2::{
        GamePolicyV2, GameType,
        game_policies_v2::{coop_probability_v2, detect_population, PopulationType},
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

struct Agent {
    scheduler: MarkerScheduler,
    score: i32,
    actions: Vec<Action>,
    rng: StdRng,
    game: GameType,
}

impl Agent {
    fn new(seed: u64, game: GameType) -> Self {
        Self {
            scheduler: MarkerScheduler::new(0),
            score: 0,
            actions: Vec::new(),
            rng: StdRng::seed_from_u64(seed),
            game,
        }
    }
    
    fn act(&mut self, markers: &[Marker], round: usize, adaptive_explore: bool) -> Action {
        let policy = GamePolicyV2::new(self.game);
        let coop_prob = coop_probability_v2(&policy, markers, round);
        
        // Adaptive exploration: match strategy phases
        let explore_rate = if adaptive_explore {
            if round < 200 {
                0.05  // Very low exploration during bootstrap
            } else if round < 500 {
                0.10  // Medium exploration during transition
            } else {
                0.15  // Normal exploration in steady state
            }
        } else {
            RANDOM_EXPLORATION_RATE  // Fixed 0.3
        };
        
        if self.rng.gen::<f32>() < explore_rate {
            if self.rng.gen::<f32>() > 0.5 { Action::C } else { Action::D }
        } else {
            if self.rng.gen::<f32>() < coop_prob { Action::C } else { Action::D }
        }
    }
    
    fn record(&mut self, my: Action, payoff: i32) {
        self.actions.push(my);
        self.score += payoff;
        let _ = self.scheduler.tick(my.to_f32());
    }
    
    fn marker(&self) -> Marker { self.scheduler.current_marker() }
    fn coherence(&self) -> f32 {
        if self.actions.len() < 10 { return 0.5; }
        let vals: Vec<f32> = self.actions.iter().map(|a| a.to_f32()).collect();
        let mean = vals.iter().sum::<f32>() / vals.len() as f32;
        1.0 - (mean * (1.0 - mean) * 4.0).min(1.0)  // Variance-based coherence
    }
}

fn payoff_pd(my: Action, opp: Action) -> i32 {
    match (my, opp) {
        (Action::C, Action::C) => 3,
        (Action::C, Action::D) => 0,
        (Action::D, Action::C) => 5,
        (Action::D, Action::D) => 1,
    }
}

fn main() {
    println!("Strategy Layer v2 - Debug Homogenous Population\n");
    
    // Test: 4 ON agents with adaptive exploration
    let rounds = 1000;
    let mut agents: Vec<Agent> = (0..4)
        .map(|i| Agent::new(i as u64 * 1000, GameType::PD))
        .collect();
    
    let mut cc_count = 0;
    let mut dd_count = 0;
    let mut cd_count = 0;
    
    for round in 0..rounds {
        let markers: Vec<Marker> = agents.iter().map(|a| a.marker()).collect();
        let pop = detect_population(&markers);
        
        let acts: Vec<Action> = agents.iter_mut()
            .map(|a| a.act(&markers, round, true))  // Adaptive exploration
            .collect();
        
        // Count outcomes
        for i in 0..4 {
            for j in (i+1)..4 {
                match (acts[i], acts[j]) {
                    (Action::C, Action::C) => cc_count += 1,
                    (Action::D, Action::D) => dd_count += 1,
                    _ => cd_count += 1,
                }
                let pi = payoff_pd(acts[i], acts[j]);
                let pj = payoff_pd(acts[j], acts[i]);
                agents[i].record(acts[i], pi);
                agents[j].record(acts[j], pj);
            }
        }
        
        // Debug first 20 rounds
        if round < 20 {
            let avg_coherence = agents.iter().map(|a| a.coherence()).sum::<f32>() / 4.0;
            println!("Round {}: pop={:?}, avg_coh={:.2}, acts={:?}", 
                round, pop, avg_coherence, 
                acts.iter().map(|a| if *a == Action::C { 'C' } else { 'D' }).collect::<Vec<_>>());
        }
    }
    
    let total_pairs = rounds * 6;  // C(4,2) = 6 pairs per round
    println!("\n--- Final Results ---");
    println!("CC pairs: {}/{} ({:.1}%)", cc_count, total_pairs, 100.0 * cc_count as f32 / total_pairs as f32);
    println!("DD pairs: {}/{} ({:.1}%)", dd_count, total_pairs, 100.0 * dd_count as f32 / total_pairs as f32);
    println!("CD pairs: {}/{} ({:.1}%)", cd_count, total_pairs, 100.0 * cd_count as f32 / total_pairs as f32);
    
    for (i, agent) in agents.iter().enumerate() {
        println!("Agent {}: score={}, coherence={:.3}", i, agent.score, agent.coherence());
    }
    
    let avg_score: i32 = agents.iter().map(|a| a.score).sum::<i32>() / 4;
    println!("\nAverage score: {}", avg_score);
    println!("Expected if all C: {}", 3 * rounds * 3);  // 3 partners * 3 payoff * rounds
    println!("Expected if all D: {}", 1 * rounds * 3);  // 3 partners * 1 payoff * rounds
}
