//! L1: Meso-Cluster Dynamics
//! 
//! 微单元自组织成局部团簇，涌现吸引子、记忆、竞争。

use crate::micro_unit::{MicroUnit, UnitId};
use crate::plasticity::PlasticityRule;
use std::collections::{HashMap, HashSet};

/// 团簇ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct ClusterId(pub usize);

/// 团簇 - 自组织的单元组
/// 
/// 不是预定义的，而是从连接密度中检测出来的
#[derive(Debug, Clone)]
pub struct Cluster {
    pub id: ClusterId,
    
    /// 属于这个团簇的单元
    pub units: HashSet<UnitId>,
    
    /// 团簇整体激活（平均或峰值）
    pub activation: f32,
    
    /// 团簇内聚力（内部连接密度）
    pub cohesion: f32,
    
    /// 团簇稳定性（随时间的变化度）
    pub stability: f32,
    
    /// 团簇年龄
    pub age: u64,
    
    /// 历史激活轨迹（用于检测吸引子）
    pub activation_history: Vec<f32>,
    
    /// 当前占据"主导地位"
    pub is_dominant: bool,
    
    /// 与外界的连接强度
    pub external_connections: HashMap<ClusterId, f32>,
}

impl Cluster {
    pub fn new(id: usize) -> Self {
        Self {
            id: ClusterId(id),
            units: HashSet::new(),
            activation: 0.0,
            cohesion: 0.0,
            stability: 0.0,
            age: 0,
            activation_history: Vec::with_capacity(100),
            is_dominant: false,
            external_connections: HashMap::new(),
        }
    }
    
    /// 计算团簇激活（取单元最大或平均）
    pub fn compute_activation(&mut self, units: &HashMap<UnitId, MicroUnit>) {
        if self.units.is_empty() {
            self.activation = 0.0;
            return;
        }
        
        let sum: f32 = self.units
            .iter()
            .filter_map(|id| units.get(id))
            .map(|u| u.activation.abs())
            .sum();
        
        self.activation = sum / self.units.len() as f32;
        
        // 记录历史
        self.activation_history.push(self.activation);
        if self.activation_history.len() > 100 {
            self.activation_history.remove(0);
        }
    }
    
    /// 检测是否是稳定吸引子
    pub fn is_attractor(&self) -> bool {
        if self.activation_history.len() < 20 {
            return false;
        }
        
        let recent = &self.activation_history[self.activation_history.len()-20..];
        let mean = recent.iter().sum::<f32>() / recent.len() as f32;
        let variance = recent.iter()
            .map(|&x| (x - mean).powi(2))
            .sum::<f32>() / recent.len() as f32;
        
        // 高激活 + 低方差 = 稳定吸引子
        mean > 0.5 && variance < 0.05
    }
    
    /// 计算记忆保持能力
    pub fn memory_persistence(&self) -> f32 {
        if self.activation_history.len() < 10 {
            return 0.0;
        }
        
        // 简单的自相关近似
        let half = self.activation_history.len() / 2;
        let first_half: f32 = self.activation_history[..half].iter().sum();
        let second_half: f32 = self.activation_history[half..].iter().sum();
        
        let correlation = 1.0 - ((first_half - second_half).abs() / half as f32);
        correlation.clamp(0.0, 1.0)
    }
}

/// 团簇检测器
/// 
/// 从单元连接图中识别团簇
pub struct ClusterDetector {
    /// 密度阈值（多高才算团簇）
    pub density_threshold: f32,
    /// 最小团簇大小
    pub min_cluster_size: usize,
    /// 最大团簇数（资源限制）
    pub max_clusters: usize,
    /// 下一次分配的团簇ID
    next_cluster_id: usize,
}

impl ClusterDetector {
    pub fn new() -> Self {
        Self {
            density_threshold: 0.3,
            min_cluster_size: 5,
            max_clusters: 20,
            next_cluster_id: 0,
        }
    }
    
    /// 检测团簇（基于连接密度的简单算法）
    pub fn detect_clusters(
        &mut self,
        units: &HashMap<UnitId, MicroUnit>,
        _existing_clusters: &mut HashMap<ClusterId, Cluster>,
    ) -> HashMap<ClusterId, Cluster> {
        // 1. 构建邻接矩阵（简化版）
        let mut adjacency: HashMap<UnitId, Vec<UnitId>> = HashMap::new();
        for (id, unit) in units {
            let neighbors: Vec<_> = unit.outputs.keys()
                .filter(|&target_id| {
                    // 只考虑强连接
                    unit.outputs.get(target_id)
                        .map(|c| c.weight.abs() > self.density_threshold)
                        .unwrap_or(false)
                })
                .cloned()
                .collect();
            adjacency.insert(*id, neighbors);
        }
        
        // 2. 简单的标签传播/并查集
        let mut unit_to_cluster: HashMap<UnitId, ClusterId> = HashMap::new();
        let mut clusters: HashMap<ClusterId, Cluster> = HashMap::new();
        
        for (unit_id, neighbors) in &adjacency {
            if neighbors.len() < 2 {
                continue; // 孤立点不形成团簇
            }
            
            // 找邻居所属的团簇
            let neighbor_clusters: HashSet<_> = neighbors
                .iter()
                .filter_map(|n| unit_to_cluster.get(n))
                .cloned()
                .collect();
            
            if let Some(&existing_id) = neighbor_clusters.iter().next() {
                // 加入现有团簇
                unit_to_cluster.insert(*unit_id, existing_id);
                clusters.get_mut(&existing_id).unwrap().units.insert(*unit_id);
            } else if clusters.len() < self.max_clusters {
                // 创建新团簇
                let new_id = ClusterId(self.next_cluster_id);
                self.next_cluster_id += 1;
                
                let mut cluster = Cluster::new(new_id.0);
                cluster.units.insert(*unit_id);
                clusters.insert(new_id, cluster);
                unit_to_cluster.insert(*unit_id, new_id);
            }
        }
        
        // 3. 过滤小团簇
        clusters.retain(|_, c| c.units.len() >= self.min_cluster_size);
        
        clusters
    }
}

/// 团簇竞争协调器
/// 
/// 管理团簇间的竞争与协调，类似"winner-take-all"或"soft competition"
#[derive(Debug, Clone)]
pub struct ClusterCompetition {
    /// 竞争强度（0=完全独立，1=强烈竞争）
    pub competition_strength: f32,
    
    /// 当前主导团簇
    pub dominant_cluster: Option<ClusterId>,
    
    /// 上一次状态切换的时间
    pub last_switch_tick: u64,
    
    /// 状态切换历史
    pub switch_history: Vec<(u64, ClusterId, ClusterId)>, // (tick, from, to)
}

impl ClusterCompetition {
    pub fn new() -> Self {
        Self {
            competition_strength: 0.5,
            dominant_cluster: None,
            last_switch_tick: 0,
            switch_history: Vec::new(),
        }
    }
    
    /// 更新竞争状态
    pub fn update_competition(
        &mut self,
        clusters: &mut HashMap<ClusterId, Cluster>,
        current_tick: u64,
    ) {
        // 1. 找出最活跃的团簇
        let mut max_activation = 0.0;
        let mut winner = None;
        
        for (id, cluster) in clusters.iter() {
            if cluster.activation > max_activation {
                max_activation = cluster.activation;
                winner = Some(*id);
            }
        }
        
        // 重置所有主导标记
        for cluster in clusters.values_mut() {
            cluster.is_dominant = false;
        }
        
        // 2. 应用竞争抑制
        if let Some(winner_id) = winner {
            clusters.get_mut(&winner_id).unwrap().is_dominant = true;
            
            // 抑制其他团簇（降低它们的有效激活）
            for (id, cluster) in clusters.iter_mut() {
                if *id != winner_id {
                    let suppression = max_activation * self.competition_strength;
                    cluster.activation = (cluster.activation - suppression).max(0.0);
                }
            }
            
            // 3. 检测状态切换
            if self.dominant_cluster != Some(winner_id) {
                if let Some(old) = self.dominant_cluster {
                    self.switch_history.push((current_tick, old, winner_id));
                }
                self.dominant_cluster = Some(winner_id);
                self.last_switch_tick = current_tick;
            }
        }
    }
    
    /// 获取当前主导团簇的持续时间
    pub fn dominance_duration(&self, current_tick: u64) -> u64 {
        current_tick - self.last_switch_tick
    }
    
    /// 检测是否发生regime shift（长时间后的状态切换）
    pub fn detect_regime_shift(&self, min_duration: u64) -> Option<&(u64, ClusterId, ClusterId)> {
        self.switch_history.iter()
            .filter(|(tick, _, _)| *tick >= min_duration)
            .last()
    }
}

/// 工作记忆维持器
/// 
/// 维持团簇的激活状态，实现工作记忆功能
#[derive(Debug, Clone)]
pub struct WorkingMemory {
    /// 记忆容量（同时保持多少团簇活跃）
    pub capacity: usize,
    
    /// 当前保持活跃的团簇
    pub active_memories: Vec<MemorySlot>,
    
    /// 记忆衰减率
    pub decay_rate: f32,
    
    /// 记忆刷新增益
    pub refresh_boost: f32,
}

#[derive(Debug, Clone)]
pub struct MemorySlot {
    pub cluster_id: ClusterId,
    pub strength: f32, // 记忆强度
    pub age: u64,
}

impl WorkingMemory {
    pub fn new(capacity: usize) -> Self {
        Self {
            capacity,
            active_memories: Vec::with_capacity(capacity),
            decay_rate: 0.05,
            refresh_boost: 0.1,
        }
    }
    
    /// 更新记忆状态
    pub fn update(&mut self, clusters: &mut HashMap<ClusterId, Cluster>) {
        // 1. 衰减现有记忆
        for slot in &mut self.active_memories {
            slot.strength *= 1.0 - self.decay_rate;
            slot.age += 1;
        }
        
        // 2. 移除失效记忆
        self.active_memories.retain(|slot| slot.strength > 0.1);
        
        // 3. 如果团簇仍然活跃，刷新记忆
        for slot in &mut self.active_memories {
            if let Some(cluster) = clusters.get(&slot.cluster_id) {
                if cluster.activation > 0.5 {
                    slot.strength = (slot.strength + self.refresh_boost).min(1.0);
                }
            }
        }
        
        // 4. 将主导团簇纳入记忆（如果有空间）
        if let Some(dominant_id) = clusters.iter()
            .find(|(_, c)| c.is_dominant)
            .map(|(id, _)| *id) {
            
            let already_in_memory = self.active_memories.iter()
                .any(|s| s.cluster_id == dominant_id);
            
            if !already_in_memory && self.active_memories.len() < self.capacity {
                let activation = clusters.get(&dominant_id).map(|c| c.activation).unwrap_or(0.0);
                self.active_memories.push(MemorySlot {
                    cluster_id: dominant_id,
                    strength: activation,
                    age: 0,
                });
            }
        }
    }
    
    /// 获取最强记忆的团簇ID
    pub fn strongest_memory(&self) -> Option<ClusterId> {
        self.active_memories.iter()
            .max_by(|a, b| a.strength.partial_cmp(&b.strength).unwrap())
            .map(|s| s.cluster_id)
    }
}

/// L1层整体管理器
pub struct MesoLayer {
    pub detector: ClusterDetector,
    pub competition: ClusterCompetition,
    pub working_memory: WorkingMemory,
    pub clusters: HashMap<ClusterId, Cluster>,
}

impl MesoLayer {
    pub fn new() -> Self {
        Self {
            detector: ClusterDetector::new(),
            competition: ClusterCompetition::new(),
            working_memory: WorkingMemory::new(4), // 4个工作记忆槽
            clusters: HashMap::new(),
        }
    }
    
    /// L1完整更新周期
    pub fn update(&mut self, units: &HashMap<UnitId, MicroUnit>, tick: u64) {
        // 1. 检测/更新团簇
        self.clusters = self.detector.detect_clusters(units, &mut self.clusters);
        
        // 2. 更新每个团簇的激活
        for cluster in self.clusters.values_mut() {
            cluster.compute_activation(units);
            cluster.age += 1;
        }
        
        // 3. 团簇竞争
        self.competition.update_competition(&mut self.clusters, tick);
        
        // 4. 工作记忆更新
        self.working_memory.update(&mut self.clusters);
    }
    
    /// 获取当前状态摘要
    pub fn status_summary(&self) -> L1Status {
        L1Status {
            num_clusters: self.clusters.len(),
            num_attractors: self.clusters.values().filter(|c| c.is_attractor()).count(),
            dominant_cluster: self.competition.dominant_cluster,
            memory_slots_used: self.working_memory.active_memories.len(),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct L1Status {
    pub num_clusters: usize,
    pub num_attractors: usize,
    pub dominant_cluster: Option<ClusterId>,
    pub memory_slots_used: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::micro_unit::{MicroUnit, UnitType};
    
    fn create_test_units() -> HashMap<UnitId, MicroUnit> {
        let mut units = HashMap::new();
        for i in 0..10 {
            units.insert(UnitId(i), MicroUnit::new(i, UnitType::Excitatory));
        }
        units
    }
    
    #[test]
    fn test_cluster_creation() {
        let mut layer = MesoLayer::new();
        let units = create_test_units();
        
        layer.update(&units, 0);
        
        // 初始应该没有团簇（因为没有连接）
        assert_eq!(layer.clusters.len(), 0);
    }
    
    #[test]
    fn test_attractor_detection() {
        let mut cluster = Cluster::new(0);
        
        // 模拟稳定的高激活历史
        for _ in 0..30 {
            cluster.activation_history.push(0.8);
        }
        cluster.activation = 0.8;
        
        assert!(cluster.is_attractor());
    }
    
    #[test]
    fn test_working_memory_capacity() {
        let wm = WorkingMemory::new(3);
        assert_eq!(wm.capacity, 3);
        assert!(wm.active_memories.is_empty());
    }
}
