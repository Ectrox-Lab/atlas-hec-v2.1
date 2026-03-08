//! Self Report Interface: 自我报告接口
//! 
//! 让系统能够外化自己的内部状态。
//! 第一次能说出："I exist."

use super::{SelfKernel, SelfState};

/// 自我报告生成器
pub struct SelfReport;

impl SelfReport {
    /// 生成 "我是谁" 报告
    /// 
    /// 这是最关键的函数：系统第一次能说出自己的身份。
    pub fn who_am_i(state: &SelfState) -> String {
        let uptime = state.identity.uptime_seconds();
        let hours = uptime / 3600;
        let minutes = (uptime % 3600) / 60;
        let seconds = uptime % 60;
        
        format!(
            "I am {}.\n\
             Created at: {} (Unix timestamp)\n\
             Uptime: {:02}h:{:02}m:{:02}s\n\
             Current step: {}\n\
             Energy level: {:.2}\n\
             Total reward: {:.2}\n\
             Neurons: {}",
            state.identity.id,
            state.identity.created_at,
            hours,
            minutes,
            seconds,
            state.step_count,
            state.energy_level,
            state.reward_total,
            state.neuron_count,
        )
    }
    
    /// 生成状态快照报告
    pub fn current_state(state: &SelfState) -> String {
        state.to_report()
    }
    
    /// 生成简短状态 (用于定期报告)
    pub fn brief_status(state: &SelfState) -> String {
        format!(
            "[{}] Step: {} | Energy: {:.2} | Reward: {:.2} | Action: {}",
            state.identity.id,
            state.step_count,
            state.energy_level,
            state.reward_total,
            state.last_action
        )
    }
    
    /// 生成格式化的自我报告 (用于打印)
    pub fn formatted_report(kernel: &SelfKernel) -> String {
        let mut report = String::new();
        
        // Header
        report.push_str("╔═══════════════════════════════════════════════════════════╗\n");
        report.push_str("║                    SELF KERNEL REPORT                     ║\n");
        report.push_str("╚═══════════════════════════════════════════════════════════╝\n\n");
        
        // Identity section
        report.push_str("IDENTITY:\n");
        report.push_str(&format!("  {}\n", kernel.state.identity.id));
        report.push_str(&format!("  Uptime: {} seconds\n\n", kernel.state.identity.uptime_seconds()));
        
        // State section
        report.push_str("CURRENT STATE:\n");
        report.push_str(&format!("  Step: {}\n", kernel.state.step_count));
        report.push_str(&format!("  Energy: {:.2}\n", kernel.state.energy_level));
        report.push_str(&format!("  Reward: {:.2} (avg: {:.4})\n", 
            kernel.state.reward_total,
            kernel.state.average_reward()));
        report.push_str(&format!("  Neurons: {}\n", kernel.state.neuron_count));
        report.push_str(&format!("  Last Action: {}\n\n", kernel.state.last_action));
        
        // Memory section
        report.push_str("AUTOBIOGRAPHICAL MEMORY:\n");
        report.push_str(&format!("  {}\n\n", kernel.memory.summary()));
        
        // Recent episodes
        if !kernel.memory.is_empty() {
            report.push_str("RECENT EPISODES:\n");
            for ep in kernel.memory.recent(3) {
                report.push_str(&format!("  - {}\n", ep.summary()));
            }
        }
        
        report
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::self_kernel::{Identity, AutobiographicalMemory};
    
    fn create_test_kernel() -> SelfKernel {
        let identity = Identity::new(1);
        let state = SelfState::new(identity);
        let memory = AutobiographicalMemory::new(100);
        
        SelfKernel { state, memory }
    }
    
    #[test]
    fn test_who_am_i() {
        let kernel = create_test_kernel();
        let report = SelfReport::who_am_i(&kernel.state);
        
        assert!(report.contains("atlas-v2.3-instance-001"));
        assert!(report.contains("Current step:"));
        assert!(report.contains("Energy level:"));
    }
    
    #[test]
    fn test_brief_status() {
        let kernel = create_test_kernel();
        let status = SelfReport::brief_status(&kernel.state);
        
        assert!(status.contains("atlas-v2.3-instance-001"));
        assert!(status.contains("Step:"));
        assert!(status.contains("Energy:"));
    }
}
