//! SelfState: 系统内部状态表示
//! 
//! 这不是AI的"哲学自我"，
//! 而是 system internal state representation。

use super::Identity;

/// 运行时数据 (从主循环传入)
#[derive(Clone, Debug)]
pub struct RuntimeData {
    pub energy: f32,
    pub reward: f32,
    pub neurons: usize,
    pub action: String,
}

/// 系统内部状态
#[derive(Clone, Debug)]
pub struct SelfState {
    /// 身份标识 (永远不变)
    pub identity: Identity,
    
    /// 当前步数计数
    pub step_count: u64,
    
    /// 能量水平 (0.0 - 1.0)
    pub energy_level: f32,
    
    /// 累计奖励
    pub reward_total: f32,
    
    /// 当前神经元数量
    pub neuron_count: usize,
    
    /// 上一个动作
    pub last_action: String,
    
    /// 最后更新时间戳
    pub timestamp: u64,
}

impl SelfState {
    /// 创建新状态
    pub fn new(identity: Identity) -> Self {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Self {
            identity,
            step_count: 0,
            energy_level: 1.0,
            reward_total: 0.0,
            neuron_count: 10000, // 默认初始值
            last_action: "initialized".to_string(),
            timestamp,
        }
    }
    
    /// 更新状态 (每步调用)
    pub fn update(&mut self, data: RuntimeData) {
        self.step_count += 1;
        self.energy_level = data.energy.clamp(0.0, 1.0);
        self.reward_total += data.reward;
        self.neuron_count = data.neurons;
        self.last_action = data.action;
        
        self.timestamp = std::time::SystemTime::now()
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
            "Step: {} | Energy: {:.2} | Reward: {:.2} (avg: {:.4}) | Neurons: {} | Action: {}",
            self.step_count,
            self.energy_level,
            self.reward_total,
            self.average_reward(),
            self.neuron_count,
            self.last_action
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_state_creation() {
        let identity = Identity::new(1);
        let state = SelfState::new(identity);
        
        assert_eq!(state.step_count, 0);
        assert_eq!(state.energy_level, 1.0);
        assert_eq!(state.reward_total, 0.0);
        assert_eq!(state.last_action, "initialized");
    }
    
    #[test]
    fn test_state_update() {
        let identity = Identity::new(1);
        let mut state = SelfState::new(identity);
        
        let data = RuntimeData {
            energy: 0.75,
            reward: 10.0,
            neurons: 10050,
            action: "move_left".to_string(),
        };
        
        state.update(data);
        
        assert_eq!(state.step_count, 1);
        assert_eq!(state.energy_level, 0.75);
        assert_eq!(state.reward_total, 10.0);
        assert_eq!(state.neuron_count, 10050);
        assert_eq!(state.last_action, "move_left");
    }
}
