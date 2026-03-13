use rayon::prelude::*;
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// E1 Phase A: Critical Coupling Coarse Sweep
/// 
/// Parameter space:
/// - N: [1000, 3000, 10000, 30000, 100000] (5 points)
/// - K: 0.1-5.0 (log-uniform, 20 points)  
/// - sigma: [0.1, 0.5, 1.0] (3 points)
/// - mu: 1.0 (fixed)
/// 
/// Total: ~300 configs per sigma = 900-1500 runs
/// Concurrency: 48-64 cores
/// Expected time: 4-6 hours

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
}

/// Kuramoto model simulation - Optimized using mean-field approximation
/// dθ_i/dt = ω_i + K * r * sin(ψ - θ_i)
/// where r*e^(iψ) = <e^(iθ)>
/// This is exact for all-to-all coupling and reduces O(N^2) to O(N)
fn simulate_kuramoto(params: &Params, config_id: usize) -> Result {
    use rand::distributions::{Distribution, Uniform};
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    let mut rng = StdRng::seed_from_u64(config_id as u64 + 42);
    
    let n = params.n;
    let k = params.k;
    let dt = 0.01;
    let total_steps = 5000;
    let warmup_steps = 1000;
    
    // Initialize phases uniformly
    let uniform = Uniform::new(0.0, 2.0 * std::f64::consts::PI);
    let mut phases: Vec<f64> = (0..n).map(|_| uniform.sample(&mut rng)).collect();
    
    // Initialize natural frequencies from normal distribution
    let omega_dist = rand_distr::Normal::new(params.mu, params.sigma).unwrap();
    let omegas: Vec<f64> = (0..n)
        .map(|_| omega_dist.sample(&mut rng))
        .collect();
    
    let mut r_history: Vec<f64> = Vec::with_capacity(total_steps - warmup_steps);
    
    for step in 0..total_steps {
        // Compute order parameter: r * e^(iψ) = (1/N) * Σ_j e^(iθ_j)
        let (sum_cos, sum_sin) = phases.iter().fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
        let r = ((sum_cos / n as f64).powi(2) + (sum_sin / n as f64).powi(2)).sqrt();
        let psi = (sum_sin / n as f64).atan2(sum_cos / n as f64);
        
        if step >= warmup_steps {
            r_history.push(r);
        }
        
        // Update phases using mean-field coupling: K * r * sin(ψ - θ_i)
        // This is equivalent to (K/N) * Σ_j sin(θ_j - θ_i) for all-to-all
        for i in 0..n {
            let coupling = k * r * (psi - phases[i]).sin();
            phases[i] = (phases[i] + (omegas[i] + coupling) * dt).rem_euclid(2.0 * std::f64::consts::PI);
        }
    }
    
    // Compute statistics
    let r_final = *r_history.last().unwrap();
    let r_max = r_history.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let r_min = r_history.iter().cloned().fold(f64::INFINITY, f64::min);
    let r_mean = r_history.iter().sum::<f64>() / r_history.len() as f64;
    let r_var = r_history.iter().map(|&r| (r - r_mean).powi(2)).sum::<f64>() / r_history.len() as f64;
    let r_std = r_var.sqrt();
    
    // Find convergence time (when r stabilizes within 5% of final)
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
    }
}

fn generate_param_space() -> Vec<Params> {
    let n_values = vec![1000, 3000, 10000, 30000, 100000];
    let sigma_values = vec![0.1, 0.5, 1.0];
    let mu = 1.0;
    
    // K: 0.1-5.0, log-uniform, 20 points
    let k_values: Vec<f64> = (0..20)
        .map(|i| {
            let t = i as f64 / 19.0;
            let log_k = (0.1_f64.ln()) * (1.0 - t) + (5.0_f64.ln()) * t;
            log_k.exp()
        })
        .collect();
    
    let mut params = Vec::new();
    for &n in &n_values {
        for &k in &k_values {
            for &sigma in &sigma_values {
                params.push(Params { n, k, sigma, mu });
            }
        }
    }
    params
}

fn main() {
    println!("=== E1 Phase A: Critical Coupling Coarse Sweep ===");
    println!("Starting at: {:?}", std::time::SystemTime::now());
    
    let params = generate_param_space();
    let total = params.len();
    println!("Total configurations: {}", total);
    println!("N values: [1000, 3000, 10000, 30000, 100000]");
    println!("K range: 0.1-5.0 (20 points, log-uniform)");
    println!("Sigma values: [0.1, 0.5, 1.0]");
    println!();
    
    // Create output directory
    let out_dir = "../../../results/e1_phase_a";
    fs::create_dir_all(out_dir).expect("Failed to create output directory");
    
    let counter = Arc::new(AtomicUsize::new(0));
    let start_time = std::time::Instant::now();
    
    // Parallel execution
    let results: Vec<Result> = params
        .par_iter()
        .enumerate()
        .map(|(i, p)| {
            let result = simulate_kuramoto(p, i);
            
            let count = counter.fetch_add(1, Ordering::Relaxed) + 1;
            if count % 50 == 0 || count == total {
                let elapsed = start_time.elapsed().as_secs_f64();
                let rate = count as f64 / elapsed;
                let remaining = (total - count) as f64 / rate;
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
    
    // Write results to CSV
    let csv_path = format!("{}/sweep_results.csv", out_dir);
    let mut writer = csv::Writer::from_path(&csv_path).expect("Failed to create CSV");
    
    for r in &results {
        writer.serialize(r).expect("Failed to write record");
    }
    writer.flush().expect("Failed to flush CSV");
    
    // Generate summary
    let total_time = start_time.elapsed().as_secs_f64();
    let summary = format!(
        "=== E1 Phase A Complete ===\n\
         Total configs: {}\n\
         Total time: {:.1} min\n\
         Avg rate: {:.1} configs/sec\n\
         Output: {}\n\
         \n\
         Quick stats:\n\
         - r_final range: [{:.3}, {:.3}]\n\
         - r_final mean: {:.3}\n\
         - Configs with r > 0.8: {}\n\
         - Configs with r < 0.2: {}\n",
        total,
        total_time / 60.0,
        total as f64 / total_time,
        csv_path,
        results.iter().map(|r| r.r_final).fold(f64::INFINITY, f64::min),
        results.iter().map(|r| r.r_final).fold(f64::NEG_INFINITY, f64::max),
        results.iter().map(|r| r.r_final).sum::<f64>() / results.len() as f64,
        results.iter().filter(|r| r.r_final > 0.8).count(),
        results.iter().filter(|r| r.r_final < 0.2).count(),
    );
    
    let summary_path = format!("{}/summary.txt", out_dir);
    let mut summary_file = File::create(&summary_path).expect("Failed to create summary");
    summary_file.write_all(summary.as_bytes()).expect("Failed to write summary");
    
    println!();
    println!("{}", summary);
    println!("=== E1 Phase A Finished ===");
}
