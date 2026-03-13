//! Self History: 自我历史记录窗口
//! 
//! 记录系统最近的行为，支持"我刚才做了什么"查询。

use std::collections::VecDeque;

use crate::self_kernel::self_state::RuntimeSnapshot;

/// 行为记录
#[derive(Debug, Clone)]
pub struct ActionRecord {
    /// 步数
    pub step: u64,
    /// 时间戳
    pub unix_time: u64,
    /// 动作名称
    pub action: String,
    /// 奖励变化
    pub reward_delta: f32,
    /// 总奖励
    pub reward_total: f32,
    /// 能量水平
    pub energy_level: f32,
    /// 神经元数量
    pub neuron_count: usize,
    /// 活跃神经元数量
    pub active_neuron_count: usize,
    /// 当前模式
    pub mode: String,
    /// 环境标签
    pub environment_tag: String,
}

impl ActionRecord {
    /// 从运行时快照创建记录
    pub fn from_snapshot(snapshot: &RuntimeSnapshot) -> Self {
        Self {
            step: snapshot.step,
            unix_time: snapshot.unix_time,
            action: snapshot.last_action.clone(),
            reward_delta: snapshot.reward_delta,
            reward_total: snapshot.reward_total,
            energy_level: snapshot.energy_level,
            neuron_count: snapshot.neuron_count,
            active_neuron_count: snapshot.active_neuron_count,
            mode: snapshot.current_mode.clone(),
            environment_tag: snapshot.environment_tag.clone(),
        }
    }
    
    /// 简短描述
    pub fn summary(&self) -> String {
        format!(
            "[Step {}] {} | Reward: {:.2} | Energy: {:.2}",
            self.step, self.action, self.reward_delta, self.energy_level
        )
    }
}

/// 自我历史窗口
#[derive(Debug, Clone)]
pub struct SelfHistoryWindow {
    /// 容量
    capacity: usize,
    /// 记录队列
    records: VecDeque<ActionRecord>,
}

impl SelfHistoryWindow {
    /// 创建新历史窗口
    /// 
    /// # 参数
    /// * `capacity` - 最大容量 (建议至少8)
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            records: VecDeque::with_capacity(capacity),
        }
    }
    
    /// 添加记录
    /// 
    /// 如果超过容量，自动丢弃最旧的记录。
    pub fn push(&mut self, record: ActionRecord) {
        if self.records.len() >= self.capacity {
            self.records.pop_front();
        }
        self.records.push_back(record);
    }
    
    /// 获取记录数量
    pub fn len(&self) -> usize {
        self.records.len()
    }
    
    /// 是否为空
    pub fn is_empty(&self) -> bool {
        self.records.is_empty()
    }
    
    /// 获取最新的记录
    pub fn latest(&self) -> Option<&ActionRecord> {
        self.records.back()
    }
    
    /// 获取最近的N条记录
    pub fn recent(&self, n: usize) -> Vec<&ActionRecord> {
        self.records.iter().rev().take(n).collect()
    }
    
    /// 获取最后一个动作名称
    pub fn last_action_name(&self) -> Option<&str> {
        self.latest().map(|r| r.action.as_str())
    }
    
    /// 获取第一个记录 (最旧的)
    pub fn oldest(&self) -> Option<&ActionRecord> {
        self.records.front()
    }
    
    /// 清空历史
    pub fn clear(&mut self) {
        self.records.clear();
    }
    
    /// 生成摘要
    pub fn summary(&self) -> String {
        if self.records.is_empty() {
            return "No history yet.".to_string();
        }
        
        let first = self.records.front().unwrap();
        let last = self.records.back().unwrap();
        
        format!(
            "Total records: {} | First: Step {} | Last: Step {}",
            self.records.len(),
            first.step,
            last.step
        )
    }
}

impl Default for SelfHistoryWindow {
    fn default() -> Self {
        Self::new(128)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    fn create_test_snapshot(step: u64, action: &str) -> RuntimeSnapshot {
        RuntimeSnapshot {
            step,
            unix_time: 1700000000 + step,
            energy_level: 0.8,
            reward_delta: 1.0,
            reward_total: step as f32,
            neuron_count: 10000,
            active_neuron_count: 1000,
            last_action: action.to_string(),
            current_mode: "explore".to_string(),
            environment_tag: "gridworld".to_string(),
        }
    }
    
    #[test]
    fn test_history_creation() {
        let history = SelfHistoryWindow::new(100);
        assert_eq!(history.len(), 0);
        assert!(history.is_empty());
    }
    
    #[test]
    fn test_history_push() {
        let mut history = SelfHistoryWindow::new(3);
        
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(1, "a")));
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(2, "b")));
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(3, "c")));
        
        assert_eq!(history.len(), 3);
        
        // 超过容量，最旧的应该被丢弃
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(4, "d")));
        assert_eq!(history.len(), 3);
        
        // 第一个应该是step 2 (step 1被丢弃)
        let first = history.records.front().unwrap();
        assert_eq!(first.step, 2);
    }
    
    #[test]
    fn test_latest() {
        let mut history = SelfHistoryWindow::new(10);
        
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(1, "a")));
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(2, "b")));
        
        let latest = history.latest().unwrap();
        assert_eq!(latest.step, 2);
        assert_eq!(latest.action, "b");
    }
    
    #[test]
    fn test_recent() {
        let mut history = SelfHistoryWindow::new(10);
        
        for i in 1..=5 {
            history.push(ActionRecord::from_snapshot(&create_test_snapshot(i, &format!("action{}", i))));
        }
        
        let recent = history.recent(3);
        assert_eq!(recent.len(), 3);
        assert_eq!(recent[0].step, 5); // 最新的
        assert_eq!(recent[2].step, 3);
    }
    
    #[test]
    fn test_last_action_name() {
        let mut history = SelfHistoryWindow::new(10);
        
        history.push(ActionRecord::from_snapshot(&create_test_snapshot(1, "move_left")));
        
        assert_eq!(history.last_action_name(), Some("move_left"));
    }
}
