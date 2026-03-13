//! Episode: 自传记忆的最小单位
//! 
//! 记录系统经历的一个事件片段。

/// 记忆片段
#[derive(Clone, Debug)]
pub struct Episode {
    /// 步数编号
    pub step: u64,
    
    /// 事件描述
    pub event: String,
    
    /// 累计奖励
    pub reward: f32,
    
    /// 能量水平
    pub energy: f32,
    
    /// 神经元数量
    pub neurons: usize,
    
    /// 时间戳
    pub timestamp: u64,
}

impl Episode {
    /// 创建新记忆片段
    pub fn new(
        step: u64,
        event: String,
        reward: f32,
        energy: f32,
        neurons: usize,
    ) -> Self {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs();
        
        Self {
            step,
            event,
            reward,
            energy,
            neurons,
            timestamp,
        }
    }
    
    /// 简短描述
    pub fn summary(&self) -> String {
        format!(
            "[Step {}] {} | Reward: {:.2} | Energy: {:.2}",
            self.step,
            self.event,
            self.reward,
            self.energy
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_episode_creation() {
        let ep = Episode::new(
            100,
            "moved_north".to_string(),
            50.0,
            0.8,
            10000,
        );
        
        assert_eq!(ep.step, 100);
        assert_eq!(ep.event, "moved_north");
        assert_eq!(ep.reward, 50.0);
        assert!(ep.timestamp > 0);
    }
    
    #[test]
    fn test_episode_summary() {
        let ep = Episode::new(
            100,
            "moved_north".to_string(),
            50.0,
            0.8,
            10000,
        );
        
        let summary = ep.summary();
        assert!(summary.contains("Step 100"));
        assert!(summary.contains("moved_north"));
    }
}
