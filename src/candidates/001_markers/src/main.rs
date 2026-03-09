//! 001 Consistency Markers - Week 1 Sprint Runner

use markers_001::run_week1_experiment;

fn main() {
    println!("=== 001 Consistency Markers - Week 1 Experiment ===\n");
    
    // Run experiment
    let result = run_week1_experiment();
    
    // Print results
    println!("\n{:#?}", result);
    
    // Gate decision
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
