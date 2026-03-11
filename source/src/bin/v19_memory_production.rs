//! v19 Memory Production - 5 MVEs with multi-seed analysis

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, Position, PopulationDynamics, PopulationParams,
    HazardRateTracker, compute_condensation_index, StateVector,
    GRID_X, GRID_Y, GRID_Z,
};

use std::collections::VecDeque;
use std::fs::File;
use std::io::Write;
use std::time::Instant;

const MUTATION_RATE: f32 = 0.05;
const ARCHIVE_SAMPLE_PROB: f32 = 0.01;
const MAX_TICKS: usize = 10000;
const N_SEEDS: usize = 5;

#[derive(Clone, Copy, Debug)]
pub enum AblationType { None, Cell, Lineage, Archive }

#[derive(Clone)]
pub struct ThreeLayerMemory {
    pub cell_memories: Vec<Option<VecDeque<(usize, f32)>>>,
    pub lineage_memories: Vec<Option<(f32, usize)>>,
    pub archive: Vec<(usize, usize)>,
    pub ablation: AblationType,
    pub sampling_rate: f32,
}

impl ThreeLayerMemory {
    pub fn new(n: usize, ablation: AblationType, sampling_rate: f32) -> Self {
        Self {
            cell_memories: match ablation {
                AblationType::Cell => vec![None; n],
                _ => (0..n).map(|_| Some(VecDeque::with_capacity(100))).collect(),
            },
            lineage_memories: match ablation {
                AblationType::Lineage => vec![None; n],
                _ => (0..n).map(|_| Some((0.0, 0))).collect(),
            },
            archive: Vec::new(),
            ablation,
            sampling_rate,
        }
    }
    
    pub fn cell_tick(&mut self, agent_id: usize, tick: usize) {
        if matches!(self.ablation, AblationType::Cell) { return; }
        if let Some(Some(mem)) = self.cell_memories.get_mut(agent_id) {
            mem.push_back((tick, 1.0));
            if mem.len() > 100 { mem.pop_front(); }
        }
    }
    
    pub fn on_reproduction(&mut self, parent_id: usize, child_id: usize) {
        if matches!(self.ablation, AblationType::Lineage) { return; }
        
        let parent_bias = self.lineage_memories.get(parent_id)
            .and_then(|m| m.as_ref())
            .map(|(b, _)| *b)
            .unwrap_or(0.0);
        
        if child_id >= self.lineage_memories.len() {
            self.lineage_memories.resize_with(child_id + 1, || None);
        }
        
        let mut child_bias = parent_bias;
        if fastrand::f32() < MUTATION_RATE {
            child_bias += (fastrand::f32() - 0.5) * 0.1;
            child_bias = child_bias.clamp(-1.0, 1.0);
        }
        
        let gen = self.lineage_memories.get(parent_id)
            .and_then(|m| m.as_ref())
            .map(|(_, g)| g + 1)
            .unwrap_or(0);
        
        self.lineage_memories[child_id] = Some((child_bias, gen));
        
        if !matches!(self.ablation, AblationType::Archive) {
            if fastrand::f32() < self.sampling_rate {
                if let Some((bias, _)) = self.lineage_memories[child_id] {
                    self.lineage_memories[child_id] = Some((bias * 0.9 + 0.3 * 0.1, gen));
                }
            }
        }
    }
    
    pub fn on_death(&mut self, agent_id: usize, tick: usize) {
        if matches!(self.ablation, AblationType::Archive) { return; }
        let recent = self.archive.iter().filter(|(t, _)| *t > tick.saturating_sub(1000)).count();
        if recent < 10 {
            self.archive.push((tick, agent_id));
        }
    }
}

#[derive(Clone, Copy)]
pub struct RunConfig {
    pub ablation: AblationType,
    pub sampling_rate: f32,
    pub seed: u64,
}

impl RunConfig {
    pub fn mve1(seed: u64) -> Self { Self { ablation: AblationType::Cell, sampling_rate: ARCHIVE_SAMPLE_PROB, seed } }
    pub fn mve2(seed: u64) -> Self { Self { ablation: AblationType::Lineage, sampling_rate: ARCHIVE_SAMPLE_PROB, seed } }
    pub fn mve3(seed: u64) -> Self { Self { ablation: AblationType::Archive, sampling_rate: 0.0, seed } }
    pub fn mve4(p: f32, seed: u64) -> Self { Self { ablation: AblationType::None, sampling_rate: p, seed } }
    pub fn baseline(seed: u64) -> Self { Self { ablation: AblationType::None, sampling_rate: ARCHIVE_SAMPLE_PROB, seed } }
}

#[derive(Clone, Debug)]
pub struct Metrics {
    pub tick: usize, pub population: usize, pub avg_cdi: f64, pub avg_ci: f64,
    pub extinct_count: usize, pub avg_cell_memory: f64, pub lineage_count: usize,
    pub archive_count: usize, pub hazard_rate: f64,
}

impl Metrics {
    pub fn csv_header() -> &'static str {
        "generation,population,avg_cdi,avg_ci,extinct_count,avg_cell_memory,lineage_count,archive_count,hazard_rate"
    }
    pub fn to_csv(&self) -> String {
        format!("{},{},{:.4},{:.4},{},{:.2},{},{},{:.4}",
            self.tick, self.population, self.avg_cdi, self.avg_ci, self.extinct_count,
            self.avg_cell_memory, self.lineage_count, self.archive_count, self.hazard_rate)
    }
}

fn run_experiment(config: RunConfig) -> Vec<Metrics> {
    fastrand::seed(config.seed);
    let mut world = GridWorld::new();
    for i in 0..100 { world.spawn_agent((i * 11) % GRID_X, (i * 17) % GRID_Y, (i * 5) % GRID_Z); }
    world.spawn_food_random(100, 60.0);
    
    let mut population = PopulationDynamics::new(PopulationParams::default());
    let mut hazard = HazardRateTracker::new(5000);
    let mut memory = ThreeLayerMemory::new(5000, config.ablation, config.sampling_rate);
    
    let mut history = Vec::new();
    let mut extinct = false;
    
    for tick in (0..MAX_TICKS).step_by(100) {
        population.step(&mut world);
        for _ in 0..population.deaths_this_tick { hazard.record_death(tick); }
        
        for id in 0..world.agents.len() {
            if world.agents.get(id).map(|a| a.alive).unwrap_or(false) {
                memory.cell_tick(id, tick);
            }
        }
        
        let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
        let n = alive.len();
        if n == 0 && !extinct { extinct = true; }
        
        let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
        let ci = compute_condensation_index(&phases);
        let cdi = if n > 0 { alive.iter().map(|a| a.cdi_contribution() as f64).sum::<f64>() / n as f64 } else { 0.0 };
        
        let cell_mem = if matches!(config.ablation, AblationType::Cell) { 0.0 }
            else { memory.cell_memories.iter().filter_map(|m| m.as_ref()).map(|m| m.len()).sum::<usize>() as f64 / memory.cell_memories.iter().filter(|m| m.is_some()).count().max(1) as f64 };
        
        let lineage_count = if matches!(config.ablation, AblationType::Lineage) { 0 }
            else { memory.lineage_memories.iter().filter(|m| m.is_some()).count() };
        
        history.push(Metrics {
            tick, population: n, avg_cdi: cdi, avg_ci: ci,
            extinct_count: if extinct { 1 } else { 0 }, avg_cell_memory: cell_mem,
            lineage_count, archive_count: memory.archive.len(), hazard_rate: hazard.hazard_rate(),
        });
        
        world.step();
    }
    history
}

fn run_mve(name: &str, config_fn: fn(u64) -> RunConfig, seeds: &[u64]) -> Vec<Vec<Metrics>> {
    println!("\n{}", "=".repeat(60));
    println!("MVE: {} ({} seeds)", name, seeds.len());
    println!("{}", "=".repeat(60));
    
    let start = Instant::now();
    let mut results = Vec::new();
    
    for (i, seed) in seeds.iter().enumerate() {
        let history = run_experiment(config_fn(*seed));
        if let Some(last) = history.last() {
            println!("  Seed {}/{}: N={} at tick {}, extinct={}", i + 1, seeds.len(), last.population, history.len() * 100, last.extinct_count);
        }
        results.push(history);
    }
    
    println!("  Completed in {:.1}s", start.elapsed().as_secs_f64());
    results
}

fn export(name: &str, runs: &[Vec<Metrics>]) {
    let filename = format!("/tmp/mve_{}.csv", name.to_lowercase().replace(" ", "_"));
    let mut file = File::create(&filename).unwrap();
    writeln!(file, "{}", Metrics::csv_header()).unwrap();
    for (i, run) in runs.iter().enumerate() {
        for m in run { writeln!(file, "{},run_{}", m.to_csv(), i).unwrap(); }
    }
    println!("  Exported: {}", filename);
}

fn summarize(name: &str, runs: &[Vec<Metrics>]) {
    let final_pops: Vec<usize> = runs.iter().filter_map(|r| r.last().map(|m| m.population)).collect();
    let extinct = runs.iter().filter(|r| r.last().map(|m| m.population == 0).unwrap_or(false)).count();
    let mean_pop = if !final_pops.is_empty() { final_pops.iter().sum::<usize>() as f64 / final_pops.len() as f64 } else { 0.0 };
    let min_cdi: Vec<f64> = runs.iter().filter_map(|r| r.iter().map(|m| m.avg_cdi).min_by(|a, b| a.partial_cmp(b).unwrap())).collect();
    let mean_min_cdi = if !min_cdi.is_empty() { min_cdi.iter().sum::<f64>() / min_cdi.len() as f64 } else { 0.0 };
    
    println!("  [Summary] Mean N={:.0}, Extinct={}/{} ({:.0}%), Mean min CDI={:.3}",
        mean_pop, extinct, runs.len(), extinct as f64 / runs.len() as f64 * 100.0, mean_min_cdi);
}

fn main() {
    println!("v19 Memory Production: 5 MVEs\n");
    let seeds: Vec<u64> = (0..N_SEEDS as u64).map(|i| 1000 + i).collect();
    
    // MVE-1: Cell Ablation
    let mve1 = run_mve("Cell Ablation", RunConfig::mve1, &seeds);
    export("cell_ablation", &mve1);
    summarize("Cell Ablation", &mve1);
    
    // MVE-2: Lineage Ablation
    let mve2 = run_mve("Lineage Ablation", RunConfig::mve2, &seeds);
    export("lineage_ablation", &mve2);
    summarize("Lineage Ablation", &mve2);
    
    // MVE-3: Archive Disconnect
    let mve3 = run_mve("Archive Disconnect", RunConfig::mve3, &seeds);
    export("archive_disconnect", &mve3);
    summarize("Archive Disconnect", &mve3);
    
    // MVE-4: Sampling Dose
    println!("\n{}", "=".repeat(60));
    println!("MVE-4: Sampling Dose");
    println!("{}", "=".repeat(60));
    for p in [0.0f32, 0.01, 0.10] {
        let runs: Vec<Vec<Metrics>> = seeds.iter().map(|s| run_experiment(RunConfig::mve4(p, *s))).collect();
        let mean_pop = runs.iter().filter_map(|r| r.last().map(|m| m.population)).sum::<usize>() as f64 / runs.len() as f64;
        println!("  p={:.2}: mean N={:.0}", p, mean_pop);
        export(&format!("sampling_dose_{:.2}", p), &runs);
    }
    
    // Baseline
    let baseline = run_mve("Baseline", RunConfig::baseline, &seeds);
    export("baseline", &baseline);
    summarize("Baseline", &baseline);
    
    println!("\nComplete. Output in /tmp/mve_*.csv");
}
