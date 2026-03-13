//! P2 Self Preservation Smoke Test
//!
//! 验证 P2 最小闭环: 从健康状态到危险状态的行为切换。

use agl_mwe::self_preservation::homeostasis::HomeostasisState;
use agl_mwe::self_preservation::SelfPreservationKernel;

fn main() {
    println!("═══════════════════════════════════════════════════════════");
    println!("🛡️  P2 Self Preservation Kernel - Smoke Test");
    println!("═══════════════════════════════════════════════════════════");
    println!();

    // 使用较低的恢复阈值以确保测试覆盖所有路径
    let policy = agl_mwe::self_preservation::PreservationPolicy::with_thresholds(0.60, 0.40);
    let mut spk = SelfPreservationKernel::new().with_policy(policy);

    // 三个测试状态: 健康 -> 压力 -> 危险
    let states = [
        HomeostasisState::healthy(),
        HomeostasisState::moderate_stress(),
        HomeostasisState::high_risk(),
    ];

    println!("Testing state transitions...\n");

    for (i, s) in states.iter().enumerate() {
        let action = spk.step(s);
        let risk = spk.last_risk().unwrap();

        println!("[{}] State: {}", i, s.to_report());
        println!("    Risk: {} (dominant: {})",
            risk.to_report(),
            risk.dominant_factor
        );
        println!("    Action: {:?}", action);
        println!("    Explanation: {}", spk.why_did_i_change_behavior());
        println!();
    }

    println!("═══════════════════════════════════════════════════════════");
    println!("📊 Verification");
    println!("═══════════════════════════════════════════════════════════");
    println!();

    // 验证标准检查
    let metrics = spk.metrics();
    let steps = metrics.total_steps();
    let interventions = metrics.intervention_steps();
    let intervention_rate = metrics.intervention_rate();

    println!("Total steps: {}", steps);
    println!("Intervention steps: {}", interventions);
    println!("Intervention rate: {:.1}%", intervention_rate * 100.0);
    println!();

    // 检查: 高危险时应该触发干预
    let last_action = spk.last_action().unwrap();
    let is_recovery = last_action == agl_mwe::self_preservation::PreservationAction::EnterRecovery;

    println!("✅ Last state is high risk -> action is EnterRecovery: {}",
        if is_recovery { "PASS" } else { "FAIL" });

    // 检查: 风险上升时干预率应该提高
    let has_interventions = interventions > 0;
    println!("✅ Interventions occurred during risk escalation: {}",
        if has_interventions { "PASS" } else { "FAIL" });

    println!();
    println!("{}", spk.to_report());

    println!("═══════════════════════════════════════════════════════════");
    if is_recovery && has_interventions {
        println!("🎉 P2 Smoke Test PASSED!");
        println!("   Self-preservation loop is working.");
        println!("   System switches behavior based on predicted risk.");
    } else {
        println!("❌ P2 Smoke Test FAILED");
        println!("   System is not responding correctly to risk.");
    }
    println!("═══════════════════════════════════════════════════════════");
}
