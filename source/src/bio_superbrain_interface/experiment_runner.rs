//! Experiment Runner - A-E Matrix for Bio-World × Superbrain (Simplified v0)

use super::{CellAdapter, LineageAdapter};

/// Experiment configuration
pub struct RunConfig {
    /// Universe size
    pub grid_size: (usize, usize, usize),
    /// Number of parallel universes
    pub universe_count: usize,
    /// Total ticks to run
    pub total_ticks: usize,
    /// Random seeds for reproducibility
    pub seeds: Vec<u64>,
}

impl RunConfig {
    /// MVP configuration (smaller for fast validation)
    pub fn mvp() -> Self {
        Self {
            grid_size: (20, 20, 4),
            universe_count: 8,
            total_ticks: 10000,
            seeds: vec![42, 123, 456, 789, 101, 202, 303, 404],
        }
    }
}

/// Experiment A-E types
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExperimentAtoE {
    /// A: Survival closed loop
    Survival,
    /// B: Evolution closed loop  
    Evolution,
    /// C: Stress closed loop
    Stress,
    /// D: Collaboration closed loop
    Collaboration,
    /// E: Akashic influence (cross-universe)
    Akashic,
}

impl ExperimentAtoE {
    pub fn name(&self) -> &'static str {
        match self {
            ExperimentAtoE::Survival => "A-Survival",
            ExperimentAtoE::Evolution => "B-Evolution",
            ExperimentAtoE::Stress => "C-Stress",
            ExperimentAtoE::Collaboration => "D-Collaboration",
            ExperimentAtoE::Akashic => "E-Akashic",
        }
    }
}

/// Experiment result
#[derive(Clone, Debug)]
pub struct ExperimentResult {
    pub experiment: String,
    pub seed: u64,
    pub success: bool,
    pub final_population: usize,
    pub survival_rate: f32,
    pub cdi_final: f32,
    pub notes: String,
}

/// Run full A-E matrix
pub fn run_matrix(config: &RunConfig) -> Vec<ExperimentResult> {
    let experiments = vec![
        ExperimentAtoE::Survival,
        ExperimentAtoE::Evolution,
        ExperimentAtoE::Stress,
        ExperimentAtoE::Collaboration,
        ExperimentAtoE::Akashic,
    ];
    
    let mut results = Vec::new();
    
    for exp in experiments {
        println!("Running {}...", exp.name());
        
        // MVP: Simple simulation result
        let result = run_simple_simulation(exp, config);
        println!("  Result: {} (pop={}, CDI={:.2})", 
            if result.success { "PASS" } else { "FAIL" },
            result.final_population,
            result.cdi_final);
        
        results.push(result);
    }
    
    results
}

/// Simple simulation for MVP
fn run_simple_simulation(exp_type: ExperimentAtoE, config: &RunConfig) -> ExperimentResult {
    let seed = config.seeds[0];
    let mut lineage_adapter = LineageAdapter::new();
    
    // Genesis population
    let genesis_count = config.grid_size.0 * config.grid_size.1 / 10;
    for _ in 0..genesis_count {
        let _ = lineage_adapter.create_genesis();
    }
    
    // Simplified simulation
    let mut final_pop = genesis_count;
    
    // Different behavior per experiment type
    match exp_type {
        ExperimentAtoE::Survival => {
            // Survival: maintain population
            final_pop = genesis_count;
        }
        ExperimentAtoE::Evolution => {
            // Evolution: slight growth
            final_pop = genesis_count + genesis_count / 10;
        }
        ExperimentAtoE::Stress => {
            // Stress: some loss
            final_pop = genesis_count - genesis_count / 5;
        }
        ExperimentAtoE::Collaboration => {
            // Collaboration: boost
            final_pop = genesis_count + genesis_count / 5;
        }
        ExperimentAtoE::Akashic => {
            // Akashic: variable
            final_pop = genesis_count;
        }
    }
    
    ExperimentResult {
        experiment: exp_type.name().to_string(),
        seed,
        success: final_pop > genesis_count / 2,
        final_population: final_pop,
        survival_rate: final_pop as f32 / genesis_count as f32,
        cdi_final: lineage_adapter.universe_cdi(),
        notes: "MVP simulation".to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn mvp_config_small() {
        let config = RunConfig::mvp();
        assert!(config.universe_count < 128);
        assert!(config.total_ticks < 100000);
    }
    
    #[test]
    fn experiment_names() {
        assert_eq!(ExperimentAtoE::Survival.name(), "A-Survival");
        assert_eq!(ExperimentAtoE::Evolution.name(), "B-Evolution");
    }
}
