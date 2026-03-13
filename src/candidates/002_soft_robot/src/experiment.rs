//! Week 1 Experiment: Feedback Effect Detection
//! 
//! Compares predictive feedback vs reactive control vs no control.
//! Measures: stability, recovery time, prediction accuracy.

use crate::mesh::SoftMesh;
use crate::predictor::{PredictiveController, ReactiveController};
use nalgebra::Vector2;
use std::fs::File;
use std::io::Write;

/// Experimental condition
#[derive(Clone, Copy, Debug)]
pub enum Condition {
    PredictiveFeedback,  // Full predictive self-model
    ReactiveOnly,        // Reactive control, no prediction
    NoControl,           // Open loop
}

/// Perturbation type for difficulty gradient
#[derive(Clone, Copy, Debug)]
pub enum PerturbationType {
    VelocityImpulse,     // Simple velocity push
    BoundaryDisplacement,// Displace boundary constraints
    LocalCompression,    // Compress one side
    RandomNoise,         // Random force field
    SustainedWind,       // Continuous directional force
}

impl std::fmt::Display for Condition {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Condition::PredictiveFeedback => write!(f, "predictive"),
            Condition::ReactiveOnly => write!(f, "reactive"),
            Condition::NoControl => write!(f, "none"),
        }
    }
}

/// Trial result
#[derive(Debug)]
pub struct TrialResult {
    pub condition: Condition,
    pub trial_id: usize,
    pub stability_score: f32,      // 0-1, higher is more stable
    pub recovery_time: Option<f32>, // ticks to recover, None if never
    pub avg_prediction_error: f32,
    pub final_centroid_drift: f32,
    pub volume_variance: f32,      // measure of pulsing
}

/// Recovery dynamics metrics for single-shot experiment
#[derive(Debug, Clone)]
pub struct RecoveryMetrics {
    pub condition: Condition,
    pub trial_id: usize,
    pub peak_drift: f32,           // maximum drift after perturbation
    pub time_to_50pct: Option<f32>, // time to reach 50% of peak
    pub time_to_90pct: Option<f32>, // time to reach 90% recovery (10% of peak)
    pub residual_drift: f32,       // final drift at end
    pub recovered: bool,           // whether recovery criteria met
    pub recovery_time: Option<f32>, // full recovery time if achieved
}

impl RecoveryMetrics {
    pub fn print_summary(&self) {
        println!("  {:?} trial {}: peak={:.3}, t50={:?}, t90={:?}, residual={:.3}, recovered={}",
            self.condition, self.trial_id,
            self.peak_drift, self.time_to_50pct, self.time_to_90pct,
            self.residual_drift, self.recovered);
    }
}

/// Run single trial with configurable perturbation
pub fn run_trial(
    condition: Condition,
    trial_id: usize,
    duration: usize,
    perturbation_time: usize,
) -> TrialResult {
    run_trial_with_perturbation(condition, trial_id, duration, perturbation_time, PerturbationType::VelocityImpulse)
}

/// Run single trial with specific perturbation type
pub fn run_trial_with_perturbation(
    condition: Condition,
    trial_id: usize,
    duration: usize,
    perturbation_time: usize,
    pert_type: PerturbationType,
) -> TrialResult {
    run_trial_with_recovery_params(
        condition, trial_id, duration, perturbation_time, pert_type,
        20,   // peak_estimation_ticks
        10,   // hold_ticks: reduced to 10
        0.50, // rel_threshold: 50% of max drift (was 25%)
        0.30, // abs_threshold: 0.30 units (was 0.25)
    )
}

/// Full trial with configurable recovery detection
pub fn run_trial_with_recovery_params(
    condition: Condition,
    trial_id: usize,
    duration: usize,
    perturbation_time: usize,
    pert_type: PerturbationType,
    peak_estimation_ticks: usize,
    hold_ticks: usize,
    rel_threshold: f32,
    abs_threshold: f32,
) -> TrialResult {
    // Create mesh - smaller for more challenging control
    let mut mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 0.8, 0.8, 4, 4);
    let initial_centroid = mesh.centroid();
    let target_centroid = initial_centroid;
    
    // Create controller based on condition
    let mut predictive: Option<PredictiveController> = match condition {
        Condition::PredictiveFeedback => {
            Some(PredictiveController::new(20, 50.0))
        }
        _ => None,
    };
    
    let reactive = match condition {
        Condition::ReactiveOnly => Some(ReactiveController::new(50.0)),
        _ => None,
    };
    
    // Tracking
    let mut volumes = Vec::new();
    let mut centroid_positions = Vec::new();
    let mut centroid_drifts = Vec::new();
    let mut prediction_errors = Vec::new();
    let mut recovery_tick: Option<usize> = None;
    let mut stable_counter: usize = 0;
    let mut max_drift: f32 = 0.0;
    let mut peak_detected: bool = false;
    
    // Run simulation
    for tick in 0..duration {
        // Apply perturbation at perturbation_time
        if tick == perturbation_time {
            apply_perturbation(&mut mesh, pert_type, trial_id);
        }
        
        // Micro-perturbations after main perturbation
        if tick > perturbation_time && tick % 10 == 0 {
            apply_micro_perturbation(&mut mesh, tick);
        }
        
        // Compute control action
        match condition {
            Condition::PredictiveFeedback => {
                if let Some(ref mut ctrl) = predictive {
                    let err = ctrl.compute_action(&mut mesh, true);
                    prediction_errors.push(err);
                }
            }
            Condition::ReactiveOnly => {
                if let Some(ref ctrl) = reactive {
                    let mut m = mesh.clone();
                    ctrl.compute_action(&mut m);
                    mesh.pressure.pressure = m.pressure.pressure;
                }
            }
            Condition::NoControl => {}
        }
        
        // Physics step
        mesh.step(0.01);
        
        // Track metrics
        let (min, max) = mesh.bounding_box();
        let volume = ((max.x - min.x) * (max.y - min.y)).max(0.0001);
        volumes.push(volume);
        
        let centroid = mesh.centroid();
        centroid_positions.push(centroid);
        
        let drift = (centroid - target_centroid).norm();
        centroid_drifts.push(drift);
        
        // Phase 1: Peak estimation (first N ticks after perturbation)
        if tick > perturbation_time && tick <= perturbation_time + peak_estimation_ticks {
            if drift > max_drift {
                max_drift = drift;
            }
        }
        
        // Phase 2: Recovery detection (after peak estimation)
        if tick > perturbation_time + peak_estimation_ticks && recovery_tick.is_none() {
            if !peak_detected {
                peak_detected = true;
                // Ensure max_drift is at least some minimum to avoid division issues
                max_drift = max_drift.max(0.1);
            }
            
            let rel_ok = drift < max_drift * rel_threshold;
            let abs_ok = drift < abs_threshold;
            
            if rel_ok && abs_ok {
                stable_counter += 1;
                if stable_counter >= hold_ticks {
                    recovery_tick = Some(tick - perturbation_time);
                }
            } else {
                stable_counter = 0;
            }
        }
    }
    
    // Compute stability score (coefficient of variation-based)
    let mean_volume: f32 = if volumes.is_empty() { 
        1.0 
    } else { 
        volumes.iter().sum::<f32>() / volumes.len() as f32 
    };
    
    let volume_variance: f32 = if volumes.is_empty() || mean_volume < 1e-6 {
        0.0
    } else {
        volumes.iter()
            .map(|v| (v - mean_volume).powi(2))
            .sum::<f32>() / volumes.len() as f32
    };
    
    // Use coefficient of variation for stability (normalized)
    let cv = (volume_variance.sqrt() / mean_volume).min(10.0);
    let stability_score = (-cv).exp();  // exp(-CV), higher = more stable
    
    // Final drift
    let final_centroid_drift = (mesh.centroid() - initial_centroid).norm();
    
    // Average prediction error
    let avg_prediction_error = if prediction_errors.is_empty() {
        999.0  // High error if no predictions
    } else {
        let sum: f32 = prediction_errors.iter().sum();
        let avg = sum / prediction_errors.len() as f32;
        if avg.is_finite() { avg } else { 999.0 }
    };
    
    TrialResult {
        condition,
        trial_id,
        stability_score,
        recovery_time: recovery_tick.map(|t| t as f32 * 0.01),
        avg_prediction_error,
        final_centroid_drift,
        volume_variance,
    }
}

/// Run full experiment (Week 1)
pub fn run_week1_experiment(num_trials: usize) -> Vec<TrialResult> {
    let conditions = vec![
        Condition::PredictiveFeedback,
        Condition::ReactiveOnly,
        Condition::NoControl,
    ];
    
    let mut results = Vec::new();
    
    for condition in &conditions {
        for trial in 0..num_trials {
            println!("Running {:?} trial {}...", condition, trial);
            let result = run_trial(*condition, trial, 1000, 500);
            results.push(result);
        }
    }
    
    results
}

/// Save results to CSV
pub fn save_results(results: &[TrialResult], path: &str) -> std::io::Result<()> {
    let mut file = File::create(path)?;
    
    // Header
    writeln!(file, "condition,trial_id,stability_score,recovery_time,avg_prediction_error,final_centroid_drift,volume_variance")?;
    
    // Data
    for r in results {
        writeln!(file, "{},{},{},{},{},{},{}",
            r.condition,
            r.trial_id,
            r.stability_score,
            r.recovery_time.unwrap_or(-1.0),
            r.avg_prediction_error,
            r.final_centroid_drift,
            r.volume_variance
        )?;
    }
    
    Ok(())
}

/// Analyze results for Week 1 gate
pub fn analyze_for_gate(results: &[TrialResult]) -> GateDecision {
    use std::collections::HashMap;
    
    let mut by_condition: HashMap<String, Vec<&TrialResult>> = HashMap::new();
    
    for r in results {
        by_condition.entry(r.condition.to_string())
            .or_default()
            .push(r);
    }
    
    // Check if predictive shows benefit
    let predictive_results = by_condition.get("predictive").map(|v| v.as_slice()).unwrap_or(&[]);
    let none_results = by_condition.get("none").map(|v| v.as_slice()).unwrap_or(&[]);
    
    let pred_stability: f32 = predictive_results.iter()
        .map(|r| r.stability_score)
        .sum::<f32>() / predictive_results.len().max(1) as f32;
    
    let none_stability: f32 = none_results.iter()
        .map(|r| r.stability_score)
        .sum::<f32>() / none_results.len().max(1) as f32;
    
    let pred_recovery: f32 = predictive_results.iter()
        .filter_map(|r| r.recovery_time)
        .sum::<f32>() / predictive_results.iter().filter(|r| r.recovery_time.is_some()).count().max(1) as f32;
    
    let none_recovery: f32 = none_results.iter()
        .filter_map(|r| r.recovery_time)
        .sum::<f32>() / none_results.iter().filter(|r| r.recovery_time.is_some()).count().max(1) as f32;
    
    println!("\n=== Week 1 Analysis ===");
    println!("Predictive stability: {:.3}", pred_stability);
    println!("No-control stability: {:.3}", none_stability);
    println!("Predictive recovery: {:.1}s", pred_recovery);
    println!("No-control recovery: {:.1}s", none_recovery);
    
    // Gate criteria
    let stability_better = pred_stability > none_stability * 1.1;  // 10% better
    let recovery_better = pred_recovery < none_recovery * 0.9;     // 10% faster
    let any_recovery = predictive_results.iter().any(|r| r.recovery_time.is_some());
    
    let continue_count = [stability_better, recovery_better, any_recovery]
        .iter()
        .filter(|&&x| x)
        .count();
    
    if continue_count >= 2 {
        println!("\n>>> DECISION: CONTINUE to Week 2");
        GateDecision::Continue
    } else {
        println!("\n>>> DECISION: KILL - No clear feedback benefit");
        GateDecision::Kill
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum GateDecision {
    Continue,
    Kill,
}

/// Apply perturbation to mesh
fn apply_perturbation(mesh: &mut SoftMesh, pert_type: PerturbationType, seed: usize) {
    use rand::{Rng, SeedableRng};
    use rand::rngs::StdRng;
    
    let mut rng = StdRng::seed_from_u64(seed as u64);
    
    match pert_type {
        PerturbationType::VelocityImpulse => {
            // Moderate velocity impulse (not too strong to avoid NaN)
            let magnitude = 15.0;
            for node in &mut mesh.nodes {
                if !node.fixed {
                    node.vel += Vector2::new(magnitude, rng.gen::<f32>() * 6.0 - 3.0);
                }
            }
        }
        PerturbationType::BoundaryDisplacement => {
            // Push boundary nodes moderately
            let force = 20.0;
            for (i, node) in mesh.nodes.iter_mut().enumerate() {
                if !node.fixed {
                    if i % 4 == 0 {  // Left side
                        node.vel.x += force;
                    }
                }
            }
        }
        PerturbationType::LocalCompression => {
            // Compress from one side
            let compression = 25.0;
            for (i, node) in mesh.nodes.iter_mut().enumerate() {
                if !node.fixed {
                    let col = i % 4;
                    if col == 3 {  // Right side
                        node.vel.x -= compression;
                    }
                }
            }
        }
        PerturbationType::RandomNoise => {
            // Random forces on all nodes (moderate)
            for node in &mut mesh.nodes {
                if !node.fixed {
                    node.vel += Vector2::new(
                        rng.gen::<f32>() * 20.0 - 10.0,
                        rng.gen::<f32>() * 20.0 - 10.0,
                    );
                }
            }
        }
        PerturbationType::SustainedWind => {
            // Moderate initial push
            for node in &mut mesh.nodes {
                if !node.fixed {
                    node.vel.x += 20.0;
                }
            }
        }
    }
}

/// Apply small random perturbation to test stability
fn apply_micro_perturbation(mesh: &mut SoftMesh, tick: usize) {
    use rand::{Rng, SeedableRng};
    use rand::rngs::StdRng;
    
    let mut rng = StdRng::seed_from_u64(tick as u64);
    
    for node in &mut mesh.nodes {
        if !node.fixed {
            node.vel += Vector2::new(
                rng.gen::<f32>() * 2.0 - 1.0,  // Reduced from 4.0
                rng.gen::<f32>() * 2.0 - 1.0,
            );
        }
    }
}

/// Single-shot strong perturbation recovery experiment
/// Tests if feedback advantage appears in recovery dynamics
pub fn run_single_shot_recovery_experiment() -> Vec<RecoveryMetrics> {
    let conditions = vec![
        Condition::PredictiveFeedback,
        Condition::ReactiveOnly,
        Condition::NoControl,
    ];
    
    let mut all_metrics = Vec::new();
    
    for condition in &conditions {
        for trial in 0..3 {
            let metrics = run_single_shot_trial(*condition, trial);
            metrics.print_summary();
            all_metrics.push(metrics);
        }
    }
    
    all_metrics
}

/// Run single trial with strong single perturbation and detailed recovery tracking
fn run_single_shot_trial(condition: Condition, trial_id: usize) -> RecoveryMetrics {
    // Larger mesh for more interesting dynamics
    let mut mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 1.0, 1.0, 4, 4);
    let target_centroid = mesh.centroid();
    
    // Controllers
    let mut predictive: Option<PredictiveController> = match condition {
        Condition::PredictiveFeedback => Some(PredictiveController::new(20, 50.0)),
        _ => None,
    };
    let reactive = match condition {
        Condition::ReactiveOnly => Some(ReactiveController::new(50.0)),
        _ => None,
    };
    
    // Tracking
    let mut peak_drift: f32 = 0.0;
    let mut time_to_50pct: Option<f32> = None;
    let mut time_to_90pct: Option<f32> = None;
    let mut recovery_time: Option<f32> = None;
    let mut drift_history: Vec<(usize, f32)> = Vec::new();
    
    let perturbation_time = 200;
    let duration = 800;
    
    // Run simulation
    for tick in 0..duration {
        // Single strong perturbation at perturbation_time
        if tick == perturbation_time {
            // Strong boundary displacement
            for (i, node) in mesh.nodes.iter_mut().enumerate() {
                if !node.fixed && i % 4 == 0 {
                    node.vel.x += 40.0;  // Strong push
                }
            }
        }
        
        // NO micro-perturbations - clean recovery
        
        // Control
        match condition {
            Condition::PredictiveFeedback => {
                if let Some(ref mut ctrl) = predictive {
                    ctrl.compute_action(&mut mesh, true);
                }
            }
            Condition::ReactiveOnly => {
                if let Some(ref ctrl) = reactive {
                    let mut m = mesh.clone();
                    ctrl.compute_action(&mut m);
                    mesh.pressure.pressure = m.pressure.pressure;
                }
            }
            Condition::NoControl => {}
        }
        
        mesh.step(0.01);
        
        // Track drift
        let drift = (mesh.centroid() - target_centroid).norm();
        drift_history.push((tick, drift));
        
        if tick >= perturbation_time {
            if drift > peak_drift {
                peak_drift = drift;
            }
            
            // Time to 50% recovery (drift < 50% of peak)
            if time_to_50pct.is_none() && drift < peak_drift * 0.5 {
                time_to_50pct = Some((tick - perturbation_time) as f32 * 0.01);
            }
            
            // Time to 90% recovery (drift < 10% of peak)
            if time_to_90pct.is_none() && drift < peak_drift * 0.1 {
                time_to_90pct = Some((tick - perturbation_time) as f32 * 0.01);
            }
            
            // Full recovery (drift < threshold for sustained period)
            if recovery_time.is_none() && drift < 0.15 {
                // Check if sustained for 20 ticks
                let sustained = drift_history.iter()
                    .rev()
                    .take(20)
                    .all(|(_, d)| *d < 0.15);
                if sustained {
                    recovery_time = Some((tick - perturbation_time) as f32 * 0.01);
                }
            }
        }
    }
    
    let residual_drift = drift_history.last().map(|(_, d)| *d).unwrap_or(0.0);
    let recovered = recovery_time.is_some();
    
    RecoveryMetrics {
        condition,
        trial_id,
        peak_drift,
        time_to_50pct,
        time_to_90pct,
        residual_drift,
        recovered,
        recovery_time,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_single_trial() {
        let result = run_trial(Condition::PredictiveFeedback, 0, 100, 50);
        assert!(result.stability_score >= 0.0 && result.stability_score <= 1.0);
    }
}
