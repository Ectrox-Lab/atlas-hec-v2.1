//! Homeostasis: 生理/资源稳态状态
//!
//! 把"我是否在变差"压成几个可测量。
//! 纯工程结构，不是哲学结构。

/// 稳态状态
#[derive(Debug, Clone)]
pub struct HomeostasisState {
    /// 能量水平 0..1
    pub energy: f32,
    /// 疲劳度 0..1
    pub fatigue: f32,
    /// 热负荷 0..1
    pub thermal_load: f32,
    /// 稳定性评分 0..1
    pub stability_score: f32,
    /// 奖励速度 (近期奖励趋势)
    pub reward_velocity: f32,
    /// 预测误差 (模型失配度)
    pub prediction_error: f32,
}

impl HomeostasisState {
    /// 创建新状态
    pub fn new(energy: f32, fatigue: f32) -> Self {
        Self {
            energy: energy.clamp(0.0, 1.0),
            fatigue: fatigue.clamp(0.0, 1.0),
            thermal_load: 0.0,
            stability_score: 1.0,
            reward_velocity: 0.0,
            prediction_error: 0.0,
        }
    }

    /// 健康状态 (默认)
    pub fn healthy() -> Self {
        Self {
            energy: 0.90,
            fatigue: 0.10,
            thermal_load: 0.20,
            stability_score: 0.90,
            reward_velocity: 0.01,
            prediction_error: 0.05,
        }
    }

    /// 轻度疲劳
    pub fn mild_stress() -> Self {
        Self {
            energy: 0.70,
            fatigue: 0.35,
            thermal_load: 0.30,
            stability_score: 0.85,
            reward_velocity: -0.01,
            prediction_error: 0.08,
        }
    }

    /// 中度疲劳
    pub fn moderate_stress() -> Self {
        Self {
            energy: 0.45,
            fatigue: 0.60,
            thermal_load: 0.35,
            stability_score: 0.75,
            reward_velocity: -0.02,
            prediction_error: 0.15,
        }
    }

    /// 高度危险
    pub fn high_risk() -> Self {
        Self {
            energy: 0.20,
            fatigue: 0.85,
            thermal_load: 0.40,
            stability_score: 0.55,
            reward_velocity: -0.03,
            prediction_error: 0.30,
        }
    }

    /// 从 DigitalMetabolism 转换
    /// 
    /// 注意：需要确保 biomimetic 模块已导出
    #[cfg(feature = "biomimetic")]
    pub fn from_metabolism(metabolism: &crate::biomimetic::metabolism::DigitalMetabolism) -> Self {
        Self {
            energy: 1.0 - metabolism.adenosine_level(), // 腺苷高 = 能量低
            fatigue: metabolism.adenosine_level(),
            thermal_load: metabolism.compute_load(),
            stability_score: 0.85, // 默认
            reward_velocity: 0.0,  // 需要外部计算
            prediction_error: 0.0, // 需要外部计算
        }
    }

    /// 格式化报告
    pub fn to_report(&self) -> String {
        format!(
            "energy={:.2} fatigue={:.2} thermal={:.2} stability={:.2} reward_vel={:.4} pred_err={:.2}",
            self.energy,
            self.fatigue,
            self.thermal_load,
            self.stability_score,
            self.reward_velocity,
            self.prediction_error
        )
    }
}

impl Default for HomeostasisState {
    fn default() -> Self {
        Self::healthy()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_homeostasis_creation() {
        let h = HomeostasisState::new(0.8, 0.2);
        assert_eq!(h.energy, 0.8);
        assert_eq!(h.fatigue, 0.2);
    }

    #[test]
    fn test_clamping() {
        let h = HomeostasisState::new(1.5, -0.5);
        assert_eq!(h.energy, 1.0);
        assert_eq!(h.fatigue, 0.0);
    }

    #[test]
    fn test_predefined_states() {
        let healthy = HomeostasisState::healthy();
        assert!(healthy.energy > 0.8);
        assert!(healthy.fatigue < 0.2);

        let risk = HomeostasisState::high_risk();
        assert!(risk.energy < 0.3);
        assert!(risk.fatigue > 0.8);
    }
}
