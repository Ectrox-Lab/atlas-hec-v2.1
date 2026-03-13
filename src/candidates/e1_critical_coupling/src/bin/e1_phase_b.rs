use rayon::prelude::*;
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// E1 Phase B: Critical Region Refinement
/// 
/// Based on Phase A results, focus on critical regions:
/// - σ=0.1: K ∈ [0.15, 0.40] (K_c ≈ 0.2-0.34)
/// - σ=0.5: K ∈ [0.80, 1.10] (K_c ≈ 0.96)
/// - σ=1.0: K ∈ [1.50, 2.10] (K_c ≈ 1.79)
///
/// N values: [5e4, 7e4, 1e5, 3e5] (increased for finite-size scaling)
/// K points: 50 per σ (linear dense sampling)
/// Total: 4N × 50K × 3σ = 600 configs

#[derive(Debug, Clone, Copy)]
struct Params {
    n: usize,
    k: f64,
    sigma: f64,
    mu: f64,
}

#[derive(Debug, Serialize)]
struct Result {
    n: usize,
    k: f64,
    sigma: f64,
    mu: f64,
    r_final: f64,
    r_max: f64,
    r_min: f64,
    r_std: f64,
    convergence_time: usize,
    config_id: usize,
    initial_sync: bool,
}

fn simulate_kuramoto(params: &Params, config_id: usize, initial_sync: bool) -> Result {
    use rand::distributions::{Distribution, Uniform};
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    let mut rng = StdRng::seed_from_u64(config_id as u64 + 10000);
    
    let n = params.n;
    let k = params.k;
    let dt = 0.005;
    let total_steps = 10000;
    let warmup_steps = 2000;
    
    let uniform: Uniform<f64> = Uniform::new(0.0, 2.0 * std::f64::consts::PI);
    let mut phases: Vec<f64> = if initial_sync {
        let narrow: Uniform<f64> = Uniform::new(-0.5, 0.5);
        (0..n).map(|_| {
            let v: f64 = narrow.sample(&mut rng);
            v.rem_euclid(2.0 * std::f64::consts::PI)
        }).collect()
    } else {
        (0..n).map(|_| uniform.sample(&mut rng)).collect()
    };
    
    let omega_dist = rand_distr::Normal::new(params.mu, params.sigma).unwrap();
    let omegas: Vec<f64> = (0..n)
        .map(|_| omega_dist.sample(&mut rng))
        .collect();
    
    let mut r_history: Vec<f64> = Vec::with_capacity(total_steps - warmup_steps);
    
    for step in 0..total_steps {
        let (sum_cos, sum_sin): (f64, f64) = phases.iter().fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
        let r = ((sum_cos / n as f64).powi(2) + (sum_sin / n as f64).powi(2)).sqrt();
        let psi = (sum_sin / n as f64).atan2(sum_cos / n as f64);
        
        if step >= warmup_steps {
            r_history.push(r);
        }
        
        for i in 0..n {
            let coupling = k * r * (psi - phases[i]).sin();
            phases[i] = (phases[i] + (omegas[i] + coupling) * dt)
                .rem_euclid(2.0 * std::f64::consts::PI);
        }
    }
    
    let r_final = *r_history.last().unwrap();
    let r_max = r_history.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let r_min = r_history.iter().cloned().fold(f64::INFINITY, f64::min);
    let r_mean = r_history.iter().sum::<f64>() / r_history.len() as f64;
    let r_var = r_history.iter().map(|&r| (r - r_mean).powi(2)).sum::<f64>() / r_history.len() as f64;
    let r_std = r_var.sqrt();
    
    let threshold = 0.05 * r_final;
    let convergence_time = r_history.iter().enumerate().rev().find(|(_, &r)| {
        (r - r_final).abs() > threshold
    }).map(|(i, _)| i + warmup_steps).unwrap_or(warmup_steps);
    
    Result {
        n: params.n,
        k: params.k,
        sigma: params.sigma,
        mu: params.mu,
        r_final,
        r_max,
        r_min,
        r_std,
        convergence_time,
        config_id,
        initial_sync,
    }
}

fn generate_param_space() -> Vec<(Params, bool)> {
    let n_values = vec![50_000, 70_000, 100_000, 300_000];
    let sigma_k_ranges = vec![
        (0.1, 0.15, 0.40),
        (0.5, 0.80, 1.10),
        (1.0, 1.50, 2.10),
    ];
    let mu = 1.0;
    let k_points = 50;
    
    let mut params = Vec::new();
    for &n in &n_values {
        for &(sigma, k_min, k_max) in &sigma_k_ranges {
            for i in 0..k_points {
                let k = k_min + (k_max - k_min) * (i as f64 / (k_points - 1) as f64);
                params.push((Params { n, k, sigma, mu }, false));
                params.push((Params { n, k, sigma, mu }, true));
            }
        }
    }
    params
}

fn main() {
    println!("=== E1 Phase B: Critical Region Refinement ===");
    println!("Starting at: {:?}", std::time::SystemTime::now());
    
    let param_configs = generate_param_space();
    let total = param_configs.len();
    println!("Total configurations: {}", total);
    println!("N values: [50000, 70000, 100000, 300000]");
    println!("K ranges (dense sampling):");
    println!("  σ=0.1: [0.15, 0.40] (50 points)");
    println!("  σ=0.5: [0.80, 1.10] (50 points)");
    println!("  σ=1.0: [1.50, 2.10] (50 points)");
    println!("Initial conditions: disordered + ordered (hysteresis test)");
    println!();
    
    let out_dir = "../../../results/e1_phase_b";
    fs::create_dir_all(out_dir).expect("Failed to create output directory");
    
    let counter = Arc::new(AtomicUsize::new(0));
    let start_time = std::time::Instant::now();
    
    let results: Vec<Result> = param_configs
        .par_iter()
        .enumerate()
        .map(|(i, (p, init_sync))| {
            let result = simulate_kuramoto(p, i, *init_sync);
            
            let count = counter.fetch_add(1, Ordering::Relaxed) + 1;
            if count % 50 == 0 || count == total {
                let elapsed = start_time.elapsed().as_secs_f64();
                let rate = count as f64 / elapsed;
                let remaining = (total - count) as f64 / rate.max(0.1);
                println!(
                    "Progress: {}/{} ({:.1}%) | Rate: {:.1} configs/sec | ETA: {:.1} min",
                    count, total,
                    100.0 * count as f64 / total as f64,
                    rate,
                    remaining / 60.0
                );
            }
            
            result
        })
        .collect();
    
    let csv_path = format!("{}/refinement_results.csv", out_dir);
    let mut writer = csv::Writer::from_path(&csv_path).expect("Failed to create CSV");
    
    for r in &results {
        writer.serialize(r).expect("Failed to write record");
    }
    writer.flush().expect("Failed to flush CSV");
    
    let total_time = start_time.elapsed().as_secs_f64();
    
    let mut hysteresis_cases = 0;
    for i in (0..results.len()).step_by(2) {
        if i + 1 < results.len() {
            let r_disordered = results[i].r_final;
            let r_ordered = results[i + 1].r_final;
            if (r_ordered - r_disordered).abs() > 0.3 {
                hysteresis_cases += 1;
            }
        }
    }
    
    let summary = format!(
        "=== E1 Phase B Complete ===\n\
         Total configs: {}\n\
         Total time: {:.1} min\n\
         Avg rate: {:.1} configs/sec\n\
         Output: {}\n\
         \n\
         Hysteresis detection:\n\
         - Cases with |r_ordered - r_disordered| > 0.3: {}\n\
         - Hysteresis present: {}\n",
        total,
        total_time / 60.0,
        total as f64 / total_time,
        csv_path,
        hysteresis_cases,
        if hysteresis_cases > 10 { "LIKELY (first-order transition)" } else { "NO (second-order transition)" }
    );
    
    let summary_path = format!("{}/summary.txt", out_dir);
    let mut summary_file = File::create(&summary_path).expect("Failed to create summary");
    summary_file.write_all(summary.as_bytes()).expect("Failed to write summary");
    
    println!();
    println!("{}", summary);
    println!("=== E1 Phase B Finished ===");
}
