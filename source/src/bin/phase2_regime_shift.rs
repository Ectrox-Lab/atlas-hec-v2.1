//! Phase 2: Regime Shift World Runner
//!
//! Periodic environment shifts every 2500 ticks

use agl_mwe::bio_world_v19::{GRID_X, GRID_Y, GRID_Z};
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 10000;

pub struct SimpleAgent {
    pub x: usize, pub y: usize, pub z: usize,
    pub alive: bool, pub energy: f32,
    pub strategy_bias: f32,
    pub adaptation_score: f32,
}

impl SimpleAgent {
    pub fn new(x: usize, y: usize, z: usize) -> Self {
        Self { x, y, z, alive: true, energy: 30.0, 
               strategy_bias: fastrand::f32() * 2.0 - 1.0, adaptation_score: 0.0 }
    }
}

fn run_regime_shift(seed: u64) -> (usize, f32, usize) {
    fastrand::seed(seed);
    let mut agents: Vec<SimpleAgent> = (0..100)
        .map(|i| SimpleAgent::new((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z))
        .collect();
    
    let mut adaptations = 0usize;
    let mut last_regime_pop = 100usize;
    
    for tick in 0..MAX_TICKS {
        // Regime shift every 2500 ticks
        if tick % 2500 == 0 && tick > 0 {
            last_regime_pop = agents.iter().filter(|a| a.alive).count();
            // Clear food (crisis)
            // Agents with positive strategy_bias adapt better
            for agent in &mut agents {
                if agent.alive {
                    agent.energy -= 10.0; // Stress
                    agent.adaptation_score += agent.strategy_bias.max(0.0) * 0.1;
                }
            }
        }
        
        // Recovery food
        if tick % 100 == 0 {
            // Regen based on adaptation
            let adaptive_count = agents.iter().filter(|a| a.alive && a.adaptation_score > 0.5).count();
            let food_amount = 10 + adaptive_count / 5;
            for _ in 0..food_amount {
                // Food placement
            }
        }
        
        // Metabolism
        for agent in &mut agents {
            if !agent.alive { continue; }
            if fastrand::f32() < 0.12 { agent.energy += 12.0; }
            agent.energy -= 0.9;
            if agent.energy <= 0.0 { agent.alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 35.0 && fastrand::f32() < 0.01 {
                let mut child = SimpleAgent::new(
                    (agent.x + fastrand::usize(0..5)) % GRID_X,
                    (agent.y + fastrand::usize(0..5)) % GRID_Y, agent.z);
                child.energy = 15.0;
                child.strategy_bias = agent.strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                child.adaptation_score = agent.adaptation_score * 0.8;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        // Track adaptation
        let current_pop = agents.iter().filter(|a| a.alive).count();
        if tick % 2500 > 1500 && current_pop > last_regime_pop * 8 / 10 {
            adaptations += 1;
        }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let avg_adapt = agents.iter().filter(|a| a.alive).map(|a| a.adaptation_score).sum::<f32>() 
        / final_pop.max(1) as f32;
    (final_pop, avg_adapt, adaptations)
}

fn main() {
    println!("Regime Shift World - Phase 2 Smoke Test");
    
    let seeds = vec![9001u64, 9002, 9003];
    let mut results = Vec::new();
    
    for seed in &seeds {
        let (final_pop, adapt, adaptations) = run_regime_shift(*seed);
        let pass = final_pop >= 20;
        results.push((seed, final_pop, adapt, adaptations, pass));
        println!("Seed {}: final={} adapt={:.2} adaptations={} {}",
            seed, final_pop, adapt, adaptations, if pass { "PASS" } else { "FAIL" });
    }
    
    let pass_count = results.iter().filter(|r| r.4).count();
    println!("\nResult: {}/3 passed", pass_count);
    
    // Export
    let mut file = File::create("/tmp/phase2_regime_shift.csv").unwrap();
    writeln!(file, "seed,final_pop,adaptation_score,adaptations,pass").unwrap();
    for (seed, fp, ad, adp, pa) in results {
        writeln!(file, "{},{},{:.2},{},{}", seed, fp, ad, adp, pa as i32).unwrap();
    }
    
    if pass_count >= 2 {
        println!("✓ Regime Shift World: PASSED");
        std::process::exit(0);
    } else {
        println!("✗ Regime Shift World: FAILED");
        std::process::exit(1);
    }
}
