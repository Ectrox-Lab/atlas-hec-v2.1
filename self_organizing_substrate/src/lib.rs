//! Self-Organizing Cognitive Substrate (SOCS)
//! 
//! 从局部简单规则出发，逐层长出复杂认知能力的可扩展基底。
//! 
//! ## 架构层次
//! 
//! - **L0 (MicroUnit)**: 细胞/神经元层级的简单单元，只保留激活、能量、
//!   记忆痕迹、预测误差、可塑性5个状态。
//! 
//! - **L1 (ClusterDynamics)**: 团簇动力学，单元自组织成局部吸引子，
//!   涌现工作记忆和竞争协调。
//! 
//! - **L2 (GlobalWorkspace)**: 全局工作空间，从团簇竞争中涌现广播机制，
//!   实现全局信息共享。
//! 
//! ## 设计原则
//! 
//! 1. 少规则，不少约束
//! 2. 局部可学习，全球不直控
//! 3. 学习来自反馈，不来自人工答案
//! 4. 先长结构，再长能力
//! 5. 自优化从受限自改开始
//! 
//! ## 使用示例
//! 
//! ```rust,ignore
//! use self_organizing_substrate::substrate_open_world_bridge::SubstrateEnvironmentBridge;
//! 
//! // 创建1000单元的基底
//! let mut substrate = SubstrateEnvironmentBridge::new(1000);
//! 
//! // 每tick提供感知输入，获得行动倾向
//! loop {
//!     let input = gather_sensory_input();
//!     let tendencies = substrate.tick(&input);
//!     execute_action(tendencies.select_action());
//!     
//!     // 根据结果提供奖励/惩罚
//!     substrate.deliver_reward(success as f32);
//! }
//! ```

pub mod micro_unit;
pub mod plasticity;
pub mod cluster_dynamics;
pub mod global_workspace;
pub mod substrate_open_world_bridge;

/// 验证6个动力学现象的测试工具
pub mod verification {
    use crate::substrate_open_world_bridge::{SubstrateEnvironmentBridge, SensoryInput, Interoception, TemporalContext};
    use std::collections::HashMap;
    
    /// 验证结果
    #[derive(Debug, Clone)]
    pub struct VerificationResult {
        pub test_name: &'static str,
        pub passed: bool,
        pub metrics: HashMap<String, f32>,
        pub notes: String,
    }
    
    /// 测试1: 稳定吸引子形成
    pub fn test_attractor_formation(ticks: usize) -> VerificationResult {
        let mut substrate = SubstrateEnvironmentBridge::new(500);
        let mut attractor_count = 0;
        
        // 提供恒定输入
        let constant_input = SensoryInput {
            nearby_entities: vec![],
            resource_signals: vec![],
            threat_signals: vec![],
            interoception: Interoception {
                energy: 0.6,
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
        
        for _ in 0..ticks {
            substrate.tick(&constant_input);
            let report = substrate.full_report();
            if report.l1.num_attractors > 0 {
                attractor_count += 1;
            }
        }
        
        let attractor_ratio = attractor_count as f32 / ticks as f32;
        let passed = attractor_ratio > 0.3; // 至少30%时间有吸引子
        
        VerificationResult {
            test_name: "Attractor Formation",
            passed,
            metrics: [("attractor_ratio".to_string(), attractor_ratio)].into(),
            notes: format!("Attractor present {}% of time", attractor_ratio * 100.0),
        }
    }
    
    /// 测试2: 记忆保持
    pub fn test_memory_persistence(ticks: usize) -> VerificationResult {
        let mut substrate = SubstrateEnvironmentBridge::new(500);
        
        // 先提供强输入建立记忆
        let strong_input = SensoryInput {
            nearby_entities: vec![],
            resource_signals: vec![crate::substrate_open_world_bridge::ResourceSignal {
                direction: 0.0,
                intensity: 1.0,
                resource_type: crate::substrate_open_world_bridge::ResourceType::Energy,
            }],
            threat_signals: vec![],
            interoception: Interoception {
                energy: 0.8,
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
        
        // 建立100ticks
        for _ in 0..100 {
            substrate.tick(&strong_input);
        }
        
        // 然后撤除输入，看记忆保持多久
        let weak_input = SensoryInput {
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
                tick: 100,
                cycle_phase: 0.0,
                recent_events: vec![],
            },
        };
        
        let mut persistence_count = 0;
        for _ in 0..ticks {
            substrate.tick(&weak_input);
            let report = substrate.full_report();
            if report.l1.memory_slots_used > 0 {
                persistence_count += 1;
            }
        }
        
        let persistence_ratio = persistence_count as f32 / ticks as f32;
        let passed = persistence_ratio > 0.5;
        
        VerificationResult {
            test_name: "Memory Persistence",
            passed,
            metrics: [("persistence_ratio".to_string(), persistence_ratio)].into(),
            notes: format!("Memory persisted {}% of time after input removal", persistence_ratio * 100.0),
        }
    }
    
    /// 测试3: 故障恢复
    pub fn test_failure_recovery() -> VerificationResult {
        let mut substrate = SubstrateEnvironmentBridge::new(500);
        
        // 正常运行
        let normal_input = SensoryInput {
            nearby_entities: vec![],
            resource_signals: vec![],
            threat_signals: vec![],
            interoception: Interoception {
                energy: 0.6,
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
        
        for _ in 0..200 {
            substrate.tick(&normal_input);
        }
        
        let coherence_before = substrate.full_report().l2.global_coherence;
        
        // 模拟故障：大量单元能量耗尽
        for unit in substrate.units.values_mut() {
            unit.energy = 0.05;
        }
        
        // 恢复期
        for _ in 0..300 {
            substrate.tick(&normal_input);
        }
        
        let coherence_after = substrate.full_report().l2.global_coherence;
        let recovered = coherence_after > coherence_before * 0.7;
        
        VerificationResult {
            test_name: "Failure Recovery",
            passed: recovered,
            metrics: [
                ("coherence_before".to_string(), coherence_before),
                ("coherence_after".to_string(), coherence_after),
            ].into(),
            notes: if recovered { "Recovery successful".to_string() } else { "Recovery failed".to_string() },
        }
    }
    
    /// 运行所有验证测试
    pub fn run_all_verifications() -> Vec<VerificationResult> {
        vec![
            test_attractor_formation(500),
            test_memory_persistence(200),
            test_failure_recovery(),
        ]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_module_integration() {
        // 确保所有模块可以一起编译
        let _ = verification::run_all_verifications();
    }
}
