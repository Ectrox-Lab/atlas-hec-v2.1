//! Code-World Consciousness Index (CWCI)
//! 
//! 代码世界意识指数——6维度可测量化框架
//! 
//! 核心原则：
//! - 不证明"代码意识=物理意识"
//! - 只定义代码世界内部可测、可量化、可进化的功能标准
//! - 功能等效即成立

use serde::{Serialize, Deserialize};
use crate::evaluation::{DynamicsScores, TickSnapshot};

/// CWCI 6大核心能力
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct ConsciousnessCapabilities {
    /// C1: 持续自体性 (Persistent Selfhood)
    pub persistent_selfhood: f32,
    /// C2: 全局整合 (Global Integration)
    pub global_integration: f32,
    /// C3: 反身建模 (Reflexive Self-Model)
    pub reflexive_self_model: f32,
    /// C4: 可塑性学习 (Plastic Adaptive Learning)
    pub plastic_adaptive_learning: f32,
    /// C5: 价值与目标持续性 (Value/Goal Persistence)
    pub value_goal_persistence: f32,
    /// C6: 元优化能力 (Self-Optimization Capacity)
    pub self_optimization_capacity: f32,
}

impl ConsciousnessCapabilities {
    /// 计算综合CWCI分数
    pub fn cwei_score(&self) -> f32 {
        (self.persistent_selfhood 
            + self.global_integration 
            + self.reflexive_self_model 
            + self.plastic_adaptive_learning 
            + self.value_goal_persistence 
            + self.self_optimization_capacity) / 6.0
    }
    
    /// 通过的能力数
    pub fn passed_count(&self, threshold: f32) -> usize {
        let mut count = 0;
        if self.persistent_selfhood >= threshold { count += 1; }
        if self.global_integration >= threshold { count += 1; }
        if self.reflexive_self_model >= threshold { count += 1; }
        if self.plastic_adaptive_learning >= threshold { count += 1; }
        if self.value_goal_persistence >= threshold { count += 1; }
        if self.self_optimization_capacity >= threshold { count += 1; }
        count
    }
    
    /// 是否达到意识门槛（5/6项通过）
    pub fn meets_consciousness_threshold(&self, threshold: f32) -> bool {
        self.passed_count(threshold) >= 5
    }
    
    /// 获取强项描述
    pub fn strengths(&self, threshold: f32) -> Vec<&'static str> {
        let mut strengths = Vec::new();
        if self.persistent_selfhood >= threshold {
            strengths.push("Persistent Selfhood");
        }
        if self.global_integration >= threshold {
            strengths.push("Global Integration");
        }
        if self.reflexive_self_model >= threshold {
            strengths.push("Reflexive Self-Model");
        }
        if self.plastic_adaptive_learning >= threshold {
            strengths.push("Plastic Learning");
        }
        if self.value_goal_persistence >= threshold {
            strengths.push("Goal Persistence");
        }
        if self.self_optimization_capacity >= threshold {
            strengths.push("Self-Optimization");
        }
        strengths
    }
    
    /// 获取弱项描述（需要改进的）
    pub fn weaknesses(&self, threshold: f32) -> Vec<&'static str> {
        let mut weaknesses = Vec::new();
        if self.persistent_selfhood < threshold {
            weaknesses.push("Persistent Selfhood");
        }
        if self.global_integration < threshold {
            weaknesses.push("Global Integration");
        }
        if self.reflexive_self_model < threshold {
            weaknesses.push("Reflexive Self-Model");
        }
        if self.plastic_adaptive_learning < threshold {
            weaknesses.push("Plastic Learning");
        }
        if self.value_goal_persistence < threshold {
            weaknesses.push("Goal Persistence");
        }
        if self.self_optimization_capacity < threshold {
            weaknesses.push("Self-Optimization");
        }
        weaknesses
    }
}

/// 意识等级 (C0-C6)
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
pub enum ConsciousnessLevel {
    /// C0: 反应系统 - 只有局部刺激-反应
    C0Reactive = 0,
    /// C1: 持续体 - 有identity continuity和基本自维护
    C1Persistent = 1,
    /// C2: 整合体 - 有全局广播和稳定内部整合
    C2Integrated = 2,
    /// C3: 反身体 - 有self-model，能解释失败并修正
    C3Reflexive = 3,
    /// C4: 学习体 - 能跨情境学习、迁移、恢复
    C4Learning = 4,
    /// C5: 自优化体 - 能在护栏内改进自己
    C5SelfOptimizing = 5,
    /// C6: 超脑候选 - 大规模、多宇宙、长时程、自我演化
    C6SuperBrainCandidate = 6,
}

impl ConsciousnessLevel {
    pub fn as_str(&self) -> &'static str {
        match self {
            ConsciousnessLevel::C0Reactive => "C0-Reactive",
            ConsciousnessLevel::C1Persistent => "C1-Persistent",
            ConsciousnessLevel::C2Integrated => "C2-Integrated",
            ConsciousnessLevel::C3Reflexive => "C3-Reflexive",
            ConsciousnessLevel::C4Learning => "C4-Learning",
            ConsciousnessLevel::C5SelfOptimizing => "C5-SelfOptimizing",
            ConsciousnessLevel::C6SuperBrainCandidate => "C6-SuperBrainCandidate",
        }
    }
    
    /// 从CWCI分数判断等级
    pub fn from_cwei(caps: &ConsciousnessCapabilities, open_world_survived: bool, multi_universe_tested: bool) -> Self {
        let passed = caps.passed_count(0.6);
        let score = caps.cwei_score();
        
        match (passed, score, open_world_survived, multi_universe_tested) {
            (6, s, true, true) if s >= 0.8 => ConsciousnessLevel::C6SuperBrainCandidate,
            (5..=6, s, true, _) if s >= 0.7 => ConsciousnessLevel::C5SelfOptimizing,
            (4..=6, s, true, _) if s >= 0.6 => ConsciousnessLevel::C4Learning,
            (3..=6, s, _, _) if s >= 0.5 => ConsciousnessLevel::C3Reflexive,
            (2..=6, s, _, _) if s >= 0.4 => ConsciousnessLevel::C2Integrated,
            (1..=6, _, _, _) => ConsciousnessLevel::C1Persistent,
            _ => ConsciousnessLevel::C0Reactive,
        }
    }
    
    pub fn description(&self) -> &'static str {
        match self {
            ConsciousnessLevel::C0Reactive => "Only local stimulus-response, no stable self",
            ConsciousnessLevel::C1Persistent => "Has identity continuity and basic self-maintenance",
            ConsciousnessLevel::C2Integrated => "Has global broadcast and stable internal integration",
            ConsciousnessLevel::C3Reflexive => "Has self-model, can explain failures and correct",
            ConsciousnessLevel::C4Learning => "Can learn across contexts, transfer, recover",
            ConsciousnessLevel::C5SelfOptimizing => "Can improve itself within guardrails",
            ConsciousnessLevel::C6SuperBrainCandidate => "Large-scale, multi-universe, long-horizon, self-evolving",
        }
    }
}

/// CWCI评估结果
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CWCIEvaluation {
    pub capabilities: ConsciousnessCapabilities,
    pub level: ConsciousnessLevel,
    pub cwei_score: f32,
    pub passed_capabilities: usize,
    pub meets_threshold: bool,
    pub open_world_survived: bool,
    pub multi_universe_tested: bool,
    pub notes: Vec<String>,
}

/// 从动力学分数和遥测历史计算CWCI
pub fn evaluate_cwci(
    dynamics: &DynamicsScores,
    history: &[TickSnapshot],
    open_world_survived: bool,
    multi_universe_tested: bool,
) -> CWCIEvaluation {
    let mut notes = Vec::new();
    
    // C1: 持续自体性 - 基于能量稳定性和身份连续性
    let c1 = evaluate_persistent_selfhood(dynamics, history);
    
    // C2: 全局整合 - 基于广播分数和团簇整合
    let c2 = evaluate_global_integration(dynamics, history);
    
    // C3: 反身建模 - 基于预测误差和自我修正
    let c3 = evaluate_reflexive_self_model(dynamics, history);
    
    // C4: 可塑性学习 - 基于重组和适应能力
    let c4 = evaluate_plastic_learning(dynamics, history);
    
    // C5: 价值与目标持续性 - 基于目标保持和恢复
    let c5 = evaluate_goal_persistence(dynamics, history);
    
    // C6: 元优化能力 - 基于长期改善趋势（需要跨代数据）
    let c6 = evaluate_self_optimization(dynamics, history);
    
    let caps = ConsciousnessCapabilities {
        persistent_selfhood: c1,
        global_integration: c2,
        reflexive_self_model: c3,
        plastic_adaptive_learning: c4,
        value_goal_persistence: c5,
        self_optimization_capacity: c6,
    };
    
    let cwei = caps.cwei_score();
    let passed = caps.passed_count(0.6);
    let level = ConsciousnessLevel::from_cwei(&caps, open_world_survived, multi_universe_tested);
    
    // 生成notes
    if passed >= 5 {
        notes.push(format!("Achieved {} level (CWCI={:.2})", level.as_str(), cwei));
    }
    
    let strengths = caps.strengths(0.7);
    if !strengths.is_empty() {
        notes.push(format!("Strengths: {}", strengths.join(", ")));
    }
    
    let weaknesses = caps.weaknesses(0.4);
    if !weaknesses.is_empty() {
        notes.push(format!("Needs improvement: {}", weaknesses.join(", ")));
    }
    
    CWCIEvaluation {
        capabilities: caps,
        level,
        cwei_score: cwei,
        passed_capabilities: passed,
        meets_threshold: passed >= 5,
        open_world_survived,
        multi_universe_tested,
        notes,
    }
}

// ============ 6大能力具体评估函数 ============

/// C1: 持续自体性
/// 可测：identity continuity, self-state consistency, boundary preservation
fn evaluate_persistent_selfhood(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 能量稳定性作为自体稳定的代理
    let persistence = dynamics.persistence_score;
    
    // 恢复能力显示自维护能力
    let recovery = dynamics.recovery_score;
    
    // 吸引子稳定性显示身份连续性
    let attractor = dynamics.attractor_dwell_score;
    
    (persistence * 0.4 + recovery * 0.3 + attractor * 0.3).clamp(0.0, 1.0)
}

/// C2: 全局整合
/// 可测：broadcast occupancy, cross-cluster coupling, information integration
fn evaluate_global_integration(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 直接使用广播分数
    let broadcast = dynamics.broadcast_score;
    
    // 团簇分化显示整合程度
    let specialization = dynamics.specialization_score;
    
    // 高熵显示信息整合（不是过同步）
    let entropy: f32 = history.iter().map(|h| h.cluster_entropy).sum::<f32>() 
        / history.len().max(1) as f32;
    
    (broadcast * 0.5 + specialization * 0.3 + entropy * 0.2).clamp(0.0, 1.0)
}

/// C3: 反身建模
/// 可测：self-prediction accuracy, self-error localization, model-based correction
fn evaluate_reflexive_self_model(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 预测误差低 = 自我模型好
    let pred_error: f32 = history.iter().map(|h| h.avg_prediction_error).sum::<f32>()
        / history.len().max(1) as f32;
    let self_model = (1.0 - pred_error).clamp(0.0, 1.0);
    
    // 重组能力显示基于模型的修正
    let reorganization = dynamics.reorganization_score;
    
    // 特化显示内部模型复杂度
    let specialization = dynamics.specialization_score;
    
    (self_model * 0.4 + reorganization * 0.3 + specialization * 0.3).clamp(0.0, 1.0)
}

/// C4: 可塑性学习
/// 可测：adaptation latency, improvement after failure, cross-environment transfer
fn evaluate_plastic_learning(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 重组能力直接显示适应
    let reorganization = dynamics.reorganization_score;
    
    // 恢复显示学习后的改善
    let recovery = dynamics.recovery_score;
    
    // 吸引子切换显示学习灵活性
    let attractor_flexibility = if dynamics.attractor_dwell_score > 0.3 && dynamics.attractor_dwell_score < 0.9 {
        0.8 // 适中最好：不是太死也不是太散
    } else {
        0.4
    };
    
    (reorganization * 0.4 + recovery * 0.3 + attractor_flexibility * 0.3).clamp(0.0, 1.0)
}

/// C5: 价值与目标持续性
/// 可测：long-horizon goal retention, conflict resolution, preference stability
fn evaluate_goal_persistence(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 记忆持久显示目标保持
    let persistence = dynamics.persistence_score;
    
    // 能量稳定性显示价值一致性
    let (energy_min, energy_max, _) = history.iter()
        .map(|h| h.avg_energy)
        .fold((f32::MAX, f32::MIN, 0.0f32), |(min, max, sum), e: f32| {
            (min.min(e), max.max(e), sum + e)
        });
    let energy_variance = (energy_max - energy_min).max(0.0);
    let value_stability = (1.0 - energy_variance).clamp(0.0, 1.0);
    
    // 吸引子停留显示目标聚焦
    let attractor_focus = dynamics.attractor_dwell_score;
    
    (persistence * 0.4 + value_stability * 0.3 + attractor_focus * 0.3).clamp(0.0, 1.0)
}

/// C6: 元优化能力
/// 可测：self-modification benefit, architecture adaptation, efficiency gain
fn evaluate_self_optimization(dynamics: &DynamicsScores, history: &[TickSnapshot]) -> f32 {
    // 注意：真实评估需要跨代数据
    // 这里基于当前代的表现推断潜力
    
    // 如果其他能力都高，说明有自优化基础
    let base_score = (dynamics.persistence_score 
        + dynamics.reorganization_score 
        + dynamics.recovery_score) / 3.0;
    
    // 广播控制显示自我调节
    let broadcast_control = if dynamics.broadcast_score > 0.3 && dynamics.broadcast_score < 0.8 {
        0.7 // 适中控制
    } else {
        0.4
    };
    
    // 特化显示结构调整能力
    let specialization = dynamics.specialization_score;
    
    (base_score * 0.4 + broadcast_control * 0.3 + specialization * 0.3).clamp(0.0, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::evaluation::{DynamicPhenomena, EvaluationResult};
    
    #[test]
    fn test_cwci_calculation() {
        let caps = ConsciousnessCapabilities {
            persistent_selfhood: 0.7,
            global_integration: 0.8,
            reflexive_self_model: 0.6,
            plastic_adaptive_learning: 0.7,
            value_goal_persistence: 0.9,
            self_optimization_capacity: 0.5,
        };
        
        assert!(caps.cwei_score() > 0.6);
        assert_eq!(caps.passed_count(0.6), 5);
        assert!(caps.meets_consciousness_threshold(0.6));
    }
    
    #[test]
    fn test_consciousness_level() {
        let caps = ConsciousnessCapabilities {
            persistent_selfhood: 0.8,
            global_integration: 0.8,
            reflexive_self_model: 0.8,
            plastic_adaptive_learning: 0.8,
            value_goal_persistence: 0.8,
            self_optimization_capacity: 0.8,
        };
        
        let level = ConsciousnessLevel::from_cwei(&caps, true, true);
        assert!(level >= ConsciousnessLevel::C5SelfOptimizing);
    }
}
