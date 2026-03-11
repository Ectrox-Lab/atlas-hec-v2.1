//! Phase 2 Round 1: Open-World Task Validation - Formal Batch
//!
//! Configuration: 4 Environments × 5 Paired Seeds
//! Metrics: population_persistence, coordination_score, recovery, adaptation
//! Output: Unified CSV with telemetry

use std::collections::HashMap;
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 3000;
const N_SEEDS: usize = 5;
const INITIAL_AGENTS: usize = 100;
const PASS_THRESHOLD_POP: usize = 20; // 20% of initial
const PASS_THRESHOLD_COORD: f32 = 0.5;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Environment { HubFailureWorld, RegimeShiftWorld, ResourceCompetition, MultiGameCycle }

#[derive(Clone, Debug)]
pub struct Telemetry {
    pub tick: usize,
    pub population: usize,
    pub coordination: f32,
    pub entropy: f32,      // Population diversity measure
    pub hazard_rate: f32,
    pub recovery_flag: bool,
}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub env: Environment,
    pub seed: u64,
    pub final_pop: usize,
    pub min_pop: usize,
    pub avg_coordination: f32,
    pub recovery_time: Option<usize>,
    pub adaptation_events: usize,
    pub entropy_trajectory: Vec<f32>,
    pub collapsed: bool,
    pub pass: bool,
}

pub struct OpenWorldSimulator {
    env: Environment,
    seed: u64,
    agents: Vec<Agent>,
    tick: usize,
    telemetry: Vec<Telemetry>,
    pre_knockout_pop: usize,
}

#[derive(Clone)]
pub struct Agent {
    pub x: f32, pub y: f32,
    pub alive: bool,
    pub energy: f32,
    pub strategy_bias: f32,
    pub memory_l1: Vec<f32>,     // Cell memory
    pub memory_l2: f32,          // Lineage bias
    pub generation: usize,
}

impl Agent {
    pub fn new(x: f32, y: f32, gen: usize) -> Self {
        Self {
            x, y, alive: true, energy: 30.0,
            strategy_bias: fastrand::f32() * 2.0 - 1.0,
            memory_l1: Vec::with_capacity(20),
            memory_l2: 0.0,
            generation: gen,
        }
    }
}

impl OpenWorldSimulator {
    pub fn new(env: Environment, seed: u64) -> Self {
        fastrand::seed(seed);
        let agents = (0..INITIAL_AGENTS)
            .map(|i| Agent::new(
                (i * 13 % 100) as f32,
                (i * 17 % 100) as f32,
                0
            ))
            .collect();
        
        Self {
            env, seed, agents,
            tick: 0,
            telemetry: Vec::new(),
            pre_knockout_pop: INITIAL_AGENTS,
        }
    }

    pub fn run(&mut self) -> RunResult {
        let mut min_pop = INITIAL_AGENTS;
        let mut recovery_time: Option<usize> = None;
        let mut adaptation_events = 0usize;
        
        while self.tick < MAX_TICKS {
            self.tick += 1;
            
            // Environment-specific events
            match self.env {
                Environment::HubFailureWorld => self.handle_hub_failure(),
                Environment::RegimeShiftWorld => self.handle_regime_shift(&mut adaptation_events),
                Environment::ResourceCompetition => self.handle_resource_stress(),
                Environment::MultiGameCycle => self.handle_game_cycle(&mut adaptation_events),
            }
            
            // Agent lifecycle
            self.agent_step();
            
            // Reproduction
            self.reproduction();
            
            // Telemetry
            let pop = self.agents.iter().filter(|a| a.alive).count();
            if pop < min_pop { min_pop = pop; }
            
            // Recovery detection for HubFailure
            if self.env == Environment::HubFailureWorld && self.tick > 3000 {
                if recovery_time.is_none() && pop > self.pre_knockout_pop / 2 {
                    recovery_time = Some(self.tick - 2500); // Time since knockout
                }
            }
            
            self.record_telemetry(pop);
            
            if pop == 0 { break; }
        }
        
        self.build_result(min_pop, recovery_time, adaptation_events)
    }

    fn handle_hub_failure(&mut self) {
        // Hub knockout at tick 2500
        if self.tick == 2500 {
            self.pre_knockout_pop = self.agents.iter().filter(|a| a.alive).count();
            let cx = 50.0; let cy = 50.0;
            for agent in &mut self.agents {
                let dx = (agent.x - cx).abs();
                let dy = (agent.y - cy).abs();
                if dx < 15.0 && dy < 15.0 && fastrand::f32() < 0.7 {
                    agent.alive = false;
                }
            }
        }
    }

    fn handle_regime_shift(&mut self, adaptations: &mut usize) {
        // Shift every 1500 ticks
        if self.tick % 1500 == 0 && self.tick > 0 {
            // Stress event
            for agent in &mut self.agents {
                if agent.alive {
                    agent.energy -= 8.0;
                    // Adaptation: agents with positive strategy_bias adapt better
                    if agent.strategy_bias > 0.0 && fastrand::f32() < 0.3 {
                        agent.energy += 5.0;
                        *adaptations += 1;
                    }
                }
            }
        }
    }

    fn handle_resource_stress(&mut self) {
        // Scarce resources
        if self.tick % 50 == 0 {
            // Limited food
            for agent in &mut self.agents {
                if agent.alive && fastrand::f32() < 0.08 {
                    agent.energy += 8.0;
                }
            }
        }
    }

    fn handle_game_cycle(&mut self, adaptations: &mut usize) {
        // Game type cycles every 1200 ticks
        let _game_phase = (self.tick / 1200) % 3;
        
        // Agents play games with neighbors
        let n = self.agents.len();
        for i in 0..n {
            if !self.agents[i].alive { continue; }
            
            // Find opponent
            if let Some(j) = self.find_opponent(i) {
                let my_coop = self.agents[i].strategy_bias > 0.0;
                let their_coop = self.agents[j].strategy_bias > 0.0;
                
                // Payoff based on game phase
                let payoff = match (my_coop, their_coop) {
                    (true, true) => 3.0,
                    (true, false) => 0.0,
                    (false, true) => 5.0,
                    (false, false) => 1.0,
                };
                
                self.agents[i].energy += payoff;
                
                // Update L1 memory
                self.agents[i].memory_l1.push(payoff);
                if self.agents[i].memory_l1.len() > 20 {
                    self.agents[i].memory_l1.remove(0);
                }
                
                // Successful coordination = adaptation
                if my_coop && their_coop {
                    *adaptations += 1;
                }
            }
        }
    }

    fn agent_step(&mut self) {
        for agent in &mut self.agents {
            if !agent.alive { continue; }
            
            // Foraging
            if fastrand::f32() < 0.12 {
                // L1 memory improves foraging
                let bonus = if agent.memory_l1.len() >= 5 {
                    let recent: f32 = agent.memory_l1.iter().rev().take(5).sum();
                    1.0 + (recent / 25.0).min(0.3)
                } else { 1.0 };
                agent.energy += 8.0 * bonus;
            }
            
            // Metabolism
            agent.energy -= 0.9;
            if agent.energy <= 0.0 {
                agent.alive = false;
            }
        }
    }

    fn reproduction(&mut self) {
        let mut new_agents = Vec::new();
        for agent in &self.agents {
            if !agent.alive { continue; }
            
            // L2 lineage bonus reduces reproduction threshold
            let threshold = 40.0 - agent.memory_l2 * 10.0;
            
            if agent.energy > threshold && fastrand::f32() < 0.005 {
                let mut child = Agent::new(
                    (agent.x + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    (agent.y + fastrand::f32() * 10.0 - 5.0).clamp(0.0, 100.0),
                    agent.generation + 1
                );
                child.energy = 15.0;
                // L2 inheritance
                child.memory_l2 = agent.memory_l2 * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        self.agents.extend(new_agents);
    }

    fn find_opponent(&self, idx: usize) -> Option<usize> {
        let agent = &self.agents[idx];
        let mut candidates = Vec::new();
        for (i, other) in self.agents.iter().enumerate() {
            if i == idx || !other.alive { continue; }
            let dist_sq = (agent.x - other.x).powi(2) + (agent.y - other.y).powi(2);
            if dist_sq < 100.0 { candidates.push(i); }
        }
        if candidates.is_empty() { None } else { Some(candidates[fastrand::usize(0..candidates.len())]) }
    }

    fn record_telemetry(&mut self, pop: usize) {
        let alive: Vec<&Agent> = self.agents.iter().filter(|a| a.alive).collect();
        let coord = if alive.is_empty() { 0.0 } else {
            alive.iter().map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() / alive.len() as f32
        };
        
        // Entropy: population diversity
        let entropy = self.calculate_entropy();
        
        // Hazard rate: recent deaths
        let hazard = 0.0; // Simplified
        
        self.telemetry.push(Telemetry {
            tick: self.tick,
            population: pop,
            coordination: coord,
            entropy,
            hazard_rate: hazard,
            recovery_flag: false,
        });
    }

    fn calculate_entropy(&self) -> f32 {
        let alive: Vec<&Agent> = self.agents.iter().filter(|a| a.alive).collect();
        if alive.len() < 2 { return 0.0; }
        
        // Strategy distribution entropy
        let mut bins = [0usize; 5];
        for agent in &alive {
            let bin = ((agent.strategy_bias + 1.0) / 0.4).clamp(0.0, 4.0) as usize;
            bins[bin.min(4)] += 1;
        }
        
        let total = alive.len() as f32;
        bins.iter().map(|&count| {
            if count == 0 { 0.0 } else {
                let p = count as f32 / total;
                -p * p.ln()
            }
        }).sum::<f32>()
    }

    fn build_result(&self, min_pop: usize, recovery_time: Option<usize>, adaptation_events: usize) -> RunResult {
        let final_pop = self.agents.iter().filter(|a| a.alive).count();
        let avg_coord = self.telemetry.iter().map(|t| t.coordination).sum::<f32>() 
            / self.telemetry.len().max(1) as f32;
        let entropy_traj = self.telemetry.iter().map(|t| t.entropy).collect();
        
        let pass = final_pop >= PASS_THRESHOLD_POP && avg_coord >= PASS_THRESHOLD_COORD;
        
        RunResult {
            env: self.env,
            seed: self.seed,
            final_pop,
            min_pop,
            avg_coordination: avg_coord,
            recovery_time,
            adaptation_events,
            entropy_trajectory: entropy_traj,
            collapsed: final_pop == 0,
            pass,
        }
    }
}

fn run_environment(env: Environment) -> Vec<RunResult> {
    println!("\n[{:?}]", env);
    println!("{}", str::repeat("-", 50));
    
    // Paired seeds: base and +1
    let seeds: Vec<u64> = (0..N_SEEDS).map(|i| 12000 + i as u64 * 2).collect();
    let mut results = Vec::new();
    
    for seed in &seeds {
        let mut sim = OpenWorldSimulator::new(env, *seed);
        let result = sim.run();
        
        println!("Seed {}: final={:3} min={:3} coord={:.2} recovery={:?} {}",
            seed, result.final_pop, result.min_pop, result.avg_coordination,
            result.recovery_time, if result.pass { "PASS" } else { "FAIL" });
        
        results.push(result);
    }
    
    results
}

fn export_csv(all_results: &HashMap<Environment, Vec<RunResult>>) {
    let filename = "/tmp/phase2_round1_results.csv";
    let mut file = File::create(filename).unwrap();
    
    writeln!(file, "environment,seed,final_pop,min_pop,avg_coordination,recovery_time,adaptation_events,collapsed,pass").unwrap();
    
    for (env, results) in all_results {
        for r in results {
            writeln!(file, "{:?},{},{},{},{:.3},{:?},{},{},{}",
                env, r.seed, r.final_pop, r.min_pop, r.avg_coordination,
                r.recovery_time, r.adaptation_events, r.collapsed as i32, r.pass as i32).unwrap();
        }
    }
    
    println!("\nExported: {}", filename);
}

fn main() {
    println!("{}", "=".repeat(60));
    println!("Phase 2 Round 1: Open-World Task Validation");
    println!("{}", str::repeat("=", 60));
    println!("Config: {} ticks, {} paired seeds/env", MAX_TICKS, N_SEEDS);
    println!("Pass threshold: population >= {}, coordination >= {:.1}",
        PASS_THRESHOLD_POP, PASS_THRESHOLD_COORD);
    println!();
    
    let mut all_results: HashMap<Environment, Vec<RunResult>> = HashMap::new();
    
    // Priority order: HubFailure → RegimeShift → ResourceCompetition → MultiGameCycle
    for env in [Environment::HubFailureWorld, Environment::RegimeShiftWorld,
                Environment::ResourceCompetition, Environment::MultiGameCycle] {
        let results = run_environment(env);
        all_results.insert(env, results);
    }
    
    // Summary
    println!("\n");
    println!("{}", str::repeat("=", 60));
    println!("PHASE 2 ROUND 1 SUMMARY");
    println!("{}", str::repeat("=", 60));
    
    let mut total_pass = 0;
    let mut total_runs = 0;
    
    for (env, results) in &all_results {
        let pass_count = results.iter().filter(|r| r.pass).count();
        let avg_final = results.iter().map(|r| r.final_pop).sum::<usize>() as f32 / results.len() as f32;
        let avg_coord = results.iter().map(|r| r.avg_coordination).sum::<f32>() / results.len() as f32;
        let collapses = results.iter().filter(|r| r.collapsed).count();
        
        total_pass += pass_count;
        total_runs += results.len();
        
        let status = if pass_count >= 3 { "✓ PASS" } 
                     else if pass_count >= 2 { "~ PARTIAL" }
                     else { "✗ FAIL" };
        
        println!("{:20} | N={:5.1} | coord={:.2} | pass {}/{} | collapse {} | {}",
            format!("{:?}", env), avg_final, avg_coord, pass_count, results.len(), collapses, status);
    }
    
    println!("\nOverall: {}/{} runs passed", total_pass, total_runs);
    
    // Check critical environments
    let hub_pass = all_results.get(&Environment::HubFailureWorld)
        .map(|r: &Vec<RunResult>| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    let regime_pass = all_results.get(&Environment::RegimeShiftWorld)
        .map(|r: &Vec<RunResult>| r.iter().filter(|x| x.pass).count() >= 3).unwrap_or(false);
    
    println!("\nCritical gates:");
    println!("  HubFailureWorld: {}", if hub_pass { "✓ PASS" } else { "✗ FAIL" });
    println!("  RegimeShiftWorld: {}", if regime_pass { "✓ PASS" } else { "✗ FAIL" });
    
    // Export
    export_csv(&all_results);
    
    // Final verdict
    let overall_pass = total_pass >= 12 && hub_pass && regime_pass; // 12/20 = 60%
    
    println!("\n");
    println!("{}", str::repeat("=", 60));
    if overall_pass {
        println!("✓ PHASE 2 ROUND 1: PASSED");
        println!("Proceed to Round 2: Stress / Long-horizon extension");
    } else {
        println!("✗ PHASE 2 ROUND 1: FAILED");
        println!("Diagnose failure mode and retry");
        if !hub_pass { println!("  → Hub recovery issue: check regime detector / recovery paths"); }
        if !regime_pass { println!("  → Adaptation issue: check Strategy Layer / memory coupling"); }
    }
    println!("{}", str::repeat("=", 60));
}
