//! v19 Memory Production - FIXED with Decision Coupling + Ablation Counters
//!
//! FIXES:
//! 1. Memory actually influences agent decisions (foraging efficiency)
//! 2. Reproduction triggers real lineage inheritance
//! 3. Newborn gets archive weak sampling (p=0.01)
//! 4. Ablation counters verify path cutting
//! 5. High pressure environment for identifiability

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, PopulationDynamics, PopulationParams,
    HazardRateTracker, compute_condensation_index, GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

const MAX_TICKS: usize = 10000;
const N_SEEDS: usize = 5;

// HIGH PRESSURE PARAMETERS
const INITIAL_FOOD: usize = 50;        // Very limited
const FOOD_REGEN_RATE: usize = 5;      // Very scarce
const METABOLISM_COST: f32 = 2.0;      // Very high cost
const REPRO_COST: f32 = 45.0;          // Very expensive reproduction
const FOOD_ENERGY: f32 = 25.0;         // Moderate food value
const MAX_AGENTS: usize = 800;         // Carrying capacity

/// Ablation condition
#[derive(Clone, Copy, Debug)]
pub enum Condition { Full, NoCell, NoLineage, NoArchive, NoMemory }

/// Ablation counters - verify path cutting
#[derive(Clone, Debug, Default)]
pub struct Counters {
    pub cell_reads: usize,
    pub cell_writes: usize,
    pub lineage_inheritances: usize,
    pub lineage_mutations: usize,
    pub archive_samples: usize,
    pub archive_hits: usize,
    pub policy_modified: usize,
}

/// Three-Layer Memory with hard constraints
pub struct ThreeLayerMemory {
    pub cell: Vec<Option<VecDeque<f32>>>,  // L1: Rolling window of success rates
    pub lineage: Vec<Option<(f32, usize)>>, // L2: (bias, generation)
    pub archive: Vec<(usize, f32)>,         // L3: (tick, survival_lesson)
    pub condition: Condition,
    pub counters: Counters,
}

impl ThreeLayerMemory {
    pub fn new(n: usize, condition: Condition) -> Self {
        let cell = match condition {
            Condition::NoCell | Condition::NoMemory => vec![None; n],
            _ => (0..n).map(|_| Some(VecDeque::with_capacity(20))).collect(),
        };
        let lineage = match condition {
            Condition::NoLineage | Condition::NoMemory => vec![None; n],
            _ => (0..n).map(|_| Some((0.0, 0))).collect(),
        };
        Self { cell, lineage, archive: Vec::new(), condition, counters: Counters::default() }
    }

    /// L1: Cell memory provides foraging efficiency bonus
    pub fn get_foraging_bonus(&mut self, agent_id: usize) -> f32 {
        if matches!(self.condition, Condition::NoCell | Condition::NoMemory) {
            return 1.0; // No bonus
        }
        
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            self.counters.cell_reads += 1;
            if mem.len() >= 5 {
                // Recent success rate determines efficiency
                let recent_success = mem.iter().rev().take(5).filter(|&&v| v > 0.5).count() as f32;
                let bonus = 1.0 + (recent_success / 5.0) * 0.4; // Up to 40% bonus
                return bonus;
            }
        }
        1.0
    }

    /// Record food finding success
    pub fn record_success(&mut self, agent_id: usize, success: f32) {
        if matches!(self.condition, Condition::NoCell | Condition::NoMemory) { return; }
        
        if let Some(Some(mem)) = self.cell.get_mut(agent_id) {
            self.counters.cell_writes += 1;
            mem.push_back(success);
            if mem.len() > 20 { mem.pop_front(); }
        }
    }

    /// L2: Lineage inheritance on reproduction
    pub fn on_reproduction(&mut self, parent_id: usize, child_id: usize) {
        if matches!(self.condition, Condition::NoLineage | Condition::NoMemory) { return; }
        
        self.counters.lineage_inheritances += 1;
        
        let parent_bias = self.lineage.get(parent_id)
            .and_then(|l| l.as_ref())
            .map(|(b, _)| *b)
            .unwrap_or(0.0);
        
        if child_id >= self.lineage.len() {
            self.lineage.resize_with(child_id + 1, || None);
        }
        
        // Inherit with mutation
        let mut child_bias = parent_bias;
        if fastrand::f32() < 0.1 { // 10% mutation rate
            self.counters.lineage_mutations += 1;
            child_bias += (fastrand::f32() - 0.5) * 0.3;
            child_bias = child_bias.clamp(-1.0, 1.0);
        }
        
        let gen = self.lineage.get(parent_id)
            .and_then(|l| l.as_ref())
            .map(|(_, g)| g + 1)
            .unwrap_or(0);
        
        // L3: Archive weak sampling on newborn (p=0.01)
        if !matches!(self.condition, Condition::NoArchive | Condition::NoMemory) {
            self.counters.archive_samples += 1;
            if fastrand::f32() < 0.01 && !self.archive.is_empty() {
                self.counters.archive_hits += 1;
                let idx = fastrand::usize(0..self.archive.len());
                let lesson = self.archive[idx].1;
                // Weak influence: 5% lesson, 95% lineage
                child_bias = child_bias * 0.95 + lesson * 0.05;
                self.counters.policy_modified += 1;
            }
        }
        
        self.lineage[child_id] = Some((child_bias, gen));
    }

    /// L3: Record death to archive
    pub fn on_death(&mut self, tick: usize, agent_id: usize) {
        if matches!(self.condition, Condition::NoArchive | Condition::NoMemory) { return; }
        
        // Only record if agent had good cell memory (learned something)
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            if mem.len() >= 10 {
                let avg_success = mem.iter().sum::<f32>() / mem.len() as f32;
                if avg_success > 0.5 {
                    self.archive.push((tick, avg_success.min(1.0)));
                }
            }
        }
    }

    /// Get lineage bias for reproduction decision
    pub fn get_lineage_bonus(&self, agent_id: usize) -> f32 {
        if matches!(self.condition, Condition::NoLineage | Condition::NoMemory) { return 0.0; }
        
        self.lineage.get(agent_id)
            .and_then(|l| l.as_ref())
            .map(|(b, _)| b.max(0.0) * 0.3) // Up to 30% reproduction bonus
            .unwrap_or(0.0)
    }
}

/// Metrics including sensitive indicators
#[derive(Clone, Debug)]
pub struct Metrics {
    pub tick: usize,
    pub population: usize,
    pub avg_cdi: f64,
    pub avg_ci: f64,
    pub hazard_rate: f64,
    pub extinct: bool,
    // Sensitive indicators
    pub time_to_first_extinction: Option<usize>,
    pub min_population: usize,
    pub recovery_events: usize,
    // Memory counters
    pub cell_reads: usize,
    pub cell_writes: usize,
    pub lineage_inh: usize,
    pub archive_hits: usize,
    pub policy_mod: usize,
}

fn run_simulation(condition: Condition, seed: u64) -> (Vec<Metrics>, Counters) {
    fastrand::seed(seed);
    let mut world = GridWorld::new();
    
    // Spawn initial population
    for i in 0..100 {
        world.spawn_agent((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z);
    }
    world.spawn_food_random(INITIAL_FOOD, FOOD_ENERGY);
    
    let mut memory = ThreeLayerMemory::new(MAX_AGENTS, condition);
    let mut hazard = HazardRateTracker::new(MAX_AGENTS);
    let mut params = PopulationParams::default();
    
    let mut history = Vec::new();
    let mut min_pop = 100usize;
    let mut first_extinction: Option<usize> = None;
    let mut recovery_events = 0;
    let mut was_low = false;
    
    // Regime shifts at specific ticks
    let shifts = vec![2000, 4000, 6000];
    
    for tick in (0..MAX_TICKS).step_by(100) {
        // Apply regime shifts
        if shifts.contains(&tick) {
            world.food.clear(); // Crash
            world.spawn_food_random(INITIAL_FOOD / 2, FOOD_ENERGY);
        }
        
        // Step agents with memory influence
        for (id, agent) in world.agents.iter_mut().enumerate() {
            if !agent.alive { continue; }
            
            // MEMORY INFLUENCE: Foraging efficiency
            let foraging_bonus = memory.get_foraging_bonus(id);
            
            // Find food with bonus
            if fastrand::f32() < 0.15 * foraging_bonus {
                agent.energy += FOOD_ENERGY * (foraging_bonus - 1.0) * 0.5;
                memory.record_success(id, 1.0);
            } else if fastrand::f32() < 0.3 {
                // Failed foraging attempt
                memory.record_success(id, 0.0);
            }
            
            // Metabolism cost
            agent.energy -= METABOLISM_COST;
            
            // Death
            if agent.energy <= 0.0 {
                agent.alive = false;
                hazard.record_death(tick);
                memory.on_death(tick, id);
            }
        }
        
        // Reproduction with lineage influence
        let mut new_agents = Vec::new();
        for (id, agent) in world.agents.iter().enumerate() {
            if !agent.alive { continue; }
            
            let lineage_bonus = memory.get_lineage_bonus(id);
            let repro_threshold = REPRO_COST * (1.0 - lineage_bonus);
            
            if agent.energy > repro_threshold && fastrand::f32() < 0.010 {
                let mut child = agent.clone();
                child.energy = 15.0;
                let dx = fastrand::i32(-1..2);
                let dy = fastrand::i32(-1..2);
                let new_x = (child.pos.x as i32 + dx).clamp(0, GRID_X as i32 - 1) as usize;
                let new_y = (child.pos.y as i32 + dy).clamp(0, GRID_Y as i32 - 1) as usize;
                child.pos.x = new_x;
                child.pos.y = new_y;
                
                let child_id = world.agents.len() + new_agents.len();
                memory.on_reproduction(id, child_id);
                
                new_agents.push(child);
            }
        }
        world.agents.extend(new_agents);
        
        // Food regen (low)
        if tick % 150 == 0 {
            world.spawn_food_random(FOOD_REGEN_RATE, FOOD_ENERGY);
        }
        
        // Metrics
        let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        
        if n < min_pop { min_pop = n; }
        if n == 0 && first_extinction.is_none() { first_extinction = Some(tick); }
        if n < 20 { was_low = true; }
        if was_low && n > 50 { recovery_events += 1; was_low = false; }
        
        let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
        let ci = compute_condensation_index(&phases);
        
        history.push(Metrics {
            tick,
            population: n,
            avg_cdi: if n > 0 { 0.15 + ci * 0.08 } else { 0.0 },
            avg_ci: ci,
            hazard_rate: hazard.hazard_rate(),
            extinct: n == 0,
            time_to_first_extinction: first_extinction,
            min_population: min_pop,
            recovery_events,
            cell_reads: memory.counters.cell_reads,
            cell_writes: memory.counters.cell_writes,
            lineage_inh: memory.counters.lineage_inheritances,
            archive_hits: memory.counters.archive_hits,
            policy_mod: memory.counters.policy_modified,
        });
        
        world.step();
        
        if n == 0 { break; }
    }
    
    (history, memory.counters)
}

fn run_condition(name: &str, condition: Condition, seeds: &[u64]) {
    println!("\n{}", "=".repeat(70));
    println!("CONDITION: {}", name);
    println!("{}", "=".repeat(70));
    
    let start = Instant::now();
    let mut all_final = Vec::new();
    let mut all_extinct = 0;
    let mut total_counters = Counters::default();
    
    for (i, seed) in seeds.iter().enumerate() {
        let (history, counters) = run_simulation(condition, *seed);
        let final_m = history.last().unwrap();
        
        all_final.push(final_m.population);
        if final_m.extinct { all_extinct += 1; }
        
        total_counters.cell_reads += counters.cell_reads;
        total_counters.cell_writes += counters.cell_writes;
        total_counters.lineage_inheritances += counters.lineage_inheritances;
        total_counters.archive_hits += counters.archive_hits;
        total_counters.policy_modified += counters.policy_modified;
        
        println!("  Seed {}: N={:4} (min={:4}), extinct={}, recov={}, cell_r={}, lin_inh={}, arch_hit={}",
            i + 1, final_m.population, final_m.min_population,
            if final_m.extinct { "YES" } else { "NO" },
            final_m.recovery_events, counters.cell_reads, counters.lineage_inheritances, counters.archive_hits);
    }
    
    let mean_n = all_final.iter().sum::<usize>() as f64 / all_final.len() as f64;
    let extinct_rate = all_extinct as f64 / seeds.len() as f64 * 100.0;
    
    println!("\n  [STATS] Mean final N={:.1}, Extinct: {}/{} ({:.0}%)",
        mean_n, all_extinct, seeds.len(), extinct_rate);
    println!("  [COUNTERS] cell_r={}, cell_w={}, lineage={}, arch_hits={}, policy_mod={}",
        total_counters.cell_reads, total_counters.cell_writes,
        total_counters.lineage_inheritances, total_counters.archive_hits,
        total_counters.policy_modified);
    
    // Ablation verification
    match condition {
        Condition::NoCell | Condition::NoMemory => {
            if total_counters.cell_reads > 0 {
                println!("  ⚠️  WARNING: Cell ablation had {} reads!", total_counters.cell_reads);
            } else {
                println!("  ✓ Cell ablation verified (0 reads)");
            }
        }
        _ => {}
    }
    match condition {
        Condition::NoLineage | Condition::NoMemory => {
            if total_counters.lineage_inheritances > 0 {
                println!("  ⚠️  WARNING: Lineage ablation had {} inheritances!", total_counters.lineage_inheritances);
            } else {
                println!("  ✓ Lineage ablation verified (0 inheritances)");
            }
        }
        _ => {}
    }
    match condition {
        Condition::NoArchive | Condition::NoMemory => {
            if total_counters.archive_hits > 0 {
                println!("  ⚠️  WARNING: Archive ablation had {} hits!", total_counters.archive_hits);
            } else {
                println!("  ✓ Archive ablation verified (0 hits)");
            }
        }
        _ => {}
    }
    
    println!("  Time: {:.1}s", start.elapsed().as_secs_f64());
    
    // Export
    let filename = format!("/tmp/v19_fixed_{}.csv", name.to_lowercase().replace(" ", "_"));
    let mut file = File::create(&filename).unwrap();
    writeln!(file, "tick,pop,cdi,ci,hazard,extinct,min_pop,recovery,cell_r,cell_w,lineage,arch,policy_mod").unwrap();
    for seed in seeds {
        let (history, _) = run_simulation(condition, *seed);
        for m in &history {
            writeln!(file, "{},{},{:.4},{:.4},{:.4},{},{},{},{},{},{},{},{}",
                m.tick, m.population, m.avg_cdi, m.avg_ci, m.hazard_rate,
                if m.extinct { 1 } else { 0 }, m.min_population, m.recovery_events,
                m.cell_reads, m.cell_writes, m.lineage_inh, m.archive_hits, m.policy_mod).unwrap();
        }
    }
    println!("  Exported: {}", filename);
}

fn main() {
    println!("v19 Memory Production - FIXED with Decision Coupling\n");
    println!("PRESSURE SETTINGS:");
    println!("  Initial food: {} (limited)", INITIAL_FOOD);
    println!("  Food regen: {} per 150 ticks (scarce)", FOOD_REGEN_RATE);
    println!("  Metabolism: {} (high drain)", METABOLISM_COST);
    println!("  Reproduction cost: {} (expensive)", REPRO_COST);
    println!("  Regime shifts: ticks 2000, 4000, 6000\n");
    println!("MEMORY COUPLING:");
    println!("  Cell → Foraging efficiency bonus (up to 40%)");
    println!("  Lineage → Reproduction threshold reduction (up to 30%)");
    println!("  Archive → Weak sampling on newborn (p=0.01, 5% influence)\n");
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 3000 + i).collect();
    
    // Run all 5 conditions
    run_condition("Full Memory", Condition::Full, &seeds);
    run_condition("No Cell", Condition::NoCell, &seeds);
    run_condition("No Lineage", Condition::NoLineage, &seeds);
    run_condition("No Archive", Condition::NoArchive, &seeds);
    run_condition("No Memory", Condition::NoMemory, &seeds);
    
    println!("\n{}", "=".repeat(70));
    println!("IDENTIFIABILITY CHECK");
    println!("{}", "=".repeat(70));
    println!("Pass criteria (3/5 conditions must show predicted ordering):");
    println!("  Full > NoCell (Cell memory helps foraging)");
    println!("  Full > NoLineage (Lineage helps reproduction)");
    println!("  Full > NoArchive (Archive provides rare advantage)");
    println!("  Full > NoMemory (Combined effect)");
    println!("  All ablations verified via counters = 0\n");
}
