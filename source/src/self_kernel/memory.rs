//! AutobiographicalMemory: 自传记忆系统
//! 
//! 存储系统的自我历史。
//! 最小策略：max_size = 10000，旧的自动丢弃。

use super::Episode;
use std::collections::VecDeque;

/// 自传记忆
#[derive(Clone, Debug)]
pub struct AutobiographicalMemory {
    /// 记忆片段队列
    pub episodes: VecDeque<Episode>,
    
    /// 最大容量
    pub max_size: usize,
}

impl AutobiographicalMemory {
    /// 创建新记忆系统
    /// 
    /// # 参数
    /// * `max_size` - 最大记忆容量 (默认10000)
    pub fn new(max_size: usize) -> Self {
        Self {
            episodes: VecDeque::with_capacity(max_size),
            max_size,
        }
    }
    
    /// 添加记忆片段
    /// 
    /// 如果超过容量，自动丢弃最旧的记忆。
    pub fn push(&mut self, episode: Episode) {
        if self.episodes.len() >= self.max_size {
            self.episodes.pop_front(); // 丢弃最旧的
        }
        self.episodes.push_back(episode);
    }
    
    /// 获取记忆数量
    pub fn len(&self) -> usize {
        self.episodes.len()
    }
    
    /// 是否为空
    pub fn is_empty(&self) -> bool {
        self.episodes.is_empty()
    }
    
    /// 获取最近的N个记忆
    pub fn recent(&self, n: usize) -> Vec<&Episode> {
        self.episodes.iter().rev().take(n).collect()
    }
    
    /// 获取最近的记忆
    pub fn last(&self) -> Option<&Episode> {
        self.episodes.back()
    }
    
    /// 生成记忆摘要
    pub fn summary(&self) -> String {
        if self.episodes.is_empty() {
            return "No memories yet.".to_string();
        }
        
        let first = self.episodes.front().unwrap();
        let last = self.episodes.back().unwrap();
        
        format!(
            "Total episodes: {} | First: Step {} | Last: Step {}",
            self.episodes.len(),
            first.step,
            last.step
        )
    }
    
    /// 清空记忆
    pub fn clear(&mut self) {
        self.episodes.clear();
    }
}

impl Default for AutobiographicalMemory {
    fn default() -> Self {
        Self::new(10000)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_memory_creation() {
        let mem = AutobiographicalMemory::new(100);
        assert_eq!(mem.len(), 0);
        assert!(mem.is_empty());
    }
    
    #[test]
    fn test_memory_push() {
        let mut mem = AutobiographicalMemory::new(3);
        
        mem.push(Episode::new(1, "a".to_string(), 1.0, 1.0, 1));
        mem.push(Episode::new(2, "b".to_string(), 2.0, 2.0, 2));
        mem.push(Episode::new(3, "c".to_string(), 3.0, 3.0, 3));
        
        assert_eq!(mem.len(), 3);
        
        // 超过容量，最旧的应该被丢弃
        mem.push(Episode::new(4, "d".to_string(), 4.0, 4.0, 4));
        assert_eq!(mem.len(), 3);
        
        // 第一个应该是step 2 (step 1被丢弃)
        let first = mem.episodes.front().unwrap();
        assert_eq!(first.step, 2);
    }
    
    #[test]
    fn test_memory_recent() {
        let mut mem = AutobiographicalMemory::new(10);
        
        for i in 1..=5 {
            mem.push(Episode::new(i, format!("action{}", i), i as f32, i as f32, i));
        }
        
        let recent = mem.recent(3);
        assert_eq!(recent.len(), 3);
        assert_eq!(recent[0].step, 5); // 最新的
        assert_eq!(recent[2].step, 3);
    }
}
