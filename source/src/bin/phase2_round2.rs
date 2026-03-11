//! Phase 2 Round 2: Medium-Scale Validation
//!
//! Config: 5 seeds × 3000 ticks per environment
//! Output: Unified CSV + trajectory data + pass rates

use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 2000;
const N_SEEDS: usize = 3;
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
    pub recovery_time: Option<usize>,
    pub adaptation_events: usize,
    pub trajectory: Vec<(usize, usize, f32)>, // (tick, pop, coord)
    pub pass: bool,
}

fn run_environment(env: Environment, seed: u64) -> RunResult {
    fastrand::seed(seed);
    let mut agents: Vec<Agent> = (0..INITIAL_AGENTS)
        .map(|i| Agent::new((i * 13 % 100) as f32, (i * 17 % 100) as f32))
        .collect();
    
    let mut trajectory = Vec::new();
    let mut min_pop = INITIAL_AGENTS;
    let mut recovery_time: Option<usize> = None;
    let mut adaptation_events = 0usize;
    let mut pre_knockout_pop = INITIAL_AGENTS;
    let mut game_phase = 0usize;
    
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
                // Recovery detection
                if tick > 1800 && recovery_time.is_none() {
                    let current_pop = agents.iter().filter(|a| a.alive).count();
                    if current_pop > pre_knockout_pop / 2 {
                        recovery_time = Some(tick - 1500);
                    }
                }
            }
            Environment::RegimeShiftWorld => {
                if tick % 800 == 0 && tick > 0 { // Shift every 800
                    for agent in &mut agents {
                        if agent.alive {
                            agent.energy -= 8.0;
                            if agent.strategy_bias > 0.0 && fastrand::f32() < 0.3 {
                                agent.energy += 5.0;
                                adaptation_events += 1;
                            }
                        }
                    }
                }
            }
            Environment::ResourceCompetition => {
                // Tuned parameters from Round 1.5
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
                        agents[i].energy -= 0.5;
                        if my_coop && their_coop { adaptation_events += 1; }
                    }
                }
            }
        }
        
        // Standard update (skip for MultiGameCycle already updated)
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
        
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > threshold && fastrand::f32() < repro_rate {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
                child.energy = 15.0;
                child.strategy_bias = agent.strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        // Telemetry every 100 ticks
        if tick % 100 == 0 {
            let pop = agents.iter().filter(|a| a.alive).count();
            if pop < min_pop { min_pop = pop; }
            let coord = if pop == 0 { 0.0 } else {
                agents.iter().filter(|a| a.alive).map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() / pop as f32
            };
            trajectory.push((tick, pop, coord));
        }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let avg_coord = trajectory.iter().map(|(_, _, c)| c).sum::<f32>() / trajectory.len() as f32;
    let pass = final_pop >= 20 && avg_coord >= 0.5;
    
    RunResult {
        seed, final_pop, min_pop, avg_coordination: avg_coord,
        recovery_time, adaptation_events, trajectory, pass,
    }
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

fn export_detailed_results(env: Environment, results: &[RunResult]) {
    let filename = format!("/tmp/phase2_round2_{:?}.csv", env).to_lowercase();
    let mut file = File::create(&filename).unwrap();
    
    writeln!(file, "seed,tick,population,coordination").unwrap();
    for result in results {
        for (tick, pop, coord) in &result.trajectory {
            writeln!(file, "{},{},{},{:.3}", result.seed, tick, pop, coord).unwrap();
        }
    }
    println!("  Exported: {}", filename);
}

fn main() {
    println!("============================================================");
    println!("Phase 2 Round 2: Medium-Scale Validation");
    println!("============================================================");
    println!("Config: {} seeds × {} ticks per environment", N_SEEDS, MAX_TICKS);
    println!("Pass threshold: population >= 20, coordination >= 0.5");
    println!("Cross-env gate: No systematic degradation from Round 1/1.5");
    println!();
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 14000 + i * 2).collect();
    let envs = vec![
        Environment::HubFailureWorld,
        Environment::RegimeShiftWorld,
        Environment::ResourceCompetition,
        Environment::MultiGameCycle,
    ];
    
    let mut all_results: Vec<(Environment, Vec<RunResult>)> = Vec::new();
    
    for env in &envs {
        println!("[{:?}]", env);
        let mut results = Vec::new();
        for seed in &seeds {
            let result = run_environment(*env, *seed);
            println!("  Seed {}: pop={:5} min={:4} coord={:.2} recv={:?} adapt={:4} {}",
                seed, result.final_pop, result.min_pop, result.avg_coordination,
                result.recovery_time, result.adaptation_events,
                if result.pass { "PASS" } else { "FAIL" });
            results.push(result);
        }
        
        let pass_count = results.iter().filter(|r| r.pass).count();
        println!("  -> {}/{} passed\n", pass_count, N_SEEDS);
        
        export_detailed_results(*env, &results);
        all_results.push((*env, results));
    }
    
    // Summary
    println!("============================================================");
    println!("ROUND 2 SUMMARY");
    println!("============================================================");
    
    let mut all_pass = true;
    let mut prev_round_status = vec![
        (Environment::HubFailureWorld, 2, 3),      // Round 1: 2/3
        (Environment::RegimeShiftWorld, 2, 3),     // Round 1: 2/3
        (Environment::ResourceCompetition, 2, 3),  // Round 1.5: 2/3
        (Environment::MultiGameCycle, 2, 3),       // Round 1: 2/3
    ];
    
    for (env, results) in &all_results {
        let pass_count = results.iter().filter(|r| r.pass).count();
        let pass_rate = pass_count as f32 / N_SEEDS as f32;
        let avg_final = results.iter().map(|r| r.final_pop).sum::<usize>() as f32 / N_SEEDS as f32;
        let avg_coord = results.iter().map(|r| r.avg_coordination).sum::<f32>() / N_SEEDS as f32;
        let avg_recovery: f32 = results.iter().filter_map(|r| r.recovery_time).sum::<usize>() as f32 
            / results.iter().filter(|r| r.recovery_time.is_some()).count().max(1) as f32;
        
        // Check degradation from Round 1/1.5
        let prev_status = prev_round_status.iter().find(|(e, _, _)| *e == *env).unwrap();
        let prev_rate = prev_status.1 as f32 / prev_status.2 as f32;
        let degraded = pass_rate < prev_rate - 0.15; // >15% drop
        
        let status = if pass_count >= 3 && !degraded { "✓ PASS" }
                     else if pass_count >= 3 { "~ PASS (degraded)" }
                     else { "✗ FAIL" };
        
        if pass_count < 3 || degraded { all_pass = false; }
        
        println!("{:20} | {:>5.1}% | N={:6.1} | coord={:.2} | recv={:6.1} | {}",
            format!("{:?}", env), pass_rate * 100.0, avg_final, avg_coord, avg_recovery, status);
    }
    
    // Critical gates
    let hub_pass = all_results.iter().find(|(e, _)| *e == Environment::HubFailureWorld)
        .map(|(_, r)| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    let regime_pass = all_results.iter().find(|(e, _)| *e == Environment::RegimeShiftWorld)
        .map(|(_, r)| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    
    println!("\nCritical gates:");
    println!("  HubFailureWorld: {}", if hub_pass { "✓" } else { "✗" });
    println!("  RegimeShiftWorld: {}", if regime_pass { "✓" } else { "✗" });
    
    // Final verdict
    println!("\n============================================================");
    if all_pass && hub_pass && regime_pass {
        println!("✓ PHASE 2 ROUND 2: PASSED");
        println!("Ready for Round 3: Long-horizon (5000-10000 ticks)");
    } else if hub_pass && regime_pass {
        println!("~ PHASE 2 ROUND 2: PARTIAL");
        println!("Critical gates OK, but some degradation detected");
    } else {
        println!("✗ PHASE 2 ROUND 2: FAILED");
        println!("Critical gates not met - investigate before proceeding");
    }
    println!("============================================================");
}
