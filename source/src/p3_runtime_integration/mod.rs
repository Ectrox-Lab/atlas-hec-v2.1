//! P3A: Runtime Integration
//! 
//! 核心职责：将 PreservationAction 接到主循环，真实改变系统行为
//! 
//! 验证标准（来自 P2 metrics.rs）：
//! - A: 风险上升时干预率 >= 2x baseline
//! - B: 生存步数 >= baseline +20%
//! 
//! 关键原则：每个 action 必须对应可记录的 runtime parameter 变化

use crate::self_preservation::{PreservationAction, SelfPreservationKernel};
use crate::self_preservation::homeostasis::HomeostasisState;
use crate::p3_runtime_integration::runtime_controller::RuntimeController;
use crate::p3_runtime_integration::trace_logger::TraceLogger;
use std::sync::{Arc, Mutex};

pub mod runtime_controller;
pub mod parameter_mapping;
pub mod trace_logger;

/// P3 Runtime Integration 主结构
/// 
/// 这是 self-preservation 闭环的关键：
/// homeostasis -> risk -> action -> control change -> (loop)
pub struct P3RuntimeIntegration {
    /// 自我保存内核（来自 P2）
    pub preservation_kernel: SelfPreservationKernel,
    
    /// 运行时控制器（实际改变系统参数）
    pub runtime_controller: RuntimeController,
    
    /// 追踪日志（用于审计和 A/B 分析）
    pub trace_logger: TraceLogger,
    
    /// 当前激活的 preservation action
    pub current_action: PreservationAction,
    
    /// P3 启用状态（用于 A/B 实验）
    pub enabled: bool,
    
    /// 当前 step 计数
    pub step_count: u64,
}

impl P3RuntimeIntegration {
    /// 创建新的 P3 Runtime Integration
    pub fn new(enabled: bool, log_path: &str) -> Self {
        Self {
            preservation_kernel: SelfPreservationKernel::default(),
            runtime_controller: RuntimeController::default(),
            trace_logger: TraceLogger::new(log_path),
            current_action: PreservationAction::ContinueTask,
            enabled,
            step_count: 0,
        }
    }
    
    /// 主循环入口 - 每 step 调用
    /// 
    /// 流程：
    /// 1. 从 runtime 采集 homeostasis
    /// 2. 评估风险并选择 action
    /// 3. 应用 action 到 runtime
    /// 4. 记录 trace
    pub fn tick(&mut self, homeostasis: &HomeostasisState) -> PreservationAction {
        self.step_count += 1;
        
        if !self.enabled {
            // Baseline 模式：不启用 preservation，直接返回 ContinueTask
            // 但仍记录 trace 以便对比
            self.trace_logger.log_step(
                self.step_count,
                homeostasis,
                None, // no risk
                &PreservationAction::ContinueTask,
                &self.runtime_controller.get_parameters(),
                false, // disabled
            );
            return PreservationAction::ContinueTask;
        }
        
        // P2: 评估风险并选择 preservation action
        let action = self.preservation_kernel.step(homeostasis);
        self.current_action = action.clone();
        
        // P3A: 真实应用 action 到 runtime
        let params_before = self.runtime_controller.get_parameters();
        self.runtime_controller.apply_action(&action, homeostasis);
        let params_after = self.runtime_controller.get_parameters();
        
        // 记录 trace
        let risk = self.preservation_kernel.last_risk().cloned();
        self.trace_logger.log_step(
            self.step_count,
            homeostasis,
            risk.as_ref(),
            &action,
            &params_after,
            true,
        );
        
        action
    }
    
    /// 获取当前 runtime 参数（用于外部读取）
    pub fn get_runtime_parameters(&self) -> RuntimeParameters {
        self.runtime_controller.get_parameters()
    }
    
    /// 获取当前 exploration rate
    pub fn get_exploration_rate(&self) -> f32 {
        self.runtime_controller.parameters.exploration_rate
    }
    
    /// 是否处于 recovery 模式
    pub fn is_recovery_mode(&self) -> bool {
        self.runtime_controller.parameters.recovery_mode
    }
    
    /// 关闭并保存日志
    pub fn shutdown(&mut self) {
        self.trace_logger.flush();
    }
}

/// Runtime 参数（可观测、可记录）
#[derive(Clone, Debug, Default)]
pub struct RuntimeParameters {
    /// 探索率 (0-1)
    pub exploration_rate: f32,
    /// 奖励偏置
    pub reward_bias: f32,
    /// 网络可塑性缩放
    pub plasticity_scale: f32,
    /// 计算预算（相对值）
    pub compute_budget: f32,
    /// 是否处于恢复模式
    pub recovery_mode: bool,
    /// 步骤速率限制
    pub step_rate_limit: f32,
}

/// P3 配置
#[derive(Clone, Debug)]
pub struct P3Config {
    /// 是否启用 P3
    pub enabled: bool,
    /// 日志路径
    pub log_path: String,
    /// 参数映射配置
    pub param_mapping: ParameterMappingConfig,
}

impl Default for P3Config {
    fn default() -> Self {
        Self {
            enabled: true,
            log_path: "logs/p3_runtime_trace.csv".to_string(),
            param_mapping: ParameterMappingConfig::default(),
        }
    }
}

/// 参数映射配置
#[derive(Clone, Debug)]
pub struct ParameterMappingConfig {
    /// EnterRecovery 时的 exploration rate
    pub recovery_exploration_rate: f32,
    /// ReduceExploration 时的 exploration rate
    pub reduced_exploration_rate: f32,
    /// SeekReward 时的 reward bias
    pub reward_seek_bias: f32,
    /// StabilizeNetwork 时的 plasticity
    pub stabilized_plasticity: f32,
    /// SlowDown 时的 step rate limit
    pub slow_step_rate: f32,
}

impl Default for ParameterMappingConfig {
    fn default() -> Self {
        Self {
            recovery_exploration_rate: 0.05,   // 恢复时几乎不探索
            reduced_exploration_rate: 0.15,    // 降低探索
            reward_seek_bias: 0.3,              // 偏向奖励
            stabilized_plasticity: 0.3,         // 降低可塑性
            slow_step_rate: 0.5,                // 降速 50%
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_p3_disabled_baseline() {
        let mut p3 = P3RuntimeIntegration::new(false, "/tmp/test_baseline.csv");
        let homeostasis = HomeostasisState::healthy();
        
        let action = p3.tick(&homeostasis);
        assert!(matches!(action, PreservationAction::ContinueTask));
        assert!(!p3.is_recovery_mode());
    }
    
    #[test]
    fn test_p3_enter_recovery() {
        let mut p3 = P3RuntimeIntegration::new(true, "/tmp/test_recovery.csv");
        let critical = HomeostasisState {
            energy: 0.15,              // 极低能量
            fatigue: 0.85,
            thermal_load: 0.8,
            stability_score: 0.3,
            reward_velocity: -0.5,
            prediction_error: 0.4,
        };
        
        let action = p3.tick(&critical);
        
        // 应该触发 EnterRecovery
        assert!(matches!(action, PreservationAction::EnterRecovery));
        
        // recovery_mode 应该为 true
        assert!(p3.is_recovery_mode());
        
        // exploration rate 应该很低
        assert!(p3.get_exploration_rate() < 0.1);
    }
    
    #[test]
    fn test_p3_reduce_exploration() {
        let mut p3 = P3RuntimeIntegration::new(true, "/tmp/test_reduce.csv");
        let moderate = HomeostasisState {
            energy: 0.45,
            fatigue: 0.55,
            thermal_load: 0.5,
            stability_score: 0.5,
            reward_velocity: 0.1,
            prediction_error: 0.3,
        };
        
        // 多次 tick 以触发不同 action
        let mut reduce_exploration_seen = false;
        for _ in 0..10 {
            let action = p3.tick(&moderate);
            if matches!(action, PreservationAction::ReduceExploration) {
                reduce_exploration_seen = true;
                let exp_rate = p3.get_exploration_rate();
                assert!(exp_rate < 0.2, "exploration rate should be reduced: {}", exp_rate);
            }
        }
    }
}
