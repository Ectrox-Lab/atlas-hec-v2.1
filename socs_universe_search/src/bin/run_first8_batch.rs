//! 运行第一批8组实验
//! 
//! 8 plans × 3 seeds = 24 universes
//! 
//! 运行: cargo run --bin run_first8_batch --release

use socs_universe_search::search_scheduler::run_first8_batch;

fn main() -> anyhow::Result<()> {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║     SOCS Universe Search v0.1 - First 8 Batch              ║");
    println!("║     5 Families × 8 Stress Profiles × 3 Seeds = 24          ║");
    println!("╚════════════════════════════════════════════════════════════╝");
    println!();
    
    // 运行批次
    run_first8_batch()?;
    
    println!();
    println!("✓ All done. Check outputs/ directory for results.");
    
    Ok(())
}
