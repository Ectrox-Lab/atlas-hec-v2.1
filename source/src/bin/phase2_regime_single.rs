//! Phase 2: Regime Shift World - Single Run Test
//!
//! Goal: Verify adaptation tracking
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
    pub adaptations: usize,
}

impl Agent {
    pub fn new(x: f32, y: f32) -> Self {
        Self { x, y, alive: true, energy: 30.0, strategy_bias: fastrand::f32() * 2.0 - 1.0, adaptations: 0 }
    }
}

fn run_regime_shift(seed: u64) -> Vec<Telemetry> {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    let mut telemetry = Vec::new();
    let mut total_adaptations = 0usize;
    
    let start = Instant::now();
    
    for tick in 0..MAX_TICKS {
        // Regime shift every 300 ticks
        if tick % 300 == 0 && tick > 0 {
            for agent in &mut agents {
                if agent.alive {
                    agent.energy -= 8.0; // Stress
                    // Adaptation: positive bias agents adapt better
                    if agent.strategy_bias > 0.0 && fastrand::f32() < 0.3 {
                        agent.energy += 5.0;
                        agent.adaptations += 1;
                        total_adaptations += 1;
                    }
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
            telemetry.push(Telemetry { tick, population: pop, coordination: coord, adaptations: total_adaptations });
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
    pub adaptations: usize,
}

fn main() {
    println!("Regime Shift World - Single Run Test");
    println!("=====================================");
    
    let seed = 14001u64;
    println!("\nRunning seed {} ({} ticks)...", seed, MAX_TICKS);
    
    let telemetry = run_regime_shift(seed);
    
    let last = telemetry.last().unwrap();
    println!("\nResult:");
    println!("  Final population: {}", last.population);
    println!("  Coordination: {:.3}", last.coordination);
    println!("  Total adaptations: {}", last.adaptations);
    println!("  Pass: {}", if last.population >= 20 { "YES" } else { "NO" });
    
    // Export CSV
    let filename = "/tmp/phase2_regime_single.csv";
    let mut file = File::create(filename).unwrap();
    writeln!(file, "tick,population,coordination,adaptations").unwrap();
    for t in &telemetry {
        writeln!(file, "{},{},{:.3},{}", t.tick, t.population, t.coordination, t.adaptations).unwrap();
    }
    println!("\nExported: {}", filename);
    
    // Check adaptations occurred
    if last.adaptations > 0 {
        println!("\n✓ Adaptation tracking active: {} events", last.adaptations);
    } else {
        println!("\n✗ WARNING: no adaptations recorded");
    }
}
