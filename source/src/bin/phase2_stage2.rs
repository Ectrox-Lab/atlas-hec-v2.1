//! Phase 2 Stage-2: Scale-Up Validation
//!
//! Config: 5 seeds × 3000 ticks
//! Goal: Prove Stage-1 results scale to larger horizon
//! Pass: All envs ≥ 3/5, no degradation >10% vs Stage-1

use std::fs::File;
use std::io::Write;
use std::time::Instant;

const MAX_TICKS: usize = 3000;
const N_SEEDS: usize = 5;
const INITIAL_AGENTS: usize = 100;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Environment { HubFailureWorld, RegimeShiftWorld, ResourceCompetition, MultiGameCycle }

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

pub struct RunResult {
    pub seed: u64,
    pub final_pop: usize,
    pub min_pop: usize,
    pub avg_coordination: f32,
    pub pass: bool,
}

fn run_environment(env: Environment, seed: u64) -> RunResult {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    let mut min_pop = INITIAL_AGENTS;
    let mut pre_knockout_pop = INITIAL_AGENTS;
    let mut game_phase = 0usize;
    
    // Telemetry every 200 ticks (reduced from 100 for performance)
    for tick in 0..MAX_TICKS {
        // Environment-specific logic
        match env {
            Environment::HubFailureWorld => {
                if tick == 1500 { // Hub knockout at 1500
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
            }
            Environment::RegimeShiftWorld => {
                if tick % 750 == 0 && tick > 0 { // Shift every 750
                    for agent in &mut agents {
                        if agent.alive {
                            agent.energy -= 8.0;
                            if agent.strategy_bias > 0.0 && fastrand::f32() < 0.3 {
                                agent.energy += 5.0;
                            }
                        }
                    }
                }
            }
            Environment::ResourceCompetition => {
                // Tuned parameters from Stage-1.5
                if tick % 50 == 0 {
                    for agent in &mut agents {
                        if agent.alive && fastrand::f32() < 0.09 {
                            agent.energy += 7.0;
                        }
                    }
                }
            }
            Environment::MultiGameCycle => {
                if tick % 1000 == 0 && tick > 0 { game_phase = (game_phase + 1) % 3; }
                
                // Game interactions (reduced payoff, Stage-1 fix)
                let n = agents.len();
                for i in 0..n.min(500) { // Cap iterations for performance
                    if i >= agents.len() || !agents[i].alive { continue; }
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
            let metabolism = if env == Environment::ResourceCompetition { 0.85 } else { 0.9 };
            for agent in &mut agents {
                if !agent.alive { continue; }
                if fastrand::f32() < 0.12 { agent.energy += 8.0; }
                agent.energy -= metabolism;
                if agent.energy <= 0.0 { agent.alive = false; }
            }
        }
        
        // Reproduction
        let threshold = if env == Environment::ResourceCompetition { 38.0 } else { 40.0 };
        let repro_rate = match env {
            Environment::ResourceCompetition => 0.005,
            Environment::MultiGameCycle => 0.004,
            _ => 0.005,
        };
        
        // Limit reproduction checks for performance
        let n = agents.len();
        let mut new_agents = Vec::new();
        for i in 0..n {
            if !agents[i].alive { continue; }
            if agents[i].energy > threshold && fastrand::f32() < repro_rate {
                let mut child = Agent::new(
                    (agents[i].x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agents[i].y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
                child.energy = 15.0;
                child.strategy_bias = agents[i].strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        // Track min population
        if tick % 200 == 0 {
            let pop = agents.iter().filter(|a| a.alive).count();
            if pop < min_pop { min_pop = pop; }
        }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    
    // Calculate average coordination
    let alive: Vec<&Agent> = agents.iter().filter(|a| a.alive).collect();
    let avg_coord = if alive.is_empty() { 0.0 } else {
        alive.iter().map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() / alive.len() as f32
    };
    
    let pass = final_pop >= 20 && avg_coord >= 0.5;
    
    RunResult { seed, final_pop, min_pop, avg_coordination: avg_coord, pass }
}

fn find_opponent(agents: &[Agent], idx: usize) -> Option<usize> {
    let mut candidates = Vec::new();
    // Sample subset for performance
    let start = idx + 1;
    let end = (idx + 50).min(agents.len());
    for i in start..end {
        if i >= agents.len() || !agents[i].alive { continue; }
        let dist_sq = (agents[idx].x - agents[i].x).powi(2) + (agents[idx].y - agents[i].y).powi(2);
        if dist_sq < 100.0 { candidates.push(i); }
    }
    if candidates.is_empty() { None } else { Some(candidates[fastrand::usize(0..candidates.len())]) }
}

fn main() {
    println!("============================================================");
    println!("Phase 2 Stage-2: Scale-Up Validation");
    println!("============================================================");
    println!("Config: {} seeds × {} ticks per environment", N_SEEDS, MAX_TICKS);
    println!("Pass threshold: population >= 20, coordination >= 0.5");
    println!("Degradation gate: No env >10% drop vs Stage-1 (2/3 baseline)");
    println!();
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 15000 + i * 2).collect();
    let envs = vec![
        Environment::HubFailureWorld,
        Environment::RegimeShiftWorld,
        Environment::ResourceCompetition,
        Environment::MultiGameCycle,
    ];
    
    // Stage-1 baseline for comparison (2/3 = 67%)
    let stage1_baseline = 0.67f32;
    
    let mut all_results: Vec<(Environment, Vec<RunResult>)> = Vec::new();
    let start_total = Instant::now();
    
    for (env_idx, env) in envs.iter().enumerate() {
        println!("[{}/4] {:?}", env_idx + 1, env);
        let env_start = Instant::now();
        let mut results = Vec::new();
        
        for seed in &seeds {
            let result = run_environment(*env, *seed);
            println!("  Seed {}: pop={:5} min={:4} coord={:.2} {}",
                seed, result.final_pop, result.min_pop, result.avg_coordination,
                if result.pass { "✓" } else { "✗" });
            results.push(result);
        }
        
        let pass_count = results.iter().filter(|r| r.pass).count();
        let pass_rate = pass_count as f32 / N_SEEDS as f32;
        let env_elapsed = env_start.elapsed();
        println!("  -> {}/{} = {:.0}% in {:.1}s\n", pass_count, N_SEEDS, pass_rate * 100.0, env_elapsed.as_secs_f64());
        
        all_results.push((*env, results));
    }
    
    let total_elapsed = start_total.elapsed();
    
    // Summary
    println!("============================================================");
    println!("STAGE-2 SUMMARY");
    println!("============================================================");
    println!("Total time: {:.1}s", total_elapsed.as_secs_f64());
    println!();
    
    let mut all_pass = true;
    let mut any_degradation = false;
    
    for (env, results) in &all_results {
        let pass_count = results.iter().filter(|r| r.pass).count();
        let pass_rate = pass_count as f32 / N_SEEDS as f32;
        let avg_final = results.iter().map(|r| r.final_pop).sum::<usize>() as f32 / N_SEEDS as f32;
        let avg_coord = results.iter().map(|r| r.avg_coordination).sum::<f32>() / N_SEEDS as f32;
        
        // Check degradation (>10% drop vs Stage-1 baseline 67%)
        let degraded = pass_rate < stage1_baseline - 0.10;
        if degraded { any_degradation = true; }
        
        let status = if pass_count >= 3 && !degraded { "✓ PASS" }
                     else if pass_count >= 3 { "~ PASS (degraded)" }
                     else { "✗ FAIL" };
        
        if pass_count < 3 || degraded { all_pass = false; }
        
        println!("{:20} | {:>5.0}% | N={:6.1} | coord={:.2} | {}",
            format!("{:?}", env), pass_rate * 100.0, avg_final, avg_coord, status);
    }
    
    // Critical gates
    let hub_pass = all_results.iter().find(|(e, _)| *e == Environment::HubFailureWorld)
        .map(|(_, r)| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    let regime_pass = all_results.iter().find(|(e, _)| *e == Environment::RegimeShiftWorld)
        .map(|(_, r)| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    
    println!("\nCritical gates:");
    println!("  HubFailureWorld: {}", if hub_pass { "✓" } else { "✗" });
    println!("  RegimeShiftWorld: {}", if regime_pass { "✓" } else { "✗" });
    println!("  Degradation check: {}", if !any_degradation { "✓ PASS" } else { "✗ FAIL" });
    
    // Export CSV
    let filename = "/tmp/phase2_stage2_results.csv";
    let mut file = File::create(filename).unwrap();
    writeln!(file, "environment,seed,final_pop,min_pop,coordination,pass").unwrap();
    for (env, results) in &all_results {
        for r in results {
            writeln!(file, "{:?},{},{},{},{:.3},{}", env, r.seed, r.final_pop, r.min_pop, r.avg_coordination, r.pass as i32).unwrap();
        }
    }
    println!("\nExported: {}", filename);
    
    // Final verdict
    println!("\n============================================================");
    if all_pass && hub_pass && regime_pass {
        println!("✓ PHASE 2 STAGE-2: PASSED");
        println!("Scale-up validation complete. Ready for Phase 3.");
    } else if hub_pass && regime_pass && !any_degradation {
        println!("~ PHASE 2 STAGE-2: PARTIAL");
        println!("Critical gates OK, some envs marginal");
    } else {
        println!("✗ PHASE 2 STAGE-2: FAILED");
        println!("Scale-up reveals instability");
    }
    println!("============================================================");
}
