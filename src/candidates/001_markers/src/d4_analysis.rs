//! D4 Semantic Metric Validation
//! 
//! Retrospective analysis of 001 coherence/consistency metrics
//! Breaks down aggregate metrics into interpretable sub-metrics

use crate::environment::{Environment, Strategy, MarkerMode};
use std::fs::File;
use std::io::Write;

/// Detailed coherence metrics for a single agent over time
#[derive(Debug, Clone)]
pub struct AgentCoherenceRecord {
    pub tick: usize,
    pub decision_coherence: u8,
    pub tick_smoothness: u8,
    pub action: f32,  // 0.0 or 1.0
    pub marker_coherence: u8,  // what's in the marker
}

/// Sub-metrics for semantic validation
#[derive(Debug, Clone)]
pub struct CoherenceSubMetrics {
    // Temporal stability
    pub decision_variance: f32,
    pub tick_variance: f32,
    pub decision_trend: f32,  // slope over time
    
    // Cross-level consistency
    pub decision_tick_correlation: f32,
    
    // Signal quality
    pub signal_to_noise: f32,
    pub coherence_action_correlation: f32,
    
    // Aggregate (for comparison)
    pub avg_decision_coherence: f32,
    pub avg_tick_smoothness: f32,
}

/// Run detailed metric collection for D4 analysis
pub fn run_d4_metric_collection(mode: MarkerMode, num_trials: usize, ticks: usize) -> Vec<Vec<AgentCoherenceRecord>> {
    let mut all_trial_records = Vec::new();
    
    for trial in 0..num_trials {
        let mut env = Environment::new(
            4,
            vec![
                Strategy::TitForTat,
                Strategy::TitForTat,
                Strategy::TitForTat,
                Strategy::TitForTat,
            ]
        );
        
        // Configure based on mode
        match mode {
            MarkerMode::Baseline => {
                env.marker_enabled = false;
            }
            MarkerMode::WriteOnly => {
                env.marker_enabled = true;
            }
            MarkerMode::ReadOnly => {
                env.marker_enabled = true;
                for agent in &mut env.agents {
                    agent.marker_system = crate::marker::ScheduledMarker::new_with_fixed(agent.id, 128);
                }
            }
            MarkerMode::Full => {
                env.marker_enabled = true;
            }
        }
        
        // Collect records for agent 0
        let mut records = Vec::new();
        
        for tick in 0..ticks {
            // Get detailed metrics before step
            let agent = &env.agents[0];
            let tracker = agent.marker_system.tracker();
            
            let record = AgentCoherenceRecord {
                tick,
                decision_coherence: tracker.decision_coherence(),
                tick_smoothness: tracker.tick_smoothness(),
                action: agent.action_history.last().map(|a| a.to_f32()).unwrap_or(0.5),
                marker_coherence: agent.marker_system.current_marker().coherence(),
            };
            records.push(record);
            
            // Run one step
            env.step();
        }
        
        all_trial_records.push(records);
    }
    
    all_trial_records
}

/// Compute sub-metrics from records
pub fn compute_sub_metrics(records: &[AgentCoherenceRecord]) -> CoherenceSubMetrics {
    let n = records.len() as f32;
    if n < 2.0 {
        return CoherenceSubMetrics {
            decision_variance: 0.0,
            tick_variance: 0.0,
            decision_trend: 0.0,
            decision_tick_correlation: 0.0,
            signal_to_noise: 0.0,
            coherence_action_correlation: 0.0,
            avg_decision_coherence: 128.0,
            avg_tick_smoothness: 128.0,
        };
    }
    
    // Averages
    let avg_dc: f32 = records.iter().map(|r| r.decision_coherence as f32).sum::<f32>() / n;
    let avg_ts: f32 = records.iter().map(|r| r.tick_smoothness as f32).sum::<f32>() / n;
    let avg_act: f32 = records.iter().map(|r| r.action).sum::<f32>() / n;
    let avg_mc: f32 = records.iter().map(|r| r.marker_coherence as f32).sum::<f32>() / n;
    
    // Variances
    let dc_var: f32 = records.iter()
        .map(|r| (r.decision_coherence as f32 - avg_dc).powi(2))
        .sum::<f32>() / n;
    let ts_var: f32 = records.iter()
        .map(|r| (r.tick_smoothness as f32 - avg_ts).powi(2))
        .sum::<f32>() / n;
    
    // Trend (simple linear regression slope)
    let mean_x = records.iter().map(|r| r.tick as f32).sum::<f32>() / n;
    let cov_xy: f32 = records.iter()
        .map(|r| (r.tick as f32 - mean_x) * (r.decision_coherence as f32 - avg_dc))
        .sum::<f32>();
    let var_x: f32 = records.iter()
        .map(|r| (r.tick as f32 - mean_x).powi(2))
        .sum::<f32>();
    let trend = if var_x > 0.0 { cov_xy / var_x } else { 0.0 };
    
    // Decision-tick correlation
    let cov_dt: f32 = records.iter()
        .map(|r| (r.decision_coherence as f32 - avg_dc) * (r.tick_smoothness as f32 - avg_ts))
        .sum::<f32>() / n;
    let corr_dt = if dc_var > 0.0 && ts_var > 0.0 { 
        cov_dt / (dc_var.sqrt() * ts_var.sqrt()) 
    } else { 
        0.0 
    };
    
    // Signal-to-noise (mean / std)
    let snr = if dc_var > 0.0 { avg_dc / dc_var.sqrt() } else { 0.0 };
    
    // Coherence-action correlation
    let cov_ca: f32 = records.iter()
        .map(|r| (r.decision_coherence as f32 - avg_dc) * (r.action - avg_act))
        .sum::<f32>() / n;
    let act_var: f32 = records.iter()
        .map(|r| (r.action - avg_act).powi(2))
        .sum::<f32>() / n;
    let corr_ca = if dc_var > 0.0 && act_var > 0.0 {
        cov_ca / (dc_var.sqrt() * act_var.sqrt())
    } else {
        0.0
    };
    
    CoherenceSubMetrics {
        decision_variance: dc_var,
        tick_variance: ts_var,
        decision_trend: trend,
        decision_tick_correlation: corr_dt,
        signal_to_noise: snr,
        coherence_action_correlation: corr_ca,
        avg_decision_coherence: avg_dc,
        avg_tick_smoothness: avg_ts,
    }
}

/// Export records to CSV for external analysis
pub fn export_to_csv(records: &[AgentCoherenceRecord], path: &str) -> std::io::Result<()> {
    let mut file = File::create(path)?;
    writeln!(file, "tick,decision_coherence,tick_smoothness,action,marker_coherence")?;
    
    for r in records {
        writeln!(file, "{},{},{},{},{}",
            r.tick,
            r.decision_coherence,
            r.tick_smoothness,
            r.action,
            r.marker_coherence
        )?;
    }
    
    Ok(())
}

/// Main D4 analysis entry point
pub fn run_d4_analysis() {
    println!("=== D4 Semantic Metric Validation ===\n");
    
    let modes = vec![
        (MarkerMode::Baseline, "baseline"),
        (MarkerMode::WriteOnly, "write_only"),
        (MarkerMode::ReadOnly, "read_only"),
        (MarkerMode::Full, "full"),
    ];
    
    for (mode, name) in modes {
        println!("Analyzing {:?}...", mode);
        
        let all_records = run_d4_metric_collection(mode, 3, 200);
        
        // Compute sub-metrics for each trial
        for (trial_idx, records) in all_records.iter().enumerate() {
            let metrics = compute_sub_metrics(records);
            
            println!("  Trial {}:", trial_idx);
            println!("    Avg decision coherence: {:.1}", metrics.avg_decision_coherence);
            println!("    Avg tick smoothness: {:.1}", metrics.avg_tick_smoothness);
            println!("    Decision variance: {:.1}", metrics.decision_variance);
            println!("    Tick variance: {:.1}", metrics.tick_variance);
            println!("    Decision trend: {:.3}", metrics.decision_trend);
            println!("    Decision-tick correlation: {:.3}", metrics.decision_tick_correlation);
            println!("    Signal-to-noise: {:.2}", metrics.signal_to_noise);
            println!("    Coherence-action correlation: {:.3}", metrics.coherence_action_correlation);
            
            // Export CSV
            let filename = format!("d4_{}_trial{}.csv", name, trial_idx);
            if let Err(e) = export_to_csv(records, &filename) {
                eprintln!("    Failed to export {}: {}", filename, e);
            } else {
                println!("    Exported: {}", filename);
            }
        }
        
        println!();
    }
    
    // Summary analysis
    println!("=== D4 Key Questions ===\n");
    
    println!("Q1: Is decision coherence stable over time?");
    println!("  Check: decision_variance and decision_trend in CSVs\n");
    
    println!("Q2: Does decision coherence correlate with tick smoothness?");
    println!("  Check: decision_tick_correlation in CSVs\n");
    
    println!("Q3: Does coherence correlate with actual actions?");
    println!("  Check: coherence_action_correlation in CSVs\n");
    
    println!("Q4: Which mode has best signal-to-noise?");
    println!("  Compare signal_to_noise across modes\n");
    
    println!("CSV files created for external analysis.");
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_d4_collection() {
        let records = run_d4_metric_collection(MarkerMode::Baseline, 1, 50);
        assert_eq!(records.len(), 1);
        assert_eq!(records[0].len(), 50);
    }
    
    #[test]
    fn test_sub_metrics() {
        let records = vec![
            AgentCoherenceRecord {
                tick: 0,
                decision_coherence: 128,
                tick_smoothness: 128,
                action: 0.0,
                marker_coherence: 128,
            },
            AgentCoherenceRecord {
                tick: 1,
                decision_coherence: 200,
                tick_smoothness: 150,
                action: 1.0,
                marker_coherence: 200,
            },
        ];
        
        let metrics = compute_sub_metrics(&records);
        assert!(metrics.avg_decision_coherence > 0.0);
    }
}
