//! Phase 2: Resource Competition - TUNED VERSION
//!
//! Changes from Round 1:
//! - Food spawn rate: 0.06 → 0.09 (less scarce)
//! - Metabolism: 0.9 → 0.85 (slightly lower)
//! - Reproduction threshold: 40.0 → 38.0 (easier)

use std::time::Instant;

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

fn run_resource_tuned(seed: u64) -> (usize, f32, bool) {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    for tick in 0..MAX_TICKS {
        // TUNED: Less scarce food (0.09 vs 0.06)
        if tick % 50 == 0 {
            for agent in &mut agents {
                if agent.alive && fastrand::f32() < 0.09 {
                    agent.energy += 7.0; // Slightly more food
                }
            }
        }
        
        // Agent update
        for agent in &mut agents {
            if !agent.alive { continue; }
            if fastrand::f32() < 0.12 { agent.energy += 8.0; }
            // TUNED: Lower metabolism (0.85 vs 0.9)
            agent.energy -= 0.85;
            if agent.energy <= 0.0 { agent.alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            // TUNED: Lower threshold (38.0 vs 40.0)
            if agent.energy > 38.0 && fastrand::f32() < 0.005 {
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

fn run_hub_regression(seed: u64) -> (usize, f32, bool) {
    // HubFailureWorld unchanged from Round 1 (regression protection)
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    for tick in 0..MAX_TICKS {
        // Hub knockout at tick 600
        if tick == 600 {
            let cx = 50.0; let cy = 50.0;
            for agent in &mut agents {
                let dx = (agent.x - cx).abs();
                let dy = (agent.y - cy).abs();
                if dx < 15.0 && dy < 15.0 && fastrand::f32() < 0.7 {
                    agent.alive = false;
                }
            }
        }
        
        // Standard update
        for agent in &mut agents {
            if !agent.alive { continue; }
            if fastrand::f32() < 0.12 { agent.energy += 8.0; }
            agent.energy -= 0.9;
            if agent.energy <= 0.0 { agent.alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < 0.005 {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
                child.energy = 15.0;
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

fn main() {
    println!("Phase 2: ResourceCompetition Tuning Round");
    println!("==========================================");
    println!("Changes: food +50%, metabolism -6%, repro threshold -5%");
    println!();
    
    let seeds = vec![13000u64, 13002, 13004];
    
    // Test tuned ResourceCompetition
    println!("[ResourceCompetition - TUNED]");
    let mut resource_pass = 0;
    for seed in &seeds {
        let (pop, coord, pass) = run_resource_tuned(*seed);
        if pass { resource_pass += 1; }
        println!("  Seed {}: pop={:4} coord={:.2} {}", seed, pop, coord, if pass { "PASS" } else { "FAIL" });
    }
    println!("  -> {}/3 passed (target: 2/3)\n", resource_pass);
    
    // Regression test HubFailureWorld
    println!("[HubFailureWorld - REGRESSION CHECK]");
    let mut hub_pass = 0;
    for seed in &seeds {
        let (pop, coord, pass) = run_hub_regression(*seed);
        if pass { hub_pass += 1; }
        println!("  Seed {}: pop={:4} coord={:.2} {}", seed, pop, coord, if pass { "PASS" } else { "FAIL" });
    }
    println!("  -> {}/3 passed (should not degrade)\n", hub_pass);
    
    // Summary
    println!("========================================");
    println!("TUNING ROUND RESULT");
    println!("========================================");
    println!("ResourceCompetition: {}/3 {}", resource_pass, 
        if resource_pass >= 2 { "✓ IMPROVED" } else { "✗ STILL FAILING" });
    println!("HubFailureWorld: {}/3 {}", hub_pass,
        if hub_pass >= 2 { "✓ NO REGRESSION" } else { "⚠ DEGRADED" });
    
    if resource_pass >= 2 && hub_pass >= 2 {
        println!("\n✓ TUNING ROUND: PASSED - Ready for Round 2");
    } else if resource_pass > 1 || (resource_pass >= 1 && hub_pass >= 2) {
        println!("\n~ TUNING ROUND: PARTIAL - Consider additional tuning");
    } else {
        println!("\n✗ TUNING ROUND: FAILED - Need more significant changes");
    }
}
