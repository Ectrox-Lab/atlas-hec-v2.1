//! L0: Micro-Unit
//! 
//! 最简认知单元，类似神经元但功能更抽象。
//! 只保留最小状态，只与局部邻居交互。

use std::collections::HashMap;

/// 微单元ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct UnitId(pub usize);

/// 微单元状态
/// 
/// 设计原则：状态尽可能少，让复杂性从连接和动力学中涌现
#[derive(Debug, Clone)]
pub struct MicroUnit {
    pub id: UnitId,
    
    // === 核心状态 ===
    /// 激活水平 [-1.0, 1.0]
    /// 负值表示抑制，正值表示兴奋
    pub activation: f32,
    
    /// 能量预算 [0.0, 1.0]
    /// 所有操作消耗能量，能量不足时进入休眠
    pub energy: f32,
    
    /// 局部记忆痕迹 [0.0, 1.0]
    /// 不是存储内容，而是"最近是否活跃"的衰减痕迹
    pub memory_trace: f32,
    
    /// 预测误差 [0.0, 1.0]
    /// 期望输入与实际输入的差异，驱动学习
    pub prediction_error: f32,
    
    /// 可塑性状态 [0.0, 1.0]
    /// 当前学习敏感度，受误差和能量调节
    pub plasticity: f32,
    
    /// 单元类型（影响默认参数）
    pub unit_type: UnitType,
    
    // === 邻居连接 ===
    /// 输入连接: 来源单元ID -> 连接权重
    pub inputs: HashMap<UnitId, Connection>,
    
    /// 输出连接: 目标单元ID -> 连接权重  
    pub outputs: HashMap<UnitId, Connection>,
    
    /// 临时输入信号缓存（由Network填充）
    pub input_buffer: f32,
    
    // === 运行时统计 ===
    /// 总接收信号（用于计算预测误差）
    pub last_input_sum: f32,
    
    /// 上一步激活（用于计算变化）
    pub last_activation: f32,
    
    /// 存活tick数
    pub age: u64,
}

/// 单元类型
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum UnitType {
    /// 兴奋性单元 - 倾向于激活邻居
    Excitatory,
    /// 抑制性单元 - 倾向于抑制邻居
    Inhibitory,
    /// 调节性单元 - 影响可塑性和能量流动
    Modulatory,
}

/// 连接结构
#[derive(Debug, Clone, Copy)]
pub struct Connection {
    /// 连接权重 [-1.0, 1.0]
    pub weight: f32,
    
    /// 连接强度（影响信号传递效率）
    pub strength: f32,
    
    /// 最近使用痕迹（用于突触可塑性）
    pub recent_use: f32,
    
    /// 连接年龄
    pub age: u64,
}

impl Connection {
    pub fn new(weight: f32) -> Self {
        Self {
            weight: weight.clamp(-1.0, 1.0),
            strength: 0.5,
            recent_use: 0.0,
            age: 0,
        }
    }
}

impl MicroUnit {
    /// 创建新单元
    pub fn new(id: usize, unit_type: UnitType) -> Self {
        Self {
            id: UnitId(id),
            activation: 0.0,
            energy: 1.0,
            memory_trace: 0.0,
            prediction_error: 0.0,
            plasticity: 0.1,
            unit_type,
            inputs: HashMap::new(),
            outputs: HashMap::new(),
            last_input_sum: 0.0,
            last_activation: 0.0,
            input_buffer: 0.0,
            age: 0,
        }
    }
    
    /// L0核心更新循环
    /// 
    /// 每个tick执行一次，只使用局部信息
    pub fn update(&mut self, config: &UnitConfig) {
        // 1. 能量代谢
        self.metabolism(config);
        
        // 2. 如果能量过低，进入休眠（跳过更新）
        if self.energy < config.dormancy_threshold {
            self.activation *= 0.5; // 快速衰减
            self.input_buffer = 0.0; // 清空输入缓冲
            self.age += 1;
            return;
        }
        
        // 3. 使用输入缓冲（由Network填充）
        let input_signal = self.input_buffer;
        self.input_buffer = 0.0; // 清空缓冲
        
        // 4. 更新预测误差（期望 vs 实际）
        // 期望基于上一次输入的简单预测
        let expected = self.last_activation * config.prediction_factor;
        self.prediction_error = (input_signal - expected).abs();
        
        // 5. 更新激活（带饱和非线性）
        let new_activation = Self::activation_function(
            input_signal + self.activation * config.self_excitation
        );
        self.last_activation = self.activation;
        self.activation = new_activation;
        
        // 6. 更新记忆痕迹（简单的指数衰减）
        self.memory_trace = self.memory_trace * config.memory_decay 
            + self.activation.abs() * (1.0 - config.memory_decay);
        
        // 7. 可塑性调节（基于误差和能量）
        // 误差大+能量足 = 高可塑性（适合学习）
        let raw_plasticity = config.base_plasticity * self.energy * (0.5 + self.prediction_error);
        self.plasticity = raw_plasticity.clamp(config.min_plasticity, config.max_plasticity);
        
        // 8. 向输出发送信号（标记连接使用）
        self.propagate_signal();
        
        self.last_input_sum = input_signal;
        self.age += 1;
    }
    
    /// 计算输入信号总和
    fn compute_input_signal(&self) -> f32 {
        let mut sum = 0.0;
        for (_source_id, conn) in &self.inputs {
            // 注意：这里需要外部提供邻居的激活值
            // 实际实现通过Network统一调度
            // 这里只计算权重结构
            sum += conn.weight * conn.strength;
        }
        // 类型特定的基线
        match self.unit_type {
            UnitType::Excitatory => sum + 0.1,
            UnitType::Inhibitory => sum - 0.1,
            UnitType::Modulatory => sum * 0.5,
        }
    }
    
    /// 激活函数（带饱和）
    fn activation_function(x: f32) -> f32 {
        // tanh-like but faster approximation
        let x = x.clamp(-3.0, 3.0);
        x / (1.0 + x.abs().sqrt())
    }
    
    /// 能量代谢
    fn metabolism(&mut self, config: &UnitConfig) {
        // 基础代谢消耗
        let base_cost = config.base_metabolism;
        
        // 激活消耗（活跃更耗能）
        let activation_cost = self.activation.abs() * config.activation_cost;
        
        // 可塑性消耗（学习也耗能）
        let plasticity_cost = self.plasticity * config.plasticity_cost;
        
        let total_cost = base_cost + activation_cost + plasticity_cost;
        self.energy = (self.energy - total_cost).clamp(0.0, 1.0);
        
        // 能量自然恢复（需要外部输入，如"食物"或"休息"）
        // 这里只定义消耗，恢复由环境或Network提供
    }
    
    /// 标记信号传播（用于Hebbian学习）
    fn propagate_signal(&mut self) {
        // 实际信号传播由Network统一处理
        // 这里只更新连接的recent_use标记
        for conn in self.outputs.values_mut() {
            conn.recent_use = conn.recent_use * 0.9 + self.activation.abs() * 0.1;
        }
    }
    
    /// 添加能量（来自环境或邻居）
    pub fn add_energy(&mut self, amount: f32) {
        self.energy = (self.energy + amount).clamp(0.0, 1.0);
    }
    
    /// 与邻居建立连接
    pub fn connect_to(&mut self, target_id: UnitId, initial_weight: f32) -> Connection {
        let conn = Connection::new(initial_weight);
        self.outputs.insert(target_id, conn);
        conn
    }
    
    /// 接收来自邻居的连接
    pub fn receive_from(&mut self, source_id: UnitId, conn: Connection) {
        self.inputs.insert(source_id, conn);
    }
    
    /// 获取当前"输出信号"（供Network传递给邻居）
    pub fn output_signal(&self) -> f32 {
        self.activation * match self.unit_type {
            UnitType::Excitatory => 1.0,
            UnitType::Inhibitory => -1.0,
            UnitType::Modulatory => 0.3,
        }
    }
}

/// 单元配置参数
#[derive(Debug, Clone, Copy)]
pub struct UnitConfig {
    /// 基础代谢率
    pub base_metabolism: f32,
    /// 激活消耗系数
    pub activation_cost: f32,
    /// 可塑性消耗系数
    pub plasticity_cost: f32,
    /// 休眠阈值
    pub dormancy_threshold: f32,
    /// 记忆衰减率
    pub memory_decay: f32,
    /// 自兴奋系数（自我维持能力）
    pub self_excitation: f32,
    /// 预测因子（期望多大程度延续过去）
    pub prediction_factor: f32,
    /// 基础可塑性
    pub base_plasticity: f32,
    /// 最小/最大可塑性
    pub min_plasticity: f32,
    pub max_plasticity: f32,
}

impl Default for UnitConfig {
    fn default() -> Self {
        Self {
            base_metabolism: 0.001,
            activation_cost: 0.01,
            plasticity_cost: 0.005,
            dormancy_threshold: 0.1,
            memory_decay: 0.95,
            self_excitation: 0.3,
            prediction_factor: 0.8,
            base_plasticity: 0.1,
            min_plasticity: 0.01,
            max_plasticity: 1.0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_unit_creation() {
        let unit = MicroUnit::new(0, UnitType::Excitatory);
        assert_eq!(unit.energy, 1.0);
        assert_eq!(unit.activation, 0.0);
    }
    
    #[test]
    fn test_energy_consumption() {
        let mut unit = MicroUnit::new(0, UnitType::Excitatory);
        unit.activation = 1.0;
        unit.plasticity = 0.5;
        
        let config = UnitConfig::default();
        let initial_energy = unit.energy;
        
        unit.update(&config);
        
        // 能量应该下降
        assert!(unit.energy < initial_energy);
    }
    
    #[test]
    fn test_dormancy() {
        let mut unit = MicroUnit::new(0, UnitType::Excitatory);
        unit.energy = 0.05; // 低于默认阈值0.1
        unit.activation = 1.0;
        
        let config = UnitConfig::default();
        unit.update(&config);
        
        // 应该进入休眠，激活衰减
        assert!(unit.activation < 1.0);
    }
}
