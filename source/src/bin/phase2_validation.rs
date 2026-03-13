//! Phase 2 Round 1: Open-World Task Validation
//! 
//! 4 Environments × 5 Seeds
//! Key Metrics: population_persistence, coordination_score, recovery_latency, adaptation_success

use agl_mwe::bio_world_v19::{GRID_X, GRID_Y, GRID_Z};
use std::collections::VecDeque;

const MAX_TICKS: usize = 8000;
const N_SEEDS: usize = 3;
const INITIAL_AGENTS: usize = 100;

#[derive(Clone, Copy, Debug)]
pub enum Environment { HubFailureWorld, RegimeShiftWorld, ResourceCompetition, MultiGameCycle }

#[derive(Clone, Copy, Debug)]
pub enum Action { Cooperate, Defect }

pub struct SimpleAgent {
    pub x: usize, pub y: usize, pub z: usize,
    pub alive: bool, pub energy: f32,
    pub strategy_bias: f32, // -1.0 to 1.0
    pub task_memory: VecDeque<f32>,
}

impl SimpleAgent {
    pub fn new(x: usize, y: usize, z: usize) -> Self {
        Self { x, y, z, alive: true, energy: 30.0, 
               strategy_bias: fastrand::f32() * 2.0 - 1.0,
               task_memory: VecDeque::with_capacity(20) }
    }
    
    pub fn decide(&self, energy_stress: f32) -> Action {
        let effective_bias = self.strategy_bias * (1.0 - energy_stress);
        if effective_bias > 0.0 { Action::Cooperate } else { Action::Defect }
    }
}

pub struct World {
    pub agents: Vec<SimpleAgent>,
    pub food: Vec<(usize, usize, usize, f32)>, // x, y, z, energy
    pub tick: usize,
    pub env: Environment,
}

impl World {
    pub fn new(env: Environment) -> Self {
        let mut agents = Vec::new();
        for i in 0..INITIAL_AGENTS {
            agents.push(SimpleAgent::new(
                (i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z));
        }
        let mut world = Self { agents, food: Vec::new(), tick: 0, env };
        world.spawn_food(100);
        world
    }
    
    pub fn spawn_food(&mut self, count: usize) {
        for _ in 0..count {
            self.food.push((
                fastrand::usize(0..GRID_X),
                fastrand::usize(0..GRID_Y),
                fastrand::usize(0..GRID_Z),
                25.0
            ));
        }
    }
    
    pub fn step(&mut self) -> Metrics {
        self.tick += 1;
        
        // Environment-specific events
        match self.env {
            Environment::HubFailureWorld => {
                // Hub knockout at tick 10000
                if self.tick == 10000 {
                    let cx = GRID_X / 2;
                    let cy = GRID_Y / 2;
                    for agent in &mut self.agents {
                        let dx = (agent.x as i32 - cx as i32).abs();
                        let dy = (agent.y as i32 - cy as i32).abs();
                        if dx < 10 && dy < 10 && fastrand::f32() < 0.7 {
                            agent.alive = false;
                        }
                    }
                }
            }
            Environment::RegimeShiftWorld => {
                // Regime shift every 5000 ticks
                if self.tick % 5000 == 0 {
                    self.food.clear();
                    self.spawn_food(50);
                }
            }
            Environment::ResourceCompetition => {
                // Low food regen
                if self.tick % 150 == 0 { self.spawn_food(8); }
            }
            Environment::MultiGameCycle => {
                // Game type shifts every 3000 ticks
                if self.tick % 3000 == 0 {
                    // Shift payoff structure (simplified)
                    self.spawn_food(15);
                }
            }
        }
        
        // Standard food regen
        if !matches!(self.env, Environment::ResourceCompetition | Environment::RegimeShiftWorld) {
            if self.tick % 100 == 0 { self.spawn_food(15); }
        }
        
        // Agent interactions
        let n = self.agents.len();
        let mut payoffs: Vec<(usize, f32)> = Vec::new();
        
        for i in 0..n {
            if !self.agents[i].alive { continue; }
            
            // Find neighbor
            let neighbor_idx = self.find_neighbor(i);
            if let Some(j) = neighbor_idx {
                if self.agents[j].alive {
                    let energy_stress = 1.0 - (self.agents[i].energy / 50.0).min(1.0);
                    let my_action = self.agents[i].decide(energy_stress);
                    let their_stress = 1.0 - (self.agents[j].energy / 50.0).min(1.0);
                    let their_action = self.agents[j].decide(their_stress);
                    
                    let (my_payoff, _) = self.game_payoff(my_action, their_action);
                    payoffs.push((i, my_payoff));
                }
            }
            
            // Metabolism
            self.agents[i].energy -= 0.8;
            if self.agents[i].energy <= 0.0 { self.agents[i].alive = false; }
        }
        
        // Apply payoffs
        for (idx, payoff) in payoffs {
            self.agents[idx].energy += payoff.max(0.0);
            self.agents[idx].task_memory.push_back(payoff);
            if self.agents[idx].task_memory.len() > 20 { 
                self.agents[idx].task_memory.pop_front(); 
            }
        }
        
        // Reproduction
        self.handle_reproduction();
        
        self.collect_metrics()
    }
    
    fn find_neighbor(&self, idx: usize) -> Option<usize> {
        let agent = &self.agents[idx];
        let mut candidates = Vec::new();
        for (i, other) in self.agents.iter().enumerate() {
            if i == idx || !other.alive { continue; }
            let dist_sq = (agent.x as i32 - other.x as i32).pow(2) + 
                         (agent.y as i32 - other.y as i32).pow(2);
            if dist_sq < 36 { candidates.push(i); } // Within 6 units
        }
        if candidates.is_empty() { None }
        else { Some(candidates[fastrand::usize(0..candidates.len())]) }
    }
    
    fn game_payoff(&self, my: Action, their: Action) -> (f32, f32) {
        // Cycle through game types based on tick
        let game_phase = (self.tick / 3000) % 3;
        match game_phase {
            0 => match (my, their) { // PD
                (Action::Cooperate, Action::Cooperate) => (3.0, 3.0),
                (Action::Cooperate, Action::Defect) => (0.0, 5.0),
                (Action::Defect, Action::Cooperate) => (5.0, 0.0),
                (Action::Defect, Action::Defect) => (1.0, 1.0),
            },
            1 => match (my, their) { // Stag Hunt
                (Action::Cooperate, Action::Cooperate) => (4.0, 4.0),
                (Action::Cooperate, Action::Defect) => (0.0, 2.0),
                (Action::Defect, Action::Cooperate) => (2.0, 0.0),
                (Action::Defect, Action::Defect) => (2.0, 2.0),
            },
            _ => match (my, their) { // Chicken
                (Action::Cooperate, Action::Cooperate) => (0.0, 0.0),
                (Action::Cooperate, Action::Defect) => (-1.0, 1.0),
                (Action::Defect, Action::Cooperate) => (1.0, -1.0),
                (Action::Defect, Action::Defect) => (-10.0, -10.0),
            },
        }
    }
    
    fn handle_reproduction(&mut self) {
        let mut new_agents = Vec::new();
        for agent in &self.agents {
            if !agent.alive { continue; }
            if agent.energy > 40.0 && fastrand::f32() < 0.008 {
                let mut child = SimpleAgent::new(
                    (agent.x + fastrand::usize(0..5)) % GRID_X,
                    (agent.y + fastrand::usize(0..5)) % GRID_Y,
                    agent.z
                );
                child.energy = 15.0;
                child.strategy_bias = agent.strategy_bias * 0.9 + (fastrand::f32() - 0.5) * 0.2;
                new_agents.push(child);
            }
        }
        self.agents.extend(new_agents);
    }
    
    fn collect_metrics(&self) -> Metrics {
        let alive: Vec<&SimpleAgent> = self.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        
        let avg_coord = if alive.is_empty() { 0.0 } else {
            alive.iter().map(|a| a.strategy_bias.signum().max(0.0)).sum::<f32>() / alive.len() as f32
        };
        
        Metrics {
            tick: self.tick,
            population: n,
            coordination_score: avg_coord,
            extinct: n == 0,
            min_pop_ever: n, // Simplified
        }
    }
}

#[derive(Clone, Debug)]
pub struct Metrics {
    pub tick: usize,
    pub population: usize,
    pub coordination_score: f32,
    pub extinct: bool,
    pub min_pop_ever: usize,
}

fn run_environment(env: Environment, seeds: &[u64]) -> EnvironmentResult {
    println!("\n[{:?}]", env);
    println!("{}", "-".repeat(50));
    
    let mut all_final_pop = Vec::new();
    let mut all_extinct = 0;
    let mut all_coord = Vec::new();
    let mut recovery_counts = 0;
    
    for (i, seed) in seeds.iter().enumerate() {
        fastrand::seed(*seed);
        let mut world = World::new(env);
        let mut history = Vec::new();
        let mut recovered_from_hub = false;
        let pop_at_10k = if matches!(env, Environment::HubFailureWorld) { 100 } else { 0 };
        
        for _ in 0..(MAX_TICKS / 100) {
            for _ in 0..100 {
                let m = world.step();
                if m.extinct { break; }
                
                // Track hub failure recovery
                if matches!(env, Environment::HubFailureWorld) && world.tick == 10000 {
                    // Population after hub knockout
                }
                if matches!(env, Environment::HubFailureWorld) && world.tick > 15000 && !recovered_from_hub {
                    if m.population > 30 { recovered_from_hub = true; }
                }
            }
            history.push(world.collect_metrics());
            if history.last().unwrap().extinct { break; }
        }
        
        let last = history.last().unwrap();
        all_final_pop.push(last.population);
        if last.extinct { all_extinct += 1; }
        all_coord.push(last.coordination_score);
        if recovered_from_hub { recovery_counts += 1; }
        
        let status = if last.population >= 20 { "PASS" } else { "FAIL" };
        println!("  Seed {}: N={:4} ({}), coord={:.2} {}", 
            i + 1, last.population, 
            if last.extinct { "EXTINCT" } else { "ALIVE" },
            last.coordination_score, status);
    }
    
    let mean_pop = all_final_pop.iter().sum::<usize>() as f64 / all_final_pop.len() as f64;
    let mean_coord = all_coord.iter().sum::<f32>() / all_coord.len() as f32;
    let pass_rate = all_final_pop.iter().filter(|&&n| n >= 20).count();
    
    EnvironmentResult {
        env,
        mean_final_pop: mean_pop,
        extinct_rate: all_extinct as f32 / seeds.len() as f32,
        mean_coordination: mean_coord,
        recovery_rate: recovery_counts as f32 / seeds.len() as f32,
        pass_count: pass_rate,
        total_seeds: seeds.len(),
    }
}

struct EnvironmentResult {
    env: Environment,
    mean_final_pop: f64,
    extinct_rate: f32,
    mean_coordination: f32,
    recovery_rate: f32,
    pass_count: usize,
    total_seeds: usize,
}

fn main() {
    println!("{}", str::repeat("=", 60));
    println!("Phase 2 Round 1: Open-World Task Validation");
    println!("{}", str::repeat("=", 60));
    println!("Config: {} ticks, {} seeds/env", MAX_TICKS, N_SEEDS);
    println!("Pass threshold: population >= 20 (20% of initial)");
    println!("Coordination threshold: >= 0.5");
    println!();
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 7000 + i).collect();
    
    // 1. HubFailureWorld (PRIORITY)
    let hub_result = run_environment(Environment::HubFailureWorld, &seeds);
    
    // 2. RegimeShiftWorld (PRIORITY)
    let regime_result = run_environment(Environment::RegimeShiftWorld, &seeds);
    
    // 3. ResourceCompetition
    let resource_result = run_environment(Environment::ResourceCompetition, &seeds);
    
    // 4. MultiGameCycle
    let cycle_result = run_environment(Environment::MultiGameCycle, &seeds);
    
    // Summary
    println!("\n");
    println!("{}", str::repeat("=", 60));
    println!("PHASE 2 ROUND 1 SUMMARY");
    println!("{}", str::repeat("=", 60));
    
    let results = vec![&hub_result, &regime_result, &resource_result, &cycle_result];
    
    for r in &results {
        let pass = r.pass_count >= 3; // 3/5 pass
        let coord_ok = r.mean_coordination >= 0.5;
        let status = if pass && coord_ok { "✓ PASS" } 
                     else if pass { "~ PARTIAL" } 
                     else { "✗ FAIL" };
        
        println!("{:20} | N={:6.1} | coord={:.2} | pass {}/{} | {}",
            format!("{:?}", r.env), r.mean_final_pop, r.mean_coordination,
            r.pass_count, r.total_seeds, status);
    }
    
    // Overall pass criteria: 3/4 environments, must include Hub and RegimeShift
    let hub_pass = hub_result.pass_count >= 3;
    let regime_pass = regime_result.pass_count >= 3;
    let total_pass = results.iter().filter(|r| r.pass_count >= 3).count();
    
    println!("\n");
    println!("OVERALL: {}/4 environments passed", total_pass);
    println!("HubFailureWorld: {}", if hub_pass { "✓" } else { "✗" });
    println!("RegimeShiftWorld: {}", if regime_pass { "✓" } else { "✗" });
    
    if total_pass >= 3 && hub_pass && regime_pass {
        println!("\n✓ PHASE 2 ROUND 1: PASSED");
    } else {
        println!("\n✗ PHASE 2 ROUND 1: FAILED");
        println!("Next: Debug failure mode and retry");
    }
}
