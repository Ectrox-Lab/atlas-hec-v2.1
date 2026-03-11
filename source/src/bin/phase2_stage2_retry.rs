//! Phase 2 Stage-2: FULL RETRY with Updated Parameters
//!
//! Based on Retune v2 results:
//! - HubFailureWorld: Stronger post-knockout boost
//! - ResourceCompetition: Tighter reproduction control

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
    pub post_knockout_boost: bool,
}

impl Agent {
    pub fn new(x: f32, y: f32) -> Self {
        Self { 
            x, y, alive: true, energy: 30.0, 
            strategy_bias: fastrand::f32() * 2.0 - 1.0,
            post_knockout_boost: false,
        }
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
    let mut coord_sum = 0.0;
    let mut coord_count = 0usize;
    
    for tick in 0..MAX_TICKS {
        // Environment-specific logic
        match env {
            Environment::HubFailureWorld => {
                if tick == 1500 { // Hub knockout
                    let cx = 50.0; let cy = 50.0;
                    for agent in &mut agents {
                        let dx = (agent.x - cx).abs();
                        let dy = (agent.y - cy).abs();
                        if dx < 15.0 && dy < 15.0 && fastrand::f32() < 0.7 {
                            agent.alive = false;
                        } else if agent.alive {
                            // UPDATED: Stronger post-knockout boost
                            agent.post_knockout_boost = true;
                            agent.strategy_bias = (agent.strategy_bias + 0.5).min(1.0);
                        }
                    }
                }
                
                // Post-knockout recovery
                if tick > 1500 {
                    for agent in &mut agents {
                        if agent.alive && agent.post_knockout_boost {
                            agent.energy += 0.4; // Recovery bonus
                            if agent.strategy_bias < 0.0 {
                                agent.strategy_bias += 0.02;
                            }
                        }
                    }
                }
            }
            Environment::RegimeShiftWorld => {
                // UNCHANGED from Stage-2
                if tick % 750 == 0 && tick > 0 {
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
                // UPDATED: Tighter resource control
                if tick % 60 == 0 {
                    for agent in &mut agents {
                        if agent.alive && fastrand::f32() < 0.08 {
                            agent.energy += 7.0;
                        }
                    }
                }
            }
            Environment::MultiGameCycle => {
                // UNCHANGED
                if tick % 1000 == 0 && tick > 0 {}
                
                let n = agents.len();
                for i in 0..n.min(500) {
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
                        agents[i].energy -= 0.5;
                    }
                }
            }
        }
        
        // Standard update with UPDATED parameters
        match env {
            Environment::HubFailureWorld => {
                for agent in &mut agents {
                    if !agent.alive { continue; }
                    if fastrand::f32() < 0.12 { agent.energy += 8.0; }
                    agent.energy -= 0.92; // UPDATED
                    if agent.energy <= 0.0 { agent.alive = false; }
                }
            }
            Environment::ResourceCompetition => {
                for agent in &mut agents {
                    if !agent.alive { continue; }
                    if fastrand::f32() < 0.12 { agent.energy += 8.0; }
                    agent.energy -= 0.94; // UPDATED
                    if agent.energy <= 0.0 { agent.alive = false; }
                }
            }
            Environment::RegimeShiftWorld | Environment::MultiGameCycle => {
                for agent in &mut agents {
                    if !agent.alive { continue; }
                    if fastrand::f32() < 0.12 { agent.energy += 8.0; }
                    agent.energy -= 0.9;
                    if agent.energy <= 0.0 { agent.alive = false; }
                }
            }
        }
        
        // Reproduction with UPDATED parameters
        let (threshold, repro_rate) = match env {
            Environment::HubFailureWorld => (40.0, 0.005),
            Environment::ResourceCompetition => (44.0, 0.0025), // UPDATED
            Environment::RegimeShiftWorld => (40.0, 0.005),
            Environment::MultiGameCycle => (40.0, 0.004),
        };
        
        let mut new_agents = Vec::new();
        for agent in &agents {
            if !agent.alive { continue; }
            if agent.energy > threshold && fastrand::f32() < repro_rate {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0));
                child.energy = if env == Environment::ResourceCompetition { 14.0 } else { 15.0 };
                // UPDATED: Stronger persistence for HubFailure
                let persistence = if env == Environment::HubFailureWorld { 0.97 } else { 0.9 };
                child.strategy_bias = agent.strategy_bias * persistence + (fastrand::f32() - 0.5) * 0.1;
                child.post_knockout_boost = agent.post_knockout_boost;
                new_agents.push(child);
            }
        }
        agents.extend(new_agents);
        
        // Track metrics
        if tick % 200 == 0 {
            let pop = agents.iter().filter(|a| a.alive).count();
            if pop < min_pop { min_pop = pop; }
            
            let coord = agents.iter().filter(|a| a.alive)
                .map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() / pop.max(1) as f32;
            coord_sum += coord;
            coord_count += 1;
        }
    }
    
    let final_pop = agents.iter().filter(|a| a.alive).count();
    let avg_coord = if coord_count > 0 { coord_sum / coord_count as f32 } else { 0.0 };
    let pass = final_pop >= 20 && avg_coord >= 0.5;
    
    RunResult { seed, final_pop, min_pop, avg_coordination: avg_coord, pass }
}

fn find_opponent(agents: &[Agent], idx: usize) -> Option<usize> {
    let mut candidates = Vec::new();
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
    println!("Phase 2 Stage-2: FULL RETRY with Updated Parameters");
    println!("============================================================");
    println!("Config: {} seeds × {} ticks", N_SEEDS, MAX_TICKS);
    println!("Updates: HubFailureWorld boost + ResourceCompetition tighter control");
    println!();
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 18000 + i * 2).collect();
    let envs = vec![
        Environment::HubFailureWorld,
        Environment::RegimeShiftWorld,
        Environment::ResourceCompetition,
        Environment::MultiGameCycle,
    ];
    
    let mut all_results: Vec<(Environment, Vec<RunResult>)> = Vec::new();
    let start_total = Instant::now();
    
    for (env_idx, env) in envs.iter().enumerate() {
        println!("[{}/4] {:?}", env_idx + 1, env);
        let env_start = Instant::now();
        let mut results = Vec::new();
        
        for seed in &seeds {
            let result = run_environment(*env, *seed);
            println!("  Seed {}: pop={:5} min={:3} coord={:.2} {}",
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
    println!("STAGE-2 FULL RETRY SUMMARY");
    println!("============================================================");
    println!("Total time: {:.1}s", total_elapsed.as_secs_f64());
    println!();
    
    let mut all_pass = true;
    let stage1_baseline = 0.67f32;
    
    for (env, results) in &all_results {
        let pass_count = results.iter().filter(|r| r.pass).count();
        let pass_rate = pass_count as f32 / N_SEEDS as f32;
        let avg_final = results.iter().map(|r| r.final_pop).sum::<usize>() as f32 / N_SEEDS as f32;
        let avg_coord = results.iter().map(|r| r.avg_coordination).sum::<f32>() / N_SEEDS as f32;
        
        let degraded = pass_rate < stage1_baseline - 0.10;
        let status = if pass_count >= 3 && !degraded { "✓ PASS" }
                     else if pass_count >= 3 { "~ PASS (degraded)" }
                     else { "✗ FAIL" };
        
        if pass_count < 3 || degraded { all_pass = false; }
        
        println!("{:20} | {:>5.0}% | N={:7.1} | coord={:.2} | {}",
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
    
    // Export
    let filename = "/tmp/phase2_stage2_retry_results.csv";
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
        println!("✓ PHASE 2 STAGE-2 RETRY: PASSED");
        println!("Scale-up validation successful with updated parameters.");
        println!("Ready for Phase 3: Long-Horizon Stress");
    } else if hub_pass && regime_pass {
        println!("~ PHASE 2 STAGE-2 RETRY: PARTIAL");
        println!("Critical gates OK, some environments marginal");
    } else {
        println!("✗ PHASE 2 STAGE-2 RETRY: FAILED");
        println!("Critical gates not met - further tuning needed");
    }
    println!("============================================================");
}
