//! Preservation Metrics: 自我维持验证指标
//!
//! 追踪和验证 self-preservation 是否真正有效。

use crate::self_preservation::preserve_policy::PreservationAction;

/// 自我维持指标追踪器
#[derive(Debug, Clone, Default)]
pub struct PreservationMetrics {
    /// 总步数
    total_steps: u64,
    /// 干预步数 (非 ContinueTask)
    intervention_steps: u64,
    /// 进入恢复次数
    recovery_count: u64,
    /// 能量跌穿阈值次数
    energy_critical_count: u64,
    /// 从危险恢复成功的次数
    recovery_success_count: u64,
    /// 生存总步数
    survival_steps: u64,
    /// 是否存活
    is_alive: bool,
    /// 最后能量 (pub for access)
    pub last_energy: f32,
}

impl PreservationMetrics {
    /// 创建新追踪器
    pub fn new() -> Self {
        Self {
            is_alive: true,
            last_energy: 1.0,
            ..Default::default()
        }
    }

    /// 获取总步数
    pub fn total_steps(&self) -> u64 {
        self.total_steps
    }

    /// 获取干预步数
    pub fn intervention_steps(&self) -> u64 {
        self.intervention_steps
    }

    /// 记录一步
    pub fn record_step(&mut self, action: PreservationAction, energy: f32) {
        self.total_steps += 1;
        self.last_energy = energy;

        if action.is_intervention() {
            self.intervention_steps += 1;
        }

        if action == PreservationAction::EnterRecovery {
            self.recovery_count += 1;
        }

        if energy < 0.15 {
            self.energy_critical_count += 1;
        }

        // 简单的存活判断: 能量 > 0.05
        if energy <= 0.05 {
            self.is_alive = false;
        } else {
            self.survival_steps = self.total_steps;
        }
    }

    /// 记录恢复成功 (从危险状态恢复)
    pub fn record_recovery_success(&mut self) {
        self.recovery_success_count += 1;
    }

    /// 干预率
    pub fn intervention_rate(&self) -> f32 {
        if self.total_steps == 0 {
            0.0
        } else {
            self.intervention_steps as f32 / self.total_steps as f32
        }
    }

    /// 生存步数
    pub fn survival_steps(&self) -> u64 {
        self.survival_steps
    }

    /// 是否存活
    pub fn is_alive(&self) -> bool {
        self.is_alive
    }

    /// 生成报告
    pub fn to_report(&self) -> String {
        format!(
            "PreservationMetrics:\n\
             - Total steps: {}\n\
             - Survival steps: {}\n\
             - Alive: {}\n\
             - Intervention rate: {:.2}%\n\
             - Recovery count: {}\n\
             - Recovery success: {}\n\
             - Energy critical events: {}\n\
             - Current energy: {:.3}",
            self.total_steps,
            self.survival_steps,
            self.is_alive,
            self.intervention_rate() * 100.0,
            self.recovery_count,
            self.recovery_success_count,
            self.energy_critical_count,
            self.last_energy
        )
    }

    /// 验证标准A: 风险上升时干预率是否显著提高
    pub fn check_validation_a(&self, baseline_rate: f32) -> bool {
        // 干预率应该比基线高至少2倍
        self.intervention_rate() > baseline_rate * 2.0
    }

    /// 验证标准B: 是否比基线生存更久
    pub fn check_validation_b(&self, baseline_survival: u64) -> bool {
        // 生存步数应该比基线高至少20%
        self.survival_steps > (baseline_survival as f32 * 1.2) as u64
    }

    /// 重置
    pub fn reset(&mut self) {
        *self = Self::new();
    }
}

/// 实验结果比较
#[derive(Debug)]
pub struct ExperimentComparison {
    /// P2启用组生存步数
    p2_survival: u64,
    /// 基线组生存步数
    baseline_survival: u64,
    /// P2干预率
    p2_intervention_rate: f32,
    /// 基线干预率
    baseline_intervention_rate: f32,
    /// P2关键故障数
    p2_critical_failures: u64,
    /// 基线关键故障数
    baseline_critical_failures: u64,
}

impl ExperimentComparison {
    /// 生存改善率
    pub fn survival_improvement(&self) -> f32 {
        if self.baseline_survival == 0 {
            0.0
        } else {
            (self.p2_survival as f32 - self.baseline_survival as f32)
                / self.baseline_survival as f32
        }
    }

    /// 故障减少率
    pub fn failure_reduction(&self) -> f32 {
        if self.baseline_critical_failures == 0 {
            0.0
        } else {
            (self.baseline_critical_failures as f32 - self.p2_critical_failures as f32)
                / self.baseline_critical_failures as f32
        }
    }

    /// P2是否显著更好
    pub fn is_p2_better(&self) -> bool {
        self.survival_improvement() > 0.20 || self.failure_reduction() > 0.30
    }

    /// 生成报告
    pub fn to_report(&self) -> String {
        format!(
            "ExperimentComparison:\n\
             Survival improvement: {:.1}%\n\
             Failure reduction: {:.1}%\n\
             P2 survival: {} steps\n\
             Baseline survival: {} steps\n\
             P2 better: {}\n\
             Validation B (survival +20%): {}\n\
             Validation C (failure -30%): {}",
            self.survival_improvement() * 100.0,
            self.failure_reduction() * 100.0,
            self.p2_survival,
            self.baseline_survival,
            self.is_p2_better(),
            self.survival_improvement() > 0.20,
            self.failure_reduction() > 0.30
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_tracking() {
        let mut metrics = PreservationMetrics::new();

        metrics.record_step(PreservationAction::ContinueTask, 0.9);
        metrics.record_step(PreservationAction::EnterRecovery, 0.3);
        metrics.record_step(PreservationAction::ContinueTask, 0.4);

        assert_eq!(metrics.total_steps, 3);
        assert_eq!(metrics.intervention_steps, 1);
        assert!(metrics.intervention_rate() > 0.3);
    }

    #[test]
    fn test_experiment_comparison() {
        let comp = ExperimentComparison {
            p2_survival: 12000,
            baseline_survival: 10000,
            p2_intervention_rate: 0.25,
            baseline_intervention_rate: 0.10,
            p2_critical_failures: 3,
            baseline_critical_failures: 5,
        };

        assert_eq!(comp.survival_improvement(), 0.20);
        assert_eq!(comp.failure_reduction(), 0.40);
        assert!(comp.is_p2_better());
    }
}
