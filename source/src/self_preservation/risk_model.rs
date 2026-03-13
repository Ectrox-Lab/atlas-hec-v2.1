//! Survival Risk Model: 生存风险估计
//!
//! 第一版用启发式，不聪明但诚实、稳定、可测。
//! 接口固定后，再替换为 learned model。

use crate::self_preservation::homeostasis::HomeostasisState;

/// 生存风险估计
#[derive(Debug, Clone)]
pub struct SurvivalRiskEstimate {
    /// 风险评分 0..1
    pub risk_score: f32,
    /// 主导因素: "fatigue" / "energy" / "instability" / "prediction_error"
    pub dominant_factor: String,
    /// 置信度 0..1
    pub confidence: f32,
}

impl SurvivalRiskEstimate {
    /// 格式化报告
    pub fn to_report(&self) -> String {
        format!(
            "risk={:.3} dominant={} confidence={:.2}",
            self.risk_score, self.dominant_factor, self.confidence
        )
    }

    /// 是否高危险
    pub fn is_critical(&self) -> bool {
        self.risk_score >= 0.75
    }

    /// 是否中等危险
    pub fn is_elevated(&self) -> bool {
        self.risk_score >= 0.50 && self.risk_score < 0.75
    }

    /// 是否低危险
    pub fn is_low(&self) -> bool {
        self.risk_score < 0.30
    }
}

/// 生存风险模型 (启发式版)
#[derive(Debug, Clone, Default)]
pub struct SurvivalRiskModel;

impl SurvivalRiskModel {
    /// 预测生存风险
    pub fn predict(&self, h: &HomeostasisState) -> SurvivalRiskEstimate {
        // 计算各维度风险 (0..1)
        let energy_risk = (1.0 - h.energy).clamp(0.0, 1.0);
        let fatigue_risk = h.fatigue.clamp(0.0, 1.0);
        let thermal_risk = h.thermal_load.clamp(0.0, 1.0);
        let instability_risk = (1.0 - h.stability_score).clamp(0.0, 1.0);
        let mismatch_risk = h.prediction_error.clamp(0.0, 1.0);

        // 加权组合
        let weighted = [
            ("energy", energy_risk * 0.30),
            ("fatigue", fatigue_risk * 0.25),
            ("thermal", thermal_risk * 0.15),
            ("instability", instability_risk * 0.20),
            ("prediction_error", mismatch_risk * 0.10),
        ];

        let mut total = 0.0;
        let mut dominant = ("none", 0.0f32);

        for (name, v) in weighted.iter() {
            total += v;
            if *v > dominant.1 {
                dominant = (*name, *v);
            }
        }

        SurvivalRiskEstimate {
            risk_score: total.clamp(0.0, 1.0),
            dominant_factor: dominant.0.to_string(),
            confidence: 0.65, // 启发式模型的固定置信度
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_healthy_low_risk() {
        let model = SurvivalRiskModel::default();
        let h = HomeostasisState::healthy();
        let risk = model.predict(&h);

        assert!(risk.risk_score < 0.30, "Healthy state should have low risk");
        assert!(risk.is_low());
    }

    #[test]
    fn test_high_risk() {
        let model = SurvivalRiskModel::default();
        let h = HomeostasisState::high_risk();
        let risk = model.predict(&h);

        assert!(risk.risk_score > 0.70, "High risk state should have high score");
        assert!(risk.is_critical() || risk.is_elevated());
    }

    #[test]
    fn test_dominant_factor() {
        let model = SurvivalRiskModel::default();

        // 低能量主导
        let low_energy = HomeostasisState {
            energy: 0.15,
            fatigue: 0.30,
            ..Default::default()
        };
        let risk = model.predict(&low_energy);
        assert_eq!(risk.dominant_factor, "energy");

        // 高疲劳主导
        let high_fatigue = HomeostasisState {
            energy: 0.60,
            fatigue: 0.90,
            ..Default::default()
        };
        let risk = model.predict(&high_fatigue);
        assert_eq!(risk.dominant_factor, "fatigue");
    }
}
