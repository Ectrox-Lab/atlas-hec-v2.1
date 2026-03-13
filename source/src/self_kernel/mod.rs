//! Self Kernel v0.1: 最小可验证自我核心
//! 
//! 目标：让系统第一次具备 "I exist" 的能力。
//! 
//! 核心组件：
//! - IdentityToken: 永久身份标识 (this_is_me anchor)
//! - InternalState: 内部状态表示
//! - GoalVector: 目标向量 (我想达成什么)
//! - SelfHistoryWindow: 自我历史窗口 (我刚才做了什么)
//! - SelfPredictor: 自我预测器 (如果我做X会怎样)
//! 
//! 验证标准：
//! 1. ✅ who_am_i() 返回稳定identity
//! 2. ✅ what_did_i_just_do() 返回最近动作
//! 3. ✅ what_if_i_continue() 返回预测状态
//! 4. ✅ 日志中有结构化状态记录

pub mod goal;
pub mod history;
pub mod identity;
pub mod predictor;
pub mod report;
pub mod self_state;

// 保持向后兼容，重导出旧类型
pub use episode::Episode;
pub use memory::AutobiographicalMemory;

pub use goal::{Goal, GoalStatus, GoalVector};
pub use history::{ActionRecord, SelfHistoryWindow};
pub use identity::Identity;
pub use predictor::{PredictedState, SelfPredictor};
pub use report::SelfReport;
pub use self_state::{InternalState, RuntimeSnapshot, RuntimeData, SelfState};

use std::time::{SystemTime, UNIX_EPOCH};

/// Self Kernel 主控制器
/// 
/// 这是系统的自我核心，提供：
/// - 身份锚点
/// - 状态追踪
/// - 目标管理
/// - 历史记录
/// - 未来预测
#[derive(Clone, Debug)]
pub struct SelfKernel {
    /// 身份标识 (永远不变)
    identity: Identity,
    
    /// 当前状态
    state: InternalState,
    
    /// 目标向量
    goals: GoalVector,
    
    /// 历史窗口
    history: SelfHistoryWindow,
    
    /// 预测器
    predictor: SelfPredictor,
    
    /// 记录间隔 (每N步记录一次历史)
    record_interval: u64,
    
    /// 上次记录步数
    last_recorded_step: u64,
}

impl SelfKernel {
    /// 创建新的Self Kernel
    /// 
    /// # 参数
    /// * `instance_id` - 实例编号 (用于生成identity)
    /// * `history_capacity` - 历史窗口容量
    pub fn new(instance_id: u64, history_capacity: usize) -> Self {
        let created_at = unix_now_secs();
        let identity = Identity::new(instance_id);
        let state = InternalState::new(identity.clone(), created_at);
        let goals = GoalVector::default();
        let history = SelfHistoryWindow::new(history_capacity.max(8));
        let predictor = SelfPredictor::default();
        
        Self {
            identity,
            state,
            goals,
            history,
            predictor,
            record_interval: 10,
            last_recorded_step: 0,
        }
    }
    
    /// 兼容旧版new
    pub fn new_simple(instance_id: u64) -> Self {
        Self::new(instance_id, 10000)
    }
    
    /// 设置记录间隔
    pub fn with_record_interval(mut self, interval: u64) -> Self {
        self.record_interval = interval;
        self
    }
    
    /// 获取身份
    pub fn identity(&self) -> &Identity {
        &self.identity
    }
    
    /// 获取状态
    pub fn state(&self) -> &InternalState {
        &self.state
    }
    
    /// 获取目标向量
    pub fn goals(&self) -> &GoalVector {
        &self.goals
    }
    
    /// 获取历史窗口
    pub fn history(&self) -> &SelfHistoryWindow {
        &self.history
    }
    
    /// 获取预测器
    pub fn predictor(&self) -> &SelfPredictor {
        &self.predictor
    }
    
    /// 添加目标
    pub fn add_goal(&mut self, goal: Goal) {
        self.goals.add_goal(goal);
    }
    
    /// 完成目标
    pub fn complete_goal(&mut self, goal_id: &str) -> bool {
        self.goals.complete_goal(goal_id)
    }
    
    /// 失败目标
    pub fn fail_goal(&mut self, goal_id: &str) -> bool {
        self.goals.fail_goal(goal_id)
    }
    
    /// 更新状态 (每步调用)
    /// 
    /// 在主循环的 action -> reward 之后调用
    pub fn tick(&mut self, snapshot: RuntimeSnapshot) {
        // 更新状态
        self.state.update_from_snapshot(&snapshot);
        
        // 记录历史
        let record = ActionRecord::from_snapshot(&snapshot);
        self.history.push(record);
        
        // 更新目标进度
        self.goals.update_progress_from_state(&self.state);
        
        // 检查是否需要记录episode（向后兼容）
        if self.state.step_count - self.last_recorded_step >= self.record_interval {
            self.last_recorded_step = self.state.step_count;
        }
    }
    
    /// 兼容旧版update (使用 RuntimeData)
    pub fn update(&mut self, data: RuntimeData) {
        let snapshot = RuntimeSnapshot::from_runtime_data(data, self.state.step_count + 1, unix_now_secs());
        self.tick(snapshot);
    }
    
    /// 预测未来状态
    pub fn predict_if_continue(
        &self,
        projected_steps: u64,
        assumed_action: Option<&str>,
    ) -> PredictedState {
        self.predictor.predict(
            &self.state,
            self.history.last_action_name(),
            projected_steps,
            assumed_action,
        )
    }
    
    /// 获取身份ID字符串
    pub fn id(&self) -> &str {
        &self.identity.id
    }
    
    /// 获取当前步数
    pub fn step_count(&self) -> u64 {
        self.state.step_count
    }
    
    /// 获取历史记录数
    pub fn history_len(&self) -> usize {
        self.history.len()
    }
    
    /// 兼容旧版
    pub fn memory_len(&self) -> usize {
        self.history_len()
    }
    
    /// 生成自我报告
    pub fn report(&self) -> String {
        SelfReport::formatted_report(self)
    }
    
    /// 简短状态报告
    pub fn brief_status(&self) -> String {
        format!(
            "[{}] Step: {} | Energy: {:.2} | Reward: {:.2} | Action: {} | Mode: {}",
            self.identity.id,
            self.state.step_count,
            self.state.energy_level,
            self.state.reward_total,
            self.state.last_action,
            self.state.current_mode
        )
    }
}

/// 向后兼容的类型别名
pub type SelfKernelCompat = SelfKernel;

fn unix_now_secs() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

// 保持episode.rs和memory.rs的向后兼容
pub mod episode {
    use super::*;
    
    #[derive(Clone, Debug)]
    pub struct Episode {
        pub step: u64,
        pub event: String,
        pub reward: f32,
        pub energy: f32,
        pub neurons: usize,
        pub timestamp: u64,
    }
    
    impl Episode {
        pub fn new(step: u64, event: String, reward: f32, energy: f32, neurons: usize) -> Self {
            let timestamp = unix_now_secs();
            Self { step, event, reward, energy, neurons, timestamp }
        }
        
        pub fn summary(&self) -> String {
            format!("[Step {}] {} | Reward: {:.2} | Energy: {:.2}",
                self.step, self.event, self.reward, self.energy)
        }
    }
}

pub mod memory {
    use super::episode::Episode;
    use std::collections::VecDeque;
    
    #[derive(Clone, Debug)]
    pub struct AutobiographicalMemory {
        pub episodes: VecDeque<Episode>,
        pub max_size: usize,
    }
    
    impl AutobiographicalMemory {
        pub fn new(max_size: usize) -> Self {
            Self { episodes: VecDeque::with_capacity(max_size), max_size }
        }
        
        pub fn push(&mut self, episode: Episode) {
            if self.episodes.len() >= self.max_size {
                self.episodes.pop_front();
            }
            self.episodes.push_back(episode);
        }
        
        pub fn len(&self) -> usize { self.episodes.len() }
        pub fn is_empty(&self) -> bool { self.episodes.is_empty() }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_self_kernel_creation() {
        let kernel = SelfKernel::new(1, 128);
        assert_eq!(kernel.id(), "atlas-v2.3-instance-001");
    }
    
    #[test]
    fn test_self_kernel_tick() {
        let mut kernel = SelfKernel::new(1, 128);
        
        let snapshot = RuntimeSnapshot {
            step: 1,
            unix_time: 1700000000,
            energy_level: 0.8,
            reward_delta: 10.0,
            reward_total: 10.0,
            neuron_count: 10000,
            active_neuron_count: 1000,
            last_action: "move_left".to_string(),
            current_mode: "explore".to_string(),
            environment_tag: "gridworld".to_string(),
        };
        
        kernel.tick(snapshot);
        
        assert_eq!(kernel.step_count(), 1);
        assert_eq!(kernel.history_len(), 1);
    }
    
    #[test]
    fn test_goal_integration() {
        let mut kernel = SelfKernel::new(1, 128);
        
        kernel.add_goal(Goal::new("g1", "reach 100 reward").with_target_reward(100.0));
        
        // 模拟达到目标
        let snapshot = RuntimeSnapshot {
            step: 10,
            unix_time: 1700000010,
            energy_level: 0.8,
            reward_delta: 100.0,
            reward_total: 100.0,
            neuron_count: 10000,
            active_neuron_count: 1000,
            last_action: "forage".to_string(),
            current_mode: "goal_pursuit".to_string(),
            environment_tag: "gridworld".to_string(),
        };
        
        kernel.tick(snapshot);
        
        // 目标应该自动完成
        assert_eq!(kernel.goals().goals()[0].status, GoalStatus::Completed);
    }
    
    #[test]
    fn test_prediction() {
        let kernel = SelfKernel::new(1, 128);
        
        let predicted = kernel.predict_if_continue(100, Some("explore"));
        
        assert_eq!(predicted.projected_steps, 100);
        assert_eq!(predicted.assumed_action, "explore");
        assert!(predicted.confidence > 0.0);
    }
}
