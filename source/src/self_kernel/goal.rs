//! Goal System: 目标向量与自主意图
//! 
//! 让系统能够维护"我想达成什么"。

use crate::self_kernel::self_state::InternalState;

/// 目标状态
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum GoalStatus {
    Active,
    Completed,
    Failed,
}

/// 单个目标
#[derive(Debug, Clone)]
pub struct Goal {
    pub id: String,
    pub description: String,
    pub target_reward_total: Option<f32>,
    pub min_energy_threshold: Option<f32>,
    pub status: GoalStatus,
}

impl Goal {
    /// 创建新目标
    pub fn new(id: impl Into<String>, description: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            description: description.into(),
            target_reward_total: None,
            min_energy_threshold: None,
            status: GoalStatus::Active,
        }
    }

    /// 设置目标奖励
    pub fn with_target_reward(mut self, target: f32) -> Self {
        self.target_reward_total = Some(target);
        self
    }

    /// 设置最小能量阈值
    pub fn with_min_energy(mut self, min_energy: f32) -> Self {
        self.min_energy_threshold = Some(min_energy);
        self
    }
}

/// 目标向量 - 维护多个目标
#[derive(Debug, Clone, Default)]
pub struct GoalVector {
    goals: Vec<Goal>,
}

impl GoalVector {
    /// 添加目标
    pub fn add_goal(&mut self, goal: Goal) {
        self.goals.push(goal);
    }

    /// 获取所有目标
    pub fn goals(&self) -> &[Goal] {
        &self.goals
    }

    /// 获取活跃目标
    pub fn active_goals(&self) -> impl Iterator<Item = &Goal> {
        self.goals.iter().filter(|g| g.status == GoalStatus::Active)
    }

    /// 设置目标状态
    pub fn set_status(&mut self, goal_id: &str, status: GoalStatus) -> bool {
        if let Some(goal) = self.goals.iter_mut().find(|g| g.id == goal_id) {
            goal.status = status;
            return true;
        }
        false
    }

    /// 完成目标
    pub fn complete_goal(&mut self, goal_id: &str) -> bool {
        self.set_status(goal_id, GoalStatus::Completed)
    }

    /// 失败目标
    pub fn fail_goal(&mut self, goal_id: &str) -> bool {
        self.set_status(goal_id, GoalStatus::Failed)
    }

    /// 从状态更新目标进度
    pub fn update_progress_from_state(&mut self, state: &InternalState) {
        for goal in &mut self.goals {
            if goal.status != GoalStatus::Active {
                continue;
            }

            // 检查奖励目标
            if let Some(target) = goal.target_reward_total {
                if state.reward_total >= target {
                    goal.status = GoalStatus::Completed;
                    continue;
                }
            }

            // 检查能量阈值
            if let Some(min_energy) = goal.min_energy_threshold {
                if state.energy_level < min_energy {
                    goal.status = GoalStatus::Failed;
                }
            }
        }
    }

    /// 获取主要目标描述
    pub fn primary_goal_description(&self) -> String {
        self.active_goals()
            .next()
            .map(|g| g.description.clone())
            .unwrap_or_else(|| "no active goal".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_goal_creation() {
        let goal = Goal::new("g1", "test goal")
            .with_target_reward(100.0)
            .with_min_energy(0.2);
        
        assert_eq!(goal.id, "g1");
        assert_eq!(goal.description, "test goal");
        assert_eq!(goal.target_reward_total, Some(100.0));
        assert_eq!(goal.min_energy_threshold, Some(0.2));
        assert_eq!(goal.status, GoalStatus::Active);
    }

    #[test]
    fn test_goal_vector() {
        let mut gv = GoalVector::default();
        gv.add_goal(Goal::new("g1", "goal 1").with_target_reward(50.0));
        gv.add_goal(Goal::new("g2", "goal 2"));
        
        assert_eq!(gv.goals().len(), 2);
        
        // 完成第一个目标
        assert!(gv.complete_goal("g1"));
        assert_eq!(gv.goals()[0].status, GoalStatus::Completed);
        
        // 只有一个活跃目标
        assert_eq!(gv.active_goals().count(), 1);
    }

    #[test]
    fn test_auto_complete() {
        let mut gv = GoalVector::default();
        gv.add_goal(Goal::new("g1", "reach 100 reward").with_target_reward(100.0));
        
        // 模拟状态达到目标
        let mut state = InternalState::new("test", 0);
        state.reward_total = 100.0;
        
        gv.update_progress_from_state(&state);
        
        assert_eq!(gv.goals()[0].status, GoalStatus::Completed);
    }
}
