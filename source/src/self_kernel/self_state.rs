//! SelfState: 系统内部状态表示
//! 
//! 这不是AI的"哲学自我"，
//! 而是 system internal state representation。

use super::Identity;

/// 运行时数据 (从主循环传入) - 旧版兼容
#[derive(Clone, Debug)]
pub struct RuntimeData {
    pub energy: f32,
    pub reward: f32,
    pub neurons: usize,
    pub action: String,
}

/// 运行时快照 - 新版完整格式
#[derive(Clone, Debug)]
pub struct RuntimeSnapshot {
    pub step: u64,
    pub unix_time: u64,
    pub energy_level: f32,
    pub reward_delta: f32,
    pub reward_total: f32,
    pub neuron_count: usize,
    pub active_neuron_count: usize,
    pub last_action: String,
    pub current_mode: String,
    pub environment_tag: String,
}

impl RuntimeSnapshot {
    /// 创建新的运行时快照
    pub fn new(
        step: u64,
        unix_time: u64,
        energy_level: f32,
        reward_delta: f32,
        reward_total: f32,
        neuron_count: usize,
        active_neuron_count: usize,
        last_action: impl Into<String>,
        current_mode: impl Into<String>,
        environment_tag: impl Into<String>,
    ) -> Self {
        Self {
            step,
            unix_time,
            energy_level,
            reward_delta,
            reward_total,
            neuron_count,
            active_neuron_count,
            last_action: last_action.into(),
            current_mode: current_mode.into(),
            environment_tag: environment_tag.into(),
        }
    }
    
    /// 从旧版RuntimeData转换
    pub fn from_runtime_data(data: RuntimeData, step: u64, unix_time: u64) -> Self {
        Self {
            step,
            unix_time,
            energy_level: data.energy,
            reward_delta: data.reward,
            reward_total: data.reward, // 简化处理
            neuron_count: data.neurons,
            active_neuron_count: data.neurons / 10, // 估计值
            last_action: data.action,
            current_mode: "online".to_string(),
            environment_tag: "gridworld".to_string(),
        }
    }
}

/// 系统内部状态 (新版 - 完整字段)
#[derive(Clone, Debug)]
pub struct InternalState {
    /// 身份ID字符串
    pub identity_id: String,
    
    /// 创建时间戳
    pub created_at_unix: u64,
    /// 最后更新时间戳
    pub last_update_unix: u64,
    
    /// 步数计数
    pub step_count: u64,
    
    /// 能量水平 (0.0 - 1.0)
    pub energy_level: f32,
    /// 奖励变化 (上一步)
    pub reward_delta: f32,
    /// 累计奖励
    pub reward_total: f32,
    
    /// 神经元数量
    pub neuron_count: usize,
    /// 活跃神经元数量
    pub active_neuron_count: usize,
    
    /// 当前模式
    pub current_mode: String,
    /// 环境标签
    pub environment_tag: String,
    /// 上一个动作
    pub last_action: String,
}

impl InternalState {
    /// 创建新状态
    pub fn new(identity: Identity, created_at_unix: u64) -> Self {
        Self {
            identity_id: identity.id,
            created_at_unix,
            last_update_unix: created_at_unix,
            step_count: 0,
            energy_level: 1.0,
            reward_delta: 0.0,
            reward_total: 0.0,
            neuron_count: 10000,
            active_neuron_count: 1000,
            current_mode: "boot".to_string(),
            environment_tag: "unknown".to_string(),
            last_action: "none".to_string(),
        }
    }
    
    /// 从运行时快照更新
    pub fn update_from_snapshot(&mut self, snapshot: &RuntimeSnapshot) {
        self.last_update_unix = snapshot.unix_time;
        self.step_count = snapshot.step;
        
        self.energy_level = snapshot.energy_level.clamp(0.0, 1.0);
        self.reward_delta = snapshot.reward_delta;
        self.reward_total = snapshot.reward_total;
        
        self.neuron_count = snapshot.neuron_count;
        self.active_neuron_count = snapshot.active_neuron_count;
        
        self.current_mode = snapshot.current_mode.clone();
        self.environment_tag = snapshot.environment_tag.clone();
        self.last_action = snapshot.last_action.clone();
    }
    
    /// 从旧版RuntimeData更新 (兼容)
    pub fn update(&mut self, data: RuntimeData) {
        self.step_count += 1;
        self.energy_level = data.energy.clamp(0.0, 1.0);
        self.reward_delta = data.reward;
        self.reward_total += data.reward;
        self.neuron_count = data.neurons;
        self.active_neuron_count = data.neurons / 10;
        self.last_action = data.action;
        
        self.last_update_unix = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
    }
    
    /// 获取平均奖励
    pub fn average_reward(&self) -> f32 {
        if self.step_count == 0 {
            0.0
        } else {
            self.reward_total / self.step_count as f32
        }
    }
    
    /// 格式化状态报告
    pub fn to_report(&self) -> String {
        format!(
            "Step: {} | Energy: {:.2} | Reward: {:.2} (avg: {:.4}) | Neurons: {} (active: {}) | Mode: {} | Action: {}",
            self.step_count,
            self.energy_level,
            self.reward_total,
            self.average_reward(),
            self.neuron_count,
            self.active_neuron_count,
            self.current_mode,
            self.last_action
        )
    }
}

/// 旧版SelfState类型别名 (向后兼容)
pub type SelfState = InternalState;

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_internal_state_creation() {
        let identity = Identity::new(1);
        let state = InternalState::new(identity, 1700000000);
        
        assert_eq!(state.step_count, 0);
        assert_eq!(state.energy_level, 1.0);
        assert_eq!(state.reward_total, 0.0);
        assert_eq!(state.current_mode, "boot");
    }
    
    #[test]
    fn test_update_from_snapshot() {
        let identity = Identity::new(1);
        let mut state = InternalState::new(identity, 1700000000);
        
        let snapshot = RuntimeSnapshot {
            step: 10,
            unix_time: 1700000010,
            energy_level: 0.75,
            reward_delta: 5.0,
            reward_total: 50.0,
            neuron_count: 10050,
            active_neuron_count: 1200,
            last_action: "explore".to_string(),
            current_mode: "online".to_string(),
            environment_tag: "gridworld".to_string(),
        };
        
        state.update_from_snapshot(&snapshot);
        
        assert_eq!(state.step_count, 10);
        assert_eq!(state.energy_level, 0.75);
        assert_eq!(state.reward_total, 50.0);
        assert_eq!(state.active_neuron_count, 1200);
        assert_eq!(state.current_mode, "online");
    }
    
    #[test]
    fn test_runtime_data_compat() {
        let identity = Identity::new(1);
        let mut state = InternalState::new(identity, 1700000000);
        
        let data = RuntimeData {
            energy: 0.8,
            reward: 10.0,
            neurons: 10000,
            action: "move_left".to_string(),
        };
        
        state.update(data);
        
        assert_eq!(state.step_count, 1);
        assert_eq!(state.energy_level, 0.8);
        assert_eq!(state.last_action, "move_left");
    }
}
