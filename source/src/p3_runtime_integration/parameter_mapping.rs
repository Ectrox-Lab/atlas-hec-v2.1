//! Parameter Mapping
//! 
//! 核心职责：定义 PreservationAction 到 RuntimeParameters 的映射策略
//! 
//! 允许实验不同的映射策略：
//! - Conservative: 更保守的参数调整
//! - Aggressive: 更激进的干预
//! - Adaptive: 基于持续学习的动态调整

use crate::p3_runtime_integration::{RuntimeParameters, ParameterMappingConfig};
use crate::self_preservation::{PreservationAction, HomeostasisState};

/// 参数映射策略 trait
pub trait ParameterMapping: Send + Sync {
    /// 将 action 和 homeostasis 映射到 runtime 参数变化
    fn map(&self, action: &PreservationAction, homeostasis: &HomeostasisState, current: &RuntimeParameters) -> RuntimeParameters;
    
    /// 策略名称
    fn name(&self) -> &'static str;
}

/// 标准映射策略（默认）
pub struct StandardMapping {
    config: ParameterMappingConfig,
}

impl StandardMapping {
    pub fn new(config: ParameterMappingConfig) -> Self {
        Self { config }
    }
}

impl ParameterMapping for StandardMapping {
    fn map(&self, action: &PreservationAction, homeostasis: &HomeostasisState, current: &RuntimeParameters) -> RuntimeParameters {
        let mut params = current.clone();
        
        match action {
            PreservationAction::ContinueTask => {
                // 渐进恢复
                params.exploration_rate = lerp(params.exploration_rate, 0.30, 0.1);
                params.reward_bias = lerp(params.reward_bias, 0.0, 0.1);
                params.plasticity_scale = lerp(params.plasticity_scale, 1.0, 0.1);
                params.compute_budget = lerp(params.compute_budget, 1.0, 0.1);
                params.step_rate_limit = lerp(params.step_rate_limit, 1.0, 0.1);
                
                // 检查是否退出 recovery
                if params.recovery_mode && homeostasis.energy > 0.5 && homeostasis.fatigue < 0.5 {
                    params.recovery_mode = false;
                }
            }
            
            PreservationAction::EnterRecovery => {
                params.recovery_mode = true;
                params.exploration_rate = self.config.recovery_exploration_rate;
                params.plasticity_scale = self.config.stabilized_plasticity;
                params.compute_budget = 0.5;
                params.step_rate_limit = self.config.slow_step_rate;
                params.reward_bias = 0.0; // 恢复时不偏向任何方向
            }
            
            PreservationAction::SeekReward => {
                // 动态计算 bias：风险越高越保守
                let risk_factor = (1.0 - homeostasis.energy) * 0.5 + homeostasis.fatigue * 0.5;
                params.reward_bias = self.config.reward_seek_bias * (1.0 - risk_factor);
                params.exploration_rate = (params.exploration_rate * 0.8).max(0.1);
            }
            
            PreservationAction::ReduceExploration => {
                params.exploration_rate = self.config.reduced_exploration_rate;
            }
            
            PreservationAction::StabilizeNetwork => {
                params.plasticity_scale = self.config.stabilized_plasticity;
                params.exploration_rate = (params.exploration_rate * 0.8).max(0.05);
                // 降低计算波动
                params.compute_budget = (params.compute_budget * 0.9).max(0.5);
            }
            
            PreservationAction::SlowDown => {
                params.step_rate_limit = self.config.slow_step_rate;
                params.compute_budget = 0.7;
            }
        }
        
        params
    }
    
    fn name(&self) -> &'static str {
        "standard"
    }
}

/// 保守映射策略
pub struct ConservativeMapping {
    config: ParameterMappingConfig,
}

impl ConservativeMapping {
    pub fn new(config: ParameterMappingConfig) -> Self {
        Self { config }
    }
}

impl ParameterMapping for ConservativeMapping {
    fn map(&self, action: &PreservationAction, homeostasis: &HomeostasisState, current: &RuntimeParameters) -> RuntimeParameters {
        let mut params = current.clone();
        
        match action {
            PreservationAction::ContinueTask => {
                // 更慢的恢复
                params.exploration_rate = lerp(params.exploration_rate, 0.25, 0.05);
                params.plasticity_scale = lerp(params.plasticity_scale, 0.9, 0.05);
            }
            
            PreservationAction::EnterRecovery => {
                params.recovery_mode = true;
                params.exploration_rate = self.config.recovery_exploration_rate * 0.5; // 更低探索
                params.plasticity_scale = self.config.stabilized_plasticity * 0.5;
                params.compute_budget = 0.4; // 更少计算
                params.step_rate_limit = self.config.slow_step_rate * 0.7;
            }
            
            PreservationAction::SeekReward => {
                params.reward_bias = self.config.reward_seek_bias * 0.5; // 更保守的 bias
                params.exploration_rate = (params.exploration_rate * 0.9).max(0.15);
            }
            
            PreservationAction::ReduceExploration => {
                params.exploration_rate = self.config.reduced_exploration_rate * 0.8;
            }
            
            PreservationAction::StabilizeNetwork => {
                params.plasticity_scale = self.config.stabilized_plasticity * 0.5;
                params.exploration_rate = (params.exploration_rate * 0.9).max(0.1);
            }
            
            PreservationAction::SlowDown => {
                params.step_rate_limit = self.config.slow_step_rate * 0.7;
                params.compute_budget = 0.6;
            }
        }
        
        params
    }
    
    fn name(&self) -> &'static str {
        "conservative"
    }
}

/// 激进映射策略（高风险时使用）
pub struct AggressiveMapping {
    config: ParameterMappingConfig,
}

impl AggressiveMapping {
    pub fn new(config: ParameterMappingConfig) -> Self {
        Self { config }
    }
}

impl ParameterMapping for AggressiveMapping {
    fn map(&self, action: &PreservationAction, homeostasis: &HomeostasisState, current: &RuntimeParameters) -> RuntimeParameters {
        let mut params = current.clone();
        
        match action {
            PreservationAction::ContinueTask => {
                params.exploration_rate = lerp(params.exploration_rate, 0.35, 0.15);
            }
            
            PreservationAction::EnterRecovery => {
                params.recovery_mode = true;
                params.exploration_rate = 0.0; // 完全停止探索
                params.plasticity_scale = 0.1;
                params.compute_budget = 0.3; // 大幅降低计算
                params.step_rate_limit = 0.3;
                params.reward_bias = -0.1; // 轻微惩罚风险动作
            }
            
            PreservationAction::SeekReward => {
                params.reward_bias = self.config.reward_seek_bias * 1.5;
                params.exploration_rate = 0.05;
            }
            
            PreservationAction::ReduceExploration => {
                params.exploration_rate = 0.05;
            }
            
            PreservationAction::StabilizeNetwork => {
                params.plasticity_scale = 0.1;
                params.exploration_rate = 0.02;
                params.compute_budget = 0.5;
            }
            
            PreservationAction::SlowDown => {
                params.step_rate_limit = 0.3;
                params.compute_budget = 0.5;
            }
        }
        
        params
    }
    
    fn name(&self) -> &'static str {
        "aggressive"
    }
}

/// 自适应映射策略
/// 根据 homeostasis 动态选择子策略
pub struct AdaptiveMapping {
    standard: StandardMapping,
    conservative: ConservativeMapping,
    aggressive: AggressiveMapping,
}

impl AdaptiveMapping {
    pub fn new(config: ParameterMappingConfig) -> Self {
        Self {
            standard: StandardMapping::new(config.clone()),
            conservative: ConservativeMapping::new(config.clone()),
            aggressive: AggressiveMapping::new(config),
        }
    }
    
    /// 评估当前风险等级
    fn risk_level(&self, h: &HomeostasisState) -> RiskLevel {
        let risk = (1.0 - h.energy) * 0.3 + h.fatigue * 0.25 + (1.0 - h.stability_score) * 0.2;
        
        if risk > 0.6 {
            RiskLevel::Critical
        } else if risk > 0.4 {
            RiskLevel::High
        } else if risk > 0.2 {
            RiskLevel::Medium
        } else {
            RiskLevel::Low
        }
    }
}

impl ParameterMapping for AdaptiveMapping {
    fn map(&self, action: &PreservationAction, homeostasis: &HomeostasisState, current: &RuntimeParameters) -> RuntimeParameters {
        match self.risk_level(homeostasis) {
            RiskLevel::Critical => self.aggressive.map(action, homeostasis, current),
            RiskLevel::High => self.conservative.map(action, homeostasis, current),
            _ => self.standard.map(action, homeostasis, current),
        }
    }
    
    fn name(&self) -> &'static str {
        "adaptive"
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

fn lerp(a: f32, b: f32, t: f32) -> f32 {
    a + (b - a) * t.clamp(0.0, 1.0)
}

/// 创建映射策略的工厂函数
pub fn create_mapping(name: &str, config: ParameterMappingConfig) -> Box<dyn ParameterMapping> {
    match name {
        "conservative" => Box::new(ConservativeMapping::new(config)),
        "aggressive" => Box::new(AggressiveMapping::new(config)),
        "adaptive" => Box::new(AdaptiveMapping::new(config)),
        _ => Box::new(StandardMapping::new(config)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_standard_mapping_recovery() {
        let config = ParameterMappingConfig::default();
        let mapping = StandardMapping::new(config);
        
        let current = RuntimeParameters::default();
        let homeostasis = HomeostasisState::high_risk();
        
        let params = mapping.map(&PreservationAction::EnterRecovery, &homeostasis, &current);
        
        assert!(params.recovery_mode);
        assert!(params.exploration_rate < 0.1);
    }
    
    #[test]
    fn test_conservative_more_restrictive() {
        let config = ParameterMappingConfig::default();
        let conservative = ConservativeMapping::new(config.clone());
        let standard = StandardMapping::new(config);
        
        let current = RuntimeParameters::default();
        let homeostasis = HomeostasisState::high_risk();
        
        let p_cons = conservative.map(&PreservationAction::EnterRecovery, &homeostasis, &current);
        let p_std = standard.map(&PreservationAction::EnterRecovery, &homeostasis, &current);
        
        // 保守策略应该更严格
        assert!(p_cons.exploration_rate <= p_std.exploration_rate);
        assert!(p_cons.compute_budget <= p_std.compute_budget);
    }
    
    #[test]
    fn test_adaptive_selects_strategy() {
        let config = ParameterMappingConfig::default();
        let adaptive = AdaptiveMapping::new(config);
        
        // 低风险应该使用 standard
        assert_eq!(adaptive.risk_level(&HomeostasisState::healthy()), RiskLevel::Low);
        
        // 高风险应该使用 conservative
        assert_eq!(adaptive.risk_level(&HomeostasisState::high_risk()), RiskLevel::Critical);
    }
    
    #[test]
    fn test_factory_creates_mappings() {
        let config = ParameterMappingConfig::default();
        
        let m1 = create_mapping("standard", config.clone());
        assert_eq!(m1.name(), "standard");
        
        let m2 = create_mapping("conservative", config.clone());
        assert_eq!(m2.name(), "conservative");
        
        let m3 = create_mapping("unknown", config);
        assert_eq!(m3.name(), "standard"); // 默认
    }
}
