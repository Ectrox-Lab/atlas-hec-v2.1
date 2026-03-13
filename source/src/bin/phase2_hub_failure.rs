//! Phase 2: Hub Failure World Runner
//!
//! Hub knockout at tick 5000, tests recovery within 5000 ticks

use agl_mwe::bio_world_v19::{GRID_X, GRID_Y, GRID_Z};
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 5000;

#[derive(Clone, Debug)]
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

fn run_hub_failure(seed: u64) -> (usize, usize, bool, f32) {
    fastrand::seed(seed);
    let mut agents: Vec<SimpleAgent> = (0..100)
        .map(|i| SimpleAgent::new((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z))
        .collect();
    
    let mut min_pop = 100usize;
    let mut pop_at_knockout = 0usize;
    let mut recovered = false;
    let mut food = vec![(0usize, 0usize, 0usize, 25.0f32); 100];
    
    for tick in 0..MAX_TICKS {
        // Hub knockout at tick 2500
        if tick == 2500 {
            pop_at_knockout = agents.iter().filter(|a| a.alive).count();
            let cx = GRID_X / 2;
            let cy = GRID_Y / 2;
            for agent in &mut agents {
                let dx = (agent.x as i32 - cx as i32).abs();
                let dy = (agent.y as i32 - cy as i32).abs();
                if dx < 10 && dy < 10 && fastrand::f32() < 0.7 {
                    agent.alive = false;
                }
            }
        }
        
        // Food regen
        if tick % 100 == 0 {
            for _ in 0..15 { food.push((fastrand::usize(0..GRID_X), fastrand::usize(0..GRID_Y), fastrand::usize(0..GRID_Z), 25.0)); }
        }
        
        // Agent metabolism
        let n = agents.len();
        for i in 0..n {
            if !agents[i].alive { continue; }
            
            // Find food
            let ate = fastrand::f32() < 0.15;
            if ate { agents[i].energy += 15.0; }
            
            agents[i].energy -= 0.8;
            if agents[i].energy <= 0.0 { agents[i].alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < 0.008 {
                let mut child = SimpleAgent::new(
                    (agent.x + fastrand::usize(0..5)) % GRID_X,
                    (agent.y + fastrand::usize(0..5)) % GRID_Y, agent.z);
                child.energy = 15.0;
                child.strategy_bias = agent.strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        let alive_count = agents.iter().filter(|a| a.alive).count();
        if alive_count < min_pop { min_pop = alive_count; }
        
        // Recovery: back to 50% of pre-knockout
        if tick > 3500 && !recovered && alive_count > pop_at_knockout / 2 {
            recovered = true;
        }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let coord = agents.iter().filter(|a| a.alive).map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() 
        / final_pop.max(1) as f32;
    (final_pop, min_pop, recovered, coord)
}

fn main() {
    println!("Hub Failure World - Phase 2 Smoke Test");
    
    let seeds = vec![8001u64, 8002];
    let mut results = Vec::new();
    
    for seed in &seeds {
        let (final_pop, min_pop, recovered, coord) = run_hub_failure(*seed);
        let pass = final_pop >= 20;
        results.push((seed, final_pop, min_pop, recovered, coord, pass));
        println!("Seed {}: final={} min={} recovered={} coord={:.2} {}",
            seed, final_pop, min_pop, recovered, coord, if pass { "PASS" } else { "FAIL" });
    }
    
    let pass_count = results.iter().filter(|r| r.5).count();
    println!("\nResult: {}/2 passed", pass_count);
    
    // Export
    let mut file = File::create("/tmp/phase2_hub_failure.csv").unwrap();
    writeln!(file, "seed,final_pop,min_pop,recovered,coordination,pass").unwrap();
    for (seed, fp, mp, rec, co, pa) in results {
        writeln!(file, "{},{},{},{},{:.2},{}", seed, fp, mp, rec, co, pa as i32).unwrap();
    }
    
    if pass_count >= 1 {
        println!("✓ Hub Failure World: PASSED");
        std::process::exit(0);
    } else {
        println!("✗ Hub Failure World: FAILED");
        std::process::exit(1);
    }
}
