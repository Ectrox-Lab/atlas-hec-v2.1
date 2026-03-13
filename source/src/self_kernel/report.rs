//! Self Report Interface: 自我报告接口
//! 
//! 让系统能够外化自己的内部状态。
//! 核心功能：
//! - who_am_i(): "我是谁"
//! - what_did_i_just_do(): "我刚才做了什么"
//! - what_if_i_continue(): "如果我继续会怎样"

use crate::self_kernel::{Identity, InternalState, SelfKernel, SelfHistoryWindow, SelfPredictor};
use crate::self_kernel::predictor::PredictedState;

/// 自我报告 trait
pub trait SelfReport {
    /// 回答"我是谁"
    fn who_am_i(&self) -> String;
    
    /// 回答"我刚才做了什么"
    fn what_did_i_just_do(&self) -> String;
    
    /// 回答"如果我继续会怎样"
    fn what_if_i_continue(&self, projected_steps: u64) -> String;
    
    /// 格式化完整报告
    fn formatted_report(&self) -> String;
    
    /// 简短状态
    fn brief_status(&self) -> String;
}

impl SelfReport for SelfKernel {
    fn who_am_i(&self) -> String {
        let identity = &self.identity;
        let state = &self.state;
        
        format!(
            "I am {}. step={}, energy={:.3}, reward_total={:.3}, neurons={}, mode={}, env={}",
            identity.id,
            state.step_count,
            state.energy_level,
            state.reward_total,
            state.neuron_count,
            state.current_mode,
            state.environment_tag
        )
    }
    
    fn what_did_i_just_do(&self) -> String {
        match self.history.latest() {
            Some(r) => format!(
                "I just did action='{}' at step={} with reward_delta={:.3}, energy={:.3}, active_neurons={}",
                r.action, r.step, r.reward_delta, r.energy_level, r.active_neuron_count
            ),
            None => "I have no recent action history yet.".to_string(),
        }
    }
    
    fn what_if_i_continue(&self, projected_steps: u64) -> String {
        let p: PredictedState = self.predict_if_continue(projected_steps, None);
        
        format!(
            "If I continue for {} steps with action='{}', \
             predicted_energy={:.3}, predicted_reward_total={:.3}, \
             predicted_mode={}, confidence={:.2}. {}",
            p.projected_steps,
            p.assumed_action,
            p.predicted_energy_level,
            p.predicted_reward_total,
            p.predicted_mode,
            p.confidence,
            p.rationale
        )
    }
    
    fn formatted_report(&self) -> String {
        let mut report = String::new();
        
        // Header
        report.push_str("╔═══════════════════════════════════════════════════════════╗\n");
        report.push_str("║                    SELF KERNEL REPORT                     ║\n");
        report.push_str("╚═══════════════════════════════════════════════════════════╝\n\n");
        
        // Identity section
        report.push_str("IDENTITY:\n");
        report.push_str(&format!("  {}\n", self.identity.id));
        report.push_str(&format!("  Instance: {}\n", self.identity.instance));
        report.push_str(&format!("  Created: {}\n", self.identity.created_at));
        report.push_str(&format!("  Uptime: {} seconds\n\n", self.identity.uptime_seconds()));
        
        // State section
        report.push_str("CURRENT STATE:\n");
        report.push_str(&format!("  Step: {}\n", self.state.step_count));
        report.push_str(&format!("  Energy: {:.3}\n", self.state.energy_level));
        report.push_str(&format!("  Reward: {:.3} (avg: {:.4})\n", 
            self.state.reward_total,
            self.state.average_reward()));
        report.push_str(&format!("  Neurons: {} (active: {})\n", 
            self.state.neuron_count,
            self.state.active_neuron_count));
        report.push_str(&format!("  Mode: {}\n", self.state.current_mode));
        report.push_str(&format!("  Environment: {}\n", self.state.environment_tag));
        report.push_str(&format!("  Last Action: {}\n\n", self.state.last_action));
        
        // Goals section
        report.push_str("ACTIVE GOALS:\n");
        let active_goals: Vec<_> = self.goals.active_goals().collect();
        if active_goals.is_empty() {
            report.push_str("  (no active goals)\n");
        } else {
            for goal in active_goals {
                report.push_str(&format!("  - [{}] {}\n", goal.id, goal.description));
            }
        }
        report.push_str("\n");
        
        // History section
        report.push_str("HISTORY:\n");
        report.push_str(&format!("  {}\n\n", self.history.summary()));
        
        // Recent actions
        if !self.history.is_empty() {
            report.push_str("RECENT ACTIONS:\n");
            for record in self.history.recent(3) {
                report.push_str(&format!("  - {}\n", record.summary()));
            }
        }
        
        report
    }
    
    fn brief_status(&self) -> String {
        format!(
            "[{}] Step: {} | Energy: {:.2} | Reward: {:.2} | Action: {} | Mode: {}",
            self.identity.id,
            self.state.step_count,
            self.state.energy_level,
            self.state.reward_total,
            self.state.last_action,
            self.state.current_mode
        )
    }
}

/// 兼容旧版的SelfReport实现
pub struct SelfReportOld;

impl SelfReportOld {
    /// 生成 "我是谁" 报告 (旧版格式)
    pub fn who_am_i_old(state: &InternalState, identity: &Identity) -> String {
        let uptime = identity.uptime_seconds();
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
            identity.id,
            identity.created_at,
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
    pub fn current_state(state: &InternalState) -> String {
        state.to_report()
    }
    
    /// 简短状态 (旧版)
    pub fn brief_status_old(state: &InternalState, identity: &Identity) -> String {
        format!(
            "[{}] Step: {} | Energy: {:.2} | Reward: {:.2} | Action: {}",
            identity.id,
            state.step_count,
            state.energy_level,
            state.reward_total,
            state.last_action
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::self_kernel::{SelfKernel, Goal};
    
    fn create_test_kernel() -> SelfKernel {
        let mut kernel = SelfKernel::new(1, 100);
        
        // 添加一个目标
        kernel.add_goal(Goal::new("g1", "test goal"));
        
        // 模拟几个tick
        for i in 1..=3 {
            let snapshot = crate::self_kernel::self_state::RuntimeSnapshot {
                step: i,
                unix_time: 1700000000 + i,
                energy_level: 0.8 - (i as f32 * 0.05),
                reward_delta: 1.0,
                reward_total: i as f32,
                neuron_count: 10000,
                active_neuron_count: 1000,
                last_action: format!("action{}", i),
                current_mode: "explore".to_string(),
                environment_tag: "gridworld".to_string(),
            };
            kernel.tick(snapshot);
        }
        
        kernel
    }
    
    #[test]
    fn test_who_am_i() {
        let kernel = create_test_kernel();
        let report = kernel.who_am_i();
        
        assert!(report.contains("atlas-v2.3-instance-001"));
        assert!(report.contains("step="));
        assert!(report.contains("energy="));
    }
    
    #[test]
    fn test_what_did_i_just_do() {
        let kernel = create_test_kernel();
        let report = kernel.what_did_i_just_do();
        
        assert!(report.contains("action3"));  // 最后一个动作
        assert!(report.contains("step=3"));
    }
    
    #[test]
    fn test_what_if_i_continue() {
        let kernel = create_test_kernel();
        let report = kernel.what_if_i_continue(100);
        
        assert!(report.contains("If I continue for 100 steps"));
        assert!(report.contains("predicted_energy="));
        assert!(report.contains("confidence="));
    }
    
    #[test]
    fn test_formatted_report() {
        let kernel = create_test_kernel();
        let report = kernel.formatted_report();
        
        assert!(report.contains("SELF KERNEL REPORT"));
        assert!(report.contains("IDENTITY"));
        assert!(report.contains("CURRENT STATE"));
        assert!(report.contains("ACTIVE GOALS"));
        assert!(report.contains("HISTORY"));
    }
}
