//! Self Predictor: 自我状态预测
//! 
//! 第一版使用确定性启发式预测器，不是神经网络。
//! 先把接口固定，后面再替换成真正的learned self-model。

use crate::self_kernel::self_state::InternalState;

/// 预测状态
#[derive(Debug, Clone)]
pub struct PredictedState {
    /// 预测步数
    pub projected_steps: u64,
    /// 预测能量水平
    pub predicted_energy_level: f32,
    /// 预测总奖励
    pub predicted_reward_total: f32,
    /// 预测模式
    pub predicted_mode: String,
    /// 假设动作
    pub assumed_action: String,
    /// 置信度
    pub confidence: f32,
    /// 推理说明
    pub rationale: String,
}

/// 自我预测器
#[derive(Debug, Clone, Default)]
pub struct SelfPredictor;

impl SelfPredictor {
    /// 预测未来状态
    /// 
    /// # 参数
    /// * `state` - 当前状态
    /// * `last_action` - 上一个动作（可选）
    /// * `projected_steps` - 预测步数
    /// * `assumed_action` - 假设动作（可选，默认延续last_action）
    pub fn predict(
        &self,
        state: &InternalState,
        last_action: Option<&str>,
        projected_steps: u64,
        assumed_action: Option<&str>,
    ) -> PredictedState {
        let assumed_action = assumed_action
            .or(last_action)
            .unwrap_or("continue_idle")
            .to_string();

        // 估算能量消耗
        let energy_drain = estimate_energy_drain(&assumed_action, projected_steps);
        
        // 估算奖励获得
        let reward_gain = estimate_reward_gain(&assumed_action, projected_steps);

        // 预测能量（不能低于0）
        let predicted_energy = (state.energy_level - energy_drain).clamp(0.0, 1.0);
        
        // 预测奖励
        let predicted_reward = state.reward_total + reward_gain;

        // 预测模式
        let predicted_mode = if predicted_energy < 0.20 {
            "recovery".to_string()  // 需要恢复
        } else if reward_gain > 0.0 {
            "goal_pursuit".to_string()  // 追求目标
        } else {
            state.current_mode.clone()  // 保持当前模式
        };

        PredictedState {
            projected_steps,
            predicted_energy_level: predicted_energy,
            predicted_reward_total: predicted_reward,
            predicted_mode,
            assumed_action: assumed_action.clone(),
            confidence: 0.35,  // 启发式预测器置信度较低
            rationale: format!(
                "heuristic predictor: action='{}', projected_steps={}, \
                 estimated_energy_drain={:.4}, estimated_reward_gain={:.4}",
                assumed_action, projected_steps, energy_drain, reward_gain
            ),
        }
    }
}

/// 估算能量消耗
fn estimate_energy_drain(action: &str, projected_steps: u64) -> f32 {
    let base_rate = match action {
        "move_left" | "move_right" | "move_up" | "move_down" => 0.0008,
        "move_north" | "move_south" | "move_east" | "move_west" => 0.0008,
        "explore" => 0.0010,
        "forage" => 0.0006,
        "sleep" | "rest" | "enter_rem" => -0.0004,  // 恢复能量
        _ => 0.0003,  // 默认
    };

    (projected_steps as f32) * base_rate
}

/// 估算奖励获得
fn estimate_reward_gain(action: &str, projected_steps: u64) -> f32 {
    let per_step = match action {
        "forage" => 0.020,
        "explore" => 0.008,
        "move_left" | "move_right" | "move_up" | "move_down" => 0.002,
        "move_north" | "move_south" | "move_east" | "move_west" => 0.002,
        "sleep" | "rest" | "enter_rem" => -0.001,  // 休息奖励略降
        _ => 0.0,
    };

    (projected_steps as f32) * per_step
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::self_kernel::Identity;
    use crate::self_kernel::self_state::InternalState;

    fn create_test_state() -> InternalState {
        let identity = Identity::new(1);
        let mut state = InternalState::new(identity);
        state.energy_level = 0.8;
        state.reward_total = 50.0;
        state
    }

    #[test]
    fn test_predict_explore() {
        let predictor = SelfPredictor::default();
        let state = create_test_state();

        let predicted = predictor.predict(&state, Some("explore"), 100, None);

        assert_eq!(predicted.projected_steps, 100);
        assert_eq!(predicted.assumed_action, "explore");
        assert!(predicted.predicted_energy_level < state.energy_level);  // 能量下降
        assert!(predicted.predicted_reward_total > state.reward_total);  // 奖励增加
        assert!(predicted.confidence > 0.0 && predicted.confidence <= 1.0);
    }

    #[test]
    fn test_predict_sleep() {
        let predictor = SelfPredictor::default();
        let state = create_test_state();

        let predicted = predictor.predict(&state, Some("sleep"), 100, None);

        // 睡眠应该恢复能量
        assert!(predicted.predicted_energy_level > state.energy_level);
        // 但奖励会略微下降
        assert!(predicted.predicted_reward_total < state.reward_total);
    }

    #[test]
    fn test_predict_recovery_mode() {
        let predictor = SelfPredictor::default();
        let mut state = create_test_state();
        state.energy_level = 0.15;  // 低能量

        let predicted = predictor.predict(&state, Some("explore"), 100, None);

        // 预测应该进入恢复模式
        assert_eq!(predicted.predicted_mode, "recovery");
    }

    #[test]
    fn test_default_action() {
        let predictor = SelfPredictor::default();
        let state = create_test_state();

        // 不提供动作，使用默认值
        let predicted = predictor.predict(&state, None, 50, None);
        assert_eq!(predicted.assumed_action, "continue_idle");
    }
}
