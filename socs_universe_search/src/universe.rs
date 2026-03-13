//! 单个宇宙定义
//! 
//! 一个宇宙 = 一个SOCS实例 + 特定参数配置 + 运行状态

use crate::{ParameterConfig, ArchitectureFamily};
use std::collections::HashMap;

/// 宇宙状态
pub struct Universe {
    /// 配置
    pub config: ParameterConfig,
    
    /// L0: 微单元
    pub units: Vec<MicroUnit>,
    
    /// L1: 团簇
    pub clusters: Vec<Cluster>,
    
    /// L2: 全局状态
    pub global_state: GlobalState,
    
    /// 当前tick
    tick: u64,
    
    /// 连接矩阵 (稀疏表示)
    pub connections: HashMap<(usize, usize), Connection>,
}

/// 微单元（简化版，实际使用SOCS的完整实现）
#[derive(Debug, Clone)]
pub struct MicroUnit {
    pub id: usize,
    pub activation: f32,
    pub energy: f32,
    pub memory_trace: f32,
    pub prediction_error: f32,
    pub plasticity: f32,
    pub unit_type: UnitType,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum UnitType {
    Excitatory,
    Inhibitory,
    Modulatory,
}

/// 团簇
#[derive(Debug, Clone)]
pub struct Cluster {
    pub id: usize,
    pub unit_ids: Vec<usize>,
    pub activation: f32,
    pub cohesion: f32,
    pub is_attractor: bool,
    pub is_dominant: bool,
}

/// 全局状态
#[derive(Debug, Clone)]
pub struct GlobalState {
    pub coherence: f32,
    pub broadcast_active: bool,
    pub dominant_cluster: Option<usize>,
}

/// 连接
#[derive(Debug, Clone)]
pub struct Connection {
    pub source: usize,
    pub target: usize,
    pub weight: f32,
    pub strength: f32,
}

impl Universe {
    /// 创建新宇宙
    pub fn new(config: ParameterConfig) -> Self {
        let num_units = config.num_units;
        
        // 初始化单元
        let mut units = Vec::with_capacity(num_units);
        for i in 0..num_units {
            units.push(MicroUnit {
                id: i,
                activation: 0.0,
                energy: config.energy_budget,
                memory_trace: 0.0,
                prediction_error: 0.0,
                plasticity: 0.1,
                unit_type: if i % 10 < 6 { 
                    UnitType::Excitatory 
                } else if i % 10 < 9 { 
                    UnitType::Inhibitory 
                } else { 
                    UnitType::Modulatory 
                },
            });
        }
        
        // 根据架构家族创建连接
        let connections = Self::create_connections(&config, num_units);
        
        Self {
            config,
            units,
            clusters: Vec::new(),
            global_state: GlobalState {
                coherence: 0.0,
                broadcast_active: false,
                dominant_cluster: None,
            },
            tick: 0,
            connections,
        }
    }
    
    /// 创建连接（根据架构家族）
    fn create_connections(config: &ParameterConfig, num_units: usize) -> HashMap<(usize, usize), Connection> {
        use ArchitectureFamily::*;
        
        let mut connections = HashMap::new();
        let density = config.connection_density;
        let target_connections = (num_units as f32 * density) as usize;
        
        match config.architecture {
            WormLike => {
                // 线虫型：局部连接 + 几个关键hub
                for i in 0..num_units {
                    // 局部邻居
                    for j in 1..=3 {
                        let left = (i + num_units - j) % num_units;
                        let right = (i + j) % num_units;
                        
                        connections.insert((i, left), Connection {
                            source: i, target: left,
                            weight: random_weight(), strength: 0.5,
                        });
                        connections.insert((i, right), Connection {
                            source: i, target: right,
                            weight: random_weight(), strength: 0.5,
                        });
                    }
                }
                
                // 添加几个hub（关键节点）
                let hubs = [num_units/4, num_units/2, 3*num_units/4];
                for &hub in &hubs {
                    for i in 0..num_units {
                        if i != hub && random_f32() < 0.1 {
                            connections.insert((hub, i), Connection {
                                source: hub, target: i,
                                weight: random_weight() * 2.0, strength: 0.8,
                            });
                        }
                    }
                }
            }
            
            OctopusLike => {
                // 章鱼型：臂部局部密集 + 弱中央
                let num_arms = 8;
                let arm_size = num_units / num_arms;
                let central_size = num_units - num_arms * arm_size;
                
                // 每个臂内部密集连接
                for arm in 0..num_arms {
                    let arm_start = arm * arm_size;
                    for i in arm_start..arm_start+arm_size {
                        for j in i+1..(i+20).min(arm_start+arm_size) {
                            if random_f32() < 0.3 {
                                connections.insert((i, j), Connection {
                                    source: i, target: j,
                                    weight: random_weight(), strength: 0.7,
                                });
                            }
                        }
                    }
                }
                
                // 弱中央连接
                let central_start = num_arms * arm_size;
                for i in central_start..num_units {
                    for j in (i+1)..num_units {
                        if random_f32() < 0.05 {
                            connections.insert((i, j), Connection {
                                source: i, target: j,
                                weight: random_weight(), strength: 0.3,
                            });
                        }
                    }
                }
            }
            
            TianxinPulse => {
                // 天心脉冲型：强中枢 + 节律连接
                let central_size = num_units / 10;
                
                // 中枢密集连接
                for i in 0..central_size {
                    for j in (i+1)..central_size {
                        connections.insert((i, j), Connection {
                            source: i, target: j,
                            weight: random_weight(), strength: 0.9,
                        });
                    }
                }
                
                // 外围连接到中枢
                for i in central_size..num_units {
                    let hub = (i % central_size) as usize;
                    connections.insert((hub, i), Connection {
                        source: hub, target: i,
                        weight: random_weight(), strength: 0.6,
                    });
                    connections.insert((i, hub), Connection {
                        source: i, target: hub,
                        weight: random_weight() * 0.5, strength: 0.4,
                    });
                }
                
                // 节律环连接
                for i in 0..num_units {
                    let next = (i + 1) % num_units;
                    connections.insert((i, next), Connection {
                        source: i, target: next,
                        weight: 0.3, strength: 0.5,
                    });
                }
            }
            
            RandomSparse => {
                // 随机稀疏
                for _ in 0..target_connections {
                    let source = random_usize(num_units);
                    let target = random_usize(num_units);
                    if source != target {
                        connections.insert((source, target), Connection {
                            source, target,
                            weight: random_weight(), strength: 0.5,
                        });
                    }
                }
            }
            
            ModularLattice => {
                // 模块网格：规则拓扑
                let module_size = 100;
                let num_modules = num_units / module_size;
                
                // 模块内全连接（或密集）
                for m in 0..num_modules {
                    let start = m * module_size;
                    for i in start..start+module_size {
                        for j in (i+1)..start+module_size {
                            if random_f32() < 0.2 {
                                connections.insert((i, j), Connection {
                                    source: i, target: j,
                                    weight: random_weight(), strength: 0.6,
                                });
                            }
                        }
                    }
                }
                
                // 模块间稀疏连接
                for m in 0..num_modules {
                    let next_m = (m + 1) % num_modules;
                    let start_m = m * module_size;
                    let start_next = next_m * module_size;
                    
                    for _ in 0..10 {
                        let i = start_m + random_usize(module_size);
                        let j = start_next + random_usize(module_size);
                        connections.insert((i, j), Connection {
                            source: i, target: j,
                            weight: random_weight(), strength: 0.4,
                        });
                    }
                }
            }
        }
        
        connections
    }
    
    /// 执行一个tick
    pub fn tick(&mut self) {
        self.tick += 1;
        
        // 1. 更新所有单元（局部规则）
        self.update_units();
        
        // 2. 检测/更新团簇
        self.update_clusters();
        
        // 3. 更新全局状态
        self.update_global_state();
        
        // 4. 应用可塑性（如果启用）
        self.apply_plasticity();
    }
    
    fn update_units(&mut self) {
        // 计算所有单元的输入
        let mut inputs = vec![0.0; self.units.len()];
        
        for ((source, target), conn) in &self.connections {
            if let Some(unit) = self.units.get(*source) {
                inputs[*target] += unit.activation * conn.weight * conn.strength;
            }
        }
        
        // 更新每个单元
        for (i, unit) in self.units.iter_mut().enumerate() {
            // 激活更新
            unit.activation = tanh(unit.activation * 0.8 + inputs[i]);
            
            // 能量代谢
            let cost = 0.001 + unit.activation.abs() * 0.01;
            unit.energy = (unit.energy - cost).max(0.0);
            
            // 记忆痕迹
            unit.memory_trace = unit.memory_trace * 0.95 + unit.activation.abs() * 0.05;
            
            // 预测误差
            unit.prediction_error = (inputs[i] - unit.activation).abs();
            
            // 可塑性
            unit.plasticity = 0.1 * unit.energy * (0.5 + unit.prediction_error);
        }
    }
    
    fn update_clusters(&mut self) {
        // 简化：基于连接密度检测团簇
        // 实际实现会更复杂
        
        // 这里简化：每100个单元为一个团簇
        let cluster_size = 100;
        let num_clusters = (self.units.len() + cluster_size - 1) / cluster_size;
        
        self.clusters.clear();
        for c in 0..num_clusters {
            let start = c * cluster_size;
            let end = (start + cluster_size).min(self.units.len());
            
            let unit_ids: Vec<_> = (start..end).collect();
            let activation: f32 = unit_ids.iter()
                .filter_map(|&i| self.units.get(i))
                .map(|u| u.activation.abs())
                .sum::<f32>() / unit_ids.len() as f32;
            
            self.clusters.push(Cluster {
                id: c,
                unit_ids,
                activation,
                cohesion: random_f32(), // 简化
                is_attractor: activation > 0.7,
                is_dominant: false,
            });
        }
        
        // 标记主导团簇
        if let Some(max_idx) = self.clusters.iter()
            .enumerate()
            .max_by(|a, b| a.1.activation.partial_cmp(&b.1.activation).unwrap())
            .map(|(i, _)| i) {
            self.clusters[max_idx].is_dominant = true;
            self.global_state.dominant_cluster = Some(max_idx);
        }
    }
    
    fn update_global_state(&mut self) {
        // 计算全局一致性
        let avg_activation: f32 = self.units.iter()
            .map(|u| u.activation.abs())
            .sum::<f32>() / self.units.len() as f32;
        
        self.global_state.coherence = avg_activation;
        self.global_state.broadcast_active = avg_activation > self.config.broadcast_threshold;
    }
    
    fn apply_plasticity(&mut self) {
        use crate::PlasticityProfile::*;
        
        // 根据可塑性家族调整权重
        match self.config.plasticity {
            Hebbian => {
                // Hebbian: 一起激活的单元加强连接
                for ((source, target), conn) in self.connections.iter_mut() {
                    if let (Some(s_unit), Some(t_unit)) = 
                        (self.units.get(*source), self.units.get(*target)) {
                        let correlation = s_unit.activation * t_unit.activation;
                        conn.weight += 0.001 * correlation * s_unit.plasticity;
                        conn.weight = conn.weight.clamp(-1.0, 1.0);
                    }
                }
            }
            _ => {
                // 其他可塑性规则简化处理
            }
        }
    }
    
    /// 当前tick
    pub fn current_tick(&self) -> u64 {
        self.tick
    }
    
    /// 获取状态摘要（用于验证）
    pub fn state_summary(&self) -> UniverseStateSummary {
        UniverseStateSummary {
            tick: self.tick,
            num_clusters: self.clusters.len(),
            num_attractors: self.clusters.iter().filter(|c| c.is_attractor).count(),
            avg_activation: self.units.iter().map(|u| u.activation.abs()).sum::<f32>() 
                / self.units.len() as f32,
            avg_energy: self.units.iter().map(|u| u.energy).sum::<f32>() 
                / self.units.len() as f32,
            global_coherence: self.global_state.coherence,
            has_dominant_cluster: self.global_state.dominant_cluster.is_some(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct UniverseStateSummary {
    pub tick: u64,
    pub num_clusters: usize,
    pub num_attractors: usize,
    pub avg_activation: f32,
    pub avg_energy: f32,
    pub global_coherence: f32,
    pub has_dominant_cluster: bool,
}

// 简化随机函数
fn random_f32() -> f32 {
    use std::sync::atomic::{AtomicU64, Ordering};
    static SEED: AtomicU64 = AtomicU64::new(1234567);
    
    let old = SEED.fetch_add(1, Ordering::SeqCst);
    let new = old.wrapping_mul(6364136223846793005).wrapping_add(1);
    ((new >> 32) as u32) as f32 / u32::MAX as f32
}

fn random_usize(max: usize) -> usize {
    (random_f32() * max as f32) as usize % max
}

fn random_weight() -> f32 {
    (random_f32() - 0.5) * 0.4
}

fn tanh(x: f32) -> f32 {
    x.clamp(-3.0, 3.0) / (1.0 + x.abs().sqrt())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{ArchitectureFamily, PlasticityFamily, BroadcastFamily, MemoryCoupling};
    
    fn test_config() -> ParameterConfig {
        ParameterConfig {
            architecture: ArchitectureFamily::WormLike,
            plasticity: PlasticityFamily::Hebbian,
            broadcast: BroadcastFamily::LocalCluster,
            memory: MemoryCoupling::L1L2,
            num_units: 302,
            connection_density: 0.05,
            learning_rate: 0.01,
            energy_budget: 1.0,
            competition_strength: 0.5,
            broadcast_threshold: 0.6,
            max_ticks: 1000,
            seed: 42,
        }
    }
    
    #[test]
    fn test_universe_creation() {
        let config = test_config();
        let universe = Universe::new(config);
        
        assert_eq!(universe.units.len(), 302);
        assert!(!universe.connections.is_empty());
    }
    
    #[test]
    fn test_universe_tick() {
        let config = test_config();
        let mut universe = Universe::new(config);
        
        let tick0 = universe.current_tick();
        universe.tick();
        let tick1 = universe.current_tick();
        
        assert_eq!(tick1, tick0 + 1);
    }
    
    #[test]
    fn test_state_summary() {
        let config = test_config();
        let mut universe = Universe::new(config);
        
        // 运行几个tick以初始化团簇
        for _ in 0..10 {
            universe.tick();
        }
        
        let summary = universe.state_summary();
        assert!(summary.tick >= 10);
        assert!(summary.num_clusters > 0); // 应该有团簇形成
    }
}
