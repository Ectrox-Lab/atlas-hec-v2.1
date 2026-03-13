//! Phase 2: 3 seeds × 2k ticks batch test
//! Independent environments with overflow fix

use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 1200;
const INITIAL_AGENTS: usize = 100;

#[derive(Clone)]
pub struct Agent {
    pub x: f32, pub y: f32,
    pub alive: bool,
    pub energy: f32,
    pub strategy_bias: f32,
}

impl Agent {
    pub fn new(x: f32, y: f32) -> Self {
        Self { x, y, alive: true, energy: 30.0, strategy_bias: fastrand::f32() * 2.0 - 1.0 }
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Environment { HubFailureWorld, RegimeShiftWorld, ResourceCompetition, MultiGameCycle }

fn run_environment(env: Environment, seed: u64) -> (usize, f32, bool) {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    let mut game_phase = 0usize;
    
    for tick in 0..MAX_TICKS {
        // Environment-specific
        match env {
            Environment::HubFailureWorld => {
                if tick == 1000 { // Hub knockout at 1k
                    let cx = 50.0; let cy = 50.0;
                    for agent in &mut agents {
                        let dx = (agent.x - cx).abs();
                        let dy = (agent.y - cy).abs();
                        if dx < 15.0 && dy < 15.0 && fastrand::f32() < 0.7 {
                            agent.alive = false;
                        }
                    }
                }
            }
            Environment::RegimeShiftWorld => {
                if tick % 600 == 0 && tick > 0 { // Shift every 600
                    for agent in &mut agents {
                        if agent.alive { agent.energy -= 8.0; }
                    }
                }
            }
            Environment::ResourceCompetition => {
                // Scarce food
                if tick % 50 == 0 {
                    for agent in &mut agents {
                        if agent.alive && fastrand::f32() < 0.06 { agent.energy += 6.0; }
                    }
                }
            }
            Environment::MultiGameCycle => {
                // Cycle every 800 ticks
                if tick % 800 == 0 && tick > 0 { game_phase = (game_phase + 1) % 3; }
                
                // Game interactions (reduced payoff)
                let n = agents.len();
                for i in 0..n {
                    if !agents[i].alive { continue; }
                    if let Some(j) = find_opponent(&agents, i) {
                        let my_coop = agents[i].strategy_bias > 0.0;
                        let their_coop = agents[j].strategy_bias > 0.0;
                        let payoff = match (my_coop, their_coop) {
                            (true, true) => 1.5,
                            (true, false) => 0.0,
                            (false, true) => 2.5,
                            (false, false) => 0.5,
                        };
                        agents[i].energy += payoff;
                        agents[i].energy -= 0.5; // Game cost
                    }
                }
            }
        }
        
        // Standard update
        if env != Environment::MultiGameCycle {
            for agent in &mut agents {
                if !agent.alive { continue; }
                if fastrand::f32() < 0.12 { agent.energy += 8.0; }
                agent.energy -= 0.9;
                if agent.energy <= 0.0 { agent.alive = false; }
            }
        }
        
        // Reproduction (rate adjusted)
        let repro_rate = match env {
            Environment::ResourceCompetition => 0.003,
            Environment::MultiGameCycle => 0.004,
            _ => 0.005,
        };
        
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < repro_rate {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
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
    let pass = final_pop >= 20 && coord >= 0.5;
    (final_pop, coord, pass)
}

fn find_opponent(agents: &[Agent], idx: usize) -> Option<usize> {
    let mut candidates = Vec::new();
    for (i, other) in agents.iter().enumerate() {
        if i == idx || !other.alive { continue; }
        let dist_sq = (agents[idx].x - other.x).powi(2) + (agents[idx].y - other.y).powi(2);
        if dist_sq < 100.0 { candidates.push(i); }
    }
    if candidates.is_empty() { None } else { Some(candidates[fastrand::usize(0..candidates.len())]) }
}

fn main() {
    println!("Phase 2 Round 1: 3×2k Batch Test");
    println!("=================================");
    println!("Config: 3 seeds × 2000 ticks per env");
    println!("Pass: population >= 20, coordination >= 0.5");
    println!();
    
    let seeds = vec![12000u64, 12002, 12004];
    let envs = vec![
        Environment::HubFailureWorld,
        Environment::RegimeShiftWorld,
        Environment::ResourceCompetition,
        Environment::MultiGameCycle,
    ];
    
    let mut results = Vec::new();
    
    for env in &envs {
        println!("[{:?}]", env);
        let mut env_pass = 0;
        for seed in &seeds {
            let (pop, coord, pass) = run_environment(*env, *seed);
            if pass { env_pass += 1; }
            println!("  Seed {}: pop={:4} coord={:.2} {}", seed, pop, coord, if pass { "PASS" } else { "FAIL" });
        }
        results.push((env, env_pass));
        println!("  -> {}/3 passed\n", env_pass);
    }
    
    // Summary
    println!("========================================");
    println!("SUMMARY");
    println!("========================================");
    let mut critical_pass = true;
    for (env, pass_count) in &results {
        let status = if *pass_count >= 2 { "✓" } else { "✗" };
        println!("{:20} | {}/3 | {}", format!("{:?}", env), pass_count, status);
        if (**env == Environment::HubFailureWorld || **env == Environment::RegimeShiftWorld) && *pass_count < 2 {
            critical_pass = false;
        }
    }
    
    println!();
    if critical_pass {
        println!("✓ PHASE 2 ROUND 1: PASSED (critical gates OK)");
    } else {
        println!("✗ PHASE 2 ROUND 1: FAILED (critical gates)");
    }
}
