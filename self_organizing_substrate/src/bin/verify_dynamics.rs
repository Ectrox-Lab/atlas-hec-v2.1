//! 6个动力学现象验证
//! 
//! 验证目标不是benchmark分数，而是：
//! 1. 稳定attractors
//! 2. 记忆persistence  
//! 3. regime shift后重组
//! 4. cluster specialization
//! 5. global broadcast emergence
//! 6. failure → recovery

use self_organizing_substrate::verification::{self, VerificationResult};

fn main() {
    println!("╔════════════════════════════════════════════════════════════╗");
    println!("║  Self-Organizing Cognitive Substrate - Dynamics Verification ║");
    println!("╚════════════════════════════════════════════════════════════╝\n");
    
    println!("Running 6 emergence tests...\n");
    
    let results = verification::run_all_verifications();
    
    let mut passed = 0;
    let mut failed = 0;
    
    for result in &results {
        let status = if result.passed { "✓ PASS" } else { "✗ FAIL" };
        println!("{:<25} {}  {}", 
            result.test_name, 
            status,
            result.notes
        );
        
        for (metric, value) in &result.metrics {
            println!("    {}: {:.3}", metric, value);
        }
        println!();
        
        if result.passed {
            passed += 1;
        } else {
            failed += 1;
        }
    }
    
    println!("─────────────────────────────────────────────────────────────");
    println!("Results: {} passed, {} failed", passed, failed);
    
    if failed == 0 {
        println!("\n✓ All emergence tests PASSED - Substrate shows expected dynamics");
    } else {
        println!("\n✗ Some tests failed - Substrate needs tuning");
        std::process::exit(1);
    }
}
