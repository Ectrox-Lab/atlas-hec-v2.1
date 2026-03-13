//! 001 Consistency Markers - FINAL DIAGNOSTIC EXPERIMENT

use markers_001::run_site_dissection_experiment;

fn main() {
    println!("=== 001 FINAL: Site-of-Action Dissection ===\n");
    println!("Testing where marker causes harm:\n");
    
    let results = run_site_dissection_experiment();
    
    // Analysis
    let baseline = results.iter().find(|(m, _, _)| matches!(m, markers_001::MarkerMode::Baseline)).unwrap();
    let write_only = results.iter().find(|(m, _, _)| matches!(m, markers_001::MarkerMode::WriteOnly)).unwrap();
    let read_only = results.iter().find(|(m, _, _)| matches!(m, markers_001::MarkerMode::ReadOnly)).unwrap();
    let full = results.iter().find(|(m, _, _)| matches!(m, markers_001::MarkerMode::Full)).unwrap();
    
    println!("\n=== DIAGNOSIS ===");
    
    // Test 1: Write path
    let write_harm = baseline.1 - write_only.1;
    println!("\n1. Write path harm: {:.3}", write_harm);
    if write_harm > 0.1 {
        println!("   → Write mechanism itself disturbs system");
    } else {
        println!("   → Write mechanism OK");
    }
    
    // Test 2: Read path
    let read_harm = baseline.1 - read_only.1;
    println!("\n2. Read path harm: {:.3}", read_harm);
    if read_harm > 0.1 {
        println!("   → Marker signal semantics wrong");
    } else {
        println!("   → Read mechanism OK");
    }
    
    // Test 3: Full coupling
    let full_harm = baseline.1 - full.1;
    println!("\n3. Full loop harm: {:.3}", full_harm);
    if full_harm > read_harm.max(write_harm) + 0.05 {
        println!("   → Closed-loop coupling unstable");
    }
    
    // Final verdict
    println!("\n=== VERDICT ===");
    if full_harm > 0.2 {
        if write_harm > 0.15 {
            println!("KILL: Write mechanism fundamentally harmful");
        } else if read_harm > 0.15 {
            println!("KILL: Marker signal semantics don't match task");
        } else {
            println!("KILL: Closed-loop coupling unstable");
        }
    } else {
        println!("UNCLEAR: Need more data");
    }
}
