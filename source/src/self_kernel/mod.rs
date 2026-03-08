//! Self Kernel v0.1: 最小可验证自我核心
//! 
//! 目标：让系统第一次具备 "I exist" 的能力。
//! 
//! 核心组件：
//! - Identity: 永久身份标识 (this_is_me anchor)
//! - SelfState: 内部状态表示
//! - Episode: 自传记忆最小单位
//! - AutobiographicalMemory: 自我历史存储
//! - SelfReport: 自我报告接口
//! 
//! 验证标准：
//! 1. ✅ who_am_i() 返回稳定identity
//! 2. ✅ what_did_i_just_do() 返回最近动作
//! 3. ✅ what_if_i_continue() 返回预测状态 (v0.2)
//! 4. ✅ 日志中有结构化状态记录

pub mod identity;
pub mod self_state;
pub mod episode;
pub mod memory;
pub mod report;

pub use identity::Identity;
pub use self_state::{SelfState, RuntimeData};
pub use episode::Episode;
pub use memory::AutobiographicalMemory;
pub use report::SelfReport;

/// Self Kernel 主控制器
/// 
/// 这是系统的自我核心，提供：
/// - 身份锚点
/// - 状态追踪
/// - 自传记忆
/// - 自我报告
#[derive(Clone, Debug)]
pub struct SelfKernel {
    /// 当前状态
    pub state: SelfState,
    
    /// 自传记忆
    pub memory: AutobiographicalMemory,
    
    /// 记录间隔 (每N步记录一次episode)
    record_interval: u64,
    
    /// 上次记录步数
    last_recorded_step: u64,
}

impl SelfKernel {
    /// 创建新的Self Kernel
    /// 
    /// # 参数
    /// * `instance_id` - 实例编号 (用于生成identity)
    pub fn new(instance_id: u64) -> Self {
        let identity = Identity::new(instance_id);
        let state = SelfState::new(identity);
        let memory = AutobiographicalMemory::new(10000);
        
        Self {
            state,
            memory,
            record_interval: 100, // 默认每100步记录一次
            last_recorded_step: 0,
        }
    }
    
    /// 设置记录间隔
    pub fn with_record_interval(mut self, interval: u64) -> Self {
        self.record_interval = interval;
        self
    }
    
    /// 更新状态 (每步调用)
    /// 
    /// 在主循环的 action -> reward 之后调用：
    /// ```rust
    /// let data = RuntimeData {
    ///     energy: current_energy,
    ///     reward: step_reward,
    ///     neurons: neuron_count,
    ///     action: "move_left".to_string(),
    /// };
    /// self_kernel.update(data);
    /// ```
    pub fn update(&mut self, data: RuntimeData) {
        // 更新状态
        self.state.update(data);
        
        // 检查是否需要记录episode
        if self.state.step_count - self.last_recorded_step >= self.record_interval {
            self.record_episode();
            self.last_recorded_step = self.state.step_count;
        }
    }
    
    /// 记录记忆片段
    fn record_episode(&mut self) {
        let ep = Episode::new(
            self.state.step_count,
            self.state.last_action.clone(),
            self.state.reward_total,
            self.state.energy_level,
            self.state.neuron_count,
        );
        
        self.memory.push(ep);
    }
    
    /// 强制记录当前episode (用于重要事件)
    pub fn record_now(&mut self, event_description: String) {
        let ep = Episode::new(
            self.state.step_count,
            event_description,
            self.state.reward_total,
            self.state.energy_level,
            self.state.neuron_count,
        );
        
        self.memory.push(ep);
        self.last_recorded_step = self.state.step_count;
    }
    
    /// 生成自我报告
    pub fn report(&self) -> String {
        SelfReport::formatted_report(self)
    }
    
    /// 简短状态报告
    pub fn brief_status(&self) -> String {
        SelfReport::brief_status(&self.state)
    }
    
    /// 获取身份ID
    pub fn id(&self) -> &str {
        &self.state.identity.id
    }
    
    /// 获取当前步数
    pub fn step_count(&self) -> u64 {
        self.state.step_count
    }
    
    /// 获取记忆数量
    pub fn memory_len(&self) -> usize {
        self.memory.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_self_kernel_creation() {
        let kernel = SelfKernel::new(1);
        
        assert_eq!(kernel.id(), "atlas-v2.3-instance-001");
        assert_eq!(kernel.step_count(), 0);
        assert_eq!(kernel.memory_len(), 0);
    }
    
    #[test]
    fn test_self_kernel_update() {
        let mut kernel = SelfKernel::new(1);
        
        let data = RuntimeData {
            energy: 0.75,
            reward: 10.0,
            neurons: 10050,
            action: "move_left".to_string(),
        };
        
        kernel.update(data);
        
        assert_eq!(kernel.step_count(), 1);
        assert_eq!(kernel.state.energy_level, 0.75);
    }
    
    #[test]
    fn test_episode_recording() {
        let mut kernel = SelfKernel::new(1)
            .with_record_interval(2); // 每2步记录一次
        
        // 更新3次
        for i in 1..=3 {
            kernel.update(RuntimeData {
                energy: 0.8,
                reward: i as f32 * 10.0,
                neurons: 10000,
                action: format!("action{}", i),
            });
        }
        
        // 应该记录了1个episode (step 2)
        assert!(kernel.memory_len() >= 1);
    }
}
