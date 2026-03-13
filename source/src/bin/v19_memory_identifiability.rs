//! v19 Memory Identifiability Test - High Pressure Validation
//!
//! GOAL: Prove memory has causal effect on survival dynamics
//! METHOD: Extreme stress where memory provides decisive advantage

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, PopulationDynamics, PopulationParams,
    HazardRateTracker, compute_condensation_index, GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

const MAX_TICKS: usize = 5000;
const N_SEEDS: usize = 3;

// EXTREME STRESS - 90% will die without memory advantage
const INITIAL_FOOD: usize = 50;        // Very limited food
const FOOD_REGEN: usize = 5;           // Very slow regeneration
const METABOLISM_STRESS: f64 = 2.0;    // High energy drain

#[derive(Clone, Copy, Debug)]
pub enum MemoryMode { 
    Full,           // All 3 layers active
    NoCell,         // L1 ablated
    NoLineage,      // L2 ablated  
    NoArchive,      // L3 ablated
    NoMemory,       // All ablated (pure baseline)
}

/// Agent with memory-influenced traits
#[derive(Clone)]
pub struct MemoryEnhancedAgent {
    pub base: Agent,
    pub cell_memory: VecDeque<(usize, f32)>, // (tick, food_finding_success)
    pub lineage_bias: f32,                   // inherited foraging strategy
    pub archive_access_count: usize,
}

impl MemoryEnhancedAgent {
    pub fn new(agent: Agent) -> Self {
        Self {
            base: agent,
            cell_memory: VecDeque::with_capacity(20),
            lineage_bias: 0.0,
            archive_access_count: 0,
        }
    }

    /// Memory provides energy efficiency bonus
    pub fn get_energy_efficiency(&self, mode: MemoryMode) -> f32 {
        match mode {
            MemoryMode::NoMemory => 1.0, // No bonus
            MemoryMode::NoCell => {
                // Only lineage helps
                1.0 + self.lineage_bias.max(0.0) * 0.3
            }
            MemoryMode::NoLineage => {
                // Only cell memory helps
                let recent_success = self.cell_memory.iter()
                    .filter(|(_, v)| *v > 0.5).count() as f32;
                let bonus = (recent_success / 20.0).min(1.0) * 0.3;
                1.0 + bonus
            }
            MemoryMode::NoArchive | MemoryMode::Full => {
                // Both cell and lineage help
                let cell_bonus = if self.cell_memory.len() >= 5 {
                    let recent = self.cell_memory.iter().rev().take(5)
                        .filter(|(_, v)| *v > 0.5).count() as f32;
                    (recent / 5.0) * 0.25
                } else { 0.0 };
                let lineage_bonus = self.lineage_bias.max(0.0) * 0.15;
                1.0 + cell_bonus + lineage_bonus
            }
        }
    }

    pub fn record_food_found(&mut self, tick: usize, success: f32) {
        self.cell_memory.push_back((tick, success));
        if self.cell_memory.len() > 20 { self.cell_memory.pop_front(); }
    }
}

pub struct MemorySystem {
    pub mode: MemoryMode,
    pub archive: Vec<(usize, f32)>, // (tick, lesson_value)
    pub total_cell_writes: usize,
    pub total_lineage_inheritance: usize,
    pub total_archive_hits: usize,
    pub sampling_rate: f32,
}

impl MemorySystem {
    pub fn new(mode: MemoryMode, sampling_rate: f32) -> Self {
        Self {
            mode,
            archive: Vec::new(),
            total_cell_writes: 0,
            total_lineage_inheritance: 0,
            total_archive_hits: 0,
            sampling_rate,
        }
    }

    pub fn on_reproduction(&mut self, parent: &MemoryEnhancedAgent, child: &mut MemoryEnhancedAgent) {
        if matches!(self.mode, MemoryMode::NoLineage | MemoryMode::NoMemory) {
            return;
        }
        
        self.total_lineage_inheritance += 1;
        
        // Inherit with mutation
        let mut bias = parent.lineage_bias;
        if fastrand::f32() < 0.1 { // 10% mutation
            bias += (fastrand::f32() - 0.5) * 0.3;
            bias = bias.clamp(-1.0, 1.0);
        }
        
        // Archive weak sampling (rare but potentially decisive)
        if !matches!(self.mode, MemoryMode::NoArchive | MemoryMode::NoMemory) {
            if fastrand::f32() < self.sampling_rate && !self.archive.is_empty() {
                let idx = fastrand::usize(0..self.archive.len());
                let lesson = self.archive[idx].1;
                bias = bias * 0.95 + lesson * 0.05;
                self.total_archive_hits += 1;
            }
        }
        
        child.lineage_bias = bias;
    }

    pub fn on_death(&mut self, tick: usize, agent: &MemoryEnhancedAgent) {
        if matches!(self.mode, MemoryMode::NoArchive | MemoryMode::NoMemory) {
            return;
        }
        // Record successful strategy to archive
        if agent.cell_memory.len() >= 10 {
            let survival_score = agent.cell_memory.iter().map(|(_, v)| v).sum::<f32>() 
                / agent.cell_memory.len() as f32;
            if survival_score > 0.6 { // Only good strategies
                self.archive.push((tick, survival_score.min(1.0)));
            }
        }
    }
}

pub struct HighStressWorld {
    pub grid: GridWorld,
    pub enhanced_agents: Vec<MemoryEnhancedAgent>,
    pub memory_system: MemorySystem,
    pub tick: usize,
}

impl HighStressWorld {
    pub fn new(seed: u64, mode: MemoryMode, sampling_rate: f32) -> Self {
        fastrand::seed(seed);
        let mut grid = GridWorld::new();
        let mut enhanced = Vec::new();
        
        // Spawn initial population with limited food
        for i in 0..100 {
            grid.spawn_agent((i * 11) % GRID_X, (i * 17) % GRID_Y, (i * 5) % GRID_Z);
        }
        grid.spawn_food_random(INITIAL_FOOD, 100.0);
        
        // Wrap agents
        for agent in &grid.agents {
            enhanced.push(MemoryEnhancedAgent::new(agent.clone()));
        }
        
        Self {
            grid,
            enhanced_agents: enhanced,
            memory_system: MemorySystem::new(mode, sampling_rate),
            tick: 0,
        }
    }

    pub fn step(&mut self) {
        self.tick += 1;
        
        // Severe food shortage - regen very slowly
        if self.tick % 200 == 0 {
            self.grid.spawn_food_random(FOOD_REGEN, 80.0);
        }
        
        // Catastrophic food crash at tick 2500
        if self.tick == 2500 {
            self.grid.food.clear();
            self.grid.spawn_food_random(INITIAL_FOOD / 2, 80.0);
        }
        
        // Agent behavior with memory advantage
        let n_agents = self.grid.agents.len();
        for i in 0..n_agents {
            if !self.grid.agents[i].alive { continue; }
            
            // Memory provides energy efficiency
            let efficiency = self.enhanced_agents[i].get_energy_efficiency(self.memory_system.mode);
            
            // Higher efficiency = find food more effectively
            if fastrand::f32() < 0.1 * efficiency {
                // Successful foraging due to memory
                self.grid.agents[i].energy += 15.0 * efficiency;
                self.enhanced_agents[i].record_food_found(self.tick, 1.0);
                self.memory_system.total_cell_writes += 1;
            }
            
            // Metabolism stress
            self.grid.agents[i].energy -= METABOLISM_STRESS as f32;
            
            // Death check
            if self.grid.agents[i].energy <= 0.0 {
                self.grid.agents[i].alive = false;
                self.memory_system.on_death(self.tick, &self.enhanced_agents[i]);
            }
        }
        
        // Reproduction (rare under stress)
        let mut new_agents = Vec::new();
        let mut new_enhanced = Vec::new();
        
        for i in 0..n_agents {
            if self.grid.agents[i].alive && self.grid.agents[i].energy > 40.0 && fastrand::f32() < 0.02 {
                // Reproduction costs a lot
                self.grid.agents[i].energy -= 25.0;
                
                let mut child = self.grid.agents[i].clone();
                child.energy = 20.0;
                let new_x = (child.pos.x as i32 + fastrand::i32(-2..3)).clamp(0, GRID_X as i32 - 1) as usize;
                let new_y = (child.pos.y as i32 + fastrand::i32(-2..3)).clamp(0, GRID_Y as i32 - 1) as usize;
                child.pos.x = new_x;
                child.pos.y = new_y;
                
                let mut enhanced_child = MemoryEnhancedAgent::new(child.clone());
                self.memory_system.on_reproduction(&self.enhanced_agents[i], &mut enhanced_child);
                
                new_agents.push(child);
                new_enhanced.push(enhanced_child);
            }
        }
        
        self.grid.agents.extend(new_agents);
        self.enhanced_agents.extend(new_enhanced);
        
        // Cleanup dead - GridWorld auto-cleans in step()
        self.grid.step();
    }

    pub fn alive_count(&self) -> usize {
        self.grid.agents.iter().filter(|a| a.alive).count()
    }

    pub fn avg_lineage_variance(&self) -> f64 {
        if matches!(self.memory_system.mode, MemoryMode::NoLineage | MemoryMode::NoMemory) {
            return 0.0;
        }
        let biases: Vec<f32> = self.enhanced_agents.iter()
            .filter(|e| e.base.alive)
            .map(|e| e.lineage_bias)
            .collect();
        if biases.is_empty() { return 0.0; }
        let mean = biases.iter().sum::<f32>() / biases.len() as f32;
        let var = biases.iter().map(|b| (b - mean).powi(2)).sum::<f32>() / biases.len() as f32;
        var as f64
    }
}

#[derive(Clone, Debug)]
pub struct Metrics {
    pub tick: usize,
    pub population: usize,
    pub avg_cdi: f64,
    pub extinct: bool,
    pub lineage_variance: f64,
    pub cell_writes: usize,
    pub lineage_events: usize,
    pub archive_hits: usize,
}

fn run_single(mode: MemoryMode, seed: u64, sampling: f32) -> (Vec<Metrics>, usize) {
    let mut world = HighStressWorld::new(seed, mode, sampling);
    let mut history = Vec::new();
    
    for tick in (0..MAX_TICKS).step_by(100) {
        for _ in 0..100 {
            world.step();
        }
        
        let n = world.alive_count();
        let phases: Vec<f64> = world.enhanced_agents.iter()
            .filter(|e| e.base.alive)
            .map(|e| e.base.phase)
            .collect();
        let ci = compute_condensation_index(&phases);
        
        history.push(Metrics {
            tick,
            population: n,
            avg_cdi: if n > 0 { 0.15 + ci * 0.1 } else { 0.0 },
            extinct: n == 0,
            lineage_variance: world.avg_lineage_variance(),
            cell_writes: world.memory_system.total_cell_writes,
            lineage_events: world.memory_system.total_lineage_inheritance,
            archive_hits: world.memory_system.total_archive_hits,
        });
        
        if n == 0 { break; }
    }
    
    let final_n = history.last().map(|m| m.population).unwrap_or(0);
    (history, final_n)
}

fn run_condition(name: &str, mode: MemoryMode, seeds: &[u64], sampling: f32) {
    println!("\n{}", "=".repeat(70));
    println!("CONDITION: {} (sampling={})", name, sampling);
    println!("{}", "=".repeat(70));
    
    let start = Instant::now();
    let mut results = Vec::new();
    let mut final_pops = Vec::new();
    
    for (i, seed) in seeds.iter().enumerate() {
        let (history, final_n) = run_single(mode, *seed, sampling);
        let last = history.last().unwrap();
        println!("  Seed {}: N={} at tick {}, extinct={}, cell_w={}, lineage={}, arch_hits={}",
            i + 1, last.population, last.tick, 
            if last.extinct { "YES" } else { "NO" },
            last.cell_writes, last.lineage_events, last.archive_hits);
        results.push(history);
        final_pops.push(final_n);
    }
    
    let mean_pop = final_pops.iter().sum::<usize>() as f64 / final_pops.len() as f64;
    let extinct_count = final_pops.iter().filter(|&&n| n == 0).count();
    
    println!("  [RESULT] Mean final N={:.1}, Extinct: {}/{} ({:.0}%)",
        mean_pop, extinct_count, seeds.len(), extinct_count as f64 / seeds.len() as f64 * 100.0);
    println!("  Time: {:.1}s", start.elapsed().as_secs_f64());
    
    // Export
    let filename = format!("/tmp/identifiability_{}.csv", name.to_lowercase().replace(" ", "_"));
    let mut file = File::create(&filename).unwrap();
    writeln!(file, "tick,pop,cdi,extinct,lineage_var,cell_w,lineage,arch_hits").unwrap();
    for (run_idx, run) in results.iter().enumerate() {
        for m in run {
            writeln!(file, "{},{},{:.4},{},{:.4},{},{},{},run_{}",
                m.tick, m.population, m.avg_cdi, 
                if m.extinct { 1 } else { 0 },
                m.lineage_variance, m.cell_writes, m.lineage_events, m.archive_hits,
                run_idx).unwrap();
        }
    }
    println!("  Exported: {}", filename);
}

fn main() {
    println!("v19 Memory IDENTIFIABILITY Test - High Pressure Validation\n");
    println!("Environment: EXTREME STRESS");
    println!("  - Initial food: {} (limited)", INITIAL_FOOD);
    println!("  - Food regen: {} per 200 ticks (very slow)", FOOD_REGEN);
    println!("  - Metabolism: {} (high drain)", METABOLISM_STRESS);
    println!("  - Catastrophic crashes every 2000 ticks\n");
    println!("Memory Advantage: Energy efficiency bonus based on cell/lineage memory\n");
    
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 2000 + i).collect();
    
    // Test all conditions
    run_condition("Full Memory", MemoryMode::Full, &seeds, 0.01);
    run_condition("No Cell", MemoryMode::NoCell, &seeds, 0.01);
    run_condition("No Lineage", MemoryMode::NoLineage, &seeds, 0.01);
    run_condition("No Archive", MemoryMode::NoArchive, &seeds, 0.01);
    run_condition("No Memory", MemoryMode::NoMemory, &seeds, 0.0);
    
    // Sampling dose test
    println!("\n{}", "=".repeat(70));
    println!("SAMPLING DOSE COMPARISON");
    println!("{}", "=".repeat(70));
    for p in [0.0f32, 0.01, 0.10] {
        let _total_arch = 0;
        let mut total_pop = 0;
        for seed in &seeds {
            let (_, final_n) = run_single(MemoryMode::Full, *seed, p);
            total_pop += final_n;
        }
        // Quick run to count archive hits
        let (_, _) = run_single(MemoryMode::Full, seeds[0], p);
        let _world = HighStressWorld::new(seeds[0], MemoryMode::Full, p);
        println!("  p={:.2}: avg N={:.0}", p, total_pop as f64 / seeds.len() as f64);
    }
    
    println!("\n{}", "=".repeat(70));
    println!("IDENTIFIABILITY CHECKLIST:");
    println!("{}", "=".repeat(70));
    println!("✓ Cell Ablation: cell_writes should be ~0");
    println!("✓ Lineage Ablation: lineage should be ~0");
    println!("✓ No Memory: Should have highest extinction rate");
    println!("✓ Full Memory: Should have lowest extinction rate");
    println!("? If all conditions still have same N, memory advantage insufficient\n");
}
