//! 001 Consistency Markers - Week 1 Sprint Runner

use markers_001::{run_week1_experiment, run_timescale_comparison, run_ablation_test};

fn main() {
    println!("=== 001 Consistency Markers - Week 1 Experiment ===\n");
    
    // 1. Basic experiment
    println!("--- Basic Experiment ---");
    let result = run_week1_experiment();
    println!("\n{:#?}", result);
    
    // 2. Timescale comparison
    println!("\n--- Timescale Comparison (1x/5x/10x/20x) ---");
    let timescale_results = run_timescale_comparison();
    
    // Find optimal
    let optimal = timescale_results.iter()
        .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .unwrap();
    println!("Optimal timescale: {}x (consistency={:.3})", optimal.0, optimal.1);
    
    // 3. Ablation test
    println!("\n--- Ablation Test (Full vs Ablated) ---");
    let (full, ablated) = run_ablation_test();
    println!("Full:    consistency={:.3}, coop={:.2}", 
        full.with_markers_consistency, full.with_markers_coop);
    println!("Ablated: consistency={:.3}, coop={:.2}", 
        ablated.with_markers_consistency, ablated.with_markers_coop);
    
    let ablation_delta = full.with_markers_consistency - ablated.with_markers_consistency;
    println!("Ablation delta: {:.3} (positive = marker effect)", ablation_delta);
    
    // Gate decision
    println!("\n--- Gate Decision ---");
    let decision = result.gate_decision();
    
    match decision {
        "CONTINUE" => {
            println!("\n✓ Week 1 PASSED - Proceeding to Week 2");
            std::process::exit(0);
        }
        _ => {
            println!("\n✗ Week 1 FAILED - Kill signal received");
            std::process::exit(1);
        }
    }
}
