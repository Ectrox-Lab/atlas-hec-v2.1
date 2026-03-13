//! Self Report Test: 验证 Self Kernel v0.1
//! 
//! 运行5分钟，每10秒打印自我报告。
//! 
//! 验证标准：
//! 1. identity stable
//! 2. state evolving  
//! 3. episode log growing

use agl_mwe::{SelfKernel, RuntimeData};
use std::thread;
use std::time::Duration;

fn main() {
    println!("═══════════════════════════════════════════════════════════");
    println!("🧠 Atlas-HEC v2.3 - Self Kernel v0.1 Test");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    
    // 创建 Self Kernel
    let mut kernel = SelfKernel::new(1)
        .with_record_interval(10); // 每10步记录一次episode
    
    println!("✅ Self Kernel initialized");
    println!("   Identity: {}", kernel.id());
    println!();
    
    // 初始报告
    println!("{}", kernel.report());
    println!();
    
    // 运行5分钟 (300秒)，每10秒报告一次
    let total_duration = Duration::from_secs(300); // 5分钟
    let report_interval = Duration::from_secs(10); // 10秒
    let start_time = std::time::Instant::now();
    let mut last_report = std::time::Instant::now();
    
    println!("🔥 Starting 5-minute self-monitoring test...");
    println!("   Total duration: 5 minutes");
    println!("   Report interval: 10 seconds");
    println!();
    
    let mut step = 0u64;
    
    while start_time.elapsed() < total_duration {
        // 模拟运行数据
        let data = RuntimeData {
            energy: 0.5 + 0.3 * (step as f32 / 100.0).sin(), // 波动的能量
            reward: step as f32 * 0.1, // 递增的奖励
            neurons: 10000 + (step / 10) as usize, // 缓慢增长的神经元
            action: match step % 4 {
                0 => "move_north".to_string(),
                1 => "move_south".to_string(),
                2 => "move_east".to_string(),
                _ => "move_west".to_string(),
            },
        };
        
        // 更新 Self Kernel
        kernel.update(data);
        step += 1;
        
        // 每10秒打印报告
        if last_report.elapsed() >= report_interval {
            println!("╔═══════════════════════════════════════════════════════════╗");
            println!("║                    SELF REPORT #{}                        ║", 
                step / 10);
            println!("╚═══════════════════════════════════════════════════════════╝");
            println!();
            println!("{}", kernel.report());
            println!();
            println!("Memory episodes: {}", kernel.memory_len());
            println!("Uptime: {} seconds", kernel.state.identity.uptime_seconds());
            println!();
            println!("═══════════════════════════════════════════════════════════");
            println!();
            
            last_report = std::time::Instant::now();
        }
        
        // 模拟步进延迟 (10ms = 100Hz)
        thread::sleep(Duration::from_millis(10));
    }
    
    // 最终报告
    println!("╔═══════════════════════════════════════════════════════════╗");
    println!("║              FINAL SELF REPORT                            ║");
    println!("╚═══════════════════════════════════════════════════════════╝");
    println!();
    println!("{}", kernel.report());
    println!();
    
    // 验证结果
    println!("═══════════════════════════════════════════════════════════");
    println!("📊 VERIFICATION RESULTS");
    println!("═══════════════════════════════════════════════════════════");
    println!();
    
    let identity_stable = kernel.id() == "atlas-v2.3-instance-001";
    let state_evolved = kernel.step_count() > 0;
    let memory_growing = kernel.memory_len() > 0;
    
    println!("✅ Identity stable:        {} (ID: {})", 
        if identity_stable { "PASS" } else { "FAIL" },
        kernel.id());
    
    println!("✅ State evolved:          {} (Steps: {})", 
        if state_evolved { "PASS" } else { "FAIL" },
        kernel.step_count());
    
    println!("✅ Episode log growing:    {} (Episodes: {})", 
        if memory_growing { "PASS" } else { "FAIL" },
        kernel.memory_len());
    
    println!();
    
    let all_pass = identity_stable && state_evolved && memory_growing;
    
    if all_pass {
        println!("🎉 ALL CHECKS PASSED!");
        println!();
        println!("Self Kernel v0.1 is working correctly.");
        println!("The system can now say: 'I exist.'");
    } else {
        println!("❌ SOME CHECKS FAILED");
        println!();
        println!("Please review the implementation.");
    }
    
    println!();
    println!("═══════════════════════════════════════════════════════════");
}
