//! Phase 2: Hub Failure World - Single Run Test
//!
//! Goal: Verify framework logic without performance pressure
//! Config: 1 seed, 1000 ticks, export CSV

use std::fs::File;
use std::io::Write;
use std::time::Instant;

const MAX_TICKS: usize = 1000;
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

fn run_hub_failure(seed: u64) -> Vec<Telemetry> {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    let mut telemetry = Vec::new();
    let mut pre_knockout_pop = INITIAL_AGENTS;
    
    let start = Instant::now();
    
    for tick in 0..MAX_TICKS {
        // Hub knockout at tick 500
        if tick == 500 {
            pre_knockout_pop = agents.iter().filter(|a| a.alive).count();
            let cx = 50.0; let cy = 50.0;
            for agent in &mut agents {
                let dx = (agent.x - cx).abs();
                let dy = (agent.y - cy).abs();
                if dx < 15.0 && dy < 15.0 && fastrand::f32() < 0.7 {
                    agent.alive = false;
                }
            }
        }
        
        // Agent update
        for agent in &mut agents {
            if !agent.alive { continue; }
            if fastrand::f32() < 0.12 { agent.energy += 10.0; }
            agent.energy -= 0.9;
            if agent.energy <= 0.0 { agent.alive = false; }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < 0.008 {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
                child.energy = 15.0;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        // Telemetry every 100 ticks
        if tick % 100 == 0 {
            let pop = agents.iter().filter(|a| a.alive).count();
            let coord = agents.iter().filter(|a| a.alive).map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() 
                / pop.max(1) as f32;
            telemetry.push(Telemetry { tick, population: pop, coordination: coord });
        }
    }
    
    let elapsed = start.elapsed();
    println!("  Completed in {:.2}s", elapsed.as_secs_f64());
    
    telemetry
}

#[derive(Debug)]
pub struct Telemetry {
    pub tick: usize,
    pub population: usize,
    pub coordination: f32,
}

fn main() {
    println!("Hub Failure World - Single Run Test");
    println!("====================================");
    
    let seed = 13001u64;
    println!("\nRunning seed {} ({} ticks)...", seed, MAX_TICKS);
    
    let telemetry = run_hub_failure(seed);
    
    let last = telemetry.last().unwrap();
    println!("\nResult:");
    println!("  Final population: {}", last.population);
    println!("  Coordination: {:.3}", last.coordination);
    println!("  Pass: {}", if last.population >= 20 { "YES" } else { "NO" });
    
    // Export CSV
    let filename = "/tmp/phase2_hub_single.csv";
    let mut file = File::create(filename).unwrap();
    writeln!(file, "tick,population,coordination").unwrap();
    for t in &telemetry {
        writeln!(file, "{},{},{:.3}", t.tick, t.population, t.coordination).unwrap();
    }
    println!("\nExported: {}", filename);
    
    // Verify telemetry variation
    let pops: Vec<usize> = telemetry.iter().map(|t| t.population).collect();
    let min_pop = pops.iter().min().unwrap();
    let max_pop = pops.iter().max().unwrap();
    println!("  Population range: {} - {} (variation: {})", min_pop, max_pop, max_pop - min_pop);
    
    if max_pop > min_pop {
        println!("\n✓ Framework active: metrics are varying");
    } else {
        println!("\n✗ WARNING: metrics constant");
    }
}
