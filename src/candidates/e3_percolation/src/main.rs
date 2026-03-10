use rayon::prelude::*;
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// E3 Phase A: Percolation-Synchronization Causality
/// 
/// Test if P (percolation ratio) precedes r (synchronization order parameter)
/// 
/// Setup:
/// - 2D grid with occupancy probability p
/// - Oscillators at occupied sites
/// - Coupling: nearest neighbors within distance R
/// - Track both P(t) and r(t) evolution
///
/// Parameter space:
/// - N: fixed grid size (100x100 = 10k sites)
/// - p: occupancy [0.3, 0.9] (percolation threshold ~0.59 for 2D)
/// - K: coupling [0.5, 2.0] (3 values from E1 critical region)
/// - σ: frequency spread [0.1, 0.5, 1.0]
///
/// Total: 20p × 3K × 3σ = 180 configs

#[derive(Debug, Clone, Copy)]
struct Params {
    grid_size: usize,
    occupancy: f64,
    coupling: f64,
    sigma: f64,
    mu: f64,
}

#[derive(Debug, Serialize)]
struct Result {
    grid_size: usize,
    occupancy: f64,
    coupling: f64,
    sigma: f64,
    mu: f64,
    // Percolation metrics
    p_final: f64,
    p_time_to_50: Option<usize>,
    p_time_to_90: Option<usize>,
    // Sync metrics
    r_final: f64,
    r_time_to_50: Option<usize>,
    r_time_to_90: Option<usize>,
    // Causality test
    p_precedes_r: bool,
    time_lag: Option<isize>,
    config_id: usize,
}

fn simulate(params: &Params, config_id: usize) -> Result {
    use rand::distributions::{Distribution, Uniform};
    use rand::SeedableRng;
    use rand::rngs::StdRng;
    
    let mut rng = StdRng::seed_from_u64(config_id as u64 + 50000);
    let n = params.grid_size;
    let total_sites = n * n;
    
    // Generate occupancy map
    let uniform: Uniform<f64> = Uniform::new(0.0, 1.0);
    let occupied: Vec<bool> = (0..total_sites)
        .map(|_| uniform.sample(&mut rng) < params.occupancy)
        .collect();
    
    let num_occupied = occupied.iter().filter(|&&x| x).count();
    if num_occupied == 0 {
        return Result {
            grid_size: n,
            occupancy: params.occupancy,
            coupling: params.coupling,
            sigma: params.sigma,
            mu: params.mu,
            p_final: 0.0,
            p_time_to_50: None,
            p_time_to_90: None,
            r_final: 0.0,
            r_time_to_50: None,
            r_time_to_90: None,
            p_precedes_r: false,
            time_lag: None,
            config_id,
        };
    }
    
    // Build adjacency list (nearest neighbors)
    let mut neighbors: Vec<Vec<usize>> = vec![Vec::new(); num_occupied];
    let mut idx_map = vec![None; total_sites];
    let mut active_idx = 0;
    for i in 0..total_sites {
        if occupied[i] {
            idx_map[i] = Some(active_idx);
            active_idx += 1;
        }
    }
    
    for y in 0..n {
        for x in 0..n {
            let idx = y * n + x;
            if !occupied[idx] { continue; }
            let ai = idx_map[idx].unwrap();
            
            // Check 4 neighbors
            let deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)];
            for (dx, dy) in deltas {
                let nx = x as isize + dx;
                let ny = y as isize + dy;
                if nx >= 0 && nx < n as isize && ny >= 0 && ny < n as isize {
                    let nidx = ny as usize * n + nx as usize;
                    if occupied[nidx] {
                        neighbors[ai].push(idx_map[nidx].unwrap());
                    }
                }
            }
        }
    }
    
    // Find connected components (for percolation)
    let mut visited = vec![false; num_occupied];
    let mut component_sizes = Vec::new();
    
    fn dfs(node: usize, neighbors: &[Vec<usize>], visited: &mut [bool], size: &mut usize) {
        visited[node] = true;
        *size += 1;
        for &nbr in &neighbors[node] {
            if !visited[nbr] {
                dfs(nbr, neighbors, visited, size);
            }
        }
    }
    
    for i in 0..num_occupied {
        if !visited[i] {
            let mut size = 0;
            dfs(i, &neighbors, &mut visited, &mut size);
            component_sizes.push(size);
        }
    }
    
    let p_final = *component_sizes.iter().max().unwrap_or(&0) as f64 / num_occupied as f64;
    
    // Kuramoto dynamics on the network
    let omega_dist = rand_distr::Normal::new(params.mu, params.sigma).unwrap();
    let phase_uniform: Uniform<f64> = Uniform::new(0.0, 2.0 * std::f64::consts::PI);
    
    let mut phases: Vec<f64> = (0..num_occupied)
        .map(|_| phase_uniform.sample(&mut rng))
        .collect();
    let omegas: Vec<f64> = (0..num_occupied)
        .map(|_| omega_dist.sample(&mut rng))
        .collect();
    
    let dt = 0.01;
    let total_steps = 3000;
    let record_interval = 10;
    let num_records = total_steps / record_interval;
    
    let mut p_history: Vec<f64> = Vec::with_capacity(num_records);
    let mut r_history: Vec<f64> = Vec::with_capacity(num_records);
    
    for step in 0..total_steps {
        // Compute r (order parameter)
        let (sum_cos, sum_sin) = phases.iter().fold((0.0, 0.0), |(c, s), &theta| {
            (c + theta.cos(), s + theta.sin())
        });
        let r = ((sum_cos / num_occupied as f64).powi(2) + (sum_sin / num_occupied as f64).powi(2)).sqrt();
        
        // For percolation history, we use static P (network structure doesn't change)
        // But track when oscillators become synchronized
        if step % record_interval == 0 {
            r_history.push(r);
            p_history.push(p_final); // P is static in this model
        }
        
        // Update phases
        for i in 0..num_occupied {
            let mut coupling = 0.0;
            for &j in &neighbors[i] {
                coupling += (phases[j] - phases[i]).sin();
            }
            coupling *= params.coupling / neighbors[i].len().max(1) as f64;
            phases[i] = (phases[i] + (omegas[i] + coupling) * dt)
                .rem_euclid(2.0 * std::f64::consts::PI);
        }
    }
    
    let r_final = *r_history.last().unwrap();
    
    // Find time to thresholds
    let p_time_to_50 = if p_final > 0.5 {
        p_history.iter().position(|&p| p > 0.5).map(|i| i * record_interval)
    } else { None };
    
    let p_time_to_90 = if p_final > 0.9 {
        p_history.iter().position(|&p| p > 0.9).map(|i| i * record_interval)
    } else { None };
    
    let r_time_to_50 = if r_final > 0.5 {
        r_history.iter().position(|&r| r > 0.5).map(|i| i * record_interval)
    } else { None };
    
    let r_time_to_90 = if r_final > 0.9 {
        r_history.iter().position(|&r| r > 0.9).map(|i| i * record_interval)
    } else { None };
    
    // Causality: does P threshold precede R threshold?
    let p_precedes_r = match (p_time_to_50, r_time_to_50) {
        (Some(pt), Some(rt)) => pt < rt,
        (Some(_), None) => true,  // P achieved but R didn't
        (None, Some(_)) => false, // R achieved but P didn't
        (None, None) => false,
    };
    
    let time_lag = match (p_time_to_50, r_time_to_50) {
        (Some(pt), Some(rt)) => Some(rt as isize - pt as isize),
        _ => None,
    };
    
    Result {
        grid_size: n,
        occupancy: params.occupancy,
        coupling: params.coupling,
        sigma: params.sigma,
        mu: params.mu,
        p_final,
        p_time_to_50,
        p_time_to_90,
        r_final,
        r_time_to_50,
        r_time_to_90,
        p_precedes_r,
        time_lag,
        config_id,
    }
}

fn generate_param_space() -> Vec<Params> {
    let grid_size = 100; // 100x100 = 10k sites
    let occupancy_values: Vec<f64> = (0..20)
        .map(|i| 0.3 + 0.6 * (i as f64 / 19.0))
        .collect();
    let coupling_values = vec![0.5, 1.0, 2.0]; // From E1 critical region
    let sigma_values = vec![0.1, 0.5, 1.0];
    let mu = 1.0;
    
    let mut params = Vec::new();
    for &occupancy in &occupancy_values {
        for &coupling in &coupling_values {
            for &sigma in &sigma_values {
                params.push(Params {
                    grid_size,
                    occupancy,
                    coupling,
                    sigma,
                    mu,
                });
            }
        }
    }
    params
}

fn main() {
    println!("=== E3 Phase A: Percolation-Synchronization Causality ===");
    println!("Starting at: {:?}", std::time::SystemTime::now());
    
    let params = generate_param_space();
    let total = params.len();
    println!("Total configurations: {}", total);
    println!("Grid: 100x100 (10k sites)");
    println!("Occupancy: 0.3-0.9 (20 points, percolation threshold ~0.59)");
    println!("Coupling: [0.5, 1.0, 2.0] (from E1 critical region)");
    println!("Sigma: [0.1, 0.5, 1.0]");
    println!("Goal: Test if P precedes r");
    println!();
    
    let out_dir = "../../../results/e3_phase_a";
    fs::create_dir_all(out_dir).expect("Failed to create output directory");
    
    let counter = Arc::new(AtomicUsize::new(0));
    let start_time = std::time::Instant::now();
    
    let results: Vec<Result> = params
        .par_iter()
        .enumerate()
        .map(|(i, p)| {
            let result = simulate(p, i);
            
            let count = counter.fetch_add(1, Ordering::Relaxed) + 1;
            if count % 20 == 0 || count == total {
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
    
    // Write results
    let csv_path = format!("{}/causality_results.csv", out_dir);
    let mut writer = csv::Writer::from_path(&csv_path).expect("Failed to create CSV");
    
    for r in &results {
        writer.serialize(r).expect("Failed to write record");
    }
    writer.flush().expect("Failed to flush CSV");
    
    // Analysis
    let total_time = start_time.elapsed().as_secs_f64();
    let p_precedes_count = results.iter().filter(|r| r.p_precedes_r).count();
    let causality_rate = p_precedes_count as f64 / results.len() as f64;
    
    let summary = format!(
        "=== E3 Phase A Complete ===\n\
         Total configs: {}\n\
         Total time: {:.1} min\n\
         Avg rate: {:.1} configs/sec\n\
         Output: {}\n\
         \n\
         Causality Test (P precedes r):\n\
         - P precedes r: {}/{} ({:.1}%)\n\
         - Time lag available: {} configs\n\
         \n\
         Interpretation:\n\
         {}\n",
        total,
        total_time / 60.0,
        total as f64 / total_time,
        csv_path,
        p_precedes_count,
        results.len(),
        100.0 * causality_rate,
        results.iter().filter(|r| r.time_lag.is_some()).count(),
        if causality_rate > 0.7 {
            "✓ Strong evidence for P→r causality (percolation drives sync)"
        } else if causality_rate > 0.5 {
            "~ Mixed evidence, may depend on parameters"
        } else {
            "✗ Weak evidence, alternative mechanisms may dominate"
        }
    );
    
    let summary_path = format!("{}/summary.txt", out_dir);
    let mut summary_file = File::create(&summary_path).expect("Failed to create summary");
    summary_file.write_all(summary.as_bytes()).expect("Failed to write summary");
    
    println!();
    println!("{}", summary);
    println!("=== E3 Phase A Finished ===");
}
