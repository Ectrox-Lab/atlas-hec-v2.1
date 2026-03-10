use rayon::prelude::*;
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// E1 Overnight Long-Run Validation Batch
/// 
/// Purpose: Validate long-term stability and path-dependence in 3 K-regimes
/// 
/// Design: 3 K-groups × 3 σ-levels × 5 paired seeds = 45 configs
/// - CTRL: K = K_c - Δ (sub-critical, disorder)
/// - CRIT: K ≈ K_c (critical, test hysteresis/bistability)
/// - HIGH: K = K_c + Δ (super-critical, order)
///
/// Generations: 10,000 (long-run)
/// Metrics: r, CI, P, CDI, N, E, h (v19 unified state vector)

#[derive(Debug, Clone, Copy)]
struct Params {
    n: usize,
    k: f64,
    sigma: f64,
    mu: f64,
    group: &'static str,  // "CTRL", "CRIT", "HIGH"
    seed_pair: usize,
    initial_ordered: bool, // for hysteresis test in CRIT
}

#[derive(Debug, Serialize)]
struct Result {
    n: usize,
    k: f64,
    sigma: f64,
    mu: f64,
    group: String,
    seed_pair: usize,
    initial_ordered: bool,
    
    // v19 unified metrics
    r_final: f64,
    r_early: f64,      // avg first 2000 gens
    r_mid: f64,        // avg 2000-5000 gens
    r_late: f64,       // avg 5000-10000 gens
    
    ci_final: f64,     // condensation index
    p_final: f64,      // percolation ratio (giant component)
    
    stability: f64,    // variance of r in last 1000 gens
    convergence_time: Option<usize>,
    
    // Path dependence test
    r_init: f64,       // initial r
    r_path_deviation: f64, // |r_final - r_expected|
}

fn simulate(params: &Params, config_id: usize) -> Result {
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    use rand::distributions::{Distribution, Uniform};
    
    let mut rng = StdRng::seed_from_u64(config_id as u64 + 100000);
    
    let n = params.n;
    let k = params.k;
    let dt = 0.005;
    let total_steps = 10000;
    let record_start = 1000; // skip initial transient
    
    // Initialize phases
    let uniform: Uniform<f64> = Uniform::new(0.0, 2.0 * std::f64::consts::PI);
    let mut phases: Vec<f64> = if params.initial_ordered {
        // Ordered init: narrow cluster
        let narrow: Uniform<f64> = Uniform::new(-0.3, 0.3);
        (0..n).map(|_| narrow.sample(&mut rng).rem_euclid(2.0 * std::f64::consts::PI))
            .collect()
    } else {
        // Random init: uniform
        (0..n).map(|_| uniform.sample(&mut rng)).collect()
    };
    
    // Natural frequencies
    let omega_dist = rand_distr::Normal::new(params.mu, params.sigma).unwrap();
    let omegas: Vec<f64> = (0..n).map(|_| omega_dist.sample(&mut rng)).collect();
    
    // Track r history
    let mut r_history: Vec<f64> = Vec::with_capacity(total_steps - record_start);
    let mut r_init = 0.0;
    
    for step in 0..total_steps {
        // Compute order parameter r
        let (sum_cos, sum_sin) = phases.iter().fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
        let r = ((sum_cos / n as f64).powi(2) + (sum_sin / n as f64).powi(2)).sqrt();
        let psi = (sum_sin / n as f64).atan2(sum_cos / n as f64);
        
        if step == 0 {
            r_init = r;
        }
        
        if step >= record_start {
            r_history.push(r);
        }
        
        // Update phases (mean-field Kuramoto)
        for i in 0..n {
            let coupling = k * r * (psi - phases[i]).sin();
            phases[i] = (phases[i] + (omegas[i] + coupling) * dt)
                .rem_euclid(2.0 * std::f64::consts::PI);
        }
    }
    
    // Compute v19 metrics
    let r_final = *r_history.last().unwrap();
    
    // Early (0-2000), Mid (2000-5000), Late (5000-end)
    let early_slice = &r_history[0..2000.min(r_history.len())];
    let mid_start = 2000.min(r_history.len());
    let mid_end = 5000.min(r_history.len());
    let mid_slice = &r_history[mid_start..mid_end];
    let late_start = 5000.min(r_history.len());
    let late_slice = &r_history[late_start..];
    
    let r_early = early_slice.iter().sum::<f64>() / early_slice.len() as f64;
    let r_mid = if mid_slice.is_empty() { r_early } else {
        mid_slice.iter().sum::<f64>() / mid_slice.len() as f64
    };
    let r_late = late_slice.iter().sum::<f64>() / late_slice.len() as f64;
    
    // Stability: variance in last 1000 steps
    let last_1000 = &r_history[r_history.len().saturating_sub(1000)..];
    let r_mean_last = last_1000.iter().sum::<f64>() / last_1000.len() as f64;
    let stability = last_1000.iter()
        .map(|&r| (r - r_mean_last).powi(2))
        .sum::<f64>() / last_1000.len() as f64;
    
    // Convergence time (when r stabilizes within 5% of final)
    let threshold = 0.05 * r_final;
    let convergence_time = r_history.iter().enumerate().rev()
        .find(|(_, &r)| (r - r_final).abs() > threshold)
        .map(|(i, _)| i + record_start);
    
    // Estimate CI (condensation index) and P (percolation proxy)
    // Simplified: use phase clustering as proxy
    let ci_final = estimate_ci(&phases);
    let p_final = estimate_percolation(&phases, n);
    
    // Expected r based on K-group
    let r_expected = match params.group {
        "CTRL" => 0.1,  // Low sync
        "CRIT" => 0.5,  // Middle (bistable)
        "HIGH" => 0.9,  // High sync
        _ => 0.5,
    };
    let r_path_deviation = (r_final - r_expected).abs();
    
    Result {
        n,
        k,
        sigma: params.sigma,
        mu: params.mu,
        group: params.group.to_string(),
        seed_pair: params.seed_pair,
        initial_ordered: params.initial_ordered,
        r_final,
        r_early,
        r_mid,
        r_late,
        ci_final,
        p_final,
        stability,
        convergence_time,
        r_init,
        r_path_deviation,
    }
}

fn estimate_ci(phases: &[f64]) -> f64 {
    // Simplified CI: measure phase clustering
    // Higher = more condensed (phases cluster around certain values)
    let n = phases.len();
    let mut bins = vec![0; 8];
    for &theta in phases {
        let bin = ((theta / (2.0 * std::f64::consts::PI)) * 8.0) as usize % 8;
        bins[bin] += 1;
    }
    let max_bin = *bins.iter().max().unwrap() as f64;
    max_bin / n as f64
}

fn estimate_percolation(phases: &[f64], n: usize) -> f64 {
    // Simplified P: fraction of oscillators within π/4 of mean phase
    let (sum_cos, sum_sin) = phases.iter().fold((0.0, 0.0), |(c, s), &theta| {
        (c + theta.cos(), s + theta.sin())
    });
    let mean_phase = (sum_sin / n as f64).atan2(sum_cos / n as f64);
    
    let in_cluster = phases.iter()
        .filter(|&&theta| {
            let diff = (theta - mean_phase).abs().min(2.0 * std::f64::consts::PI - (theta - mean_phase).abs());
            diff < std::f64::consts::PI / 4.0
        })
        .count();
    
    in_cluster as f64 / n as f64
}

fn generate_batch() -> Vec<Params> {
    let n = 50000; // Fixed N for consistency
    let mu = 1.0;
    
    // K_c values from Phase B results
    let k_c_map = [
        (0.1, 0.25),  // σ=0.1, K_c≈0.25
        (0.5, 1.0),   // σ=0.5, K_c≈1.0
        (1.0, 1.7),   // σ=1.0, K_c≈1.7
    ];
    
    let delta = 0.15; // Distance from critical
    
    let mut batch = Vec::new();
    
    for (sigma, k_c) in k_c_map {
        // 3 K-groups
        let k_values = [
            ("CTRL", ((k_c - delta) as f64).max(0.1)),
            ("CRIT", k_c),
            ("HIGH", k_c + delta),
        ];
        
        for (group, k) in k_values {
            // 5 paired seeds
            for seed_pair in 0..5 {
                // Random init
                batch.push(Params {
                    n,
                    k,
                    sigma,
                    mu,
                    group,
                    seed_pair,
                    initial_ordered: false,
                });
                
                // Ordered init (for CRIT group - test hysteresis)
                if group == "CRIT" {
                    batch.push(Params {
                        n,
                        k,
                        sigma,
                        mu,
                        group,
                        seed_pair,
                        initial_ordered: true,
                    });
                }
            }
        }
    }
    
    batch
}

fn main() {
    println!("=== E1 Overnight Long-Run Validation Batch ===");
    println!("Start: {:?}", std::time::SystemTime::now());
    println!();
    
    let batch = generate_batch();
    let total = batch.len();
    
    println!("Design: 3 K-groups × 3 σ-levels × 5 paired seeds + CRIT ordered-init");
    println!("Total configs: {}", total);
    println!();
    println!("K-groups:");
    println!("  CTRL: K = K_c - Δ (sub-critical, disorder expected)");
    println!("  CRIT: K ≈ K_c (critical, test hysteresis/bistability)");
    println!("  HIGH: K = K_c + Δ (super-critical, order expected)");
    println!();
    println!("σ-levels: 0.1 (K_c≈0.25), 0.5 (K_c≈1.0), 1.0 (K_c≈1.7)");
    println!();
    println!("Generations: 10,000 (long-run validation)");
    println!("Metrics: r (sync), CI (condensation), P (percolation proxy), stability");
    println!();
    
    let out_dir = "../../../results/e1_overnight_batch";
    fs::create_dir_all(out_dir).expect("Failed to create output directory");
    
    let counter = Arc::new(AtomicUsize::new(0));
    let start_time = std::time::Instant::now();
    
    // Limit concurrency to protect memory
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(48)
        .build()
        .unwrap();
    
    let results: Vec<Result> = pool.install(|| {
        batch.par_iter()
            .enumerate()
            .map(|(i, p)| {
                let result = simulate(p, i);
                
                let count = counter.fetch_add(1, Ordering::Relaxed) + 1;
                if count % 5 == 0 || count == total {
                    let elapsed = start_time.elapsed().as_secs_f64();
                    let rate = count as f64 / elapsed;
                    let remaining = (total - count) as f64 / rate.max(0.1);
                    println!(
                        "Progress: {}/{} ({:.1}%) | Rate: {:.2} configs/min | ETA: {:.1} min",
                        count, total,
                        100.0 * count as f64 / total as f64,
                        rate * 60.0,
                        remaining / 60.0
                    );
                }
                
                result
            })
            .collect()
    });
    
    // Write results
    let csv_path = format!("{}/overnight_results.csv", out_dir);
    let mut writer = csv::Writer::from_path(&csv_path).expect("Failed to create CSV");
    for r in &results {
        writer.serialize(r).expect("Failed to write record");
    }
    writer.flush().expect("Failed to flush CSV");
    
    // Analysis
    let total_time = start_time.elapsed().as_secs_f64();
    
    println!();
    println!("=== Overnight Batch Complete ===");
    println!("Total configs: {}", total);
    println!("Total time: {:.1} min", total_time / 60.0);
    println!("Output: {}", csv_path);
    println!();
    
    // Quick analysis
    analyze_overnight_results(&results);
    
    println!();
    println!("End: {:?}", std::time::SystemTime::now());
    println!("=== Batch Finished ===");
}

fn analyze_overnight_results(results: &[Result]) {
    use std::collections::HashMap;
    
    println!("=== Quick Analysis ===");
    println!();
    
    // Summary by group
    println!("By K-group (averaged over σ and seeds):");
    println!("{:<8} {:>8} {:>12} {:>12} {:>12}", 
             "Group", "N", "r_final", "r_early", "Stability");
    println!("{}", "-".repeat(55));
    
    for group in &["CTRL", "CRIT", "HIGH"] {
        let group_data: Vec<&Result> = results.iter()
            .filter(|r| r.group == *group)
            .collect();
        
        if !group_data.is_empty() {
            let n = group_data.len();
            let r_final_avg = group_data.iter().map(|r| r.r_final).sum::<f64>() / n as f64;
            let r_early_avg = group_data.iter().map(|r| r.r_early).sum::<f64>() / n as f64;
            let stab_avg = group_data.iter().map(|r| r.stability).sum::<f64>() / n as f64;
            
            println!("{:<8} {:>8} {:>12.4} {:>12.4} {:>12.6}", 
                     group, n, r_final_avg, r_early_avg, stab_avg);
        }
    }
    
    println!();
    
    // CRIT group: test hysteresis (ordered vs random init)
    let crit_ordered: Vec<&Result> = results.iter()
        .filter(|r| r.group == "CRIT" && r.initial_ordered)
        .collect();
    let crit_random: Vec<&Result> = results.iter()
        .filter(|r| r.group == "CRIT" && !r.initial_ordered)
        .collect();
    
    if !crit_ordered.is_empty() && !crit_random.is_empty() {
        let r_ord = crit_ordered.iter().map(|r| r.r_final).sum::<f64>() / crit_ordered.len() as f64;
        let r_rand = crit_random.iter().map(|r| r.r_final).sum::<f64>() / crit_random.len() as f64;
        let gap = (r_ord - r_rand).abs();
        
        println!("CRIT Group Hysteresis Test:");
        println!("  Ordered init r: {:.4}", r_ord);
        println!("  Random init r:  {:.4}", r_rand);
        println!("  Gap: {:.4} {}", gap,
                 if gap > 0.2 { "✓ STRONG HYSTERESIS" } 
                 else if gap > 0.1 { "~ Moderate" } 
                 else { "✗ Weak/None" });
    }
    
    println!();
    
    // Check bistability in CRIT
    let crit_bistable = results.iter()
        .filter(|r| r.group == "CRIT")
        .filter(|r| r.r_final < 0.3 || r.r_final > 0.7)
        .count();
    let crit_total = results.iter().filter(|r| r.group == "CRIT").count();
    
    println!("Bistability in CRIT (r<0.3 or r>0.7): {}/{} ({:.1}%)",
             crit_bistable, crit_total,
             100.0 * crit_bistable as f64 / crit_total as f64);
}
