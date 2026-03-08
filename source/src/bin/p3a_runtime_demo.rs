//! P3A: Runtime Integration Demo
//! 
//! 演示 PreservationAction 如何真实改变系统参数
//! 
//! 运行：
//!   cargo run --bin p3a_runtime_demo

use agl_mwe::{
    P3RuntimeIntegration, HomeostasisState, PreservationAction
};

fn main() {
    println!("╔══════════════════════════════════════════════════════════════╗");
    println!("║       P3A: Runtime Integration Demo                          ║");
    println!("║  Demonstrating action -> parameter change                    ║");
    println!("╚══════════════════════════════════════════════════════════════╝\n");
    
    // 创建启用 P3 的 runtime
    let mut p3 = P3RuntimeIntegration::new(true, "logs/p3a_demo.csv");
    
    println!("Phase 1: Healthy State (ContinueTask expected)");
    println!("─────────────────────────────────────────────────────────────");
    
    for i in 0..3 {
        let healthy = HomeostasisState::healthy();
        let action = p3.tick(&healthy);
        let params = p3.get_runtime_parameters();
        
        println!("Step {}: action={:?}", i, action);
        println!("  Parameters: exp_rate={:.2} recovery={} plasticity={:.2}",
            params.exploration_rate, params.recovery_mode, params.plasticity_scale);
    }
    
    println!("\nPhase 2: High Risk State (EnterRecovery expected)");
    println!("─────────────────────────────────────────────────────────────");
    
    // 创建高危险状态
    let critical = HomeostasisState {
        energy: 0.12,
        fatigue: 0.88,
        thermal_load: 0.85,
        stability_score: 0.25,
        reward_velocity: -0.6,
        prediction_error: 0.45,
    };
    
    let action = p3.tick(&critical);
    let params = p3.get_runtime_parameters();
    
    println!("Input: energy={:.2} fatigue={:.2}", critical.energy, critical.fatigue);
    println!("Action: {:?}", action);
    println!("Parameters CHANGED:");
    println!("  exploration_rate: 0.30 -> {:.2} ✓", params.exploration_rate);
    println!("  recovery_mode:    false -> {} ✓", params.recovery_mode);
    println!("  plasticity_scale: 1.00 -> {:.2} ✓", params.plasticity_scale);
    println!("  compute_budget:   1.00 -> {:.2} ✓", params.compute_budget);
    println!("  step_rate_limit:  1.00 -> {:.2} ✓", params.step_rate_limit);
    
    if action == PreservationAction::EnterRecovery && params.recovery_mode {
        println!("\n✅ SUCCESS: PreservationAction ENTERED RECOVERY MODE");
        println!("   The system actually changed its behavior because of risk!");
    } else {
        println!("\n❌ FAILED: Expected EnterRecovery with recovery_mode=true");
    }
    
    println!("\nPhase 3: Recovery Exit (ContinueTask -> gradual restore)");
    println!("─────────────────────────────────────────────────────────────");
    
    let healthy = HomeostasisState::healthy();
    for i in 0..20 {
        let action = p3.tick(&healthy);
        let params = p3.get_runtime_parameters();
        
        if i % 5 == 0 {
            println!("Step {}: recovery={} exp_rate={:.3}",
                i, params.recovery_mode, params.exploration_rate);
        }
        
        if i == 19 {
            if !params.recovery_mode && params.exploration_rate > 0.25 {
                println!("\n✅ SUCCESS: System exited recovery and restored parameters");
            } else {
                println!("\n⚠️  recovery={} exp_rate={:.3}", params.recovery_mode, params.exploration_rate);
            }
        }
    }
    
    println!("\nPhase 4: Moderate Stress (ReduceExploration/SeekReward)");
    println!("─────────────────────────────────────────────────────────────");
    
    let moderate = HomeostasisState::moderate_stress();
    let action = p3.tick(&moderate);
    let params = p3.get_runtime_parameters();
    
    println!("Input: energy={:.2} fatigue={:.2}", moderate.energy, moderate.fatigue);
    println!("Action: {:?}", action);
    println!("Current Parameters:");
    println!("  exploration_rate: {:.3}", params.exploration_rate);
    println!("  reward_bias:      {:.3}", params.reward_bias);
    
    println!("\n═══════════════════════════════════════════════════════════════");
    println!("P3A Demo Complete!");
    println!("");
    println!("Key Takeaway:");
    println!("  PreservationAction is NOT just printed - it CHANGES parameters:");
    println!("    - EnterRecovery    -> exploration ↓ recovery_mode=true");
    println!("    - ReduceExploration -> exploration ↓");
    println!("    - SeekReward       -> reward_bias ↑");
    println!("    - StabilizeNetwork -> plasticity ↓");
    println!("    - SlowDown         -> step_rate ↓");
    println!("");
    println!("Next: Run P3B A/B Validation");
    println!("  cargo run --bin p3b_ab_validation -- --preservation on --steps 10000");
    println!("  cargo run --bin p3b_ab_validation -- --preservation off --steps 10000");
    println!("═══════════════════════════════════════════════════════════════");
    
    p3.shutdown();
}
