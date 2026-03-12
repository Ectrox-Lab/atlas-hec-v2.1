//! 第一批8组实验计划表
//! 
//! 结构家族 × 宇宙压力 交叉验证

use crate::stress_profile::StressProfile;
use crate::universe_config::ArchitectureFamily;

#[derive(Clone, Debug)]
pub struct ExperimentPlan {
    pub family: ArchitectureFamily,
    pub stress: StressProfile,
    pub seeds: &'static [u64],
    pub label: &'static str,
    pub rationale: &'static str,
}

pub const DEFAULT_SEEDS: &[u64] = &[11, 23, 37];

/// 第一批8组实验：最有信息增益的配对
pub fn first8_plans() -> Vec<ExperimentPlan> {
    use ArchitectureFamily::*;
    use StressProfile::*;
    
    vec![
        ExperimentPlan {
            family: WormLike,
            stress: StableLowStress,
            seeds: DEFAULT_SEEDS,
            label: "worm_stable",
            rationale: "Test low-complexity attractor formation and persistence in minimal sparse architecture.",
        },
        ExperimentPlan {
            family: WormLike,
            stress: ResourceScarcity,
            seeds: DEFAULT_SEEDS,
            label: "worm_scarcity",
            rationale: "Test minimal sparse architecture under survival pressure - energy efficiency vs complexity.",
        },
        ExperimentPlan {
            family: OctopusLike,
            stress: HighCoordinationDemand,
            seeds: DEFAULT_SEEDS,
            label: "octopus_coordination",
            rationale: "Test distributed specialization and shared-state emergence from local competition.",
        },
        ExperimentPlan {
            family: OctopusLike,
            stress: RegimeShiftFrequent,
            seeds: DEFAULT_SEEDS,
            label: "octopus_regime_shift",
            rationale: "Test local autonomy + reorganization after rapid environmental shifts.",
        },
        ExperimentPlan {
            family: PulseCentral,
            stress: SyncRiskHigh,
            seeds: DEFAULT_SEEDS,
            label: "pulse_sync_risk",
            rationale: "Test whether central rhythm improves broadcast or causes synchronization fragility.",
        },
        ExperimentPlan {
            family: PulseCentral,
            stress: BossPressureHigh,
            seeds: DEFAULT_SEEDS,
            label: "pulse_boss_pressure",
            rationale: "Test recovery and hazard control under repeated high external shocks.",
        },
        ExperimentPlan {
            family: ModularLattice,
            stress: InheritanceNoiseHigh,
            seeds: DEFAULT_SEEDS,
            label: "lattice_inheritance_noise",
            rationale: "Test lineage/archive resilience under noisy inheritance - structured vs random advantage.",
        },
        ExperimentPlan {
            family: RandomSparse,
            stress: HighCompetition,
            seeds: DEFAULT_SEEDS,
            label: "random_competition",
            rationale: "Control family under adversarial selective pressure - pure emergence vs designed structure.",
        },
    ]
}

/// 获取实验描述
pub fn describe_plan(plan: &ExperimentPlan) -> String {
    format!(
        "[{}] {} × {} | seeds={:?}\n  Rationale: {}",
        plan.label,
        plan.family.as_str(),
        plan.stress.as_str(),
        plan.seeds,
        plan.rationale
    )
}

/// 打印实验计划摘要
pub fn print_first8_summary() {
    println!("=== First 8 Experiment Plans ===\n");
    for (i, plan) in first8_plans().iter().enumerate() {
        println!("{}.{}", i + 1, describe_plan(plan));
        println!();
    }
    println!("Total universes: {} plans × {} seeds = {}", 
        first8_plans().len(),
        DEFAULT_SEEDS.len(),
        first8_plans().len() * DEFAULT_SEEDS.len()
    );
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_first8_plans() {
        let plans = first8_plans();
        assert_eq!(plans.len(), 8);
        
        // 验证所有家族都出现
        let families: std::collections::HashSet<_> = plans.iter()
            .map(|p| p.family)
            .collect();
        assert_eq!(families.len(), 5); // 5个家族
        
        // 验证所有压力类型都不同或合理分布
        let stresses: std::collections::HashSet<_> = plans.iter()
            .map(|p| p.stress)
            .collect();
        assert_eq!(stresses.len(), 8); // 8个不同压力
    }
    
    #[test]
    fn test_plan_labels_unique() {
        let plans = first8_plans();
        let labels: std::collections::HashSet<_> = plans.iter()
            .map(|p| p.label)
            .collect();
        assert_eq!(labels.len(), plans.len()); // 标签唯一
    }
}
