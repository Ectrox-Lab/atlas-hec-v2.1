//! Bio-World × Superbrain - Research Scale Retention Test
//! 
//! Option 1 Gate: Verify A-E signals persist at 50× scale
//! Configuration: 50×50×16 grid, 128 universes, 100k ticks
//! 
//! This is a PRE-v19 test. Uses stub simulation to validate:
//! 1. Infrastructure can handle research scale
//! 2. A-E experiment patterns persist
//! 3. Computational overhead is acceptable
//!
//! Decision: If PASS → Proceed to v19 modules (Option 2)
//!          If FAIL → Debug scaling before adding complexity

use agl_mwe::bio_superbrain_interface::{RunConfig, run_matrix};

fn main() {
    println!("╔══════════════════════════════════════════════════════════╗");
    println!("║  Bio-World × Superbrain - Research Scale Retention Test  ║");
    println!("║  Option 1 Gate: 50× scale before v19 modules             ║");
    println!("╚══════════════════════════════════════════════════════════╝\n");

    // Run MVP first as sanity check
    println!("[Phase 1] MVP Sanity Check (20×20×4, 8 universes, 10k ticks)");
    let mvp_config = RunConfig::mvp();
    println!("  Config: grid={:?}, universes={}, ticks={}", 
        mvp_config.grid_size, mvp_config.universe_count, mvp_config.total_ticks);
    
    let mvp_results = run_matrix(&mvp_config);
    let mvp_passes = mvp_results.iter().filter(|r| r.success).count();
    println!("  Result: {}/5 PASS\n", mvp_passes);
    
    if mvp_passes < 5 {
        println!("❌ MVP FAILED - Cannot proceed to research scale");
        std::process::exit(1);
    }

    // Research scale test
    println!("[Phase 2] Research Scale Test (50×50×16, 128 universes, 100k ticks)");
    let research_config = RunConfig::research();
    println!("  Config: grid={:?}, universes={}, ticks={}", 
        research_config.grid_size, research_config.universe_count, research_config.total_ticks);
    println!("  Scale factors: {}× grid volume, {}× universes, {}× duration",
        (50*50*16)/(20*20*4), 128/8, 100000/10000);
    
    let start = std::time::Instant::now();
    let research_results = run_matrix(&research_config);
    let elapsed = start.elapsed();
    
    let research_passes = research_results.iter().filter(|r| r.success).count();
    
    println!("\n  Execution time: {:.2}s", elapsed.as_secs_f32());
    println!("  Result: {}/5 PASS", research_passes);
    
    // Detailed results
    println!("\n[Results] A-E Matrix at Research Scale:");
    for result in &research_results {
        let status = if result.success { "✅ PASS" } else { "❌ FAIL" };
        println!("  {}: {} (pop={}, survival={:.1}%, CDI={:.3})",
            status, result.experiment, result.final_population,
            result.survival_rate * 100.0, result.cdi_final);
    }
    
    // Signal retention check
    let d_collab = research_results.iter()
        .find(|r| r.experiment == "D-Collaboration")
        .expect("D-Collaboration required");
    
    let signal_retained = d_collab.survival_rate > 1.0;
    
    println!("\n[Signal Retention Check]");
    println!("  D-Collaboration growth: {:.1}% {}",
        (d_collab.survival_rate - 1.0) * 100.0,
        if signal_retained { "✅ RETAINED" } else { "❌ LOST" });
    
    // Decision gate output
    println!("\n╔══════════════════════════════════════════════════════════╗");
    if research_passes == 5 && signal_retained {
        println!("║  ✅ DECISION: Proceed to v19 modules (Option 2)          ║");
        println!("║     A-E signals retained at research scale               ║");
        println!("╚══════════════════════════════════════════════════════════╝");
        std::process::exit(0);
    } else {
        println!("║  ❌ DECISION: Debug scaling issues before v19            ║");
        println!("║     A-E signals degraded at research scale               ║");
        println!("╚══════════════════════════════════════════════════════════╝");
        std::process::exit(1);
    }
}
