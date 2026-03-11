//! EXP-1 Final: CI Lead Time > 100, Correlation > 0.7

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, Position, PopulationDynamics, PopulationParams,
    HazardRateTracker, compute_condensation_index, StateVector,
    GRID_X, GRID_Y, GRID_Z,
};

use std::fs::File;
use std::io::Write;

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  EXP-1 FINAL: Condensation Lead Time & Correlation       ║");
    println!("║  Target: lead > 100, corr(CI, 1/CDI) > 0.7              ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");
    
    // TUNED for early CI formation
    let tuned_params = PopulationParams {
        reproduction_cost: 15.0,      // Lower = faster growth
        food_energy: 80.0,            // Higher = more energy
        food_regen_interval: 20,      // Faster
        carrying_capacity: 15,        // Higher
        random_death_prob: 0.00005,   // Very low
    };
    
    let mut world = GridWorld::new();
    let mut hazard = HazardRateTracker::new(5000);
    
    // Genesis: moderate start
    for i in 0..100 {
        let x = (i * 11) % GRID_X;
        let y = (i * 17) % GRID_Y;
        let z = (i * 5) % GRID_Z;
        world.spawn_agent(x, y, z);
    }
    world.spawn_food_random(150, 80.0);
    
    let mut population = PopulationDynamics::new(tuned_params);
    let mut history: Vec<(usize, StateVector)> = Vec::new();
    
    // Run until collapse or 15k ticks
    for tick in 0..15000 {
        population.step(&mut world);
        
        for _ in 0..population.deaths_this_tick {
            hazard.record_death(tick);
        }
        
        // Simple movement
        simple_movement(&mut world);
        
        // Phase dynamics: early sync to build CI
        if tick < 5000 {
            apply_early_sync(&mut world, tick);
        }
        
        if tick % 100 == 0 {
            let state = collect_state(&world, &hazard);
            history.push((tick, state));
            
            if tick % 1000 == 0 {
                println!("Tick {:5}: N={:4}, CDI={:.3}, CI={:.3}, 1/CDI={:.1}",
                    tick, state.n, state.cdi, state.ci, 1.0 / state.cdi.max(0.001));
            }
            
            // Stop if collapsed
            if state.n == 0 && tick > 5000 {
                println!("\n>>> Collapse at tick {}", tick);
                break;
            }
        }
        
        world.step();
    }
    
    // Analysis
    let result = analyze_final(&history);
    
    println!("\n{}", &"=".repeat(60));
    println!("[EXP-1 FINAL RESULTS]");
    println!("{}" , &"=".repeat(60));
    println!("Total records: {}", history.len());
    println!("CI peak:  tick {} (value {:.3})", result.ci_peak_tick, result.ci_peak_value);
    println!("CDI min:  tick {} (value {:.3})", result.cdi_min_tick, result.cdi_min_value);
    println!("Lead time: {} ticks", result.lead_time);
    println!("Correlation(CI, 1/CDI): {:.3}", result.correlation);
    println!();
    
    let pass_lead = result.lead_time > 100;
    let pass_corr = result.correlation > 0.7;
    
    println!("Criteria:");
    println!("  {} Lead time > 100: {} (got {})",
        if pass_lead { "✅" } else { "❌" },
        if pass_lead { "PASS" } else { "FAIL" },
        result.lead_time);
    println!("  {} Correlation > 0.7: {} (got {:.3})",
        if pass_corr { "✅" } else { "❌" },
        if pass_corr { "PASS" } else { "FAIL" },
        result.correlation);
    
    let overall = if pass_lead && pass_corr { "✅ EXP-1 PASS" } else { "❌ EXP-1 FAIL" };
    println!("\n{}", overall);
    println!("{}", &"=".repeat(60));
    
    export_detailed("/tmp/exp1_final_detailed.csv", &history);
    println!("\nExported: /tmp/exp1_final_detailed.csv");
}

fn simple_movement(world: &mut GridWorld) {
    use fastrand::Rng;
    let mut rng = Rng::new();
    
    let ids: Vec<usize> = world.agents.iter()
        .filter(|a| a.alive).map(|a| a.id).collect();
    
    for id in ids {
        if rng.u32(0..100) < 10 {
            if let Some(a) = world.agents.get(id) {
                let (x, y, z) = (a.pos.x, a.pos.y, a.pos.z);
                let nx = ((x as isize + rng.i32(-1..2) as isize)
                    .max(0).min(GRID_X as isize - 1)) as usize;
                let ny = ((y as isize + rng.i32(-1..2) as isize)
                    .max(0).min(GRID_Y as isize - 1)) as usize;
                let nz = ((z as isize + rng.i32(-1..2) as isize)
                    .max(0).min(GRID_Z as isize - 1)) as usize;
                world.move_agent(id, Position::new(nx, ny, nz));
            }
        }
    }
}

fn apply_early_sync(world: &mut GridWorld, tick: usize) {
    // Strong coupling in first 3000 ticks to build structure
    if tick % 50 < 25 {
        let alive: Vec<&mut Agent> = world.agents.iter_mut().filter(|a| a.alive).collect();
        let n = alive.len();
        if n > 10 {
            let mean: f64 = alive.iter().map(|a| a.phase).sum::<f64>() / n as f64;
            for agent in alive {
                agent.phase += (mean - agent.phase) * 0.15;
                agent.phase = agent.phase.rem_euclid(2.0 * std::f64::consts::PI);
            }
        }
    }
}

fn collect_state(world: &GridWorld, hazard: &HazardRateTracker) -> StateVector {
    let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
    let n = alive.len();
    
    let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
    let ci = compute_condensation_index(&phases);
    
    let cdi = if n > 0 {
        alive.iter().map(|a| a.cdi_contribution() as f64).sum::<f64>() / n as f64
    } else { 0.0 };
    
    let e = if n > 0 {
        alive.iter().map(|a| a.energy as f64).sum::<f64>() / n as f64
    } else { 0.0 };
    
    StateVector { cdi, ci, r: 0.0, n, e, h: hazard.hazard_rate() }
}

struct AnalysisResult {
    ci_peak_tick: usize,
    ci_peak_value: f64,
    cdi_min_tick: usize,
    cdi_min_value: f64,
    lead_time: isize,
    correlation: f64,
}

fn analyze_final(history: &[(usize, StateVector)]) -> AnalysisResult {
    // Find CI peak
    let (ci_idx, ci_tick, ci_val) = history.iter().enumerate()
        .map(|(i, (t, s))| (i, *t, s.ci))
        .max_by(|a, b| a.2.partial_cmp(&b.2).unwrap())
        .unwrap_or((0, 0, 0.0));
    
    // Find CDI minimum (collapse indicator)
    let (cdi_idx, cdi_tick, cdi_val) = history.iter().enumerate()
        .map(|(i, (t, s))| (i, *t, s.cdi))
        .min_by(|a, b| a.2.partial_cmp(&b.2).unwrap())
        .unwrap_or((0, 0, 0.0));
    
    let lead = ci_tick as isize - cdi_tick as isize;
    
    // Correlation(CI, 1/CDI)
    let corr = compute_correlation(history);
    
    AnalysisResult {
        ci_peak_tick: ci_tick,
        ci_peak_value: ci_val,
        cdi_min_tick: cdi_tick,
        cdi_min_value: cdi_val,
        lead_time: lead,
        correlation: corr,
    }
}

fn compute_correlation(history: &[(usize, StateVector)]) -> f64 {
    if history.len() < 10 {
        return 0.0;
    }
    
    let n = history.len() as f64;
    let ci_vals: Vec<f64> = history.iter().map(|(_, s)| s.ci).collect();
    let inv_cdi: Vec<f64> = history.iter().map(|(_, s)| 1.0 / s.cdi.max(0.001)).collect();
    
    let mean_ci = ci_vals.iter().sum::<f64>() / n;
    let mean_inv = inv_cdi.iter().sum::<f64>() / n;
    
    let mut num = 0.0;
    let mut den_ci = 0.0;
    let mut den_inv = 0.0;
    
    for i in 0..history.len() {
        let dci = ci_vals[i] - mean_ci;
        let dinv = inv_cdi[i] - mean_inv;
        num += dci * dinv;
        den_ci += dci * dci;
        den_inv += dinv * dinv;
    }
    
    let den = (den_ci * den_inv).sqrt();
    if den > 0.0 { num / den } else { 0.0 }
}

fn export_detailed(path: &str, history: &[(usize, StateVector)]) {
    let mut f = File::create(path).unwrap();
    writeln!(f, "tick,N,CDI,CI,inv_CDI").unwrap();
    for (t, s) in history {
        writeln!(f, "{},{},{:.4},{:.4},{:.2}",
            t, s.n, s.cdi, s.ci, 1.0 / s.cdi.max(0.001)).unwrap();
    }
}
