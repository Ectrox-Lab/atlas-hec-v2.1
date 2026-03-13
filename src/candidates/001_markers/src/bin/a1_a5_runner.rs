use rayon::prelude::*;
use serde::Serialize;
use std::fs;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// A1 × A5: 2×2 Factorial Diagnostic
/// 
/// Tests the interaction between Write Gating and Read Gating:
/// 
/// | Condition      | Write Gating | Read Gating | Expected |
/// |----------------|--------------|-------------|----------|
/// | Baseline       | OFF          | OFF         | Control  |
/// | WriteOnly      | ON           | OFF         | Safe     |
/// | ReadOnly       | OFF          | ON          | Harmful  |
/// | Full           | ON           | ON          | Test     |

#[derive(Debug, Clone, Copy, PartialEq)]
enum MarkerMode {
    Baseline,   // No markers
    WriteOnly,  // Write/update markers, agents don't read
    ReadOnly,   // Fixed markers, agents read
    Full,       // Dynamic markers, agents read
}

impl MarkerMode {
    fn as_str(&self) -> &'static str {
        match self {
            MarkerMode::Baseline => "Baseline",
            MarkerMode::WriteOnly => "WriteOnly",
            MarkerMode::ReadOnly => "ReadOnly",
            MarkerMode::Full => "Full",
        }
    }
}

#[derive(Debug, Serialize)]
struct A1A5Result {
    condition: String,
    trial: usize,
    seed: u64,
    decision_variance: f64,
    tick_smoothness: f64,
    decision_coherence: f64,
    final_reward: f64,
}

fn compute_coherence(values: &[f32]) -> f64 {
    if values.len() < 2 {
        return 0.0;
    }
    let mean = values.iter().sum::<f32>() / values.len() as f32;
    let variance = values.iter().map(|&v| (v - mean).powi(2)).sum::<f32>() / values.len() as f32;
    let std_dev = variance.sqrt();
    
    // Coefficient of variation with protection
    let denom = mean.abs().max(0.1);
    let cv = std_dev / denom;
    
    // Convert to coherence score (0-1)
    (1.0 - cv.min(1.0)) as f64
}

fn run_single_trial(mode: MarkerMode, seed: u64, trial: usize) -> A1A5Result {
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    use rand::distributions::{Distribution, Uniform};
    
    // Configure experiment based on mode
    let (write_gating, read_gating, fixed_marker) = match mode {
        MarkerMode::Baseline => (false, false, false),
        MarkerMode::WriteOnly => (true, false, false),
        MarkerMode::ReadOnly => (false, true, true),
        MarkerMode::Full => (true, true, false),
    };
    
    let mut rng = StdRng::seed_from_u64(seed);
    let uniform = Uniform::new(-1.0f32, 1.0);
    
    let mut decisions = Vec::new();
    let mut tick_values = Vec::new();
    let mut rewards = Vec::new();
    
    // Marker value (evolves or fixed)
    let mut marker_value = 0.5f32;
    
    for step in 0..100 {
        // Agent decision
        let decision = if read_gating {
            let marker_influence = if fixed_marker { 0.5 } else { marker_value };
            uniform.sample(&mut rng) + (marker_influence - 0.5) * 0.3
        } else {
            uniform.sample(&mut rng)
        };
        
        decisions.push(decision);
        tick_values.push(decision);
        
        // Reward
        let reward = 1.0 - decision.abs();
        rewards.push(reward);
        
        // Update marker
        if write_gating && !fixed_marker {
            marker_value = marker_value * 0.9 + reward * 0.1;
            marker_value = marker_value.clamp(0.0, 1.0);
        }
    }
    
    let decision_variance = if decisions.len() > 1 {
        let mean = decisions.iter().sum::<f32>() / decisions.len() as f32;
        let var = decisions.iter().map(|&d| (d - mean).powi(2)).sum::<f32>() 
            / decisions.len() as f32;
        var as f64
    } else {
        0.0
    };
    
    let tick_smoothness = compute_coherence(&tick_values);
    let decision_coherence = compute_coherence(&decisions);
    
    A1A5Result {
        condition: mode.as_str().to_string(),
        trial,
        seed,
        decision_variance,
        tick_smoothness,
        decision_coherence,
        final_reward: rewards.last().copied().unwrap_or(0.0) as f64,
    }
}

fn generate_trials() -> Vec<(MarkerMode, u64, usize)> {
    let modes = vec![
        MarkerMode::Baseline,
        MarkerMode::WriteOnly,
        MarkerMode::ReadOnly,
        MarkerMode::Full,
    ];
    
    let mut trials = Vec::new();
    let base_seeds: Vec<u64> = (0..10).map(|i| 1000 + i as u64 * 100).collect();
    
    for (trial_idx, &base_seed) in base_seeds.iter().enumerate() {
        for mode in &modes {
            trials.push((*mode, base_seed, trial_idx));
        }
    }
    
    trials
}

fn analyze_results(results: &[A1A5Result]) {
    use std::collections::HashMap;
    
    println!("\n=== A1×A5 Analysis ===\n");
    
    let mut by_condition: HashMap<&str, Vec<&A1A5Result>> = HashMap::new();
    for r in results {
        by_condition.entry(&r.condition).or_default().push(r);
    }
    
    println!("Condition Statistics:");
    println!("{:<12} {:>6} {:>12} {:>12} {:>12}", 
             "Condition", "N", "Var(mean)", "Coh(mean)", "Reward(mean)");
    println!("{}", "-".repeat(60));
    
    for condition in &["Baseline", "WriteOnly", "ReadOnly", "Full"] {
        if let Some(data) = by_condition.get(condition) {
            let n = data.len();
            let var_mean = data.iter().map(|r| r.decision_variance).sum::<f64>() / n as f64;
            let coh_mean = data.iter().map(|r| r.decision_coherence).sum::<f64>() / n as f64;
            let rew_mean = data.iter().map(|r| r.final_reward).sum::<f64>() / n as f64;
            
            println!("{:<12} {:>6} {:>12.4} {:>12.4} {:>12.4}", 
                     condition, n, var_mean, coh_mean, rew_mean);
        }
    }
    
    println!();
    
    // Diagnostic 1: Write Gating
    println!("Diagnostic 1: Write Gating Effect");
    println!("{}", "-".repeat(40));
    let baseline_var = by_condition.get("Baseline").map(|d| {
        d.iter().map(|r| r.decision_variance).sum::<f64>() / d.len() as f64
    }).unwrap_or(0.0);
    let writeonly_var = by_condition.get("WriteOnly").map(|d| {
        d.iter().map(|r| r.decision_variance).sum::<f64>() / d.len() as f64
    }).unwrap_or(0.0);
    let full_var = by_condition.get("Full").map(|d| {
        d.iter().map(|r| r.decision_variance).sum::<f64>() / d.len() as f64
    }).unwrap_or(0.0);
    
    println!("  Baseline var:  {:.4}", baseline_var);
    println!("  WriteOnly var: {:.4}", writeonly_var);
    println!("  Full var:      {:.4}", full_var);
    
    if (writeonly_var - baseline_var).abs() < 0.05 {
        println!("  ✓ Write gating: NO HARM (confirms D4)");
    } else if writeonly_var < baseline_var {
        println!("  ~ Write gating: May reduce variance slightly");
    } else {
        println!("  ⚠ Write gating: UNEXPECTED increase in variance");
    }
    
    println!();
    
    // Diagnostic 2: Read Gating
    println!("Diagnostic 2: Read Gating Effect");
    println!("{}", "-".repeat(40));
    let readonly_var = by_condition.get("ReadOnly").map(|d| {
        d.iter().map(|r| r.decision_variance).sum::<f64>() / d.len() as f64
    }).unwrap_or(0.0);
    
    println!("  ReadOnly var: {:.4}", readonly_var);
    
    if readonly_var < baseline_var * 0.5 {
        println!("  ✗ Read gating: SUPPRESSES variance significantly");
        println!("  → Confirms D4: fixed-marker semantics harmful");
    } else if readonly_var < baseline_var {
        println!("  ~ Read gating: Reduces variance moderately");
    } else {
        println!("  ~ Read gating: No strong suppression effect");
    }
    
    println!();
    
    // Diagnostic 3: Interaction
    println!("Diagnostic 3: Interaction Effect");
    println!("{}", "-".repeat(40));
    let write_benefit = full_var - readonly_var;
    println!("  Full vs ReadOnly: {:.4}", write_benefit);
    
    if write_benefit > 0.05 {
        println!("  ✓ Dynamic write helps when read is active");
        println!("  → Full dynamic marker has benefit");
    } else if write_benefit < -0.05 {
        println!("  ✗ Dynamic write hurts when read is active");
    } else {
        println!("  ~ No clear interaction effect in this setup");
    }
    
    println!();
    println!("{}", "=".repeat(60));
    println!("CONCLUSION:");
    println!("{}", "-".repeat(60));
    
    let write_safe = (writeonly_var - baseline_var).abs() < 0.05;
    let read_problem = readonly_var < baseline_var * 0.7;
    let dynamic_helps = write_benefit > 0.03;
    
    if write_safe {
        println!("✓ Write mechanism: SAFE");
    }
    if read_problem {
        println!("✗ Fixed-marker read: HARMFUL (confirms D4)");
    }
    if dynamic_helps {
        println!("✓ Dynamic marker: Beneficial when reading active");
    }
    
    if write_safe && read_problem {
        println!();
        println!("OVERALL: Confirms D4 diagnosis");
        println!("  → Continue with dynamic marker (Full mode)");
        println!("  → Avoid fixed-marker reads (ReadOnly mode)");
    }
    
    println!("{}", "=".repeat(60));
}

fn main() {
    println!("=== A1 × A5: 2×2 Factorial Diagnostic ===");
    println!("Using paired-seed design (D1 framework)");
    println!();
    
    let trials = generate_trials();
    let total = trials.len();
    println!("Total trials: {} (4 conditions × 10 trials)", total);
    println!();
    
    let out_dir = "../../../results/a1_a5";
    fs::create_dir_all(out_dir).expect("Failed to create output directory");
    
    let counter = Arc::new(AtomicUsize::new(0));
    let start_time = std::time::Instant::now();
    
    let results: Vec<A1A5Result> = trials
        .par_iter()
        .map(|(mode, seed, trial_idx)| {
            let result = run_single_trial(*mode, *seed, *trial_idx);
            
            let count = counter.fetch_add(1, Ordering::Relaxed) + 1;
            if count % 10 == 0 || count == total {
                println!("Progress: {}/{} ({:.0}%)", count, total, 
                        100.0 * count as f64 / total as f64);
            }
            
            result
        })
        .collect();
    
    // Write CSV
    let csv_path = format!("{}/factorial_results.csv", out_dir);
    let mut writer = csv::Writer::from_path(&csv_path).expect("Failed to create CSV");
    for r in &results {
        writer.serialize(r).expect("Failed to write record");
    }
    writer.flush().expect("Failed to flush CSV");
    
    // Analyze
    analyze_results(&results);
    
    let total_time = start_time.elapsed().as_secs_f64();
    println!("\nTotal time: {:.1}s", total_time);
    println!("Output: {}", csv_path);
    println!("=== A1×A5 Complete ===");
}
