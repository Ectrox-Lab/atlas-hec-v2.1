//! Phase 2: Resource Competition Runner
//!
//! Scarce resources, territorial conflict

use agl_mwe::bio_world_v19::{GRID_X, GRID_Y, GRID_Z};
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 10000;

pub struct SimpleAgent {
    pub x: usize, pub y: usize, pub z: usize,
    pub alive: bool, pub energy: f32,
    pub strategy_bias: f32,
}

impl SimpleAgent {
    pub fn new(x: usize, y: usize, z: usize) -> Self {
        Self { x, y, z, alive: true, energy: 30.0, strategy_bias: fastrand::f32() * 2.0 - 1.0 }
    }
}

fn run_resource_competition(seed: u64) -> (usize, usize, f32) {
    fastrand::seed(seed);
    let mut agents: Vec<SimpleAgent> = (0..100)
        .map(|i| SimpleAgent::new((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z))
        .collect();
    
    let mut min_pop = 100usize;
    let mut conflict_count = 0usize;
    
    for tick in 0..MAX_TICKS {
        // Very scarce food
        if tick % 150 == 0 {
            for _ in 0..8 {
                // Limited food patches
            }
        }
        
        // Competition: agents in same region compete
        let n = agents.len();
        for i in 0..n {
            if !agents[i].alive { continue; }
            
            // Check for neighbors (conflict)
            let mut neighbor_count = 0;
            for j in 0..n {
                if i == j || !agents[j].alive { continue; }
                let dist_sq = (agents[i].x as i32 - agents[j].x as i32).pow(2) +
                             (agents[i].y as i32 - agents[j].y as i32).pow(2);
                if dist_sq < 9 { neighbor_count += 1; }
            }
            
            // More neighbors = more competition
            if neighbor_count > 2 {
                conflict_count += 1;
                agents[i].energy -= 2.0; // Competition cost
            }
            
            // Foraging
            if fastrand::f32() < 0.10 { agents[i].energy += 10.0; }
            
            // High metabolism
            agents[i].energy -= 1.0;
            if agents[i].energy <= 0.0 { agents[i].alive = false; }
        }
        
        // Reproduction (hard)
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            // Need more energy to reproduce in competition
            if agent.energy > 50.0 && fastrand::f32() < 0.005 {
                let mut child = SimpleAgent::new(
                    (agent.x + fastrand::usize(0..5)) % GRID_X,
                    (agent.y + fastrand::usize(0..5)) % GRID_Y, agent.z);
                child.energy = 12.0;
                child.strategy_bias = agent.strategy_bias * 0.85 + (fastrand::f32() - 0.5) * 0.3;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        let alive_count = agents.iter().filter(|a| a.alive).count();
        if alive_count < min_pop { min_pop = alive_count; }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let coord = agents.iter().filter(|a| a.alive).map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() 
        / final_pop.max(1) as f32;
    (final_pop, min_pop, coord)
}

fn main() {
    println!("Resource Competition - Phase 2 Smoke Test");
    
    let seeds = vec![10001u64, 10002, 10003];
    let mut results = Vec::new();
    
    for seed in &seeds {
        let (final_pop, min_pop, coord) = run_resource_competition(*seed);
        let pass = final_pop >= 20;
        results.push((seed, final_pop, min_pop, coord, pass));
        println!("Seed {}: final={} min={} coord={:.2} {}",
            seed, final_pop, min_pop, coord, if pass { "PASS" } else { "FAIL" });
    }
    
    let pass_count = results.iter().filter(|r| r.4).count();
    println!("\nResult: {}/3 passed", pass_count);
    
    // Export
    let mut file = File::create("/tmp/phase2_resource_competition.csv").unwrap();
    writeln!(file, "seed,final_pop,min_pop,coordination,pass").unwrap();
    for (seed, fp, mp, co, pa) in results {
        writeln!(file, "{},{},{},{:.2},{}", seed, fp, mp, co, pa as i32).unwrap();
    }
    
    if pass_count >= 2 {
        println!("✓ Resource Competition: PASSED");
        std::process::exit(0);
    } else {
        println!("✗ Resource Competition: FAILED");
        std::process::exit(1);
    }
}
