//! Substrate <-> Open World Bridge
//! 
//! 将自组织认知基底连接到Bio-World开放环境。
//! 关键约束：环境只提供局部感知，输出只允许低带宽action tendencies。

use crate::micro_unit::{MicroUnit, UnitId, UnitType, UnitConfig};
use crate::cluster_dynamics::{MesoLayer, L1Status};
use crate::global_workspace::{GlobalWorkspace, L2Status, EmergenceDetector, EmergenceReport};
use std::collections::HashMap;

/// 感知输入
/// 
/// 环境提供给基底的最小局部信息
#[derive(Debug, Clone)]
pub struct SensoryInput {
    /// 视觉/邻近信号
    pub nearby_entities: Vec<EntitySignal>,
    
    /// 资源信号（食物等）
    pub resource_signals: Vec<ResourceSignal>,
    
    /// 威胁信号
    pub threat_signals: Vec<ThreatSignal>,
    
    /// 自体内感觉
    pub interoception: Interoception,
    
    /// 时间信号
    pub temporal_context: TemporalContext,
}

#[derive(Debug, Clone)]
pub struct EntitySignal {
    pub direction: f32, // -1.0 (左) to 1.0 (右)
    pub distance: f32,  // 0.0 (近) to 1.0 (远)
    pub entity_type: EntityType,
    pub is_cooperative: Option<bool>, // 是否表现出合作行为
}

#[derive(Debug, Clone, Copy)]
pub enum EntityType {
    Conspecific, // 同类
    Food,
    Obstacle,
    Unknown,
}

#[derive(Debug, Clone)]
pub struct ResourceSignal {
    pub direction: f32,
    pub intensity: f32,
    pub resource_type: ResourceType,
}

#[derive(Debug, Clone, Copy)]
pub enum ResourceType {
    Energy,    // 恢复能量
    Material,  // 用于构建/连接
    Information, // 可学习的信息
}

#[derive(Debug, Clone)]
pub struct ThreatSignal {
    pub direction: f32,
    pub urgency: f32, // 0.0 (低) to 1.0 (高)
    pub threat_type: ThreatType,
}

#[derive(Debug, Clone, Copy)]
pub enum ThreatType {
    Predator,
    Environmental, // 如毒素、极端温度
    Social,        // 如攻击性的同类
}

#[derive(Debug, Clone)]
pub struct Interoception {
    /// 能量水平
    pub energy: f32,
    /// 压力/损伤
    pub stress: f32,
    /// 驱动/动机强度
    pub drive: f32,
    /// 基础代谢率
    pub metabolism: f32,
}

#[derive(Debug, Clone)]
pub struct TemporalContext {
    /// 当前tick
    pub tick: u64,
    /// 日/夜或其他周期
    pub cycle_phase: f32,
    /// 过去事件的记忆痕迹
    pub recent_events: Vec<EventMemory>,
}

#[derive(Debug, Clone)]
pub struct EventMemory {
    pub tick: u64,
    pub event_type: String,
    pub emotional_valence: f32, // -1.0 (负面) to 1.0 (正面)
}

/// 行动倾向输出
/// 
/// 基底产生的低带宽行为倾向，不是具体动作
#[derive(Debug, Clone)]
pub struct ActionTendencies {
    /// 运动倾向 [左转, 前进, 右转, 后退]
    pub movement: [f32; 4],
    
    /// 交互倾向 [接近, 回避, 互动, 忽略]
    pub interaction: [f32; 4],
    
    /// 能量管理倾向 [探索, 节能, 冲刺, 休眠]
    pub energy_management: [f32; 4],
    
    /// 社交倾向 [合作, 竞争, 观察, 孤立]
    pub social: [f32; 4],
    
    /// 信心/确定性
    pub confidence: f32,
}

impl ActionTendencies {
    /// 选择最强倾向并归一化
    pub fn select_action(&self) -> (ActionType, f32) {
        let all = [
            (ActionType::MoveLeft, self.movement[0]),
            (ActionType::MoveForward, self.movement[1]),
            (ActionType::MoveRight, self.movement[2]),
            (ActionType::MoveBack, self.movement[3]),
            (ActionType::Approach, self.interaction[0]),
            (ActionType::Avoid, self.interaction[1]),
            (ActionType::Interact, self.interaction[2]),
            (ActionType::Ignore, self.interaction[3]),
        ];
        
        all.iter()
            .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
            .map(|(a, v)| (*a, *v))
            .unwrap_or((ActionType::Ignore, 0.0))
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ActionType {
    MoveLeft, MoveForward, MoveRight, MoveBack,
    Approach, Avoid, Interact, Ignore,
}

/// 认知基底-环境接口
/// 
/// 核心对象：将SOCS连接到开放世界
pub struct SubstrateEnvironmentBridge {
    /// L0: 微单元网络
    pub units: HashMap<UnitId, MicroUnit>,
    
    /// L1: 团簇动力学
    pub meso_layer: MesoLayer,
    
    /// L2: 全局工作空间
    pub global_workspace: GlobalWorkspace,
    
    /// 涌现检测器
    pub emergence: EmergenceDetector,
    
    /// 单元配置
    pub unit_config: UnitConfig,
    
    /// 感知输入单元映射
    pub sensory_units: SensoryMapping,
    
    /// 行动输出单元映射
    pub action_units: ActionMapping,
    
    /// 当前tick
    pub tick: u64,
    
    /// 性能统计
    pub stats: BridgeStats,
}

/// 感知单元映射（环境输入 -> 特定单元群）
#[derive(Debug, Clone)]
pub struct SensoryMapping {
    /// 左侧视觉单元起始ID
    pub vision_left: Vec<UnitId>,
    /// 前方视觉单元
    pub vision_forward: Vec<UnitId>,
    /// 右侧视觉单元
    pub vision_right: Vec<UnitId>,
    
    /// 资源感知单元
    pub resource_units: Vec<UnitId>,
    
    /// 威胁感知单元
    pub threat_units: Vec<UnitId>,
    
    /// 内感受单元
    pub intero_units: Vec<UnitId>,
}

/// 行动单元映射（特定单元群 -> 行动倾向）
#[derive(Debug, Clone)]
pub struct ActionMapping {
    /// 运动倾向读取单元
    pub movement_units: Vec<UnitId>,
    
    /// 交互倾向读取单元
    pub interaction_units: Vec<UnitId>,
    
    /// 能量管理倾向读取单元
    pub energy_units: Vec<UnitId>,
    
    /// 社交倾向读取单元
    pub social_units: Vec<UnitId>,
}

#[derive(Debug, Clone, Default)]
pub struct BridgeStats {
    pub total_ticks: u64,
    pub attractors_formed: usize,
    pub state_switches: usize,
    pub integration_events: usize,
    pub avg_coherence: f32,
}

impl SubstrateEnvironmentBridge {
    /// 创建新的桥接实例
    pub fn new(num_units: usize) -> Self {
        let mut units = HashMap::new();
        
        // 创建基础单元网络
        // 分布：60% 兴奋性, 30% 抑制性, 10% 调节性
        for i in 0..num_units {
            let unit_type = if i % 10 < 6 {
                UnitType::Excitatory
            } else if i % 10 < 9 {
                UnitType::Inhibitory
            } else {
                UnitType::Modulatory
            };
            
            units.insert(UnitId(i), MicroUnit::new(i, unit_type));
        }
        
        // 创建局部连接（简化：每个单元连接最近的10个邻居）
        Self::create_local_connections(&mut units, 10);
        
        // 设置感知映射（前10%单元用于感知）
        let sensory_end = num_units / 10;
        let sensory = SensoryMapping {
            vision_left: (0..sensory_end/3).map(UnitId).collect(),
            vision_forward: (sensory_end/3..2*sensory_end/3).map(UnitId).collect(),
            vision_right: (2*sensory_end/3..sensory_end).map(UnitId).collect(),
            resource_units: (sensory_end..sensory_end+10).map(UnitId).collect(),
            threat_units: (sensory_end+10..sensory_end+20).map(UnitId).collect(),
            intero_units: (sensory_end+20..sensory_end+30).map(UnitId).collect(),
        };
        
        // 设置行动映射（后10%单元用于输出）
        let action_start = num_units * 9 / 10;
        let action = ActionMapping {
            movement_units: (action_start..action_start+10).map(UnitId).collect(),
            interaction_units: (action_start+10..action_start+20).map(UnitId).collect(),
            energy_units: (action_start+20..action_start+30).map(UnitId).collect(),
            social_units: (action_start+30..action_start+40).map(UnitId).collect(),
        };
        
        Self {
            units,
            meso_layer: MesoLayer::new(),
            global_workspace: GlobalWorkspace::new(3),
            emergence: EmergenceDetector::new(),
            unit_config: UnitConfig::default(),
            sensory_units: sensory,
            action_units: action,
            tick: 0,
            stats: BridgeStats::default(),
        }
    }
    
    /// 创建局部连接（简化版）
    fn create_local_connections(units: &mut HashMap<UnitId, MicroUnit>, connection_radius: usize) {
        let ids: Vec<_> = units.keys().cloned().collect();
        let n = ids.len();
        
        // 收集所有连接
        let mut all_connections: Vec<(UnitId, UnitId, f32)> = Vec::new();
        
        for (i, &id) in ids.iter().enumerate() {
            // 连接最近的邻居
            for j in 1..=connection_radius {
                let left = (i + n - j) % n;
                let right = (i + j) % n;
                
                // 随机权重初始化
                let w_left = (random_f32() - 0.5) * 0.2;
                let w_right = (random_f32() - 0.5) * 0.2;
                
                all_connections.push((id, ids[left], w_left));
                all_connections.push((id, ids[right], w_right));
            }
        }
        
        // 应用连接
        for (source_id, target_id, weight) in all_connections {
            if let Some(source) = units.get_mut(&source_id) {
                let _conn = source.connect_to(target_id, weight);
                // 注意：这里需要同时更新target的inputs，但我们不能直接可变借用两次
                // 所以先存储，后面再处理
            }
        }
        
        // 重新构建inputs（需要clone outputs）
        let outputs_snapshot: HashMap<_, _> = units.iter()
            .map(|(id, u)| (*id, u.outputs.clone()))
            .collect();
        
        for (source_id, outputs) in outputs_snapshot {
            for (target_id, conn) in outputs {
                if let Some(target) = units.get_mut(&target_id) {
                    target.receive_from(source_id, conn);
                }
            }
        }
    }
    
    /// 主更新循环
    /// 
    /// 每tick执行：
    /// 1. 注入感知输入
    /// 2. 更新L0单元
    /// 3. 更新L1团簇
    /// 4. 更新L2全局工作空间
    /// 5. 提取行动倾向
    pub fn tick(&mut self, input: &SensoryInput) -> ActionTendencies {
        self.tick += 1;
        
        // 1. 感知输入 -> 单元激活
        self.inject_sensory_input(input);
        
        // 2. L0更新（每个单元局部更新）
        self.update_units();
        
        // 3. L1更新（团簇动力学）
        self.meso_layer.update(&self.units, self.tick);
        
        // 4. L2更新（全局广播）
        self.global_workspace.update(&mut self.meso_layer);
        
        // 5. 提取行动倾向
        let tendencies = self.extract_action_tendencies();
        
        // 6. 涌现检测
        let report = self.emergence.analyze(self.tick, &self.meso_layer, &self.global_workspace);
        self.update_stats(&report);
        
        tendencies
    }
    
    /// 注入感知输入到对应单元
    fn inject_sensory_input(&mut self, input: &SensoryInput) {
        // 视觉输入
        for entity in &input.nearby_entities {
            let target_units = match entity.direction {
                d if d < -0.3 => &self.sensory_units.vision_left,
                d if d > 0.3 => &self.sensory_units.vision_right,
                _ => &self.sensory_units.vision_forward,
            };
            
            let intensity = (1.0 - entity.distance) * 0.5; // 越近越强
            for &unit_id in target_units.iter().take(3) {
                if let Some(unit) = self.units.get_mut(&unit_id) {
                    unit.activation = (unit.activation + intensity).min(1.0);
                    unit.add_energy(intensity * 0.1); // 感知输入提供少量能量
                }
            }
        }
        
        // 资源输入
        for resource in &input.resource_signals {
            let intensity = resource.intensity;
            for &unit_id in &self.sensory_units.resource_units {
                if let Some(unit) = self.units.get_mut(&unit_id) {
                    unit.activation = intensity;
                }
            }
        }
        
        // 威胁输入
        for threat in &input.threat_signals {
            let intensity = threat.urgency;
            for &unit_id in &self.sensory_units.threat_units {
                if let Some(unit) = self.units.get_mut(&unit_id) {
                    unit.activation = -intensity; // 威胁为负激活
                }
            }
        }
        
        // 内感受输入
        for &unit_id in &self.sensory_units.intero_units {
            if let Some(unit) = self.units.get_mut(&unit_id) {
                unit.activation = input.interoception.energy - 0.5;
            }
        }
    }
    
    /// 更新所有单元
    fn update_units(&mut self) {
        // 先收集所有需要的信息（避免借用冲突）
        let activations: HashMap<UnitId, f32> = self.units.iter()
            .map(|(id, u)| (*id, u.output_signal()))
            .collect();
        
        // 更新每个单元
        for unit in self.units.values_mut() {
            // 从输入连接接收信号
            let mut input_sum = 0.0;
            for (source_id, conn) in &unit.inputs {
                if let Some(&source_act) = activations.get(source_id) {
                    input_sum += source_act * conn.weight * conn.strength;
                }
            }
            
            // 这里简化：直接将输入累加到激活
            // 实际应在MicroUnit::update中处理
            unit.activation = (unit.activation + input_sum).clamp(-1.0, 1.0);
            
            unit.update(&self.unit_config);
        }
    }
    
    /// 从行动单元提取行动倾向
    fn extract_action_tendencies(&self) -> ActionTendencies {
        // 读取各组单元的平均激活
        let read_group = |units: &[UnitId]| -> f32 {
            let sum: f32 = units.iter()
                .filter_map(|id| self.units.get(id))
                .map(|u| u.activation)
                .sum();
            sum / units.len().max(1) as f32
        };
        
        // 运动倾向
        let m = &self.action_units.movement_units;
        let movement = [
            read_group(&m[0..2]),   // 左
            read_group(&m[2..5]),   // 前
            read_group(&m[5..7]),   // 右
            read_group(&m[7..10]),  // 后
        ];
        
        // 交互倾向
        let i = &self.action_units.interaction_units;
        let interaction = [
            read_group(&i[0..3]),   // 接近
            read_group(&i[3..6]),   // 回避
            read_group(&i[6..8]),   // 互动
            read_group(&i[8..10]),  // 忽略
        ];
        
        // 能量管理倾向
        let e = &self.action_units.energy_units;
        let energy_management = [
            read_group(&e[0..3]),   // 探索
            read_group(&e[3..6]),   // 节能
            read_group(&e[6..8]),   // 冲刺
            read_group(&e[8..10]),  // 休眠
        ];
        
        // 社交倾向
        let s = &self.action_units.social_units;
        let social = [
            read_group(&s[0..3]),   // 合作
            read_group(&s[3..6]),   // 竞争
            read_group(&s[6..8]),   // 观察
            read_group(&s[8..10]),  // 孤立
        ];
        
        // 信心 = 团簇一致性
        let confidence = self.global_workspace.global_coherence;
        
        ActionTendencies {
            movement,
            interaction,
            energy_management,
            social,
            confidence,
        }
    }
    
    /// 提供环境奖励（学习信号）
    pub fn deliver_reward(&mut self, reward: f32) {
        // 奖励调制全局可塑性
        // 实际实现会遍历连接应用reward-modulated plasticity
        // 这里简化：给所有单元能量奖励
        for unit in self.units.values_mut() {
            unit.add_energy(reward * 0.1);
        }
    }
    
    /// 提供环境惩罚
    pub fn deliver_punishment(&mut self, punishment: f32) {
        // 惩罚增加压力，降低能量
        for unit in self.units.values_mut() {
            unit.energy = (unit.energy - punishment * 0.1).max(0.0);
        }
    }
    
    /// 更新统计
    fn update_stats(&mut self, report: &EmergenceReport) {
        self.stats.total_ticks = self.tick;
        self.stats.attractors_formed += report.new_attractors;
        self.stats.state_switches += report.state_switches;
        if report.integration_event {
            self.stats.integration_events += 1;
        }
        
        // 移动平均一致性
        let alpha = 0.01;
        self.stats.avg_coherence = self.stats.avg_coherence * (1.0 - alpha)
            + self.global_workspace.global_coherence * alpha;
    }
    
    /// 获取完整状态报告
    pub fn full_report(&self) -> SubstrateReport {
        SubstrateReport {
            tick: self.tick,
            l0: L0Report {
                num_units: self.units.len(),
                avg_energy: self.units.values().map(|u| u.energy).sum::<f32>() 
                    / self.units.len() as f32,
                avg_activation: self.units.values().map(|u| u.activation.abs()).sum::<f32>()
                    / self.units.len() as f32,
            },
            l1: self.meso_layer.status_summary(),
            l2: self.global_workspace.status_summary(),
            stats: self.stats.clone(),
        }
    }
}

/// 完整状态报告
#[derive(Debug, Clone)]
pub struct SubstrateReport {
    pub tick: u64,
    pub l0: L0Report,
    pub l1: L1Status,
    pub l2: L2Status,
    pub stats: BridgeStats,
}

#[derive(Debug, Clone)]
pub struct L0Report {
    pub num_units: usize,
    pub avg_energy: f32,
    pub avg_activation: f32,
}

// 简单随机数实现（避免外部依赖）
fn random_f32() -> f32 {
    use std::sync::atomic::{AtomicU64, Ordering};
    static SEED: AtomicU64 = AtomicU64::new(12345);
    
    let old = SEED.fetch_add(1, Ordering::SeqCst);
    // LCG随机数生成器
    let new = old.wrapping_mul(6364136223846793005).wrapping_add(1);
    ((new >> 32) as u32) as f32 / u32::MAX as f32
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_bridge_creation() {
        let bridge = SubstrateEnvironmentBridge::new(1000);
        assert_eq!(bridge.units.len(), 1000);
        assert_eq!(bridge.tick, 0);
    }
    
    #[test]
    fn test_sensory_mapping() {
        let bridge = SubstrateEnvironmentBridge::new(1000);
        assert!(!bridge.sensory_units.vision_left.is_empty());
        assert!(!bridge.sensory_units.resource_units.is_empty());
    }
    
    #[test]
    fn test_action_extraction() {
        let bridge = SubstrateEnvironmentBridge::new(1000);
        let input = SensoryInput {
            nearby_entities: vec![],
            resource_signals: vec![],
            threat_signals: vec![],
            interoception: Interoception {
                energy: 0.5,
                stress: 0.0,
                drive: 0.5,
                metabolism: 0.01,
            },
            temporal_context: TemporalContext {
                tick: 0,
                cycle_phase: 0.0,
                recent_events: vec![],
            },
        };
        
        let tendencies = bridge.extract_action_tendencies();
        assert!(tendencies.confidence >= 0.0);
    }
}
