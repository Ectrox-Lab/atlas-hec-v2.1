//! D4 Semantic Metric Validation for 002
//! 
//! Breaks down aggregate stability into dynamics-aware sub-metrics
//! Tracks: overshoot, settling time, integrated error, smoothness, final deviation

use crate::mesh::SoftMesh;
use crate::predictor::{PredictiveController, ReactiveController};
use crate::experiment::Condition;
use nalgebra::Vector2;
use std::fs::File;
use std::io::Write;

/// Detailed trajectory record for a single trial
#[derive(Debug, Clone)]
pub struct TrajectoryRecord {
    pub tick: usize,
    pub centroid_drift: f32,
    pub volume: f32,
    pub pressure: f32,
    pub velocity_magnitude: f32,
}

/// Dynamics-aware sub-metrics
#[derive(Debug, Clone)]
pub struct DynamicsMetrics {
    // Response characteristics
    pub peak_drift: f32,
    pub overshoot_ratio: f32,
    
    // Timing
    pub time_to_50pct: Option<f32>,
    pub time_to_90pct: Option<f32>,
    pub settling_time: Option<f32>,
    
    // Error/integration
    pub integrated_error: f32,
    pub final_deviation: f32,
    
    // Smoothness
    pub velocity_variance: f32,
    pub jerk_metric: f32,
    
    // Stability
    pub residual_oscillation: f32,
    pub recovery_success: bool,
}

/// Run detailed trajectory collection for 002
pub fn collect_detailed_trajectory(
    condition: Condition,
    trial_id: usize,
    duration: usize,
    perturbation_time: usize,
) -> Vec<TrajectoryRecord> {
    let mut mesh = SoftMesh::new_grid(Vector2::new(0.0, 0.0), 0.8, 0.8, 4, 4);
    let target_centroid = mesh.centroid();
    
    let mut predictive: Option<PredictiveController> = match condition {
        Condition::PredictiveFeedback => Some(PredictiveController::new(20, 50.0)),
        _ => None,
    };
    let reactive = match condition {
        Condition::ReactiveOnly => Some(ReactiveController::new(50.0)),
        _ => None,
    };
    
    let mut records = Vec::new();
    
    for tick in 0..duration {
        // Apply perturbation
        if tick == perturbation_time {
            for node in &mut mesh.nodes {
                if !node.fixed {
                    node.vel.x += 20.0;
                }
            }
        }
        
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
        
        // Record detailed state
        let centroid = mesh.centroid();
        let drift = (centroid - target_centroid).norm();
        let (min, max) = mesh.bounding_box();
        let volume = (max.x - min.x) * (max.y - min.y);
        
        let vel_mag: f32 = mesh.nodes.iter()
            .map(|n| n.vel.norm())
            .sum::<f32>() / mesh.nodes.len() as f32;
        
        records.push(TrajectoryRecord {
            tick,
            centroid_drift: drift,
            volume,
            pressure: mesh.pressure.pressure,
            velocity_magnitude: vel_mag,
        });
    }
    
    records
}

/// Compute dynamics metrics from trajectory
pub fn compute_dynamics_metrics(
    records: &[TrajectoryRecord],
    perturbation_time: usize,
    target_drift: f32,
) -> DynamicsMetrics {
    let post_perturbation = &records[perturbation_time..];
    
    if post_perturbation.is_empty() {
        return DynamicsMetrics {
            peak_drift: 0.0,
            overshoot_ratio: 0.0,
            time_to_50pct: None,
            time_to_90pct: None,
            settling_time: None,
            integrated_error: 0.0,
            final_deviation: 0.0,
            velocity_variance: 0.0,
            jerk_metric: 0.0,
            residual_oscillation: 0.0,
            recovery_success: false,
        };
    }
    
    // Peak and overshoot
    let peak_drift = post_perturbation.iter()
        .map(|r| r.centroid_drift)
        .fold(0.0, f32::max);
    let overshoot_ratio = if target_drift > 0.001 {
        (peak_drift - target_drift) / target_drift
    } else {
        0.0
    };
    
    // Time to recovery thresholds
    let time_to_50pct = post_perturbation.iter()
        .find(|r| r.centroid_drift < peak_drift * 0.5)
        .map(|r| (r.tick - perturbation_time) as f32 * 0.01);
    
    let time_to_90pct = post_perturbation.iter()
        .find(|r| r.centroid_drift < peak_drift * 0.1)
        .map(|r| (r.tick - perturbation_time) as f32 * 0.01);
    
    // Settling time (within 10% of final for 20 ticks)
    let final_drift = records.last().map(|r| r.centroid_drift).unwrap_or(0.0);
    let threshold = final_drift * 1.1;
    let mut settling_time = None;
    
    for window in post_perturbation.windows(20) {
        if window.iter().all(|r| r.centroid_drift < threshold) {
            settling_time = Some((window[0].tick - perturbation_time) as f32 * 0.01);
            break;
        }
    }
    
    // Integrated error
    let integrated_error: f32 = post_perturbation.iter()
        .map(|r| r.centroid_drift)
        .sum::<f32>() * 0.01;  // dt = 0.01
    
    // Velocity variance (smoothness proxy)
    let n = post_perturbation.len() as f32;
    let mean_vel = post_perturbation.iter().map(|r| r.velocity_magnitude).sum::<f32>() / n;
    let velocity_variance = post_perturbation.iter()
        .map(|r| (r.velocity_magnitude - mean_vel).powi(2))
        .sum::<f32>() / n;
    
    // Jerk metric (acceleration of drift)
    let mut jerk_sum = 0.0;
    for i in 2..post_perturbation.len() {
        let a1 = post_perturbation[i-1].centroid_drift - post_perturbation[i-2].centroid_drift;
        let a2 = post_perturbation[i].centroid_drift - post_perturbation[i-1].centroid_drift;
        jerk_sum += (a2 - a1).abs();
    }
    let jerk_metric = if post_perturbation.len() > 2 {
        jerk_sum / (post_perturbation.len() - 2) as f32
    } else {
        0.0
    };
    
    // Residual oscillation (variance in last 50 ticks)
    let last_50 = &records[records.len().saturating_sub(50)..];
    let mean_last = last_50.iter().map(|r| r.centroid_drift).sum::<f32>() / last_50.len() as f32;
    let residual_oscillation = last_50.iter()
        .map(|r| (r.centroid_drift - mean_last).powi(2))
        .sum::<f32>() / last_50.len() as f32;
    
    // Recovery success (settled within reasonable time)
    let recovery_success = settling_time.is_some() && settling_time.unwrap() < 5.0;
    
    DynamicsMetrics {
        peak_drift,
        overshoot_ratio,
        time_to_50pct,
        time_to_90pct,
        settling_time,
        integrated_error,
        final_deviation: final_drift,
        velocity_variance,
        jerk_metric,
        residual_oscillation,
        recovery_success,
    }
}

/// Export trajectory to CSV
pub fn export_trajectory(records: &[TrajectoryRecord], path: &str) -> std::io::Result<()> {
    let mut file = File::create(path)?;
    writeln!(file, "tick,centroid_drift,volume,pressure,velocity_magnitude")?;
    
    for r in records {
        writeln!(file, "{},{},{},{},{}",
            r.tick, r.centroid_drift, r.volume, r.pressure, r.velocity_magnitude)?;
    }
    
    Ok(())
}

/// Main D4 analysis for 002
pub fn run_d4_002_analysis() {
    println!("=== D4: 002 Semantic Metric Validation ===\n");
    println!("Collecting detailed dynamics metrics...\n");
    
    let conditions = vec![
        (Condition::PredictiveFeedback, "predictive"),
        (Condition::ReactiveOnly, "reactive"),
        (Condition::NoControl, "none"),
    ];
    
    let perturbation_time = 200;
    let duration = 800;
    
    for (condition, name) in conditions {
        println!("Analyzing {}...", name);
        
        let records = collect_detailed_trajectory(condition, 0, duration, perturbation_time);
        let metrics = compute_dynamics_metrics(&records, perturbation_time, 0.05);
        
        println!("  Peak drift: {:.3}", metrics.peak_drift);
        println!("  Overshoot ratio: {:.2}", metrics.overshoot_ratio);
        println!("  Time to 50%: {:?}", metrics.time_to_50pct);
        println!("  Time to 90%: {:?}", metrics.time_to_90pct);
        println!("  Settling time: {:?}", metrics.settling_time);
        println!("  Integrated error: {:.3}", metrics.integrated_error);
        println!("  Velocity variance: {:.4}", metrics.velocity_variance);
        println!("  Jerk metric: {:.4}", metrics.jerk_metric);
        println!("  Recovery success: {}", metrics.recovery_success);
        
        // Export
        let filename = format!("d4_002_{}_trajectory.csv", name);
        if let Err(e) = export_trajectory(&records, &filename) {
            eprintln!("  Failed to export: {}", e);
        } else {
            println!("  Exported: {}", filename);
        }
        println!();
    }
    
    println!("=== D4 Key Questions for 002 ===\n");
    println!("Q1: Does peak_drift vary by condition?");
    println!("Q2: Does settling_time show condition separation?");
    println!("Q3: Is velocity_variance (smoothness) different?");
    println!("Q4: Does integrated_error distinguish conditions?");
    println!();
    println!("If any metric shows condition separation, current stability metric is insufficient.");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_trajectory_collection() {
        let records = collect_detailed_trajectory(Condition::NoControl, 0, 100, 50);
        assert_eq!(records.len(), 100);
    }
    
    #[test]
    fn test_dynamics_metrics() {
        let records = vec![
            TrajectoryRecord { tick: 0, centroid_drift: 0.0, volume: 1.0, pressure: 50.0, velocity_magnitude: 0.0 },
            TrajectoryRecord { tick: 1, centroid_drift: 0.5, volume: 1.0, pressure: 50.0, velocity_magnitude: 1.0 },
            TrajectoryRecord { tick: 2, centroid_drift: 0.1, volume: 1.0, pressure: 50.0, velocity_magnitude: 0.2 },
        ];
        
        let metrics = compute_dynamics_metrics(&records, 0, 0.05);
        assert!(metrics.peak_drift >= 0.0);
    }
}
