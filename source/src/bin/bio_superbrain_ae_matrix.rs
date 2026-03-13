//! Bio-World × Superbrain A-E Experiment Matrix Runner
//!
//! Runs minimal A-E experiment matrix to validate integration.
//! A: Survival | B: Evolution | C: Stress | D: Collaboration | E: Akashic

use agl_mwe::bio_superbrain_interface::{run_matrix, RunConfig};

fn main() {
    println!("\n{}", "=".repeat(70));
    println!("BIO-WORLD × SUPERBRAIN A-E EXPERIMENT MATRIX");
    println!("MVP Configuration | 8 Universes | 10,000 Ticks");
    println!("{}", "=".repeat(70));
    
    let config = RunConfig::mvp();
    
    println!("\nConfig:");
    println!("  Grid: {}x{}x{}", config.grid_size.0, config.grid_size.1, config.grid_size.2);
    println!("  Universes: {}", config.universe_count);
    println!("  Ticks: {}", config.total_ticks);
    println!("  Seeds: {:?}", &config.seeds[..4]);
    
    println!("\n{}", "-".repeat(70));
    println!("Running A-E Matrix...");
    println!("{}", "-".repeat(70));
    
    let results = run_matrix(&config);
    
    println!("\n{}", "=".repeat(70));
    println!("RESULTS SUMMARY");
    println!("{}", "=".repeat(70));
    
    let mut pass_count = 0;
    let mut total_cdi = 0.0;
    
    for result in &results {
        let status = if result.success { "✅ PASS" } else { "❌ FAIL" };
        println!("\n{}: {}", result.experiment, status);
        println!("  Population: {} (rate: {:.1}%)", 
            result.final_population, 
            result.survival_rate * 100.0);
        println!("  CDI: {:.3}", result.cdi_final);
        println!("  Notes: {}", result.notes);
        
        if result.success {
            pass_count += 1;
        }
        total_cdi += result.cdi_final;
    }
    
    let avg_cdi = total_cdi / results.len() as f32;
    
    println!("\n{}", "-".repeat(70));
    println!("OVERALL: {}/{} experiments pass", pass_count, results.len());
    println!("Average CDI: {:.3}", avg_cdi);
    
    // Decision gate
    println!("\n{}", "=".repeat(70));
    println!("DECISION GATE");
    println!("{}", "=".repeat(70));
    
    if pass_count >= 4 {
        println!("✅ A-D BASICALLY PASS");
        if results[4].cdi_final > 0.0 || results[4].success {
            println!("✅ E HAS POSITIVE SIGNAL");
            println!("\n→ RECOMMENDATION: Upgrade to C (Bio-World v19 core)");
        } else {
            println!("⚠️  E WEAK");
            println!("\n→ RECOMMENDATION: Strengthen B (Causal Archive)");
        }
    } else if pass_count >= 3 {
        println!("⚠️  A-C PASS, D/E WEAK");
        println!("\n→ RECOMMENDATION: Strengthen B (choose one:");
        println!("  - Causal Archive cross-universe");
        println!("  - CDI/CI/r/P state vector");
        println!("  - Network cohesion/sync/percolation)");
    } else {
        println!("❌ A-C FAIL");
        println!("\n→ RECOMMENDATION: Debug CellAdapter/Lineage/StrategyBridge");
    }
    
    println!("{}", "=".repeat(70));
}
