//! V19 Experiment Runner - EXP-1/2/3 for Bio-World v19 × Superbrain
//! 
//! Replaces stub simulation with real v19 core:
//! - GridWorld (50×50×16)
//! - PopulationDynamics  
//! - StateVector [CDI, CI, r, N, E, h]
//! - HazardRateTracker

use bio_world_v19::{
    GridWorld, PopulationDynamics, PopulationParams,
    StateVector, compute_sync_order_parameter, compute_condensation_index, compute_percolation_ratio,
    HazardRateTracker, MultiUniverseHazard,
    GRID_X, GRID_Y, GRID_Z,
};
use std::collections::HashMap;

/// Experiment types (EXP-1/2/3)
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExperimentV19 {
    /// EXP-1: Condensation Test - CI early warning validation
    CondensationTest,
    /// EXP-2: Synchronization Stress - r vs hazard causality  
    SyncStress,
    /// EXP-3: Hub Knockout - Network resilience test
    HubKnockout,
}

impl ExperimentV19 {
    pub fn name(&self) -> &'static str {
        match self {
            ExperimentV19::CondensationTest => "EXP-1-Condensation",
            ExperimentV19::SyncStress => "EXP-2-Sync-Stress",
            ExperimentV19::HubKnockout => "EXP-3-Hub-Knockout",
        }
    }
}

/// Experiment configuration
pub struct V19Config {
    pub grid_size: (usize, usize, usize),
    pub max_generations: usize,
    pub initial_population: usize,
    pub seed: u64,
    // EXP-2 specific
    pub sync_coupling: f64,
    // EXP-3 specific
    pub knockout_fraction: f64,
    pub knockout_generation: usize,
}

impl V19Config {
    /// Standard v19 configuration
    pub fn standard() -> Self {
        Self {
            grid_size: (GRID_X, GRID_Y, GRID_Z),
            max_generations: 500,
            initial_population: 1000,
            seed: 42,
            sync_coupling: 0.5,
            knockout_fraction: 0.05,
            knockout_generation: 100,
        }
    }
    
    /// EXP-2: High sync coupling
    pub fn high_sync() -> Self {
        let mut cfg = Self::standard();
        cfg.sync_coupling = 0.9;
        cfg
    }
    
    /// EXP-3: Hub knockout config
    pub fn knockout() -> Self {
        Self::standard()
    }
}

/// Unified state record for system_state.csv
#[derive(Clone, Debug)]
pub struct StateRecord {
    pub generation: usize,
    pub n: usize,              // Population
    pub cdi: f64,             // Complexity-Diversity Index
    pub ci: f64,              // Condensation Index
    pub r: f64,               // Sync order parameter
    pub p: f64,               // Percolation ratio
    pub e: f64,               // Energy/activity
    pub h: f64,               // Hazard rate
    pub extinct_count: usize,
    pub alive_universes: usize,
}

/// Experiment result
#[derive(Clone, Debug)]
pub struct V19Result {
    pub experiment: String,
    pub success: bool,
    pub state_history: Vec<StateRecord>,
    pub metrics: ExperimentMetrics,
    pub notes: String,
}

/// Per-experiment metrics
#[derive(Clone, Debug, Default)]
pub struct ExperimentMetrics {
    // EXP-1: Condensation
    pub ci_lead_time: Option<usize>,
    pub ci_cdi_correlation: Option<f64>,
    // EXP-2: Sync stress
    pub r_hazard_correlation: Option<f64>,
    pub sync_fragility_score: Option<f64>,
    // EXP-3: Hub knockout
    pub recovery_time: Option<usize>,
    pub final_extinct_rate: Option<f64>,
    pub cdi_stability: Option<f64>,
}

/// Run single experiment
pub fn run_experiment(exp: ExperimentV19, config: &V19Config) -> V19Result {
    println!("Running {}...", exp.name());
    
    let mut world = GridWorld::new(config.seed);
    let mut population = PopulationDynamics::new(
        config.initial_population,
        PopulationParams::default()
    );
    let mut hazard_tracker = HazardRateTracker::new(100);
    
    let mut state_history = Vec::new();
    let mut extinct_count = 0;
    
    // Run simulation
    for gen in 0..config.max_generations {
        // Update population
        population.step(&mut world);
        
        // Apply experiment-specific interventions
        match exp {
            ExperimentV19::SyncStress => {
                // EXP-2: Adjust sync coupling
                population.set_sync_coupling(config.sync_coupling);
            }
            ExperimentV19::HubKnockout if gen == config.knockout_generation => {
                // EXP-3: Remove top connectivity agents
                population.remove_top_agents(config.knockout_fraction);
            }
            _ => {}
        }
        
        // Check extinction
        if population.is_extinct() {
            extinct_count += 1;
            if extinct_count >= 10 {
                break; // Early stop if too many extinctions
            }
        }
        
        // Compute metrics every 10 generations
        if gen % 10 == 0 {
            let agents = population.get_agents();
            let n = agents.len();
            
            // Core metrics
            let cdi = population.compute_cdi();
            let ci = compute_condensation_index(&agents);
            let r = compute_sync_order_parameter(&agents, config.sync_coupling);
            let p = compute_percolation_ratio(&world, &agents);
            
            // Energy estimate
            let e = population.compute_total_energy();
            
            // Hazard rate
            let h = hazard_tracker.update(&agents, cdi, ci, r);
            
            state_history.push(StateRecord {
                generation: gen,
                n,
                cdi,
                ci,
                r,
                p,
                e,
                h,
                extinct_count,
                alive_universes: if n > 0 { 1 } else { 0 },
            });
        }
    }
    
    // Compute experiment-specific metrics
    let metrics = compute_experiment_metrics(exp, &state_history);
    
    // Determine success
    let success = check_success_criteria(exp, &metrics);
    
    V19Result {
        experiment: exp.name().to_string(),
        success,
        state_history,
        metrics,
        notes: format!("Completed {} generations", config.max_generations),
    }
}

/// Run all three experiments
pub fn run_exp123() -> HashMap<String, V19Result> {
    let mut results = HashMap::new();
    
    // EXP-1: Condensation Test
    let exp1 = run_experiment(ExperimentV19::CondensationTest, &V19Config::standard());
    results.insert(exp1.experiment.clone(), exp1);
    
    // EXP-2: Sync Stress (standard vs high sync)
    let exp2_standard = run_experiment(ExperimentV19::SyncStress, &V19Config::standard());
    results.insert(format!("{}-standard", exp2_standard.experiment), exp2_standard);
    
    let exp2_high = run_experiment(ExperimentV19::SyncStress, &V19Config::high_sync());
    results.insert(format!("{}-high", exp2_high.experiment), exp2_high);
    
    // EXP-3: Hub Knockout
    let exp3 = run_experiment(ExperimentV19::HubKnockout, &V19Config::knockout());
    results.insert(exp3.experiment.clone(), exp3);
    
    results
}

/// Compute experiment-specific metrics
fn compute_experiment_metrics(exp: ExperimentV19, history: &[StateRecord]) -> ExperimentMetrics {
    let mut metrics = ExperimentMetrics::default();
    
    match exp {
        ExperimentV19::CondensationTest => {
            // EXP-1: CI lead time and correlation with 1/CDI
            if let Some((lead_time, corr)) = compute_ci_metrics(history) {
                metrics.ci_lead_time = Some(lead_time);
                metrics.ci_cdi_correlation = Some(corr);
            }
        }
        ExperimentV19::SyncStress => {
            // EXP-2: r vs hazard correlation
            if let Some(corr) = compute_r_hazard_correlation(history) {
                metrics.r_hazard_correlation = Some(corr);
                metrics.sync_fragility_score = Some(corr * 100.0);
            }
        }
        ExperimentV19::HubKnockout => {
            // EXP-3: Recovery metrics
            if let Some((recovery, final_extinct, cdi_stab)) = compute_knockout_metrics(history) {
                metrics.recovery_time = Some(recovery);
                metrics.final_extinct_rate = Some(final_extinct);
                metrics.cdi_stability = Some(cdi_stab);
            }
        }
    }
    
    metrics
}

/// Check success criteria per experiment
fn check_success_criteria(exp: ExperimentV19, metrics: &ExperimentMetrics) -> bool {
    match exp {
        ExperimentV19::CondensationTest => {
            // EXP-1: CI lead time > 100, Correlation > 0.7
            metrics.ci_lead_time.map(|t| t > 100).unwrap_or(false)
                && metrics.ci_cdi_correlation.map(|c| c > 0.7).unwrap_or(false)
        }
        ExperimentV19::SyncStress => {
            // EXP-2: Measurable correlation
            metrics.r_hazard_correlation.map(|c| c.abs() > 0.3).unwrap_or(false)
        }
        ExperimentV19::HubKnockout => {
            // EXP-3: System shows resilience (recovery or controlled collapse)
            metrics.final_extinct_rate.map(|r| r < 0.5).unwrap_or(false)
        }
    }
}

// Helper metric functions
fn compute_ci_metrics(history: &[StateRecord]) -> Option<(usize, f64)> {
    if history.len() < 10 {
        return None;
    }
    
    // Find when CI starts rising before collapse
    let collapse_point = history.iter()
        .position(|s| s.n < 100)?;
    
    let ci_rise_point = history[..collapse_point].iter()
        .rposition(|s| s.ci > 0.5)?;
    
    let lead_time = collapse_point - ci_rise_point;
    
    // Correlation with 1/CDI
    let cdi_inv: Vec<f64> = history.iter()
        .map(|s| if s.cdi > 0.0 { 1.0 / s.cdi } else { 0.0 })
        .collect();
    let cis: Vec<f64> = history.iter().map(|s| s.ci).collect();
    
    let corr = pearson_correlation(&cdi_inv, &cis)?;
    
    Some((lead_time * 10, corr)) // Multiply by sampling interval
}

fn compute_r_hazard_correlation(history: &[StateRecord]) -> Option<f64> {
    let rs: Vec<f64> = history.iter().map(|s| s.r).collect();
    let hs: Vec<f64> = history.iter().map(|s| s.h).collect();
    pearson_correlation(&rs, &hs)
}

fn compute_knockout_metrics(history: &[StateRecord]) -> Option<(usize, f64, f64)> {
    let knockout_gen = 100;
    let post_knockout: Vec<_> = history.iter()
        .filter(|s| s.generation >= knockout_gen)
        .collect();
    
    if post_knockout.is_empty() {
        return None;
    }
    
    // Recovery time: when population stabilizes
    let recovery = post_knockout.iter()
        .position(|s| s.n > 500)
        .map(|p| p * 10)
        .unwrap_or(0);
    
    // Final extinction rate
    let final_extinct = if post_knockout.last()?.n == 0 { 1.0 } else { 0.0 };
    
    // CDI stability (coefficient of variation)
    let cdi_values: Vec<f64> = post_knockout.iter().map(|s| s.cdi).collect();
    let cdi_mean = cdi_values.iter().sum::<f64>() / cdi_values.len() as f64;
    let cdi_var = cdi_values.iter()
        .map(|v| (v - cdi_mean).powi(2))
        .sum::<f64>() / cdi_values.len() as f64;
    let cdi_cv = cdi_var.sqrt() / cdi_mean;
    
    Some((recovery, final_extinct, cdi_cv))
}

fn pearson_correlation(x: &[f64], y: &[f64]) -> Option<f64> {
    if x.len() != y.len() || x.len() < 2 {
        return None;
    }
    
    let n = x.len() as f64;
    let mean_x = x.iter().sum::<f64>() / n;
    let mean_y = y.iter().sum::<f64>() / n;
    
    let num: f64 = x.iter().zip(y.iter())
        .map(|(xi, yi)| (xi - mean_x) * (yi - mean_y))
        .sum();
    
    let den_x: f64 = x.iter().map(|xi| (xi - mean_x).powi(2)).sum();
    let den_y: f64 = y.iter().map(|yi| (yi - mean_y).powi(2)).sum();
    
    let den = (den_x * den_y).sqrt();
    
    if den > 0.0 {
        Some(num / den)
    } else {
        None
    }
}

/// Export state history to CSV format
pub fn export_to_csv(history: &[StateRecord]) -> String {
    let mut csv = String::from("generation,N,CDI,CI,r,P,E,h,extinct_count,alive_universes\n");
    
    for record in history {
        csv.push_str(&format!(
            "{},{},{:.6},{:.6},{:.6},{:.6},{:.6},{:.6},{},{}\n",
            record.generation,
            record.n,
            record.cdi,
            record.ci,
            record.r,
            record.p,
            record.e,
            record.h,
            record.extinct_count,
            record.alive_universes
        ));
    }
    
    csv
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn exp123_runs() {
        let results = run_exp123();
        assert_eq!(results.len(), 4); // EXP-1, EXP-2×2, EXP-3
        
        // Check EXP-1
        let exp1 = results.get("EXP-1-Condensation").expect("EXP-1 result");
        println!("EXP-1: CI lead time = {:?}, correlation = {:?}", 
            exp1.metrics.ci_lead_time, exp1.metrics.ci_cdi_correlation);
    }
}
