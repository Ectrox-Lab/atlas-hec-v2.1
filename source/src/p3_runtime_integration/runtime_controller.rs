//! Runtime Controller
//! 
//! 核心职责：将 PreservationAction 映射到真实的运行时参数变化
//! 
//! 原则：
//! - 每个 action 必须改变至少一个可观测参数
//! - 参数变化必须可记录、可审计
//! - 状态机必须清晰、可预测

use crate::p3_runtime_integration::{RuntimeParameters, ParameterMappingConfig};
use crate::self_preservation::{PreservationAction, HomeostasisState};

/// 运行时控制器 - 实际改变系统行为
#[derive(Debug, Clone)]
pub struct RuntimeController {
    /// 当前运行时参数
    pub parameters: RuntimeParameters,
    
    /// 参数映射配置
    pub config: ParameterMappingConfig,
    
    /// 默认参数（用于 reset）
    pub defaults: RuntimeParameters,
    
    /// 当前 recovery 步数计数
    pub recovery_step_count: u64,
    
    /// 是否被强制进入 recovery
    pub forced_recovery: bool,
}

impl Default for RuntimeController {
    fn default() -> Self {
        let defaults = RuntimeParameters {
            exploration_rate: 0.30,  // 默认 30% 探索
            reward_bias: 0.0,         // 无偏置
            plasticity_scale: 1.0,    // 标准可塑性
            compute_budget: 1.0,      // 标准计算预算
            recovery_mode: false,
            step_rate_limit: 1.0,     // 无限制
        };
        
        Self {
            parameters: defaults.clone(),
            config: ParameterMappingConfig::default(),
            defaults,
            recovery_step_count: 0,
            forced_recovery: false,
        }
    }
}

impl RuntimeController {
    /// 应用 preservation action 到 runtime
    /// 
    /// 这是 P3A 的核心：action -> parameter change
    pub fn apply_action(&mut self, action: &PreservationAction, homeostasis: &HomeostasisState) {
        match action {
            PreservationAction::ContinueTask => {
                // 正常模式：渐进恢复默认参数
                self.gradual_restore();
            }
            
            PreservationAction::EnterRecovery => {
                // 进入恢复模式：大幅降低探索，减少计算，稳定网络
                self.parameters.recovery_mode = true;
                self.parameters.exploration_rate = self.config.recovery_exploration_rate;
                self.parameters.plasticity_scale = self.config.stabilized_plasticity;
                self.parameters.compute_budget = 0.5; // 减半计算
                self.parameters.step_rate_limit = self.config.slow_step_rate;
                self.recovery_step_count = 0;
                self.forced_recovery = true;
            }
            
            PreservationAction::SeekReward => {
                // 偏向奖励寻求：提高 reward bias，适度降低探索
                self.parameters.reward_bias = self.config.reward_seek_bias;
                // 适度降低探索以聚焦
                self.parameters.exploration_rate = 
                    (self.parameters.exploration_rate * 0.7).max(0.1);
            }
            
            PreservationAction::ReduceExploration => {
                // 降低探索率
                self.parameters.exploration_rate = self.config.reduced_exploration_rate;
            }
            
            PreservationAction::StabilizeNetwork => {
                // 稳定网络：降低可塑性，降低噪声（通过 exploration 间接）
                self.parameters.plasticity_scale = self.config.stabilized_plasticity;
                self.parameters.exploration_rate = 
                    (self.parameters.exploration_rate * 0.8).max(0.05);
            }
            
            PreservationAction::SlowDown => {
                // 放慢：限制 step rate
                self.parameters.step_rate_limit = self.config.slow_step_rate;
                self.parameters.compute_budget = 0.7;
            }
        }
        
        // 边界检查
        self.clamp_parameters();
        
        // 如果在 recovery 模式且风险降低，检查是否应该退出
        if self.parameters.recovery_mode {
            self.recovery_step_count += 1;
            self.check_recovery_exit(homeostasis);
        }
    }
    
    /// 渐进恢复默认参数
    fn gradual_restore(&mut self) {
        let restore_rate = 0.1; // 每 step 恢复 10%
        
        self.parameters.exploration_rate = lerp(
            self.parameters.exploration_rate,
            self.defaults.exploration_rate,
            restore_rate,
        );
        
        self.parameters.reward_bias = lerp(
            self.parameters.reward_bias,
            self.defaults.reward_bias,
            restore_rate,
        );
        
        self.parameters.plasticity_scale = lerp(
            self.parameters.plasticity_scale,
            self.defaults.plasticity_scale,
            restore_rate,
        );
        
        self.parameters.compute_budget = lerp(
            self.parameters.compute_budget,
            self.defaults.compute_budget,
            restore_rate,
        );
        
        self.parameters.step_rate_limit = lerp(
            self.parameters.step_rate_limit,
            self.defaults.step_rate_limit,
            restore_rate,
        );
        
        // 如果 recovery 模式且参数接近默认，退出 recovery
        if self.parameters.recovery_mode {
            let dist_to_default = self.distance_to_default();
            if dist_to_default < 0.1 && self.recovery_step_count > 10 {
                self.parameters.recovery_mode = false;
                self.forced_recovery = false;
            }
        }
    }
    
    /// 检查是否应该退出 recovery 模式
    fn check_recovery_exit(&mut self, homeostasis: &HomeostasisState) {
        // 至少保持 5 steps
        if self.recovery_step_count < 5 {
            return;
        }
        
        // 能量恢复到安全水平
        let energy_recovered = homeostasis.energy > 0.5;
        
        // 疲劳降低
        let fatigue_reduced = homeostasis.fatigue < 0.5;
        
        // 稳定性改善
        let stable = homeostasis.stability_score > 0.6;
        
        if energy_recovered && fatigue_reduced && stable {
            self.parameters.recovery_mode = false;
            self.forced_recovery = false;
        }
    }
    
    /// 边界检查
    fn clamp_parameters(&mut self) {
        self.parameters.exploration_rate = 
            self.parameters.exploration_rate.clamp(0.0, 1.0);
        self.parameters.reward_bias = 
            self.parameters.reward_bias.clamp(-1.0, 1.0);
        self.parameters.plasticity_scale = 
            self.parameters.plasticity_scale.clamp(0.0, 2.0);
        self.parameters.compute_budget = 
            self.parameters.compute_budget.clamp(0.1, 2.0);
        self.parameters.step_rate_limit = 
            self.parameters.step_rate_limit.clamp(0.1, 2.0);
    }
    
    /// 计算与默认参数的距离
    fn distance_to_default(&self) -> f32 {
        let d_exp = (self.parameters.exploration_rate - self.defaults.exploration_rate).abs();
        let d_bias = (self.parameters.reward_bias - self.defaults.reward_bias).abs();
        let d_plastic = (self.parameters.plasticity_scale - self.defaults.plasticity_scale).abs();
        let d_compute = (self.parameters.compute_budget - self.defaults.compute_budget).abs();
        let d_rate = (self.parameters.step_rate_limit - self.defaults.step_rate_limit).abs();
        
        (d_exp + d_bias + d_plastic + d_compute + d_rate) / 5.0
    }
    
    /// 获取当前参数
    pub fn get_parameters(&self) -> RuntimeParameters {
        self.parameters.clone()
    }
    
    /// 强制设置参数（用于外部控制）
    pub fn set_parameters(&mut self, params: RuntimeParameters) {
        self.parameters = params;
        self.clamp_parameters();
    }
    
    /// 重置到默认
    pub fn reset(&mut self) {
        self.parameters = self.defaults.clone();
        self.recovery_step_count = 0;
        self.forced_recovery = false;
    }
}

/// 线性插值
fn lerp(a: f32, b: f32, t: f32) -> f32 {
    a + (b - a) * t.clamp(0.0, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_enter_recovery_changes_parameters() {
        let mut ctrl = RuntimeController::default();
        let homeostasis = HomeostasisState::high_risk();
        
        // 应用 EnterRecovery
        ctrl.apply_action(&PreservationAction::EnterRecovery, &homeostasis);
        
        // 验证参数变化
        assert!(ctrl.parameters.recovery_mode);
        assert!(ctrl.parameters.exploration_rate < 0.1);
        assert!(ctrl.parameters.plasticity_scale < 0.5);
        assert!(ctrl.parameters.compute_budget < 0.6);
        assert!(ctrl.parameters.step_rate_limit < 0.6);
    }
    
    #[test]
    fn test_reduce_exploration_changes_rate() {
        let mut ctrl = RuntimeController::default();
        let homeostasis = HomeostasisState::moderate_stress();
        
        assert!(ctrl.parameters.exploration_rate > 0.2);
        
        ctrl.apply_action(&PreservationAction::ReduceExploration, &homeostasis);
        
        assert_eq!(ctrl.parameters.exploration_rate, 0.15);
    }
    
    #[test]
    fn test_continue_task_restores_parameters() {
        let mut ctrl = RuntimeController::default();
        let homeostasis = HomeostasisState::healthy();
        
        // 先进入 recovery
        ctrl.apply_action(&PreservationAction::EnterRecovery, &homeostasis);
        assert!(ctrl.parameters.exploration_rate < 0.1);
        
        // 多次 ContinueTask 应该恢复
        for _ in 0..50 {
            ctrl.apply_action(&PreservationAction::ContinueTask, &homeostasis);
        }
        
        // 应该接近默认值
        assert!(ctrl.parameters.exploration_rate > 0.25);
    }
    
    #[test]
    fn test_recovery_exit_conditions() {
        let mut ctrl = RuntimeController::default();
        let critical = HomeostasisState::high_risk();
        
        // 进入 recovery
        ctrl.apply_action(&PreservationAction::EnterRecovery, &critical);
        assert!(ctrl.parameters.recovery_mode);
        
        // 模拟 10 steps
        ctrl.recovery_step_count = 10;
        
        // 健康状态
        let healthy = HomeostasisState::healthy();
        
        // 应用 ContinueTask（应该退出 recovery）
        for _ in 0..20 {
            ctrl.apply_action(&PreservationAction::ContinueTask, &healthy);
        }
        
        // 应该退出 recovery 模式
        assert!(!ctrl.parameters.recovery_mode);
    }
}
