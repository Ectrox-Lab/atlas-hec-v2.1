//! 架构家族详细定义
//! 
//! 线虫型、章鱼型、天心脉冲型、随机稀疏型、模块网格型的具体实现。

use crate::{ArchitectureFamily, ParameterConfig};

/// 架构家族特性
pub struct ArchitectureTraits {
    pub family: ArchitectureFamily,
    pub description: &'static str,
    pub typical_units: usize,
    pub connection_pattern: ConnectionPattern,
    pub hub_structure: HubStructure,
    pub dynamics_bias: DynamicsBias,
}

pub enum ConnectionPattern {
    LocalSparse,      // 局部稀疏
    DenseLocalSparseGlobal, // 局部密集全局稀疏
    StarTopology,     // 星型
    Random,           // 随机
    RegularLattice,   // 规则网格
}

pub enum HubStructure {
    FewCriticalHubs,  // 少数关键hub
    Distributed,      // 分布式
    Centralized,      // 集中式
    None,             // 无
}

pub struct DynamicsBias {
    pub attractor_formation: f32,
    pub memory_persistence: f32,
    pub reorganization: f32,
    pub recovery: f32,
}

impl ArchitectureTraits {
    /// 获取所有架构家族的特性
    pub fn all() -> Vec<Self> {
        vec![
            Self::worm_like(),
            Self::octopus_like(),
            Self::tianxin_pulse(),
            Self::random_sparse(),
            Self::modular_lattice(),
        ]
    }
    
    /// 线虫型（C. elegans-like）
    fn worm_like() -> Self {
        Self {
            family: ArchitectureFamily::WormLike,
            description: "302 neurons, sparse fixed topology, few critical hubs, fast reflexes",
            typical_units: 302,
            connection_pattern: ConnectionPattern::LocalSparse,
            hub_structure: HubStructure::FewCriticalHubs,
            dynamics_bias: DynamicsBias {
                attractor_formation: 0.6,  // 中等
                memory_persistence: 0.5,   // 较弱
                reorganization: 0.3,       // 较弱（拓扑固定）
                recovery: 0.7,             // 较强（简单系统易恢复）
            },
        }
    }
    
    /// 章鱼型（Octopus-like）
    fn octopus_like() -> Self {
        Self {
            family: ArchitectureFamily::OctopusLike,
            description: "Highly distributed, weak central, strong arm-local autonomy, arm-local intelligence",
            typical_units: 5000,
            connection_pattern: ConnectionPattern::DenseLocalSparseGlobal,
            hub_structure: HubStructure::Distributed,
            dynamics_bias: DynamicsBias {
                attractor_formation: 0.8,  // 强（局部密集）
                memory_persistence: 0.7,   // 较强
                reorganization: 0.8,       // 强（分布式灵活）
                recovery: 0.9,             // 强（冗余）
            },
        }
    }
    
    /// 天心脉冲型
    fn tianxin_pulse() -> Self {
        Self {
            family: ArchitectureFamily::TianxinPulse,
            description: "Strong rhythm-driven, central broadcast window, phase coupling, event-driven sync",
            typical_units: 1000,
            connection_pattern: ConnectionPattern::StarTopology,
            hub_structure: HubStructure::Centralized,
            dynamics_bias: DynamicsBias {
                attractor_formation: 0.9,  // 很强（节律稳定）
                memory_persistence: 0.8,   // 强
                reorganization: 0.5,       // 中等（节律约束）
                recovery: 0.6,             // 中等
            },
        }
    }
    
    /// 随机稀疏型
    fn random_sparse() -> Self {
        Self {
            family: ArchitectureFamily::RandomSparse,
            description: "Random connections, low average degree, no preset structure, pure emergence",
            typical_units: 2000,
            connection_pattern: ConnectionPattern::Random,
            hub_structure: HubStructure::None,
            dynamics_bias: DynamicsBias {
                attractor_formation: 0.4,  // 弱（随机不稳定）
                memory_persistence: 0.4,
                reorganization: 0.7,       // 强（随机灵活）
                recovery: 0.5,
            },
        }
    }
    
    /// 模块网格型
    fn modular_lattice() -> Self {
        Self {
            family: ArchitectureFamily::ModularLattice,
            description: "Regular topology, modular organization, local dense global sparse, hierarchical",
            typical_units: 3000,
            connection_pattern: ConnectionPattern::RegularLattice,
            hub_structure: HubStructure::FewCriticalHubs,
            dynamics_bias: DynamicsBias {
                attractor_formation: 0.7,
                memory_persistence: 0.8,   // 强（模块化记忆）
                reorganization: 0.6,
                recovery: 0.7,
            },
        }
    }
    
    /// 获取推荐的参数调整
    pub fn recommended_parameters(&self, base: ParameterConfig) -> ParameterConfig {
        match self.family {
            ArchitectureFamily::WormLike => ParameterConfig {
                learning_rate: 0.02,
                connection_density: 0.05,
                broadcast_threshold: 0.7,
                ..base
            },
            ArchitectureFamily::OctopusLike => ParameterConfig {
                learning_rate: 0.015,
                connection_density: 0.03,
                competition_strength: 0.7,
                ..base
            },
            ArchitectureFamily::TianxinPulse => ParameterConfig {
                learning_rate: 0.025,
                connection_density: 0.1,
                broadcast_threshold: 0.5,
                ..base
            },
            ArchitectureFamily::RandomSparse => ParameterConfig {
                learning_rate: 0.03,
                connection_density: 0.02,
                ..base
            },
            ArchitectureFamily::ModularLattice => ParameterConfig {
                learning_rate: 0.02,
                connection_density: 0.08,
                ..base
            },
        }
    }
    
    /// 获取神经科学参考
    pub fn neuroscience_reference(&self) -> &'static str {
        match self.family {
            ArchitectureFamily::WormLike => {
                "C. elegans: 302 neurons, fully mapped connectome, \
                 shows basic learning despite simplicity. \
                 Reference: White et al. 1986, Brenner 1974"
            }
            ArchitectureFamily::OctopusLike => {
                "Octopus: 500M neurons, 2/3 in arms, distributed control, \
                 arm autonomy with central coordination. \
                 Reference: Hochner et al. 2006"
            }
            ArchitectureFamily::TianxinPulse => {
                "Central pattern generators (CPG) + thalamic reticular nucleus. \
                 Rhythmic activity gates information flow. \
                 Reference: Marder & Bucher 2001, Steriade 2005"
            }
            ArchitectureFamily::RandomSparse => {
                "Random graph theory, small-world networks. \
                 Reference: Erdos-Renyi model, Watts-Strogatz 1998"
            }
            ArchitectureFamily::ModularLattice => {
                "Modularity in brain networks, columnar organization. \
                 Reference: Mountcastle 1997, Sporns 2013"
            }
        }
    }
}

/// 架构比较分析
pub struct ArchitectureComparison {
    pub families: Vec<ArchitectureTraits>,
}

impl ArchitectureComparison {
    pub fn new() -> Self {
        Self {
            families: ArchitectureTraits::all(),
        }
    }
    
    /// 分析哪个架构最可能产生某种动力学
    pub fn best_for_dynamics(&self, target: TargetDynamics) -> Vec<(ArchitectureFamily, f32)> {
        let mut scores: Vec<_> = self.families.iter()
            .map(|traits| {
                let score = match target {
                    TargetDynamics::AttractorFormation => traits.dynamics_bias.attractor_formation,
                    TargetDynamics::MemoryPersistence => traits.dynamics_bias.memory_persistence,
                    TargetDynamics::Reorganization => traits.dynamics_bias.reorganization,
                    TargetDynamics::Recovery => traits.dynamics_bias.recovery,
                };
                (traits.family, score)
            })
            .collect();
        
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        scores
    }
    
    /// 生成比较报告
    pub fn generate_report(&self) -> String {
        let mut report = String::new();
        
        report.push_str("# Architecture Family Comparison\n\n");
        
        for family in &self.families {
            report.push_str(&format!("## {:?}\n", family.family));
            report.push_str(&format!("{}\n\n", family.description));
            report.push_str(&format!("- Typical units: {}\n", family.typical_units));
            report.push_str(&format!("- Attractor bias: {:.1}\n", family.dynamics_bias.attractor_formation));
            report.push_str(&format!("- Memory bias: {:.1}\n", family.dynamics_bias.memory_persistence));
            report.push_str(&format!("- Reorganization bias: {:.1}\n", family.dynamics_bias.reorganization));
            report.push_str(&format!("- Recovery bias: {:.1}\n\n", family.dynamics_bias.recovery));
        }
        
        report
    }
}

pub enum TargetDynamics {
    AttractorFormation,
    MemoryPersistence,
    Reorganization,
    Recovery,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_architecture_traits() {
        let traits = ArchitectureTraits::all();
        assert_eq!(traits.len(), 5);
        
        for t in &traits {
            println!("{:?}: {}", t.family, t.description);
        }
    }
    
    #[test]
    fn test_best_for_dynamics() {
        let comparison = ArchitectureComparison::new();
        let best_attractor = comparison.best_for_dynamics(TargetDynamics::AttractorFormation);
        
        println!("Best for attractors: {:?}", best_attractor[0]);
        
        // 天心脉冲型应该有最高的吸引子偏置
        assert_eq!(best_attractor[0].0, ArchitectureFamily::TianxinPulse);
    }
}
