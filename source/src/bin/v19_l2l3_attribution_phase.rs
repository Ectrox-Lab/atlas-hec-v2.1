//! v19 L2/L3 Attribution Phase - Extended Duration + Enhanced Metrics
//!
//! TARGET: Move L2/L3 from "present but weak" to "statistically identifiable"
//!
//! SCOPE: Narrow focus on attribution, not existence
//! - Conditions: NoLineage, NoArchive, p=0.00, p=0.01, p=0.10 (vs Full as baseline)
//! - Durations: 20k, 50k ticks
//! - Metrics: Enhanced indicators for long-term adaptation

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, PopulationParams, HazardRateTracker,
    compute_condensation_index, GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;

const N_SEEDS: usize = 5;

// PERMISSIVE pressure with frequent shifts for adaptation testing
const INITIAL_FOOD: usize = 120;
const FOOD_REGEN: usize = 20;
const METABOLISM: f32 = 0.9;
const REPRO_COST: f32 = 22.0;
const REGEN_INTERVAL: usize = 80;

#[derive(Clone, Copy, Debug)]
pub enum Condition { Full, NoLineage, NoArchive, P_0_00, P_0_01, P_0_10 }

pub struct Counters {
    pub lineage_inh: usize,
    pub lineage_mut: usize,
    pub archive_samples: usize,
    pub archive_hits: usize,
    pub policy_mod: usize,
}

impl Default for Counters {
    fn default() -> Self {
        Self { lineage_inh: 0, lineage_mut: 0, archive_samples: 0, archive_hits: 0, policy_mod: 0 }
    }
}

/// Enhanced tracking for L2/L3 attribution
pub struct EnhancedTracker {
    pub shift_times: Vec<usize>,
    pub recovery_times: Vec<usize>,
    pub lineage_bias_history: Vec<Vec<f32>>, // per tick snapshot
    pub archive_access_log: Vec<(usize, usize)>, // (tick, agent_id)
    pub strategy_shifts: usize,
}

impl Default for EnhancedTracker {
    fn default() -> Self {
        Self { shift_times: Vec::new(), recovery_times: Vec::new(),
               lineage_bias_history: Vec::new(), archive_access_log: Vec::new(),
               strategy_shifts: 0 }
    }
}

pub struct ThreeLayerMemory {
    pub cell: Vec<Option<VecDeque<f32>>>,
    pub lineage: Vec<Option<(f32, usize)>>,
    pub archive: Vec<(usize, f32)>,
    pub condition: Condition,
    pub counters: Counters,
    pub tracker: EnhancedTracker,
    pub p_rate: f32,
}

impl ThreeLayerMemory {
    pub fn new(n: usize, condition: Condition) -> Self {
        let p_rate = match condition {
            Condition::P_0_00 => 0.0,
            Condition::P_0_01 => 0.01,
            Condition::P_0_10 => 0.10,
            _ => 0.01,
        };
        
        let cell = (0..n).map(|_| Some(VecDeque::with_capacity(20))).collect();
        
        let lineage = match condition {
            Condition::NoLineage | Condition::P_0_00 | Condition::P_0_01 | Condition::P_0_10
                => vec![None; n],
            _ => (0..n).map(|_| Some((0.0, 0))).collect(),
        };
        
        Self { cell, lineage, archive: Vec::new(), condition, counters: Counters::default(),
               tracker: EnhancedTracker::default(), p_rate }
    }

    pub fn get_foraging_bonus(&mut self, agent_id: usize) -> f32 {
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            if mem.len() >= 5 {
                let recent = mem.iter().rev().take(5).filter(|&&v| v > 0.5).count() as f32;
                return 1.0 + (recent / 5.0) * 0.35;
            }
        }
        1.0
    }

    pub fn record_success(&mut self, agent_id: usize, success: f32) {
        if let Some(Some(mem)) = self.cell.get_mut(agent_id) {
            mem.push_back(success);
            if mem.len() > 20 { mem.pop_front(); }
        }
    }

    pub fn on_reproduction(&mut self, parent_id: usize, child_id: usize, tick: usize) {
        if matches!(self.condition, Condition::NoLineage) { return; }
        
        self.counters.lineage_inh += 1;
        let parent_bias = self.lineage.get(parent_id).and_then(|l| l.as_ref())
            .map(|(b, _)| *b).unwrap_or(0.0);
        
        if child_id >= self.lineage.len() {
            self.lineage.resize_with(child_id + 1, || None);
        }
        
        let mut child_bias = parent_bias;
        if fastrand::f32() < 0.1 {
            self.counters.lineage_mut += 1;
            child_bias += (fastrand::f32() - 0.5) * 0.3;
            child_bias = child_bias.clamp(-1.0, 1.0);
        }
        
        let gen = self.lineage.get(parent_id).and_then(|l| l.as_ref())
            .map(|(_, g)| g + 1).unwrap_or(0);
        
        // Archive sampling
        if !matches!(self.condition, Condition::NoArchive) {
            self.counters.archive_samples += 1;
            if fastrand::f32() < self.p_rate && !self.archive.is_empty() {
                self.counters.archive_hits += 1;
                let idx = fastrand::usize(0..self.archive.len());
                let lesson = self.archive[idx].1;
                child_bias = child_bias * 0.95 + lesson * 0.05;
                self.counters.policy_mod += 1;
                self.tracker.archive_access_log.push((tick, child_id));
            }
        }
        
        // Track strategy shift
        if (child_bias - parent_bias).abs() > 0.15 {
            self.tracker.strategy_shifts += 1;
        }
        
        self.lineage[child_id] = Some((child_bias, gen));
    }

    pub fn on_death(&mut self, tick: usize, agent_id: usize) {
        if matches!(self.condition, Condition::NoArchive) { return; }
        if let Some(Some(mem)) = self.cell.get(agent_id) {
            if mem.len() >= 10 {
                let avg = mem.iter().sum::<f32>() / mem.len() as f32;
                if avg > 0.5 { self.archive.push((tick, avg.min(1.0))); }
            }
        }
    }

    pub fn get_lineage_bias(&self, agent_id: usize) -> f32 {
        self.lineage.get(agent_id).and_then(|l| l.as_ref())
            .map(|(b, _)| b.max(0.0) * 0.3).unwrap_or(0.0)
    }
    
    pub fn snapshot_lineages(&mut self) {
        let biases: Vec<f32> = self.lineage.iter()
            .filter_map(|l| l.as_ref().map(|(b, _)| *b))
            .collect();
        if !biases.is_empty() {
            self.tracker.lineage_bias_history.push(biases);
        }
    }
    
    pub fn compute_strategy_persistence(&self) -> f64 {
        if self.tracker.lineage_bias_history.len() < 10 { return 0.0; }
        
        let window = &self.tracker.lineage_bias_history[self.tracker.lineage_bias_history.len()-10..];
        let means: Vec<f64> = window.iter().map(|v| {
            if v.is_empty() { return 0.0; }
            v.iter().map(|&x| x as f64).sum::<f64>() / v.len() as f64
        }).collect();
        
        if means.len() < 2 { return 0.0; }
        let mean_diff: Vec<f64> = means.windows(2).map(|w| (w[1] - w[0]).abs()).collect();
        mean_diff.iter().sum::<f64>() / mean_diff.len() as f64
    }
}

/// Enhanced metrics for L2/L3 attribution
#[derive(Clone, Debug)]
pub struct EnhancedMetrics {
    pub tick: usize,
    pub pop: usize,
    pub cdi: f64,
    pub ci: f64,
    pub hazard: f64,
    // Core attribution metrics
    pub adaptation_latency: f64,        // Time to recover after shift
    pub strategy_persistence: f64,      // Stability of lineage bias
    pub lineage_variance: f64,          // Diversity of strategies
    pub archive_hit_rate: f64,          // Hits per 1000 ticks
    pub cross_lineage_learning: f64,    // Archive influence spread
    pub recovery_slope: f64,            // Rate of recovery
    // Counters
    pub lineage_inh: usize,
    pub archive_hits: usize,
    pub strategy_shifts: usize,
}

fn run_simulation(condition: Condition, max_ticks: usize, seed: u64) -> (Vec<EnhancedMetrics>, Counters, EnhancedTracker) {
    fastrand::seed(seed);
    let mut world = GridWorld::new();
    
    for i in 0..100 {
        world.spawn_agent((i * 13) % GRID_X, (i * 17) % GRID_Y, (i * 7) % GRID_Z);
    }
    world.spawn_food_random(INITIAL_FOOD, 30.0);
    
    let mut memory = ThreeLayerMemory::new(5000, condition);
    let mut hazard = HazardRateTracker::new(5000);
    let mut history = Vec::new();
    
    // Frequent shifts to test adaptation (every 2000 ticks)
    let shifts: Vec<usize> = (2000..max_ticks).step_by(2000).collect();
    let mut last_shift_pop = 100usize;
    let mut recovering_from: Option<usize> = None;
    let mut recovery_start_pop = 0usize;
    
    for tick in (0..max_ticks).step_by(100) {
        // Regime shift
        if shifts.contains(&tick) {
            memory.tracker.shift_times.push(tick);
            world.food.clear();
            world.spawn_food_random(INITIAL_FOOD / 2, 30.0);
            last_shift_pop = world.agents.iter().filter(|a| a.alive).count();
            recovering_from = Some(tick);
            recovery_start_pop = last_shift_pop;
        }
        
        // Agent behavior
        for (id, agent) in world.agents.iter_mut().enumerate() {
            if !agent.alive { continue; }
            
            let foraging_bonus = memory.get_foraging_bonus(id);
            if fastrand::f32() < 0.12 * foraging_bonus {
                agent.energy += 25.0 * (foraging_bonus - 1.0) * 0.5;
                memory.record_success(id, 1.0);
            } else if fastrand::f32() < 0.25 {
                memory.record_success(id, 0.0);
            }
            
            agent.energy -= METABOLISM;
            if agent.energy <= 0.0 {
                agent.alive = false;
                hazard.record_death(tick);
                memory.on_death(tick, id);
            }
        }
        
        // Reproduction with lineage
        let mut new_agents = Vec::new();
        for (id, agent) in world.agents.iter().enumerate() {
            if !agent.alive { continue; }
            let lineage_bonus = memory.get_lineage_bias(id);
            let threshold = REPRO_COST * (1.0 - lineage_bonus);
            if agent.energy > threshold && fastrand::f32() < 0.012 {
                let mut child = agent.clone();
                child.energy = 12.0;
                let dx = fastrand::i32(-1..2);
                let dy = fastrand::i32(-1..2);
                child.pos.x = (child.pos.x as i32 + dx).clamp(0, GRID_X as i32 - 1) as usize;
                child.pos.y = (child.pos.y as i32 + dy).clamp(0, GRID_Y as i32 - 1) as usize;
                let child_id = world.agents.len() + new_agents.len();
                memory.on_reproduction(id, child_id, tick);
                new_agents.push(child);
            }
        }
        world.agents.extend(new_agents);
        
        // Food regen
        if tick % REGEN_INTERVAL == 0 {
            world.spawn_food_random(FOOD_REGEN, 30.0);
        }
        
        // Metrics
        let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        
        // Calculate adaptation latency (if recovering)
        let (adaptation_latency, recovery_slope) = if let Some(shift_tick) = recovering_from {
            let elapsed = tick - shift_tick;
            // Recovery: back to 90% of pre-shift population
            if n > last_shift_pop * 9 / 10 {
                memory.tracker.recovery_times.push(elapsed);
                recovering_from = None;
                let slope = (n as f64 - recovery_start_pop as f64) / (elapsed as f64 / 100.0).max(1.0);
                (elapsed as f64, slope)
            } else {
                (elapsed as f64, 0.0)
            }
        } else {
            (0.0, 0.0)
        };
        
        // Snapshot for strategy persistence
        memory.snapshot_lineages();
        
        let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
        let ci = compute_condensation_index(&phases);
        
        // Lineage variance
        let biases: Vec<f32> = memory.lineage.iter()
            .filter_map(|l| l.as_ref().map(|(b, _)| *b))
            .collect();
        let lineage_var = if biases.is_empty() { 0.0 } else {
            let mean = biases.iter().sum::<f32>() / biases.len() as f32;
            biases.iter().map(|b| (*b - mean).powi(2)).sum::<f32>() as f64 / biases.len() as f64
        };
        
        // Archive hit rate per 1000 ticks
        let arch_rate = memory.counters.archive_hits as f64 * 1000.0 / (tick + 1).max(1) as f64;
        
        // Cross-lineage learning = unique agents accessing archive
        let unique_agents: std::collections::HashSet<usize> = memory.tracker.archive_access_log.iter()
            .filter(|(t, _)| *t > tick.saturating_sub(1000))
            .map(|(_, aid)| *aid)
            .collect();
        let cross_learning = unique_agents.len() as f64;
        
        history.push(EnhancedMetrics {
            tick, pop: n, cdi: if n > 0 { 0.15 + ci * 0.08 } else { 0.0 },
            ci, hazard: hazard.hazard_rate(), adaptation_latency,
            strategy_persistence: memory.compute_strategy_persistence(),
            lineage_variance: lineage_var, archive_hit_rate: arch_rate,
            cross_lineage_learning: cross_learning, recovery_slope,
            lineage_inh: memory.counters.lineage_inh,
            archive_hits: memory.counters.archive_hits,
            strategy_shifts: memory.tracker.strategy_shifts,
        });
        
        world.step();
        if n == 0 { break; }
    }
    
    (history, memory.counters, memory.tracker)
}

fn analyze_duration(label: &str, max_ticks: usize, seeds: &[u64]) {
    println!("\n{}", "=".repeat(75));
    println!("DURATION: {} ticks", label);
    println!("{}", "=".repeat(75));
    
    for condition in [Condition::Full, Condition::NoLineage, Condition::NoArchive,
                      Condition::P_0_00, Condition::P_0_01, Condition::P_0_10] {
        let name = format!("{:?}", condition);
        print!("{:12} | ", name);
        
        let mut finals = Vec::new();
        let mut avg_latencies = Vec::new();
        let mut avg_persistences = Vec::new();
        let mut total_lineage = 0;
        let mut total_arch_hits = 0;
        let mut total_strategy_shifts = 0;
        
        for seed in seeds {
            let (history, counters, tracker) = run_simulation(condition, max_ticks, *seed);
            let last = history.last().unwrap();
            
            finals.push(last.pop);
            total_lineage += counters.lineage_inh;
            total_arch_hits += counters.archive_hits;
            total_strategy_shifts += tracker.strategy_shifts;
            
            // Average latency across recoveries
            if !tracker.recovery_times.is_empty() {
                let avg_lat = tracker.recovery_times.iter().sum::<usize>() as f64 
                    / tracker.recovery_times.len() as f64;
                avg_latencies.push(avg_lat);
            }
            
            // Strategy persistence
            avg_persistences.push(last.strategy_persistence);
        }
        
        let mean_final = finals.iter().sum::<usize>() as f64 / finals.len() as f64;
        let mean_persist = avg_persistences.iter().sum::<f64>() / avg_persistences.len().max(1) as f64;
        let mean_latency = if avg_latencies.is_empty() { 0.0 } else {
            avg_latencies.iter().sum::<f64>() / avg_latencies.len() as f64
        };
        
        println!("N={:6.1} | Lat={:6.1} | Persist={:.4} | Lin={} | Arch={} | Shifts={}",
            mean_final, mean_latency, mean_persist,
            total_lineage / seeds.len(),
            total_arch_hits / seeds.len(),
            total_strategy_shifts / seeds.len());
    }
}

fn main() {
    println!("v19 L2/L3 Attribution Phase - Extended Duration Test\n");
    println!("Focus: NoLineage, NoArchive, p=0.00/0.01/0.10 (vs Full)");
    println!("Enhanced metrics: adaptation_latency, strategy_persistence, cross_lineage_learning\n");
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 5000 + i).collect();
    
    // 20k ticks
    analyze_duration("20,000", 20000, &seeds);
    
    // 50k ticks  
    analyze_duration("50,000", 50000, &seeds);
    
    // Success criteria
    println!("\n{}", "=".repeat(75));
    println!("SUCCESS CRITERIA (L2/L3 Attribution)");
    println!("{}", "=".repeat(75));
    println!("1. NoLineage shows HIGHER adaptation_latency than Full");
    println!("2. NoArchive shows LOWER cross_lineage_learning than Full");
    println!("3. p=0.00 vs p=0.01 vs p=0.10 separate on at least one metric");
    println!("4. Effects stable across 5 seeds");
    println!("\nCurrent: L2/L3 mechanism active, attribution pending...");
}
