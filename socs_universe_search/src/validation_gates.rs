//! 6门验证协议
//! 
//! 验证目标不是benchmark分数，而是6个动力学现象：
//! 1. 稳定attractors
//! 2. 记忆persistence
//! 3. regime shift后重组
//! 4. cluster specialization
//! 5. global broadcast emergence
//! 6. failure → recovery

use crate::universe::{Universe, UniverseStateSummary};
use std::collections::VecDeque;

/// 6门验证器
pub struct ValidationGates {
    /// 历史状态记录
    pub history: VecDeque<UniverseStateSummary>,
    
    /// 吸引子检测器
    pub attractor_detector: AttractorDetector,
    
    /// 记忆持久检测器
    pub memory_detector: MemoryPersistenceDetector,
    
    /// 重组检测器
    pub reorganization_detector: ReorganizationDetector,
    
    /// 团簇分化检测器
    pub specialization_detector: SpecializationDetector,
    
    /// 广播涌现检测器
    pub broadcast_detector: BroadcastEmergenceDetector,
    
    /// 故障恢复检测器
    pub recovery_detector: RecoveryDetector,
    
    /// 最大历史长度
    max_history: usize,
}

impl ValidationGates {
    pub fn new() -> Self {
        Self {
            history: VecDeque::with_capacity(10000),
            attractor_detector: AttractorDetector::new(),
            memory_detector: MemoryPersistenceDetector::new(),
            reorganization_detector: ReorganizationDetector::new(),
            specialization_detector: SpecializationDetector::new(),
            broadcast_detector: BroadcastEmergenceDetector::new(),
            recovery_detector: RecoveryDetector::new(),
            max_history: 10000,
        }
    }
    
    /// 观察一个tick
    pub fn observe(&mut self, tick: u64, universe: &Universe) {
        let summary = universe.state_summary();
        
        // 记录历史
        self.history.push_back(summary.clone());
        if self.history.len() > self.max_history {
            self.history.pop_front();
        }
        
        // 更新各个检测器
        self.attractor_detector.observe(tick, &summary);
        self.memory_detector.observe(tick, &summary);
        self.reorganization_detector.observe(tick, &summary);
        self.specialization_detector.observe(tick, &summary);
        self.broadcast_detector.observe(tick, &summary);
        self.recovery_detector.observe(tick, &summary);
    }
    
    /// 计算6门分数
    pub fn compute_scores(&self) -> crate::DynamicsScores {
        crate::DynamicsScores {
            attractor_formation: self.attractor_detector.score(),
            memory_persistence: self.memory_detector.score(),
            reorganization: self.reorganization_detector.score(),
            cluster_specialization: self.specialization_detector.score(),
            broadcast_emergence: self.broadcast_detector.score(),
            failure_recovery: self.recovery_detector.score(),
        }
    }
    
    /// 检测早期失败（用于提前终止）
    pub fn early_failure_detected(&self) -> bool {
        // 如果能量耗尽或完全死寂
        if let Some(latest) = self.history.back() {
            latest.avg_energy < 0.01 || latest.avg_activation < 0.001
        } else {
            false
        }
    }
    
    /// 稳定性评级
    pub fn stability_rating(&self) -> f32 {
        if self.history.len() < 100 {
            return 0.0;
        }
        
        let recent: Vec<_> = self.history.iter().rev().take(100).collect();
        let mean_energy: f32 = recent.iter().map(|s| s.avg_energy).sum::<f32>() / 100.0;
        let variance: f32 = recent.iter()
            .map(|s| (s.avg_energy - mean_energy).powi(2))
            .sum::<f32>() / 100.0;
        
        // 高能量 + 低方差 = 高稳定性
        (mean_energy * (1.0 - variance.sqrt())).clamp(0.0, 1.0)
    }
}

// ==================== 门1: 吸引子形成 ====================

pub struct AttractorDetector {
    attractor_episodes: Vec<(u64, u64)>, // (start_tick, end_tick)
    current_attractor_start: Option<u64>,
    stable_count: usize,
}

impl AttractorDetector {
    fn new() -> Self {
        Self {
            attractor_episodes: Vec::new(),
            current_attractor_start: None,
            stable_count: 0,
        }
    }
    
    fn observe(&mut self, tick: u64, summary: &UniverseStateSummary) {
        let is_stable = summary.num_attractors > 0 && summary.global_coherence > 0.5;
        
        match (self.current_attractor_start, is_stable) {
            (None, true) => {
                // 新吸引子开始
                self.current_attractor_start = Some(tick);
            }
            (Some(start), false) => {
                // 吸引子结束
                if tick - start > 50 { // 至少持续50ticks
                    self.attractor_episodes.push((start, tick));
                }
                self.current_attractor_start = None;
            }
            (Some(_), true) => {
                self.stable_count += 1;
            }
            _ => {}
        }
    }
    
    fn score(&self) -> f32 {
        // 基于吸引子出现频率和持续时间评分
        let total_attractor_time: u64 = self.attractor_episodes.iter()
            .map(|(s, e)| e - s)
            .sum();
        
        (total_attractor_time as f32 / 1000.0).min(1.0)
    }
}

// ==================== 门2: 记忆持久 ====================

pub struct MemoryPersistenceDetector {
    persistence_events: Vec<(u64, u64)>, // (input_tick, memory_duration)
    last_dominant: Option<usize>,
    persistence_count: usize,
}

impl MemoryPersistenceDetector {
    fn new() -> Self {
        Self {
            persistence_events: Vec::new(),
            last_dominant: None,
            persistence_count: 0,
        }
    }
    
    fn observe(&mut self, tick: u64, summary: &UniverseStateSummary) {
        // 检测主导团簇的变化
        // 简化：用global_coherence作为记忆强度的代理
        if summary.global_coherence > 0.6 {
            self.persistence_count += 1;
        }
    }
    
    fn score(&self) -> f32 {
        (self.persistence_count as f32 / 500.0).min(1.0)
    }
}

// ==================== 门3: 重组 ====================

pub struct ReorganizationDetector {
    regime_shifts: Vec<u64>,
    coherence_history: Vec<f32>,
}

impl ReorganizationDetector {
    fn new() -> Self {
        Self {
            regime_shifts: Vec::new(),
            coherence_history: Vec::with_capacity(1000),
        }
    }
    
    fn observe(&mut self, tick: u64, summary: &UniverseStateSummary) {
        self.coherence_history.push(summary.global_coherence);
        
        // 检测相变（一致性突变）
        if self.coherence_history.len() >= 20 {
            let recent_avg: f32 = self.coherence_history.iter().rev().take(10).sum::<f32>() / 10.0;
            let previous_avg: f32 = self.coherence_history.iter().rev().skip(10).take(10).sum::<f32>() / 10.0;
            
            if (recent_avg - previous_avg).abs() > 0.3 {
                self.regime_shifts.push(tick);
            }
        }
    }
    
    fn score(&self) -> f32 {
        // 重组能力 = 经历相变后恢复的次数
        (self.regime_shifts.len() as f32 / 5.0).min(1.0)
    }
}

// ==================== 门4: 团簇分化 ====================

pub struct SpecializationDetector {
    cluster_diversity_history: Vec<f32>,
}

impl SpecializationDetector {
    fn new() -> Self {
        Self {
            cluster_diversity_history: Vec::with_capacity(1000),
        }
    }
    
    fn observe(&mut self, _tick: u64, summary: &UniverseStateSummary) {
        // 用attractor数量作为分化的代理
        let diversity = (summary.num_attractors as f32 / summary.num_clusters.max(1) as f32)
            .min(1.0);
        self.cluster_diversity_history.push(diversity);
    }
    
    fn score(&self) -> f32 {
        if self.cluster_diversity_history.is_empty() {
            return 0.0;
        }
        
        let avg_diversity: f32 = self.cluster_diversity_history.iter().sum::<f32>() 
            / self.cluster_diversity_history.len() as f32;
        avg_diversity
    }
}

// ==================== 门5: 广播涌现 ====================

pub struct BroadcastEmergenceDetector {
    broadcast_events: Vec<u64>,
    coherence_threshold_crosses: usize,
}

impl BroadcastEmergenceDetector {
    fn new() -> Self {
        Self {
            broadcast_events: Vec::new(),
            coherence_threshold_crosses: 0,
        }
    }
    
    fn observe(&mut self, tick: u64, summary: &UniverseStateSummary) {
        // 广播 = 高一致性 + 有主导团簇
        if summary.global_coherence > 0.6 && summary.has_dominant_cluster {
            self.broadcast_events.push(tick);
            self.coherence_threshold_crosses += 1;
        }
    }
    
    fn score(&self) -> f32 {
        (self.broadcast_events.len() as f32 / 300.0).min(1.0)
    }
}

// ==================== 门6: 故障恢复 ====================

pub struct RecoveryDetector {
    failure_events: Vec<u64>,
    recovery_events: Vec<(u64, u64)>, // (failure_tick, recovery_tick)
    in_failure: bool,
    failure_start: Option<u64>,
}

impl RecoveryDetector {
    fn new() -> Self {
        Self {
            failure_events: Vec::new(),
            recovery_events: Vec::new(),
            in_failure: false,
            failure_start: None,
        }
    }
    
    fn observe(&mut self, tick: u64, summary: &UniverseStateSummary) {
        let is_failing = summary.avg_energy < 0.2 || summary.avg_activation < 0.1;
        
        match (self.in_failure, is_failing) {
            (false, true) => {
                // 故障开始
                self.failure_events.push(tick);
                self.in_failure = true;
                self.failure_start = Some(tick);
            }
            (true, false) => {
                // 故障恢复
                if let Some(start) = self.failure_start {
                    self.recovery_events.push((start, tick));
                }
                self.in_failure = false;
                self.failure_start = None;
            }
            _ => {}
        }
    }
    
    fn score(&self) -> f32 {
        if self.failure_events.is_empty() {
            return 0.5; // 没有故障也没有恢复
        }
        
        let recovery_rate = self.recovery_events.len() as f32 
            / self.failure_events.len() as f32;
        recovery_rate
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{ArchitectureFamily, PlasticityFamily, BroadcastFamily, MemoryCoupling, ParameterConfig};
    
    #[test]
    fn test_validation_gates() {
        let mut gates = ValidationGates::new();
        let config = ParameterConfig {
            architecture: ArchitectureFamily::WormLike,
            plasticity: PlasticityFamily::Hebbian,
            broadcast: BroadcastFamily::LocalCluster,
            memory: MemoryCoupling::L1L2,
            num_units: 100,
            connection_density: 0.05,
            learning_rate: 0.01,
            energy_budget: 1.0,
            competition_strength: 0.5,
            broadcast_threshold: 0.6,
            max_ticks: 100,
            seed: 42,
        };
        
        let mut universe = Universe::new(config);
        
        for tick in 0..100 {
            universe.tick();
            gates.observe(tick, &universe);
        }
        
        let scores = gates.compute_scores();
        println!("Scores: {:?}", scores);
        
        // 所有分数应该在合理范围内
        assert!(scores.attractor_formation >= 0.0 && scores.attractor_formation <= 1.0);
        assert!(scores.memory_persistence >= 0.0 && scores.memory_persistence <= 1.0);
    }
}
