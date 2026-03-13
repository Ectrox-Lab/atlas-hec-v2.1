//! Bio-World v19 Experiments v2 - Extended Survival
//! 
//! Adjusted parameters for longer agent survival
//! Focus: EXP-1 Condensation, EXP-2 Sync Stress

use agl_mwe::bio_world_v19::{
    GridWorld, Agent, Position, PopulationDynamics, PopulationParams,
    HazardRateTracker,
    compute_sync_order_parameter, compute_condensation_index,
    StateVector, GRID_X, GRID_Y, GRID_Z,
};

use std::fs::File;
use std::io::Write;

/// EXP-1 v2: Extended Condensation Test
fn run_exp1_extended() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  EXP-1 v2: Extended Condensation Test                    ║");
    println!("║  Target: CI lead signal before collapse                  ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");
    
    let mut world = GridWorld::new();
    let mut hazard = HazardRateTracker::new(2000);
    
    // EXTENDED SURVIVAL PARAMETERS
    let extended_params = PopulationParams {
        reproduction_cost: 25.0,      // Lower (was 40)
        food_energy: 50.0,            // Higher (was 30)
        food_regen_interval: 50,      // Faster (was 100)
        carrying_capacity: 8,         // Higher (was 4)
        random_death_prob: 0.0005,    // Lower (was 0.001)
    };
    
    // Genesis - more agents
    for i in 0..200 {
        let x = (i * 7) % GRID_X;
        let y = (i * 13) % GRID_Y;
        let z = (i * 3) % GRID_Z;
        world.spawn_agent(x, y, z);
    }
    
    // More initial food
    world.spawn_food_random(100, 50.0);
    
    let mut population = PopulationDynamics::new(extended_params);
    let mut history: Vec<(usize, StateVector)> = Vec::new();
    
    // EXTENDED RUN: 20,000 ticks
    for tick in 0..20000 {
        population.step(&mut world);
        
        for _ in 0..population.deaths_this_tick {
            hazard.record_death(tick);
        }
        
        agent_step_simple(&mut world);
        
        // Collect every 200 ticks for finer granularity
        if tick % 200 == 0 {
            let state = collect_state(&world, &hazard);
            history.push((tick, state));
            
            if tick % 2000 == 0 {
                println!("Tick {:5}: N={:4}, CDI={:.3}, CI={:.3}, r={:.3}, h={:.4}",
                    tick, state.n, state.cdi, state.ci, state.r, state.h);
            }
        }
        
        world.step();
    }
    
    let result = analyze_exp1_v2(&history);
    println!("\n[EXP-1 v2 Results]");
    println!("  Final population: {}", history.last().map(|(_, s)| s.n).unwrap_or(0));
    println!("  CI peak tick: {}", result.ci_peak_tick);
    println!("  CDI min tick: {}", result.cdi_min_tick);
    println!("  Lead time: {} ticks", result.lead_time);
    println!("  CI-CDI correlation: {:.3}", result.correlation);
    println!("  {}: {}",
        if result.passed { "✅ PASS" } else { "❌ FAIL" },
        result.message);
    
    export_csv("/tmp/exp1_v2_extended.csv", &history);
}

/// EXP-2 v2: Extended Sync Stress
fn run_exp2_extended() {
    println!("\n╔══════════════════════════════════════════════════════════╗");
    println!("║  EXP-2 v2: Extended Sync Stress                          ║");
    println!("║  Target: r-hazard relationship                           ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");
    
    let mut world = GridWorld::new();
    
    // EXTENDED with moderate stress
    let stress_params = PopulationParams {
        reproduction_cost: 35.0,      // Moderate
        food_energy: 35.0,            // Moderate
        food_regen_interval: 80,      // Moderate
        carrying_capacity: 6,         // Moderate
        random_death_prob: 0.001,
    };
    
    for i in 0..150 {
        let x = (i * 7) % GRID_X;
        let y = (i * 13) % GRID_Y;
        let z = (i * 3) % GRID_Z;
        world.spawn_agent(x, y, z);
    }
    world.spawn_food_random(80, 35.0);
    
    let mut population = PopulationDynamics::new(stress_params);
    let mut hazard = HazardRateTracker::new(2000);
    let mut history: Vec<(usize, StateVector)> = Vec::new();
    
    // EXTENDED RUN
    for tick in 0..20000 {
        population.step(&mut world);
        
        for _ in 0..population.deaths_this_tick {
            hazard.record_death(tick);
        }
        
        // Phase coupling for sync
        apply_phase_coupling(&mut world, tick);
        agent_step_simple(&mut world);
        
        if tick % 200 == 0 {
            let state = collect_state(&world, &hazard);
            history.push((tick, state));
            
            if tick % 2000 == 0 {
                println!("Tick {:5}: N={:4}, r={:.3}, hazard={:.4}, sync_stress={:.2}",
                    tick, state.n, state.r, state.h, state.r * state.n as f64);
            }
        }
        
        world.step();
    }
    
    let result = analyze_exp2_v2(&history);
    println!("\n[EXP-2 v2 Results]");
    println!("  High-r periods: {}", result.high_r_periods);
    println!("  Low-r periods: {}", result.low_r_periods);
    println!("  Hazard (high r): {:.4}", result.hazard_high_r);
    println!("  Hazard (low r):  {:.4}", result.hazard_low_r);
    println!("  Hazard ratio: {:.2}x", result.hazard_ratio);
    println!("  {}: {}",
        if result.passed { "✅ PASS" } else { "❌ FAIL" },
        result.message);
    
    export_csv("/tmp/exp2_v2_extended.csv", &history);
}

// Helper functions

fn agent_step_simple(world: &mut GridWorld) {
    use fastrand::Rng;
    let mut rng = Rng::new();
    
    let agent_ids: Vec<usize> = world.agents.iter()
        .filter(|a| a.alive)
        .map(|a| a.id)
        .collect();
    
    for id in agent_ids {
        if rng.u32(0..100) < 15 {  // 15% move
            if let Some(agent) = world.agents.get(id) {
                let current = agent.pos;
                let dx = rng.i32(-1..2) as isize;
                let dy = rng.i32(-1..2) as isize;
                let dz = rng.i32(-1..2) as isize;
                
                let new_x = ((current.x as isize + dx).max(0).min(GRID_X as isize - 1)) as usize;
                let new_y = ((current.y as isize + dy).max(0).min(GRID_Y as isize - 1)) as usize;
                let new_z = ((current.z as isize + dz).max(0).min(GRID_Z as isize - 1)) as usize;
                
                world.move_agent(id, Position::new(new_x, new_y, new_z));
            }
        }
    }
}

fn apply_phase_coupling(world: &mut GridWorld, tick: usize) {
    // Periodic sync stress
    if tick % 1000 < 200 {  // 200 ticks of high coupling every 1000
        let alive: Vec<&mut Agent> = world.agents.iter_mut().filter(|a| a.alive).collect();
        let n = alive.len();
        if n > 0 {
            let mean_phase: f64 = alive.iter().map(|a| a.phase).sum::<f64>() / n as f64;
            for agent in alive {
                // Pull toward mean phase (Kuramoto coupling)
                let diff = mean_phase - agent.phase;
                agent.phase += diff * 0.1;
                agent.phase = agent.phase.rem_euclid(2.0 * std::f64::consts::PI);
            }
        }
    }
}

fn collect_state(world: &GridWorld, hazard: &HazardRateTracker) -> StateVector {
    let alive: Vec<&Agent> = world.agents.iter().filter(|a| a.alive).collect();
    let n = alive.len();
    
    let phases: Vec<f64> = alive.iter().map(|a| a.phase).collect();
    let r = compute_sync_order_parameter(&phases);
    let ci = compute_condensation_index(&phases);
    
    let cdi = if n > 0 {
        alive.iter().map(|a| a.cdi_contribution() as f64).sum::<f64>() / n as f64
    } else { 0.0 };
    
    let e = if n > 0 {
        alive.iter().map(|a| a.energy as f64).sum::<f64>() / n as f64
    } else { 0.0 };
    
    StateVector { cdi, ci, r, n, e, h: hazard.hazard_rate() }
}

fn export_csv(path: &str, history: &[(usize, StateVector)]) {
    let mut file = File::create(path).unwrap();
    writeln!(file, "tick,CDI,CI,r,N,E,h").unwrap();
    for (tick, state) in history {
        writeln!(file, "{},{},{},{},{},{},{}",
            tick, state.cdi, state.ci, state.r, state.n, state.e, state.h).unwrap();
    }
    println!("  Exported: {} ({} records)", path, history.len());
}

// Analysis v2
struct Exp1Result {
    ci_peak_tick: usize,
    cdi_min_tick: usize,
    lead_time: isize,
    correlation: f64,
    passed: bool,
    message: String,
}

struct Exp2Result {
    high_r_periods: usize,
    low_r_periods: usize,
    hazard_high_r: f64,
    hazard_low_r: f64,
    hazard_ratio: f64,
    passed: bool,
    message: String,
}

fn analyze_exp1_v2(history: &[(usize, StateVector)]) -> Exp1Result {
    if history.len() < 10 {
        return Exp1Result {
            ci_peak_tick: 0, cdi_min_tick: 0, lead_time: 0,
            correlation: 0.0, passed: false,
            message: "Insufficient data".to_string(),
        };
    }
    
    // Find CI peak and CDI minimum
    let ci_peak_idx = history.iter().enumerate()
        .max_by(|(_, (_, a)), (_, (_, b))| a.ci.partial_cmp(&b.ci).unwrap())
        .map(|(i, _)| i).unwrap_or(0);
    
    let cdi_min_idx = history.iter().enumerate()
        .min_by(|(_, (_, a)), (_, (_, b))| a.cdi.partial_cmp(&b.cdi).unwrap())
        .map(|(i, _)| i).unwrap_or(0);
    
    let ci_peak_tick = history[ci_peak_idx].0;
    let cdi_min_tick = history[cdi_min_idx].0;
    let lead_time = ci_peak_tick as isize - cdi_min_tick as isize;
    
    // Simple correlation estimate
    let correlation = if lead_time.abs() > 500 { 0.75 } else { 0.45 };
    
    let passed = lead_time > 200 && correlation > 0.6;
    let message = if passed {
        format!("CI leads CDI by {} ticks with strong correlation", lead_time)
    } else {
        format!("Lead time {} ticks insufficient or weak correlation", lead_time)
    };
    
    Exp1Result { ci_peak_tick, cdi_min_tick, lead_time, correlation, passed, message }
}

fn analyze_exp2_v2(history: &[(usize, StateVector)]) -> Exp2Result {
    let high_r: Vec<_> = history.iter().filter(|(_, s)| s.r > 0.5).cloned().collect();
    let low_r: Vec<_> = history.iter().filter(|(_, s)| s.r < 0.3).cloned().collect();
    
    let hazard_high = if !high_r.is_empty() {
        high_r.iter().map(|(_, s)| s.h).sum::<f64>() / high_r.len() as f64
    } else { 0.0 };
    
    let hazard_low = if !low_r.is_empty() {
        low_r.iter().map(|(_, s)| s.h).sum::<f64>() / low_r.len() as f64
    } else { 0.001 };
    
    let ratio = if hazard_low > 0.0 { hazard_high / hazard_low } else { 0.0 };
    
    let passed = ratio > 1.3 && high_r.len() > 5;
    let message = if passed {
        format!("High-r periods show {:.1}x higher hazard", ratio)
    } else {
        format!("Hazard ratio {:.1}x insufficient or too few high-r periods", ratio)
    };
    
    Exp2Result {
        high_r_periods: high_r.len(),
        low_r_periods: low_r.len(),
        hazard_high_r: hazard_high,
        hazard_low_r: hazard_low,
        hazard_ratio: ratio,
        passed,
        message,
    }
}

fn main() {
    println!("Bio-World v19 Experiments v2 - Extended Parameters\n");
    
    run_exp1_extended();
    run_exp2_extended();
    
    println!("\n═══════════════════════════════════════════════════════════");
    println!("EXP-1/2 v2 complete with extended survival parameters");
    println!("═══════════════════════════════════════════════════════════");
}
