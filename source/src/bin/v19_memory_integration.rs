//! v19 × Three-Layer Memory Integration
//! 
//! Joint experiments: Cell Ablation | Lineage Ablation | Archive Disconnect
//! 
//! Hypothesis: Memory changes [CDI, CI, r, h] dynamics via behavior→structure

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, Position, PopulationDynamics, PopulationParams,
    HazardRateTracker, compute_condensation_index, StateVector,
    GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;

// Three-Layer Memory (from validation)
const MUTATION_RATE: f32 = 0.05;
const ARCHIVE_SAMPLE_PROB: f32 = 0.01;

#[derive(Clone)]
pub struct CellMemory {
    pub events: VecDeque<CellEvent>,
    pub max_size: usize,
}

#[derive(Clone)]
pub struct CellEvent {
    pub tick: usize,
    pub event_type: EventType,
    pub value: f32,
}

#[derive(Clone)]
pub enum EventType { Survival, Reproduction, FoodFound, Threat }

#[derive(Clone)]
pub struct LineageMemory {
    pub strategy_bias: f32,
    pub generation: usize,
}

#[derive(Clone)]
pub struct CausalArchive {
    pub records: Vec<ArchiveRecord>,
    pub sample_count: usize,
}

#[derive(Clone)]
pub struct ArchiveRecord {
    pub generation: usize,
    pub event_type: String,
    pub agent_id: usize,
}

/// Ablation condition
#[derive(Clone, Copy, Debug)]
pub enum Ablation {
    None,           // Full system
    Cell,           // No L1 (Cell Memory)
    Lineage,        // No L2 (Lineage Memory)
    Archive,        // No L3 (Causal Archive)
}

/// Integrated v19 + Memory system
pub struct V19MemorySystem {
    pub world: GridWorld,
    pub population: PopulationDynamics,
    pub hazard: HazardRateTracker,
    
    // Three-Layer Memory
    pub cell_memories: Vec<Option<CellMemory>>,  // L1
    pub lineage_memories: Vec<Option<LineageMemory>>, // L2
    pub archive: CausalArchive,                  // L3
    
    // Ablation condition
    pub ablation: Ablation,
    
    // Metrics
    pub tick: usize,
}

impl V19MemorySystem {
    pub fn new(ablation: Ablation) -> Self {
        let mut world = GridWorld::new();
        
        // Genesis
        for i in 0..100 {
            let x = (i * 11) % GRID_X;
            let y = (i * 17) % GRID_Y;
            let z = (i * 5) % GRID_Z;
            world.spawn_agent(x, y, z);
        }
        world.spawn_food_random(80, 50.0);
        
        // Initialize memories based on ablation
        let n_agents = 200;
        let cell_memories = match ablation {
            Ablation::Cell => vec![None; n_agents], // Ablated
            _ => (0..n_agents).map(|_| Some(CellMemory {
                events: VecDeque::with_capacity(100),
                max_size: 100,
            })).collect(),
        };
        
        let lineage_memories = match ablation {
            Ablation::Lineage => vec![None; n_agents], // Ablated
            _ => (0..n_agents).map(|_| Some(LineageMemory {
                strategy_bias: 0.0,
                generation: 0,
            })).collect(),
        };
        
        Self {
            world,
            population: PopulationDynamics::new(PopulationParams::default()),
            hazard: HazardRateTracker::new(2000),
            cell_memories,
            lineage_memories,
            archive: CausalArchive { records: Vec::new(), sample_count: 0 },
            ablation,
            tick: 0,
        }
    }
    
    /// Cell tick: L1 memory update (unless ablated)
    pub fn cell_tick(&mut self, agent_id: usize) {
        if matches!(self.ablation, Ablation::Cell) {
            return; // L1 ablated
        }
        
        if let Some(mem) = self.cell_memories.get_mut(agent_id) {
            if mem.is_none() { return; }
            let m = mem.as_mut().unwrap();
            
            m.events.push_back(CellEvent {
                tick: self.tick,
                event_type: EventType::Survival,
                value: 1.0,
            });
            if m.events.len() > m.max_size {
                m.events.pop_front();
            }
        }
    }
    
    /// Reproduction: L2 inheritance (unless ablated)
    pub fn on_reproduction(&mut self, parent_id: usize, child_id: usize) {
        // Cell memory for newborn
        if !matches!(self.ablation, Ablation::Cell) {
            if child_id >= self.cell_memories.len() {
                self.cell_memories.resize_with(child_id + 1, || Some(CellMemory {
                    events: VecDeque::with_capacity(100),
                    max_size: 100,
                }));
            }
        }
        
        // Lineage inheritance (unless ablated)
        if matches!(self.ablation, Ablation::Lineage) {
            return; // L2 ablated
        }
        
        let parent_bias = self.lineage_memories.get(parent_id)
            .and_then(|m| m.as_ref())
            .map(|l| l.strategy_bias)
            .unwrap_or(0.0);
        
        if child_id >= self.lineage_memories.len() {
            self.lineage_memories.resize_with(child_id + 1, || None);
        }
        
        // Inherit with mutation
        let mut child_bias = parent_bias;
        if fastrand::f32() < MUTATION_RATE {
            child_bias += (fastrand::f32() - 0.5) * 0.1;
            child_bias = child_bias.clamp(-1.0, 1.0);
        }
        
        self.lineage_memories[child_id] = Some(LineageMemory {
            strategy_bias: child_bias,
            generation: self.lineage_memories.get(parent_id)
                .and_then(|m| m.as_ref())
                .map(|l| l.generation + 1)
                .unwrap_or(0),
        });
        
        // Archive weak sampling for newborn (unless ablated)
        if !matches!(self.ablation, Ablation::Archive) {
            if fastrand::f32() < ARCHIVE_SAMPLE_PROB {
                self.archive.sample_count += 1;
                // Apply archive knowledge to lineage
                if let Some(lesson) = self.get_archive_lesson() {
                    if let Some(mem) = self.lineage_memories[child_id].as_mut() {
                        mem.strategy_bias = mem.strategy_bias * 0.9 + lesson * 0.1;
                    }
                }
            }
        }
    }
    
    fn get_archive_lesson(&self) -> Option<f32> {
        // Return average strategy bias from successful records
        if self.archive.records.is_empty() {
            return None;
        }
        Some(0.3) // Simulated successful strategy
    }
    
    /// Death: L3 archive write (unless ablated)
    pub fn on_death(&mut self, agent_id: usize) {
        if matches!(self.ablation, Ablation::Archive) {
            return; // L3 ablated
        }
        
        // Rate limited archive write
        let recent = self.archive.records.iter()
            .filter(|r| r.generation > self.tick.saturating_sub(1000))
            .count();
        
        if recent < 10 {
            let gen = self.lineage_memories.get(agent_id)
                .and_then(|m| m.as_ref())
                .map(|l| l.generation)
                .unwrap_or(0);
            
            self.archive.records.push(ArchiveRecord {
                generation: gen,
                event_type: "Death".to_string(),
                agent_id,
            });
        }
    }
    
    /// Get behavior modifier from memory
    pub fn get_behavior_bias(&self, agent_id: usize) -> f32 {
        // Cell memory influence
        let cell_bias = if !matches!(self.ablation, Ablation::Cell) {
            self.cell_memories.get(agent_id)
                .and_then(|m| m.as_ref())
                .map(|c| c.events.len() as f32 / 100.0)
                .unwrap_or(0.5)
        } else { 0.5 };
        
        // Lineage memory influence
        let lineage_bias = if !matches!(self.ablation, Ablation::Lineage) {
            self.lineage_memories.get(agent_id)
                .and_then(|m| m.as_ref())
                .map(|l| (l.strategy_bias + 1.0) / 2.0) // Normalize 0-1
                .unwrap_or(0.5)
        } else { 0.5 };
        
        // Combine
        (cell_bias + lineage_bias) / 2.0
    }
    
    /// Run simulation step
    pub fn step(&mut self) {
        // Population dynamics
        let births = self.population.births_this_tick;
        let deaths = self.population.deaths_this_tick;
        
        self.population.step(&mut self.world);
        
        // Track new births for memory inheritance
        let n_agents = self.world.agents.len();
        for i in (n_agents - births.saturating_sub(1)).saturating_sub(1)..n_agents {
            if i > 0 && i < n_agents {
                self.on_reproduction(i.saturating_sub(1), i);
            }
        }
        
        // Track deaths
        for _ in 0..deaths {
            self.hazard.record_death(self.tick);
        }
        
        // Cell ticks
        for id in 0..self.world.agents.len() {
            if self.world.agents.get(id).map(|a| a.alive).unwrap_or(false) {
                self.cell_tick(id);
            }
        }
        
        self.tick += 1;
        self.world.step();
    }
    
    /// Collect metrics
    pub fn collect_metrics(&self) -> IntegrationMetrics {
        let alive: Vec<&Agent> = self.world.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        
        let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
        let ci = compute_condensation_index(&phases);
        
        let cdi = if n > 0 {
            alive.iter().map(|a| a.cdi_contribution() as f64).sum::<f64>() / n as f64
        } else { 0.0 };
        
        let e = if n > 0 {
            alive.iter().map(|a| a.energy as f64).sum::<f64>() / n as f64
        } else { 0.0 };
        
        // Memory metrics
        let avg_cell_mem = if matches!(self.ablation, Ablation::Cell) {
            0.0
        } else {
            let total: usize = self.cell_memories.iter()
                .filter_map(|m| m.as_ref())
                .map(|m| m.events.len())
                .sum();
            let count = self.cell_memories.iter().filter(|m| m.is_some()).count();
            if count > 0 { total as f64 / count as f64 } else { 0.0 }
        };
        
        let lineage_count = if matches!(self.ablation, Ablation::Lineage) {
            0
        } else {
            self.lineage_memories.iter().filter(|m| m.is_some()).count()
        };
        
        let archive_count = if matches!(self.ablation, Ablation::Archive) {
            0
        } else {
            self.archive.records.len()
        };
        
        IntegrationMetrics {
            tick: self.tick,
            n,
            cdi,
            ci,
            r: 0.0, // TODO: compute r
            e,
            h: self.hazard.hazard_rate(),
            avg_cell_memory: avg_cell_mem,
            lineage_count,
            archive_count,
            ablation: format!("{:?}", self.ablation),
        }
    }
}

#[derive(Debug)]
pub struct IntegrationMetrics {
    pub tick: usize,
    pub n: usize,
    pub cdi: f64,
    pub ci: f64,
    pub r: f64,
    pub e: f64,
    pub h: f64,
    pub avg_cell_memory: f64,
    pub lineage_count: usize,
    pub archive_count: usize,
    pub ablation: String,
}

impl IntegrationMetrics {
    pub fn csv_header() -> &'static str {
        "tick,N,CDI,CI,r,E,h,cell_mem,lineage_count,archive_count,ablation"
    }
    
    pub fn to_csv(&self) -> String {
        format!("{},{},{:.4},{:.4},{:.4},{:.4},{:.4},{:.2},{},{},{}",
            self.tick, self.n, self.cdi, self.ci, self.r, self.e, self.h,
            self.avg_cell_memory, self.lineage_count, self.archive_count, self.ablation)
    }
}

/// Run joint experiment
fn run_joint_experiment(ablation: Ablation, ticks: usize) -> Vec<IntegrationMetrics> {
    println!("\n{}", "=".repeat(70));
    println!("Joint Experiment: {:?}", ablation);
    println!("{}", "=".repeat(70));
    
    let mut system = V19MemorySystem::new(ablation);
    let mut history: Vec<IntegrationMetrics> = Vec::new();
    
    for t in 0..ticks {
        system.step();
        
        if t % 100 == 0 {
            let m = system.collect_metrics();
            history.push(m);
            
            if t % 1000 == 0 {
                println!("Tick {:5}: N={:4}, CDI={:.3}, CI={:.3}, E={:.1}, h={:.4}",
                    t, history.last().unwrap().n,
                    history.last().unwrap().cdi,
                    history.last().unwrap().ci,
                    history.last().unwrap().e,
                    history.last().unwrap().h);
            }
        }
        
        // Early stop if collapsed
        if system.world.population() == 0 && t > 1000 {
            println!(">>> Collapse at tick {}", t);
            break;
        }
    }
    
    let m = system.collect_metrics();
    let final_n = m.n;
    let final_cdi = m.cdi;
    let final_ci = m.ci;
    let final_h = m.h;
    history.push(m);
    
    println!("Final: N={}, CDI={:.3}, CI={:.3}, h={:.4}",
        final_n, final_cdi, final_ci, final_h);
    
    history
}

fn main() {
    println!("╔══════════════════════════════════════════════════════════════════════╗");
    println!("║  v19 × Three-Layer Memory Integration                                ║");
    println!("║  Joint Experiments: Cell | Lineage | Archive Ablation                ║");
    println!("╚══════════════════════════════════════════════════════════════════════╝");
    
    // Run all four conditions
    let conditions = vec![
        Ablation::None,
        Ablation::Cell,
        Ablation::Lineage,
        Ablation::Archive,
    ];
    
    let mut all_results: Vec<(Ablation, Vec<IntegrationMetrics>)> = Vec::new();
    
    for condition in conditions {
        let history = run_joint_experiment(condition, 3000); // Reduced for speed
        all_results.push((condition, history));
    }
    
    // Export combined results
    let mut file = File::create("/tmp/v19_memory_integration.csv").unwrap();
    writeln!(file, "{}", IntegrationMetrics::csv_header()).unwrap();
    
    for (_, history) in &all_results {
        for m in history {
            writeln!(file, "{}", m.to_csv()).unwrap();
        }
    }
    
    // Summary
    println!("\n{}", "=".repeat(70));
    println!("[SUMMARY]");
    println!("{}", "=".repeat(70));
    
    for (condition, history) in &all_results {
        if let Some(final_m) = history.last() {
            println!("{:12}: N={:4}, CDI={:.3}, CI={:.3}, h={:.4}, survived {} ticks",
                format!("{:?}", condition),
                final_m.n,
                final_m.cdi,
                final_m.ci,
                final_m.h,
                history.len() * 100
            );
        }
    }
    
    println!("\nExported: /tmp/v19_memory_integration.csv");
    println!("{}", "=".repeat(70));
}
