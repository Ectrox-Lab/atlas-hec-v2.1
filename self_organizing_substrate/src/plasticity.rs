//! 可塑性规则
//! 
//! 定义连接如何根据局部活动历史调整。
//! 核心原则：只有局部信息，没有全局监督。

use crate::micro_unit::{MicroUnit, Connection};

/// 可塑性规则trait
/// 
/// 不同的学习规则可以实现这个trait
pub trait PlasticityRule {
    /// 根据pre/post活动计算权重变化
    /// 
    /// # Arguments
    /// * `pre_activation` - 前突触单元激活
    /// * `post_activation` - 后突触单元激活
    /// * `pre_trace` - 前突触记忆痕迹
    /// * `post_trace` - 后突触记忆痕迹
    /// * `current_weight` - 当前连接权重
    /// * `reward_signal` - 可选的奖励调制（三因素学习）
    /// 
    /// # Returns
    /// 权重变化量（delta w）
    fn compute_weight_change(
        &self,
        pre_activation: f32,
        post_activation: f32,
        pre_trace: f32,
        post_trace: f32,
        current_weight: f32,
        reward_signal: Option<f32>,
    ) -> f32;
    
    /// 规则名称
    fn name(&self) -> &'static str;
}

/// Hebbian学习: "一起激活，一起连接"
/// 
/// 最简单的关联学习：如果pre和post都活跃，加强连接
pub struct HebbianRule {
    /// 学习率
    pub learning_rate: f32,
    /// 权重衰减（防止无限增长）
    pub weight_decay: f32,
    /// LTP阈值（post需要多活跃才能长时程增强）
    pub ltp_threshold: f32,
    /// LTD阈值（post多不活跃导致长时程抑制）
    pub ltd_threshold: f32,
}

impl HebbianRule {
    pub fn new(learning_rate: f32) -> Self {
        Self {
            learning_rate,
            weight_decay: 0.0001,
            ltp_threshold: 0.5,
            ltd_threshold: 0.2,
        }
    }
}

impl PlasticityRule for HebbianRule {
    fn compute_weight_change(
        &self,
        pre_activation: f32,
        post_activation: f32,
        _pre_trace: f32,
        _post_trace: f32,
        current_weight: f32,
        _reward_signal: Option<f32>,
    ) -> f32 {
        // 标准Hebbian: pre * post
        let correlation = pre_activation * post_activation;
        
        // 非线性调制：只有当post足够活跃时才增强
        let modulation = if post_activation > self.ltp_threshold {
            1.0 // 长时程增强(LTP)
        } else if post_activation < self.ltd_threshold {
            -0.5 // 长时程抑制(LTD)
        } else {
            0.0 // 无变化
        };
        
        let delta = self.learning_rate * correlation * modulation;
        
        // 权重衰减（向0收缩）
        let decay = -self.weight_decay * current_weight;
        
        delta + decay
    }
    
    fn name(&self) -> &'static str {
        "Hebbian"
    }
}

/// STDP: Spike-Timing Dependent Plasticity
/// 
/// 时间敏感的可塑性：pre在post之前激活 → 增强
/// pre在post之后激活 → 减弱
pub struct STDPRule {
    /// 增强学习率（pre-before-post）
    pub a_plus: f32,
    /// 抑制学习率（post-before-pre）
    pub a_minus: f32,
    /// 时间常数（影响时间窗口）
    pub tau: f32,
}

impl STDPRule {
    pub fn standard() -> Self {
        Self {
            a_plus: 0.01,
            a_minus: 0.0105, // 稍微不对称，抑制略强
            tau: 20.0, // tick单位
        }
    }
}

impl PlasticityRule for STDPRule {
    fn compute_weight_change(
        &self,
        pre_activation: f32,
        post_activation: f32,
        pre_trace: f32,
        post_trace: f32,
        _current_weight: f32,
        _reward_signal: Option<f32>,
    ) -> f32 {
        // 使用痕迹近似时间关系
        // pre_trace高 + post刚激活 ≈ pre-before-post
        // post_trace高 + pre刚激活 ≈ post-before-pre
        
        let ltp = pre_trace * post_activation; // pre先于post活跃
        let ltd = post_trace * pre_activation; // post先于pre活跃
        
        self.a_plus * ltp - self.a_minus * ltd
    }
    
    fn name(&self) -> &'static str {
        "STDP"
    }
}

/// 预测性可塑性: 最小化预测误差
/// 
/// 连接调整目标是让post能更好预测pre
pub struct PredictiveRule {
    /// 误差学习率
    pub error_lr: f32,
    /// 预测的折扣因子
    pub gamma: f32,
}

impl PredictiveRule {
    pub fn new() -> Self {
        Self {
            error_lr: 0.05,
            gamma: 0.9,
        }
    }
}

impl PlasticityRule for PredictiveRule {
    fn compute_weight_change(
        &self,
        pre_activation: f32,
        post_activation: f32,
        pre_trace: f32,
        _post_trace: f32,
        _current_weight: f32,
        _reward_signal: Option<f32>,
    ) -> f32 {
        // 目标：让 post_activation ≈ predicted_pre
        // predicted_pre ≈ current_weight * pre_trace（过去pre的痕迹）
        
        let predicted_pre = pre_trace; // 简化：用pre的过去作为预测目标
        let prediction_error = post_activation - predicted_pre;
        
        // 调整权重减少误差
        -self.error_lr * pre_activation * prediction_error
    }
    
    fn name(&self) -> &'static str {
        "Predictive"
    }
}

/// 奖励调制可塑性 (三因素学习)
/// 
/// Hebbian + 全局奖励信号
/// 这是最简单的" credit assignment"机制
pub struct RewardModulatedRule {
    /// 基础Hebbian规则
    pub hebbian: HebbianRule,
    /// 奖励基线（用于减去平均奖励）
    pub reward_baseline: f32,
    /// 基线学习率
    pub baseline_lr: f32,
}

impl RewardModulatedRule {
    pub fn new(learning_rate: f32) -> Self {
        Self {
            hebbian: HebbianRule::new(learning_rate),
            reward_baseline: 0.0,
            baseline_lr: 0.001,
        }
    }
    
    /// 更新奖励基线（移动平均）
    pub fn update_baseline(&mut self, reward: f32) {
        self.reward_baseline += self.baseline_lr * (reward - self.reward_baseline);
    }
}

impl PlasticityRule for RewardModulatedRule {
    fn compute_weight_change(
        &self,
        pre_activation: f32,
        post_activation: f32,
        pre_trace: f32,
        post_trace: f32,
        current_weight: f32,
        reward_signal: Option<f32>,
    ) -> f32 {
        let base_change = self.hebbian.compute_weight_change(
            pre_activation, post_activation, pre_trace, post_trace, 
            current_weight, None
        );
        
        if let Some(reward) = reward_signal {
            // 调制：只有超过基线的奖励才增强
            let advantage = reward - self.reward_baseline;
            base_change * (1.0 + advantage).max(0.0)
        } else {
            base_change
        }
    }
    
    fn name(&self) -> &'static str {
        "RewardModulated"
    }
}

/// 结构可塑性: 连接的新生和消亡
/// 
/// 不只是调整权重，还能创建/删除连接
pub struct StructuralPlasticity {
    /// 创建新连接的阈值（两单元都足够活跃且没有连接）
    pub formation_threshold: f32,
    /// 删除弱连接的阈值
    pub pruning_threshold: f32,
    /// 连接最大年龄（老化删除）
    pub max_age: u64,
    /// 最大连接数（资源约束）
    pub max_connections: usize,
}

impl StructuralPlasticity {
    pub fn new() -> Self {
        Self {
            formation_threshold: 0.6,
            pruning_threshold: 0.05,
            max_age: 10000,
            max_connections: 100,
        }
    }
    
    /// 检查是否应该形成新连接
    pub fn should_form(&self, unit_a: &MicroUnit, unit_b: &MicroUnit) -> bool {
        // 两者都活跃
        let both_active = unit_a.activation.abs() > 0.5 && unit_b.activation.abs() > 0.5;
        
        // 且没有已有连接
        let not_connected = !unit_a.outputs.contains_key(&unit_b.id) 
            && !unit_b.outputs.contains_key(&unit_a.id);
        
        // 连接数没满
        let has_capacity = unit_a.outputs.len() < self.max_connections 
            && unit_b.inputs.len() < self.max_connections;
        
        both_active && not_connected && has_capacity
    }
    
    /// 检查连接是否应该被删除
    pub fn should_prune(&self, conn: &Connection) -> bool {
        // 权重太弱
        let too_weak = conn.weight.abs() < self.pruning_threshold;
        
        // 太久不用
        let unused = conn.recent_use < 0.01;
        
        // 太老
        let too_old = conn.age > self.max_age;
        
        (too_weak && unused) || too_old
    }
}



/// 可塑性规则类型（使用Box<dyn>实现多态）
#[derive(Debug, Clone, Copy)]
pub enum PlasticityRuleType {
    Hebbian { lr: f32 },
    STDP,
    Predictive,
    RewardModulated { lr: f32 },
}

impl PlasticityRuleType {
    /// 创建对应的规则实例
    pub fn create(&self) -> Box<dyn PlasticityRule> {
        match *self {
            Self::Hebbian { lr } => Box::new(HebbianRule::new(lr)),
            Self::STDP => Box::new(STDPRule::standard()),
            Self::Predictive => Box::new(PredictiveRule::new()),
            Self::RewardModulated { lr } => Box::new(RewardModulatedRule::new(lr)),
        }
    }
}

/// 连接更新器 - 使用Box<dyn>
/// 
/// 将可塑性规则应用到具体连接
pub struct ConnectionUpdater<'a> {
    pub rule: &'a dyn PlasticityRule,
    pub plasticity_factor: f32, // 单元可塑性的乘数
}

impl<'a> ConnectionUpdater<'a> {
    pub fn new(rule: &'a dyn PlasticityRule, plasticity: f32) -> Self {
        Self {
            rule,
            plasticity_factor: plasticity,
        }
    }
    
    /// 更新单个连接
    pub fn update(
        &self,
        conn: &mut Connection,
        pre_unit: &MicroUnit,
        post_unit: &MicroUnit,
        reward: Option<f32>,
    ) {
        let delta = self.rule.compute_weight_change(
            pre_unit.activation,
            post_unit.activation,
            pre_unit.memory_trace,
            post_unit.memory_trace,
            conn.weight,
            reward,
        );
        
        // 应用变化，受可塑性因子调节
        conn.weight = (conn.weight + delta * self.plasticity_factor)
            .clamp(-1.0, 1.0);
        
        // 更新连接元数据
        conn.age += 1;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_hebbian_ltp() {
        let rule = HebbianRule::new(0.1);
        
        // pre和post都活跃，且post超过LTP阈值
        let delta = rule.compute_weight_change(
            1.0, 0.8, 0.0, 0.0, 0.0, None
        );
        
        assert!(delta > 0.0, "LTP should increase weight");
    }
    
    #[test]
    fn test_hebbian_ltd() {
        let rule = HebbianRule::new(0.1);
        
        // pre活跃但post低于LTD阈值
        let delta = rule.compute_weight_change(
            1.0, 0.1, 0.0, 0.0, 0.5, None
        );
        
        assert!(delta < 0.0, "LTD should decrease weight");
    }
    
    #[test]
    fn test_weight_bounds() {
        // 测试构造时自动clamp
        let conn_over = Connection::new(1.5); // 超出范围
        assert!(conn_over.weight.abs() <= 1.0, "Weight should be clamped to [-1, 1]");
        assert_eq!(conn_over.weight, 1.0);
        
        let conn_under = Connection::new(-2.0);
        assert!(conn_under.weight.abs() <= 1.0);
        assert_eq!(conn_under.weight, -1.0);
        
        let conn_ok = Connection::new(0.5);
        assert_eq!(conn_ok.weight, 0.5);
    }
}
