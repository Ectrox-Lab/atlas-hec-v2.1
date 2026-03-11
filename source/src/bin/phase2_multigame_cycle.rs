//! Phase 2: Multi-Game Cycle Runner
//!
//! Cycles through PD / Stag Hunt / Chicken

use agl_mwe::bio_world_v19::{GRID_X, GRID_Y, GRID_Z};
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 10000;

#[derive(Clone, Copy)]
pub enum GameType { PD, StagHunt, Chicken }

pub struct SimpleAgent {
    pub x: usize, pub y: usize, pub z: usize,
    pub alive: bool, pub energy: f32,
    pub strategy_bias: f32, // -1 = defect, 1 = cooperate
    pub game_memory: [f32; 3], // payoff memory for each game type
}

impl SimpleAgent {
    pub fn new(x: usize, y: usize, z: usize) -> Self {
        Self { x, y, z, alive: true, energy: 30.0, 
               strategy_bias: fastrand::f32() * 2.0 - 1.0,
               game_memory: [0.0, 0.0, 0.0] }
    }
    
    pub fn decide(&self, game: GameType, stress: f32) -> bool { // true = cooperate
        let base_prob = (self.strategy_bias + 1.0) / 2.0; // 0 to 1
        let adjusted = base_prob * (1.0 - stress * 0.5); // Stress increases defection
        fastrand::f32() < adjusted
    }
}

fn game_payoff(my_coop: bool, their_coop: bool, game: GameType) -> (f32, f32) {
    match game {
        GameType::PD => match (my_coop, their_coop) {
            (true, true) => (3.0, 3.0),
            (true, false) => (0.0, 5.0),
            (false, true) => (5.0, 0.0),
            (false, false) => (1.0, 1.0),
        },
        GameType::StagHunt => match (my_coop, their_coop) {
            (true, true) => (4.0, 4.0),
            (true, false) => (0.0, 2.0),
            (false, true) => (2.0, 0.0),
            (false, false) => (2.0, 2.0),
        },
        GameType::Chicken => match (my_coop, their_coop) {
            (true, true) => (0.0, 0.0),
            (true, false) => (-1.0, 1.0),
            (false, true) => (1.0, -1.0),
            (false, false) => (-5.0, -5.0),
        },
    }
}

fn run_multigame_cycle(seed: u64) -> (usize, f32, f32) {
    fastrand::seed(seed);
    let mut agents: Vec<SimpleAgent> = (0..100)
        .map(|i| SimpleAgent::new((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z))
        .collect();
    
    let mut game_transitions = 0usize;
    let mut current_game = GameType::PD;
    
    for tick in 0..MAX_TICKS {
        // Cycle games every 3000 ticks
        if tick % 3000 == 0 && tick > 0 {
            current_game = match current_game {
                GameType::PD => { game_transitions += 1; GameType::StagHunt }
                GameType::StagHunt => { game_transitions += 1; GameType::Chicken }
                GameType::Chicken => { game_transitions += 1; GameType::PD }
            };
        }
        
        // Food
        if tick % 100 == 0 {
            for _ in 0..12 {}
        }
        
        // Game interactions
        let n = agents.len();
        for i in 0..n {
            if !agents[i].alive { continue; }
            
            // Find opponent
            if let Some(j) = find_opponent(&agents, i) {
                let stress = 1.0 - (agents[i].energy / 50.0).min(1.0);
                let my_coop = agents[i].decide(current_game, stress);
                let their_stress = 1.0 - (agents[j].energy / 50.0).min(1.0);
                let their_coop = agents[j].decide(current_game, their_stress);
                
                let (my_payoff, _) = game_payoff(my_coop, their_coop, current_game);
                agents[i].energy += my_payoff.max(0.0);
                
                // Update game memory
                let game_idx = match current_game {
                    GameType::PD => 0, GameType::StagHunt => 1, GameType::Chicken => 2,
                };
                agents[i].game_memory[game_idx] = agents[i].game_memory[game_idx] * 0.9 + my_payoff * 0.1;
            }
            
            // Metabolism
            agents[i].energy -= 0.85;
            if agents[i].energy <= 0.0 { agents[i].alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < 0.01 {
                let mut child = SimpleAgent::new(
                    (agent.x + fastrand::usize(0..5)) % GRID_X,
                    (agent.y + fastrand::usize(0..5)) % GRID_Y, agent.z);
                child.energy = 15.0;
                child.strategy_bias = agent.strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let coord = agents.iter().filter(|a| a.alive).map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() 
        / final_pop.max(1) as f32;
    let game_knowledge = agents.iter().filter(|a| a.alive)
        .map(|a| a.game_memory.iter().sum::<f32>() / 3.0).sum::<f32>() / final_pop.max(1) as f32;
    (final_pop, coord, game_knowledge)
}

fn find_opponent(agents: &[SimpleAgent], idx: usize) -> Option<usize> {
    let mut candidates = Vec::new();
    for (i, other) in agents.iter().enumerate() {
        if i == idx || !other.alive { continue; }
        let dist_sq = (agents[idx].x as i32 - other.x as i32).pow(2) +
                     (agents[idx].y as i32 - other.y as i32).pow(2);
        if dist_sq < 36 { candidates.push(i); }
    }
    if candidates.is_empty() { None } else { Some(candidates[fastrand::usize(0..candidates.len())]) }
}

fn main() {
    println!("Multi-Game Cycle - Phase 2 Smoke Test");
    
    let seeds = vec![11001u64, 11002, 11003];
    let mut results = Vec::new();
    
    for seed in &seeds {
        let (final_pop, coord, knowledge) = run_multigame_cycle(*seed);
        let pass = final_pop >= 20;
        results.push((seed, final_pop, coord, knowledge, pass));
        println!("Seed {}: final={} coord={:.2} knowledge={:.2} {}",
            seed, final_pop, coord, knowledge, if pass { "PASS" } else { "FAIL" });
    }
    
    let pass_count = results.iter().filter(|r| r.4).count();
    println!("\nResult: {}/3 passed", pass_count);
    
    // Export
    let mut file = File::create("/tmp/phase2_multigame_cycle.csv").unwrap();
    writeln!(file, "seed,final_pop,coordination,game_knowledge,pass").unwrap();
    for (seed, fp, co, kn, pa) in results {
        writeln!(file, "{},{},{:.2},{:.2},{}", seed, fp, co, kn, pa as i32).unwrap();
    }
    
    if pass_count >= 2 {
        println!("✓ Multi-Game Cycle: PASSED");
        std::process::exit(0);
    } else {
        println!("✗ Multi-Game Cycle: FAILED");
        std::process::exit(1);
    }
}
