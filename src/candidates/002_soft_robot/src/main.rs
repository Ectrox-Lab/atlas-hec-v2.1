//! 002 Soft Robot - Week 1 Sprint Runner

use soft_robot_002::run_week1_experiment;
use soft_robot_002::save_results;
use soft_robot_002::analyze_for_gate;

fn main() {
    println!("=== 002 Soft Robot - Week 1 Experiment ===\n");
    
    // Run experiment
    let results = run_week1_experiment(5);  // 5 trials per condition
    
    // Save results
    if let Err(e) = save_results(&results, "week1_results.csv") {
        eprintln!("Failed to save results: {}", e);
    }
    
    // Analyze for gate
    let decision = analyze_for_gate(&results);
    
    match decision {
        soft_robot_002::experiment::GateDecision::Continue => {
            println!("\n✓ Week 1 PASSED - Proceeding to Week 2");
            std::process::exit(0);
        }
        soft_robot_002::experiment::GateDecision::Kill => {
            println!("\n✗ Week 1 FAILED - Kill signal received");
            std::process::exit(1);
        }
    }
}
