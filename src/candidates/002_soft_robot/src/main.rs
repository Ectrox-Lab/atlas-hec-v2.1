//! 002 Soft Robot - FINAL: Single-Shot Recovery Experiment

use soft_robot_002::run_single_shot_recovery_experiment;

fn main() {
    println!("=== 002 FINAL: Single-Shot Shape Recovery ===\n");
    println!("Strong single perturbation + clean recovery tracking\n");
    
    let metrics = run_single_shot_recovery_experiment();
    
    // Aggregate analysis
    println!("\n=== SUMMARY ===");
    
    for cond in ["predictive", "reactive", "none"] {
        let cond_metrics: Vec<_> = metrics.iter()
            .filter(|m| m.condition.to_string() == cond)
            .collect();
        
        if cond_metrics.is_empty() { continue; }
        
        let avg_peak: f32 = cond_metrics.iter().map(|m| m.peak_drift).sum::<f32>() / cond_metrics.len() as f32;
        let avg_t50: f32 = cond_metrics.iter()
            .filter_map(|m| m.time_to_50pct)
            .sum::<f32>() / cond_metrics.iter().filter(|m| m.time_to_50pct.is_some()).count().max(1) as f32;
        let avg_t90: f32 = cond_metrics.iter()
            .filter_map(|m| m.time_to_90pct)
            .sum::<f32>() / cond_metrics.iter().filter(|m| m.time_to_90pct.is_some()).count().max(1) as f32;
        let avg_residual: f32 = cond_metrics.iter().map(|m| m.residual_drift).sum::<f32>() / cond_metrics.len() as f32;
        let recovery_rate: f32 = cond_metrics.iter().filter(|m| m.recovered).count() as f32 / cond_metrics.len() as f32;
        
        println!("\n{:?}:", cond);
        println!("  Peak drift:     {:.3}", avg_peak);
        println!("  Time to 50%:    {:.2}s", avg_t50);
        println!("  Time to 90%:    {:.2}s", avg_t90);
        println!("  Residual:       {:.3}", avg_residual);
        println!("  Recovery rate:  {:.0}%", recovery_rate * 100.0);
    }
    
    // Verdict
    println!("\n=== VERDICT ===");
    let pred_metrics: Vec<_> = metrics.iter()
        .filter(|m| m.condition.to_string() == "predictive")
        .collect();
    let noctl_metrics: Vec<_> = metrics.iter()
        .filter(|m| m.condition.to_string() == "none")
        .collect();
    
    if pred_metrics.is_empty() || noctl_metrics.is_empty() {
        println!("INSUFFICIENT DATA");
        return;
    }
    
    let pred_t90: f32 = pred_metrics.iter()
        .filter_map(|m| m.time_to_90pct)
        .sum::<f32>() / pred_metrics.iter().filter(|m| m.time_to_90pct.is_some()).count().max(1) as f32;
    let noctl_t90: f32 = noctl_metrics.iter()
        .filter_map(|m| m.time_to_90pct)
        .sum::<f32>() / noctl_metrics.iter().filter(|m| m.time_to_90pct.is_some()).count().max(1) as f32;
    
    if pred_t90 < noctl_t90 * 0.8 {
        println!("CONTINUE: Predictive feedback shows faster recovery");
    } else if pred_t90 > noctl_t90 * 1.2 {
        println!("PIVOT: Predictive feedback slower - mechanism needs redesign");
    } else {
        println!("KILL: No clear feedback advantage in recovery task");
    }
}
