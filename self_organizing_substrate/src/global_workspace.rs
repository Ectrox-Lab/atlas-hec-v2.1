//! L2: Global Workspace
//! 
//! 全局广播机制，从L1团簇竞争中涌现。
//! 不是人工写的"意识模块"，而是信息如何占据全局带宽的自然结果。

use crate::micro_unit::UnitId;
use crate::cluster_dynamics::{ClusterId, Cluster, MesoLayer};
use std::collections::{HashMap, VecDeque};

/// 广播内容
/// 
/// 在全局工作空间中传播的信息
#[derive(Debug, Clone)]
pub struct Broadcast {
    /// 来源团簇
    pub source_cluster: ClusterId,
    
    /// 内容（团簇激活模式的压缩表示）
    pub content: BroadcastContent,
    
    /// 信号强度（决定传播范围）
    pub signal_strength: f32,
    
    /// 时效性（衰减计数）
    pub ttl: u32, // time to live
    
    /// 创建时间
    pub created_at: u64,
    
    /// 传播足迹（哪些单元已接收）
    pub reach: Vec<UnitId>,
}

#[derive(Debug, Clone)]
pub enum BroadcastContent {
    /// 激活模式（向量压缩）
    ActivationPattern(Vec<f32>),
    
    /// 预测误差信号（驱动学习）
    PredictionError(f32, Vec<ClusterId>), // (magnitude, affected_clusters)
    
    /// 协调请求（需要其他团簇配合）
    CoordinationRequest { target_clusters: Vec<ClusterId>, priority: f32 },
    
    /// 异常/新奇信号
    NoveltySignal { location: ClusterId, surprise: f32 },
}

/// 全局工作空间
/// 
/// 核心机制：
/// 1. 团簇竞争获得广播权（winner-take-all或graded）
/// 2. 获胜团簇的状态被广播到全局
/// 3. 其他团簇根据广播调整自己的状态
/// 4. 广播内容随时间衰减，需要持续"刷新"才能维持
#[derive(Debug, Clone)]
pub struct GlobalWorkspace {
    /// 当前活跃的广播
    pub active_broadcasts: Vec<Broadcast>,
    
    /// 广播容量（同时能传播多少信号）
    pub capacity: usize,
    
    /// 广播阈值（需要多高激活才能获得广播权）
    pub broadcast_threshold: f32,
    
    /// 全局一致性（所有团簇的协调程度）
    pub global_coherence: f32,
    
    /// 全局激活水平（整体网络活跃度）
    pub global_activation: f32,
    
    /// 广播历史（用于分析涌现行为）
    pub broadcast_history: VecDeque<BroadcastRecord>,
    
    /// 最大历史长度
    pub max_history: usize,
    
    /// 当前tick
    pub current_tick: u64,
}

#[derive(Debug, Clone)]
pub struct BroadcastRecord {
    pub tick: u64,
    pub source: ClusterId,
    pub content_type: &'static str,
    pub strength: f32,
    pub reach_size: usize,
}

impl GlobalWorkspace {
    pub fn new(capacity: usize) -> Self {
        Self {
            active_broadcasts: Vec::with_capacity(capacity),
            capacity,
            broadcast_threshold: 0.6,
            global_coherence: 0.0,
            global_activation: 0.0,
            broadcast_history: VecDeque::with_capacity(1000),
            max_history: 1000,
            current_tick: 0,
        }
    }
    
    /// L2完整更新周期
    /// 
    /// 从L1团簇状态中涌现全局广播
    pub fn update(&mut self, l1: &mut MesoLayer) {
        self.current_tick += 1;
        
        // 1. 衰减现有广播
        self.decay_broadcasts();
        
        // 2. 清理过期广播
        self.active_broadcasts.retain(|b| b.ttl > 0);
        
        // 3. 计算全局统计
        self.compute_global_stats(&l1.clusters);
        
        // 4. 选择新的广播者（从主导团簇）
        self.select_broadcasters(&l1.clusters);
        
        // 5. 传播广播到接收者（影响其他团簇）
        self.propagate_broadcasts(l1);
        
        // 6. 记录历史
        self.record_history();
    }
    
    /// 衰减所有活跃广播
    fn decay_broadcasts(&mut self) {
        for broadcast in &mut self.active_broadcasts {
            broadcast.ttl = broadcast.ttl.saturating_sub(1);
            broadcast.signal_strength *= 0.95;
        }
    }
    
    /// 计算全局统计
    fn compute_global_stats(&mut self, clusters: &HashMap<ClusterId, Cluster>) {
        if clusters.is_empty() {
            self.global_activation = 0.0;
            self.global_coherence = 0.0;
            return;
        }
        
        // 全局激活 = 平均团簇激活
        let total_activation: f32 = clusters.values()
            .map(|c| c.activation)
            .sum();
        self.global_activation = total_activation / clusters.len() as f32;
        
        // 全局一致性 = 团簇间激活的方差倒数（越相似越一致）
        let mean = self.global_activation;
        let variance: f32 = clusters.values()
            .map(|c| (c.activation - mean).powi(2))
            .sum::<f32>() / clusters.len() as f32;
        self.global_coherence = (1.0 - variance.sqrt()).max(0.0);
    }
    
    /// 选择哪些团簇获得广播权
    fn select_broadcasters(&mut self, clusters: &HashMap<ClusterId, Cluster>) {
        // 找出达到广播阈值的团簇
        let candidates: Vec<_> = clusters.values()
            .filter(|c| c.activation > self.broadcast_threshold && c.is_dominant)
            .collect();
        
        // 按激活排序，取前capacity个
        let mut sorted: Vec<_> = candidates.iter().map(|&c| c).collect();
        sorted.sort_by(|a, b| b.activation.partial_cmp(&a.activation).unwrap());
        
        for cluster in sorted.iter().take(self.capacity) {
            // 检查是否已有来自该团簇的活跃广播
            let already_broadcasting = self.active_broadcasts.iter()
                .any(|b| b.source_cluster == cluster.id);
            
            if !already_broadcasting {
                let broadcast = self.create_broadcast(cluster);
                if self.active_broadcasts.len() < self.capacity {
                    self.active_broadcasts.push(broadcast);
                }
            }
        }
    }
    
    /// 从团簇创建广播内容
    fn create_broadcast(&self, cluster: &Cluster) -> Broadcast {
        // 简化：团簇的激活模式作为内容
        let pattern = vec![cluster.activation, cluster.cohesion, cluster.stability];
        
        Broadcast {
            source_cluster: cluster.id,
            content: BroadcastContent::ActivationPattern(pattern),
            signal_strength: cluster.activation,
            ttl: 50, // 存活50 ticks
            created_at: self.current_tick,
            reach: Vec::new(),
        }
    }
    
    /// 传播广播到其他团簇（调制它们的状态）
    fn propagate_broadcasts(&mut self, l1: &mut MesoLayer) {
        for broadcast in &self.active_broadcasts {
            match &broadcast.content {
                BroadcastContent::ActivationPattern(pattern) => {
                    // 广播模式调制其他团簇的激活
                    for (cluster_id, cluster) in l1.clusters.iter_mut() {
                        if *cluster_id != broadcast.source_cluster {
                            // 距离越近（连接越强），调制越大
                            let connection_strength = broadcast.signal_strength 
                                * cluster.external_connections.get(&broadcast.source_cluster)
                                    .unwrap_or(&0.1);
                            
                            // 调制激活（增强相似模式，抑制不相似）
                            let modulation = (pattern[0] - cluster.activation) 
                                * connection_strength * 0.1;
                            cluster.activation = (cluster.activation + modulation).clamp(0.0, 1.0);
                        }
                    }
                }
                BroadcastContent::PredictionError(_magnitude, affected) => {
                    // 误差信号增强相关团簇的可塑性
                    for cluster_id in affected {
                        if let Some(cluster) = l1.clusters.get_mut(cluster_id) {
                            // 标记高误差，驱动学习
                            // 暂时增加可塑性（实际实现会更复杂）
                            cluster.stability *= 0.9;
                        }
                    }
                }
                _ => {}
            }
        }
    }
    
    /// 记录广播历史
    fn record_history(&mut self) {
        for broadcast in &self.active_broadcasts {
            let record = BroadcastRecord {
                tick: self.current_tick,
                source: broadcast.source_cluster,
                content_type: match &broadcast.content {
                    BroadcastContent::ActivationPattern(_) => "activation",
                    BroadcastContent::PredictionError(_, _) => "error",
                    BroadcastContent::CoordinationRequest { .. } => "coordination",
                    BroadcastContent::NoveltySignal { .. } => "novelty",
                },
                strength: broadcast.signal_strength,
                reach_size: broadcast.reach.len(),
            };
            
            if self.broadcast_history.len() >= self.max_history {
                self.broadcast_history.pop_front();
            }
            self.broadcast_history.push_back(record);
        }
    }
    
    /// 广播新颖信号（从外部检测到的异常）
    pub fn broadcast_novelty(&mut self, location: ClusterId, surprise: f32) {
        if surprise > self.broadcast_threshold && self.active_broadcasts.len() < self.capacity {
            let broadcast = Broadcast {
                source_cluster: location,
                content: BroadcastContent::NoveltySignal { location, surprise },
                signal_strength: surprise,
                ttl: 30,
                created_at: self.current_tick,
                reach: Vec::new(),
            };
            self.active_broadcasts.push(broadcast);
        }
    }
    
    /// 获取当前主导广播的序列（用于分析整合流）
    pub fn get_dominant_sequence(&self, window: usize) -> Vec<ClusterId> {
        self.broadcast_history.iter()
            .rev()
            .take(window)
            .filter(|r| r.strength > 0.5)
            .map(|r| r.source)
            .collect()
    }
    
    /// 检测全局整合事件（多个团簇快速交替广播）
    pub fn detect_integration_event(&self) -> bool {
        let recent: Vec<_> = self.broadcast_history.iter()
            .rev()
            .take(20)
            .collect();
        
        if recent.len() < 10 {
            return false;
        }
        
        // 检查是否有多个不同来源
        let unique_sources: std::collections::HashSet<_> = recent.iter()
            .map(|r| r.source)
            .collect();
        
        // 多个来源 + 高整体强度 = 整合事件
        unique_sources.len() > 2 && 
            recent.iter().map(|r| r.strength).sum::<f32>() / recent.len() as f32 > 0.5
    }
}

/// 全局工作空间状态摘要
#[derive(Debug, Clone, Copy)]
pub struct L2Status {
    /// 活跃广播数
    pub num_broadcasts: usize,
    /// 全局一致性
    pub global_coherence: f32,
    /// 全局激活水平
    pub global_activation: f32,
    /// 是否有整合事件
    pub integration_event: bool,
}

impl GlobalWorkspace {
    pub fn status_summary(&self) -> L2Status {
        L2Status {
            num_broadcasts: self.active_broadcasts.len(),
            global_coherence: self.global_coherence,
            global_activation: self.global_activation,
            integration_event: self.detect_integration_event(),
        }
    }
}

/// 涌现检测器
/// 
/// 分析L1/L2动力学，检测 emergent phenomena
pub struct EmergenceDetector {
    /// 吸引子形成历史
    pub attractor_formation_times: Vec<u64>,
    
    /// 状态切换历史
    pub state_transitions: Vec<(u64, String, String)>, // (tick, from, to)
    
    /// 协调涌现时间
    pub coherence_emergence: Vec<u64>,
    
    /// 故障恢复时间
    pub recovery_events: Vec<(u64, u64)>, // (failure_tick, recovery_tick)
}

impl EmergenceDetector {
    pub fn new() -> Self {
        Self {
            attractor_formation_times: Vec::new(),
            state_transitions: Vec::new(),
            coherence_emergence: Vec::new(),
            recovery_events: Vec::new(),
        }
    }
    
    /// 分析当前状态，检测涌现现象
    pub fn analyze(&mut self, tick: u64, l1: &MesoLayer, l2: &GlobalWorkspace) -> EmergenceReport {
        let mut report = EmergenceReport::default();
        
        // 1. 检测吸引子
        for cluster in l1.clusters.values() {
            if cluster.is_attractor() && cluster.age == tick {
                // 新形成的吸引子
                self.attractor_formation_times.push(tick);
                report.new_attractors += 1;
            }
        }
        
        // 2. 检测状态切换
        if let Some(&(t, _from, _to)) = l1.competition.switch_history.last() {
            if t == tick {
                report.state_switches += 1;
            }
        }
        
        // 3. 检测协调涌现
        if l2.global_coherence > 0.7 && l2.global_activation > 0.5 {
            if self.coherence_emergence.last() != Some(&tick) {
                self.coherence_emergence.push(tick);
                report.coherence_emergence = true;
            }
        }
        
        // 4. 检测整合事件
        if l2.detect_integration_event() {
            report.integration_event = true;
        }
        
        report
    }
}

#[derive(Debug, Clone, Default)]
pub struct EmergenceReport {
    pub new_attractors: usize,
    pub state_switches: usize,
    pub coherence_emergence: bool,
    pub integration_event: bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_broadcast_creation() {
        let ws = GlobalWorkspace::new(3);
        assert_eq!(ws.capacity, 3);
        assert!(ws.active_broadcasts.is_empty());
    }
    
    #[test]
    fn test_global_stats() {
        let mut ws = GlobalWorkspace::new(3);
        let mut clusters = HashMap::new();
        
        let mut c1 = Cluster::new(0);
        c1.activation = 0.8;
        clusters.insert(ClusterId(0), c1);
        
        let mut c2 = Cluster::new(1);
        c2.activation = 0.4;
        clusters.insert(ClusterId(1), c2);
        
        ws.compute_global_stats(&clusters);
        
        assert_eq!(ws.global_activation, 0.6);
    }
    
    #[test]
    fn test_emergence_report() {
        let report = EmergenceReport::default();
        assert_eq!(report.new_attractors, 0);
        assert!(!report.coherence_emergence);
    }
}
