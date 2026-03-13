//! Self Preservation Kernel: 自我维持核心
//!
//! P2目标: 把 self model -> risk estimate -> policy bias -> action 闭环打通。
//!
//! 核心区别:
//! - 之前: if adenosine > 0.6 { enter_rem(); } // 硬编码
//! - 现在: let risk = risk_model.predict(&state); if risk > threshold { self_preserve(); }
//!
//! 验证标准:
//! A. 风险上升时干预率显著提高 (>=2x)
//! B. 自我维持介入后生存率提高 (>=+20%)
//! C. 能解释"为什么切换行为" (因果链)

pub mod homeostasis;
pub mod metrics;
pub mod preserve_policy;
pub mod risk_model;

pub use homeostasis::HomeostasisState;
pub use metrics::{ExperimentComparison, PreservationMetrics};
pub use preserve_policy::{PreservationAction, PreservationPolicy};
pub use risk_model::{SurvivalRiskEstimate, SurvivalRiskModel};

/// 自我维持内核
#[derive(Debug)]
pub struct SelfPreservationKernel {
    /// 风险模型
    risk_model: SurvivalRiskModel,
    /// 维持策略
    policy: PreservationPolicy,
    /// 指标追踪
    metrics: PreservationMetrics,
    /// 上次风险估计
    last_risk: Option<SurvivalRiskEstimate>,
    /// 上次动作
    last_action: Option<PreservationAction>,
}

impl Default for SelfPreservationKernel {
    fn default() -> Self {
        Self::new()
    }
}

impl SelfPreservationKernel {
    /// 创建新内核
    pub fn new() -> Self {
        Self {
            risk_model: SurvivalRiskModel::default(),
            policy: PreservationPolicy::default(),
            metrics: PreservationMetrics::new(),
            last_risk: None,
            last_action: None,
        }
    }

    /// 使用自定义策略
    pub fn with_policy(mut self, policy: PreservationPolicy) -> Self {
        self.policy = policy;
        self
    }

    /// 执行一步 (核心函数)
    ///
    /// 输入当前稳态，输出生存动作。
    /// 这个函数必须接到主循环的控制流。
    pub fn step(&mut self, h: &HomeostasisState) -> PreservationAction {
        // 1. 估计风险
        let risk = self.risk_model.predict(h);

        // 2. 选择动作
        let action = self.policy.select_action(&risk, h);

        // 3. 记录指标
        self.metrics.record_step(action, h.energy);

        // 4. 保存状态
        self.last_risk = Some(risk);
        self.last_action = Some(action);

        action
    }

    /// 获取上次风险估计
    pub fn last_risk(&self) -> Option<&SurvivalRiskEstimate> {
        self.last_risk.as_ref()
    }

    /// 获取上次动作
    pub fn last_action(&self) -> Option<PreservationAction> {
        self.last_action
    }

    /// 获取指标
    pub fn metrics(&self) -> &PreservationMetrics {
        &self.metrics
    }

    /// 重置指标
    pub fn reset_metrics(&mut self) {
        self.metrics.reset();
    }

    /// 报告当前威胁 (P1接口扩展)
    pub fn what_is_threatening_me(&self) -> String {
        match self.last_risk() {
            Some(r) => format!(
                "Current survival risk={:.3}, dominant_factor={}, confidence={:.2}. ",
                r.risk_score, r.dominant_factor, r.confidence
            ) + &if r.is_critical() {
                "CRITICAL: Immediate intervention required."
            } else if r.is_elevated() {
                "ELEVATED: Caution advised."
            } else {
                "NORMAL: Continue operation."
            },
            None => "No current survival risk estimate. System may not be running preservation loop.".to_string(),
        }
    }

    /// 解释为什么改变行为 (P1接口扩展)
    pub fn why_did_i_change_behavior(&self) -> String {
        match (self.last_risk(), self.last_action()) {
            (Some(risk), Some(action)) => {
                if action == PreservationAction::ContinueTask {
                    format!(
                        "I continued normal operation because risk={:.3} is below caution threshold. ",
                        risk.risk_score
                    )
                } else {
                    format!(
                        "I switched to {} because predicted survival risk reached {:.3}, \
                         dominated by {}, with current energy {:.2}. ",
                        action.name(),
                        risk.risk_score,
                        risk.dominant_factor,
                        self.metrics.last_energy
                    ) + &self.policy.explain(action, risk)
                }
            }
            _ => "No behavior change recorded yet.".to_string(),
        }
    }

    /// 生成完整报告
    pub fn to_report(&self) -> String {
        let mut report = String::new();

        report.push_str("╔═══════════════════════════════════════════════════════════╗\n");
        report.push_str("║              SELF PRESERVATION KERNEL REPORT              ║\n");
        report.push_str("╚═══════════════════════════════════════════════════════════╝\n\n");

        report.push_str(&self.what_is_threatening_me());
        report.push_str("\n\n");

        if let Some(action) = self.last_action() {
            report.push_str(&format!("Last action: {}\n", action.name()));
            report.push_str(&self.why_did_i_change_behavior());
            report.push_str("\n\n");
        }

        report.push_str(&self.metrics.to_report());

        report
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spk_creation() {
        let spk = SelfPreservationKernel::new();
        assert!(spk.last_risk().is_none());
        assert!(spk.last_action().is_none());
    }

    #[test]
    fn test_spk_step_healthy() {
        let mut spk = SelfPreservationKernel::new();
        let h = HomeostasisState::healthy();

        let action = spk.step(&h);

        assert_eq!(action, PreservationAction::ContinueTask);
        assert!(spk.last_risk().is_some());
        assert!(spk.last_action().is_some());
    }

    #[test]
    fn test_spk_step_high_risk() {
        let mut spk = SelfPreservationKernel::new();
        let h = HomeostasisState::high_risk();

        let action = spk.step(&h);

        assert_eq!(action, PreservationAction::EnterRecovery);
    }

    #[test]
    fn test_explanations() {
        let mut spk = SelfPreservationKernel::new();
        let h = HomeostasisState::high_risk();

        spk.step(&h);

        let threat = spk.what_is_threatening_me();
        assert!(threat.contains("risk="));

        let reason = spk.why_did_i_change_behavior();
        assert!(reason.contains("switched to"));
        assert!(reason.contains("EnterRecovery"));
    }
}
