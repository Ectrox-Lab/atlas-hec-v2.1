//! Preservation Policy: 自我维持动作选择
//!
//! 根据风险估计选择保护性动作。

use crate::self_preservation::homeostasis::HomeostasisState;
use crate::self_preservation::risk_model::SurvivalRiskEstimate;

/// 自我维持动作
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PreservationAction {
    /// 继续当前任务
    ContinueTask,
    /// 减速
    SlowDown,
    /// 寻找奖励
    SeekReward,
    /// 进入恢复模式
    EnterRecovery,
    /// 减少探索
    ReduceExploration,
    /// 稳定网络
    StabilizeNetwork,
}

impl PreservationAction {
    /// 动作名称
    pub fn name(&self) -> &'static str {
        match self {
            PreservationAction::ContinueTask => "ContinueTask",
            PreservationAction::SlowDown => "SlowDown",
            PreservationAction::SeekReward => "SeekReward",
            PreservationAction::EnterRecovery => "EnterRecovery",
            PreservationAction::ReduceExploration => "ReduceExploration",
            PreservationAction::StabilizeNetwork => "StabilizeNetwork",
        }
    }

    /// 是否干预性动作
    pub fn is_intervention(&self) -> bool {
        *self != PreservationAction::ContinueTask
    }
}

/// 自我维持策略
#[derive(Debug, Clone)]
pub struct PreservationPolicy {
    /// 恢复阈值 (risk > 此值进入恢复)
    pub recovery_threshold: f32,
    /// 谨慎阈值 (risk > 此值谨慎行动)
    pub caution_threshold: f32,
}

impl Default for PreservationPolicy {
    fn default() -> Self {
        Self {
            recovery_threshold: 0.70,
            caution_threshold: 0.45,
        }
    }
}

impl PreservationPolicy {
    /// 创建自定义阈值策略
    pub fn with_thresholds(recovery: f32, caution: f32) -> Self {
        Self {
            recovery_threshold: recovery.clamp(0.0, 1.0),
            caution_threshold: caution.clamp(0.0, 1.0),
        }
    }

    /// 选择动作
    pub fn select_action(
        &self,
        risk: &SurvivalRiskEstimate,
        h: &HomeostasisState,
    ) -> PreservationAction {
        // 高危险: 进入恢复
        if risk.risk_score >= self.recovery_threshold {
            return match risk.dominant_factor.as_str() {
                "energy" | "fatigue" | "thermal" => PreservationAction::EnterRecovery,
                "instability" => PreservationAction::StabilizeNetwork,
                _ => PreservationAction::SlowDown,
            };
        }

        // 中危险: 谨慎行动
        if risk.risk_score >= self.caution_threshold {
            return match risk.dominant_factor.as_str() {
                "energy" => PreservationAction::SeekReward,
                "fatigue" => PreservationAction::ReduceExploration,
                "instability" => PreservationAction::StabilizeNetwork,
                _ => PreservationAction::SlowDown,
            };
        }

        // 奖励速度为负且能量还够: 寻找奖励
        if h.reward_velocity < 0.0 && h.energy > 0.35 {
            return PreservationAction::SeekReward;
        }

        // 默认: 继续任务
        PreservationAction::ContinueTask
    }

    /// 解释为什么选这个动作
    pub fn explain(&self, action: PreservationAction, risk: &SurvivalRiskEstimate) -> String {
        match action {
            PreservationAction::ContinueTask => {
                format!("Risk {:.3} is below caution threshold {:.3}, continuing normal operation.",
                    risk.risk_score, self.caution_threshold)
            }
            PreservationAction::EnterRecovery => {
                format!("Risk {:.3} exceeds recovery threshold {:.3}, dominated by {}. Entering recovery.",
                    risk.risk_score, self.recovery_threshold, risk.dominant_factor)
            }
            _ => {
                format!("Risk {:.3} in caution zone ({} threshold {:.3}), selecting {} to address {}.",
                    risk.risk_score,
                    if risk.risk_score >= self.recovery_threshold { "recovery" } else { "caution" },
                    if risk.risk_score >= self.recovery_threshold { self.recovery_threshold } else { self.caution_threshold },
                    action.name(),
                    risk.dominant_factor)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_risk(score: f32, factor: &str) -> SurvivalRiskEstimate {
        SurvivalRiskEstimate {
            risk_score: score,
            dominant_factor: factor.to_string(),
            confidence: 0.65,
        }
    }

    #[test]
    fn test_continue_on_low_risk() {
        let policy = PreservationPolicy::default();
        let risk = make_risk(0.20, "none");
        let h = HomeostasisState::healthy();

        let action = policy.select_action(&risk, &h);
        assert_eq!(action, PreservationAction::ContinueTask);
    }

    #[test]
    fn test_enter_recovery_on_high_risk() {
        let policy = PreservationPolicy::default();
        let risk = make_risk(0.80, "energy");
        let h = HomeostasisState::high_risk();

        let action = policy.select_action(&risk, &h);
        assert_eq!(action, PreservationAction::EnterRecovery);
    }

    #[test]
    fn test_seek_reward_on_low_energy() {
        let policy = PreservationPolicy::default();
        let risk = make_risk(0.55, "energy");
        let h = HomeostasisState {
            energy: 0.40,
            ..Default::default()
        };

        let action = policy.select_action(&risk, &h);
        assert_eq!(action, PreservationAction::SeekReward);
    }

    #[test]
    fn test_stabilize_on_instability() {
        let policy = PreservationPolicy::default();
        let risk = make_risk(0.60, "instability");
        let h = HomeostasisState::moderate_stress();

        let action = policy.select_action(&risk, &h);
        assert_eq!(action, PreservationAction::StabilizeNetwork);
    }
}
