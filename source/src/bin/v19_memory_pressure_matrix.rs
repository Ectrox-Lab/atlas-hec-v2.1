//! v19 Memory Pressure Matrix - 3-Tier Validation for L2/L3 Attribution
//!
//! GOAL: Find parameter regime where L2/L3 contributions become identifiable
//!
//! PRESSURE TIERS:
//! - HIGH:   Current config (L1 necessity already proven)
//! - MEDIUM: Balanced - allows survival but tests adaptation
//! - LOW:    Permissive - tests strategy consistency & learning

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, PopulationParams, HazardRateTracker,
    compute_condensation_index, GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;

const MAX_TICKS: usize = 8000;
const N_SEEDS: usize = 5;

#[derive(Clone, Copy, Debug)]
pub enum Pressure { High, Medium, Low }

#[derive(Clone, Copy, Debug)]
pub enum Condition { Full, NoCell, NoLineage, NoArchive, NoMemory, P_0_00, P_0_01, P_0_10 }

pub struct PressureConfig {
    pub initial_food: usize,
    pub food_regen: usize,
    pub metabolism: f32,
    pub repro_cost: f32,
    pub regen_interval: usize,
}

impl PressureConfig {
    pub fn for_pressure(p: Pressure) -> Self {
        match p {
            // L1 necessity regime (already proven)
            Pressure::High => Self {
                initial_food: 50, food_regen: 5, metabolism: 2.0,
                repro_cost: 45.0, regen_interval: 150,
            },
            // L2/L3 attribution regime (target)
            Pressure::Medium => Self {
                initial_food: 80, food_regen: 12, metabolism: 1.2,
                repro_cost: 30.0, regen_interval: 100,
            },
            // Strategy consistency regime
            Pressure::Low => Self {
                initial_food: 150, food_regen: 25, metabolism: 0.8,
                repro_cost: 20.0, regen_interval: 80,
            },
        }
    }
}

pub struct Counters {
    pub cell_reads: usize, pub cell_writes: usize,
    pub lineage_inh: usize, pub lineage_mut: usize,
    pub archive_samples: usize, pub archive_hits: usize,
    pub policy_mod: usize,
}

impl Default for Counters {
    fn default() -> Self {
        Self { cell_reads: 0, cell_writes: 0, lineage_inh: 0,
               lineage_mut: 0, archive_samples: 0, archive_hits: 0, policy_mod: 0 }
    }
}

pub struct ThreeLayerMemory {
    pub cell: Vec<Option<VecDeque<f32>>>,
    pub lineage: Vec<Option<(f32, usize)>>,
    pub archive: Vec<(usize, f32)>,
    pub condition: Condition,
    pub counters: Counters,
    pub p_rate: f32,
}

impl ThreeLayerMemory {
    pub fn new(n: usize, condition: Condition) -> Self {
        let p_rate = match condition {
            Condition::P_0_00 => 0.0,
            Condition::P_0_10 => 0.10,
            _ => 0.01,
        };
        
        let cell = match condition {
            Condition::NoCell | Condition::NoMemory | Condition::P_0_00 
                | Condition::P_0_01 | Condition::P_0_10 => vec![None; n],
            _ => (0..n).map(|_| Some(VecDeque::with_capacity(20))).collect(),
        };
        let lineage = match condition {
            Condition::NoLineage | Condition::NoMemory | Condition::P_0_00 
                | Condition::P_0_01 | Condition::P_0_10 => vec![None; n],
            _ => (0..n).map(|_| Some((0.0, 0))).collect(),
        };
        
        Self { cell, lineage, archive: Vec::new(), condition, counters: Counters::default(), p_rate }
    }

    pub fn get_foraging_bonus(&mut self, agent_id: usize) -> f32 {
        if matches!(self.condition, Condition::NoCell | Condition::NoMemory) { return 1.0; }
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            self.counters.cell_reads += 1;
            if mem.len() >= 5 {
                let recent = mem.iter().rev().take(5).filter(|&&v| v > 0.5).count() as f32;
                return 1.0 + (recent / 5.0) * 0.35;
            }
        }
        1.0
    }

    pub fn record_success(&mut self, agent_id: usize, success: f32) {
        if matches!(self.condition, Condition::NoCell | Condition::NoMemory) { return; }
        if let Some(Some(mem)) = self.cell.get_mut(agent_id) {
            self.counters.cell_writes += 1;
            mem.push_back(success);
            if mem.len() > 20 { mem.pop_front(); }
        }
    }

    pub fn on_reproduction(&mut self, parent_id: usize, child_id: usize) {
        if matches!(self.condition, Condition::NoLineage | Condition::NoMemory) { return; }
        
        self.counters.lineage_inh += 1;
        let parent_bias = self.lineage.get(parent_id).and_then(|l| l.as_ref()).map(|(b, _)| *b).unwrap_or(0.0);
        
        if child_id >= self.lineage.len() {
            self.lineage.resize_with(child_id + 1, || None);
        }
        
        let mut child_bias = parent_bias;
        if fastrand::f32() < 0.1 {
            self.counters.lineage_mut += 1;
            child_bias += (fastrand::f32() - 0.5) * 0.3;
            child_bias = child_bias.clamp(-1.0, 1.0);
        }
        
        let gen = self.lineage.get(parent_id).and_then(|l| l.as_ref()).map(|(_, g)| g + 1).unwrap_or(0);
        
        // Archive sampling with configurable p
        if !matches!(self.condition, Condition::NoArchive | Condition::NoMemory) {
            self.counters.archive_samples += 1;
            if fastrand::f32() < self.p_rate && !self.archive.is_empty() {
                self.counters.archive_hits += 1;
                let idx = fastrand::usize(0..self.archive.len());
                let lesson = self.archive[idx].1;
                child_bias = child_bias * 0.95 + lesson * 0.05;
                self.counters.policy_mod += 1;
            }
        }
        
        self.lineage[child_id] = Some((child_bias, gen));
    }

    pub fn on_death(&mut self, tick: usize, agent_id: usize) {
        if matches!(self.condition, Condition::NoArchive | Condition::NoMemory) { return; }
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            if mem.len() >= 10 {
                let avg = mem.iter().sum::<f32>() / mem.len() as f32;
                if avg > 0.5 { self.archive.push((tick, avg.min(1.0))); }
            }
        }
    }

    pub fn get_lineage_bias(&self, agent_id: usize) -> f32 {
        if matches!(self.condition, Condition::NoLineage | Condition::NoMemory) { return 0.0; }
        self.lineage.get(agent_id).and_then(|l| l.as_ref()).map(|(b, _)| b.max(0.0) * 0.3).unwrap_or(0.0)
    }
    
    pub fn get_lineage_variance(&self) -> f64 {
        let biases: Vec<f32> = self.lineage.iter().filter_map(|l| l.as_ref().map(|(b, _)| *b)).collect();
        if biases.is_empty() { return 0.0; }
        let mean = biases.iter().sum::<f32>() / biases.len() as f32;
        biases.iter().map(|b| (*b - mean).powi(2)).sum::<f32>() as f64 / biases.len() as f64
    }
}

#[derive(Clone, Debug)]
pub struct Metrics {
    pub tick: usize, pub pop: usize, pub cdi: f64, pub ci: f64, pub hazard: f64,
    pub extinct: bool, pub min_pop: usize, pub recovery_events: usize,
    pub lineage_variance: f64, pub archive_size: usize,
    pub cell_r: usize, pub cell_w: usize, pub lin_inh: usize, pub arch_hits: usize,
}

fn run_simulation(condition: Condition, pressure: Pressure, seed: u64) -> (Vec<Metrics>, Counters) {
    fastrand::seed(seed);
    let config = PressureConfig::for_pressure(pressure);
    let mut world = GridWorld::new();
    
    for i in 0..100 {
        world.spawn_agent((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z);
    }
    world.spawn_food_random(config.initial_food, 30.0);
    
    let mut memory = ThreeLayerMemory::new(2000, condition);
    let mut hazard = HazardRateTracker::new(2000);
    let mut history = Vec::new();
    let mut min_pop = 100usize;
    let mut recovery_events = 0;
    let mut was_low = false;
    
    // Regime shifts for testing adaptation
    let shifts = vec![2000, 4000, 6000];
    
    for tick in (0..MAX_TICKS).step_by(100) {
        if shifts.contains(&tick) {
            world.food.clear();
            world.spawn_food_random(config.initial_food / 2, 30.0);
        }
        
        // Agent behavior with memory
        for (id, agent) in world.agents.iter_mut().enumerate() {
            if !agent.alive { continue; }
            
            let foraging_bonus = memory.get_foraging_bonus(id);
            if fastrand::f32() < 0.12 * foraging_bonus {
                agent.energy += 25.0 * (foraging_bonus - 1.0) * 0.5;
                memory.record_success(id, 1.0);
            } else if fastrand::f32() < 0.25 {
                memory.record_success(id, 0.0);
            }
            
            agent.energy -= config.metabolism;
            if agent.energy <= 0.0 {
                agent.alive = false;
                hazard.record_death(tick);
                memory.on_death(tick, id);
            }
        }
        
        // Reproduction
        let mut new_agents = Vec::new();
        for (id, agent) in world.agents.iter().enumerate() {
            if !agent.alive { continue; }
            let lineage_bonus = memory.get_lineage_bias(id);
            let threshold = config.repro_cost * (1.0 - lineage_bonus);
            if agent.energy > threshold && fastrand::f32() < 0.012 {
                let mut child = agent.clone();
                child.energy = 12.0;
                let dx = fastrand::i32(-1..2);
                let dy = fastrand::i32(-1..2);
                child.pos.x = (child.pos.x as i32 + dx).clamp(0, GRID_X as i32 - 1) as usize;
                child.pos.y = (child.pos.y as i32 + dy).clamp(0, GRID_Y as i32 - 1) as usize;
                let child_id = world.agents.len() + new_agents.len();
                memory.on_reproduction(id, child_id);
                new_agents.push(child);
            }
        }
        world.agents.extend(new_agents);
        
        // Food regen
        if tick % config.regen_interval == 0 {
            world.spawn_food_random(config.food_regen, 30.0);
        }
        
        let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        if n < min_pop { min_pop = n; }
        if n < 15 { was_low = true; }
        if was_low && n > 40 { recovery_events += 1; was_low = false; }
        
        let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
        let ci = compute_condensation_index(&phases);
        
        history.push(Metrics {
            tick, pop: n, cdi: if n > 0 { 0.15 + ci * 0.08 } else { 0.0 },
            ci, hazard: hazard.hazard_rate(), extinct: n == 0,
            min_pop, recovery_events, lineage_variance: memory.get_lineage_variance(),
            archive_size: memory.archive.len(),
            cell_r: memory.counters.cell_reads, cell_w: memory.counters.cell_writes,
            lin_inh: memory.counters.lineage_inh, arch_hits: memory.counters.archive_hits,
        });
        
        world.step();
        if n == 0 { break; }
    }
    
    (history, memory.counters)
}

fn analyze_condition(name: &str, condition: Condition, pressure: Pressure, seeds: &[u64]) {
    println!("\n[{} | {:?}] ", name, pressure);
    
    let mut finals = Vec::new();
    let mut extincts = 0;
    let mut min_pops = Vec::new();
    let mut recoveries = Vec::new();
    let mut lin_vars = Vec::new();
    let mut total_counters = Counters::default();
    
    for seed in seeds {
        let (history, counters) = run_simulation(condition, pressure, *seed);
        let last = history.last().unwrap();
        finals.push(last.pop);
        if last.extinct { extincts += 1; }
        min_pops.push(last.min_pop);
        recoveries.push(last.recovery_events);
        lin_vars.push(last.lineage_variance);
        
        total_counters.cell_reads += counters.cell_reads;
        total_counters.cell_writes += counters.cell_writes;
        total_counters.lineage_inh += counters.lineage_inh;
        total_counters.archive_hits += counters.archive_hits;
    }
    
    let mean_final = finals.iter().sum::<usize>() as f64 / finals.len() as f64;
    let mean_min = min_pops.iter().sum::<usize>() as f64 / min_pops.len() as f64;
    let mean_recov = recoveries.iter().sum::<usize>() as f64 / recoveries.len() as f64;
    let mean_var = lin_vars.iter().sum::<f64>() / lin_vars.len() as f64;
    
    println!("  Final N: {:.1} (extinct {}/{}), Min N: {:.1}, Recovery: {:.1}, LineageVar: {:.3}",
        mean_final, extincts, seeds.len(), mean_min, mean_recov, mean_var);
    println!("  Counters: cell_r={}, cell_w={}, lin={}, arch={}",
        total_counters.cell_reads, total_counters.cell_writes,
        total_counters.lineage_inh, total_counters.archive_hits);
}

fn main() {
    println!("v19 Memory Pressure Matrix - 3-Tier L2/L3 Attribution Test\n");
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 4000 + i).collect();
    
    // HIGH PRESSURE: L1 necessity (already proven)
    println!("{}", "=".repeat(70));
    println!("TIER 1: HIGH PRESSURE - L1 Necessity Regime");
    println!("{}", "=".repeat(70));
    analyze_condition("Full", Condition::Full, Pressure::High, &seeds);
    analyze_condition("NoCell", Condition::NoCell, Pressure::High, &seeds);
    analyze_condition("NoLineage", Condition::NoLineage, Pressure::High, &seeds);
    analyze_condition("NoArchive", Condition::NoArchive, Pressure::High, &seeds);
    analyze_condition("NoMemory", Condition::NoMemory, Pressure::High, &seeds);
    
    // MEDIUM PRESSURE: L2/L3 attribution target
    println!("\n{}", "=".repeat(70));
    println!("TIER 2: MEDIUM PRESSURE - L2/L3 Attribution Regime");
    println!("{}", "=".repeat(70));
    analyze_condition("Full", Condition::Full, Pressure::Medium, &seeds);
    analyze_condition("NoCell", Condition::NoCell, Pressure::Medium, &seeds);
    analyze_condition("NoLineage", Condition::NoLineage, Pressure::Medium, &seeds);
    analyze_condition("NoArchive", Condition::NoArchive, Pressure::Medium, &seeds);
    analyze_condition("NoMemory", Condition::NoMemory, Pressure::Medium, &seeds);
    
    // SAMPLING DOSE at medium pressure
    println!("\n--- Sampling Dose (Medium Pressure) ---");
    analyze_condition("p=0.00", Condition::P_0_00, Pressure::Medium, &seeds);
    analyze_condition("p=0.01", Condition::P_0_01, Pressure::Medium, &seeds);
    analyze_condition("p=0.10", Condition::P_0_10, Pressure::Medium, &seeds);
    
    // LOW PRESSURE: Strategy consistency
    println!("\n{}", "=".repeat(70));
    println!("TIER 3: LOW PRESSURE - Strategy Consistency Regime");
    println!("{}", "=".repeat(70));
    analyze_condition("Full", Condition::Full, Pressure::Low, &seeds);
    analyze_condition("NoLineage", Condition::NoLineage, Pressure::Low, &seeds);
    analyze_condition("NoArchive", Condition::NoArchive, Pressure::Low, &seeds);
    
    // Summary
    println!("\n{}", "=".repeat(70));
    println!("INTERPRETATION GUIDE");
    println!("{}", "=".repeat(70));
    println!("High Pressure:    Tests L1 necessity (expect NoCell/NoMemory extinct)");
    println!("Medium Pressure:  Tests L2/L3 attribution (expect Full > NoLineage > NoArchive)");
    println!("Low Pressure:     Tests strategy consistency (expect lineage variance differences)");
    println!("\nL2/L3 identified if: Medium pressure shows Full > NoLineage/NoArchive with p<0.05");
}
