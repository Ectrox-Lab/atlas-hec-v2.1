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

/// Run single trial
pub fn run_trial(
    condition: Condition,
    trial_id: usize,
    duration: usize,
    perturbation_time: usize,
) -> TrialResult {
    // Create mesh
    let mut mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 1.0, 1.0, 4, 4);
    let initial_centroid = mesh.centroid();
    
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
    let mut prediction_errors = Vec::new();
    let mut recovery_tick: Option<usize> = None;
    let perturbation_magnitude = 20.0;  // Reduced from 100
    
    // Run simulation
    for tick in 0..duration {
        // Apply perturbation at perturbation_time
        if tick == perturbation_time {
            // Push the mesh
            for node in &mut mesh.nodes {
                if !node.fixed {
                    node.vel += Vector2::new(perturbation_magnitude, 0.0);
                }
            }
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
        let volume = ((max.x - min.x) * (max.y - min.y)).max(0.0001);  // Min floor
        volumes.push(volume);
        centroid_positions.push(mesh.centroid());
        
        // Check recovery
        if tick > perturbation_time {
            let drift = (mesh.centroid() - initial_centroid).norm();
            if drift < 0.1 && recovery_tick.is_none() {
                recovery_tick = Some(tick - perturbation_time);
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

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_single_trial() {
        let result = run_trial(Condition::PredictiveFeedback, 0, 100, 50);
        assert!(result.stability_score >= 0.0 && result.stability_score <= 1.0);
    }
}
