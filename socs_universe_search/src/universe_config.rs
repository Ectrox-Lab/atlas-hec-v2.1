//! UniverseConfig 完整定义
//! 
//! v0 最小配置结构，保留所有护栏约束。

use serde::{Serialize, Deserialize};
use crate::stress_profile::{StressProfile, StressProfileConfig};

/// 架构家族
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ArchitectureFamily {
    WormLike,       // 线虫型：小而稀疏
    OctopusLike,    // 章鱼型：分布式自治
    PulseCentral,   // 脉冲中枢型：节律驱动
    ModularLattice, // 模块网格型：规则拓扑
    RandomSparse,   // 随机稀疏型：最弱先验
}

impl ArchitectureFamily {
    pub fn all() -> Vec<Self> {
        vec![
            Self::WormLike,
            Self::OctopusLike,
            Self::PulseCentral,
            Self::ModularLattice,
            Self::RandomSparse,
        ]
    }
    
    pub fn as_str(&self) -> &'static str {
        match self {
            ArchitectureFamily::WormLike => "worm_like",
            ArchitectureFamily::OctopusLike => "octopus_like",
            ArchitectureFamily::PulseCentral => "pulse_central",
            ArchitectureFamily::ModularLattice => "modular_lattice",
            ArchitectureFamily::RandomSparse => "random_sparse",
        }
    }
}

/// 环境家族
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum EnvironmentFamily {
    StableLowStress,      // 稳定低压力
    RegimeShiftModerate,  // 中等regime shift
    FailureBurst,         // 突发故障
}

impl EnvironmentFamily {
    pub fn all() -> Vec<Self> {
        vec![
            Self::StableLowStress,
            Self::RegimeShiftModerate,
            Self::FailureBurst,
        ]
    }
}

/// 可塑性配置组合
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum PlasticityProfile {
    PredictiveHeavy,
    Balanced,
    HebbianHeavy,
}

impl PlasticityProfile {
    pub fn all() -> Vec<Self> {
        vec![Self::PredictiveHeavy, Self::Balanced, Self::HebbianHeavy]
    }
}

/// 广播配置组合
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum BroadcastProfile {
    LowBroadcast,
    MediumBroadcast,
}

impl BroadcastProfile {
    pub fn all() -> Vec<Self> {
        vec![Self::LowBroadcast, Self::MediumBroadcast]
    }
}

/// 竞争配置组合
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum CompetitionProfile {
    LowCompetition,
    HighCompetition,
}

impl CompetitionProfile {
    pub fn all() -> Vec<Self> {
        vec![Self::LowCompetition, Self::HighCompetition]
    }
}

/// 规模配置
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ScaleProfile {
    Small,   // 1024
    Medium,  // 2048
}

impl ScaleProfile {
    pub fn all() -> Vec<Self> {
        vec![Self::Small, Self::Medium]
    }
    
    pub fn n_units(&self) -> usize {
        match self {
            Self::Small => 1024,
            Self::Medium => 2048,
        }
    }
}

/// Universe 完整配置
/// 
/// 关键约束保留：
/// - l3_sampling_p = 0.01 (弱采样)
/// - 无 direct archive → cell 路径
/// - 局部信息 only
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UniverseConfig {
    // ==================== 标识 ====================
    pub universe_id: u64,
    pub seed: u64,
    pub family: ArchitectureFamily,
    
    // ==================== 规模 ====================
    pub n_units: usize,
    pub ticks: usize,
    
    // ==================== 拓扑 ====================
    pub local_degree: usize,        // 局部连接数
    pub long_range_degree: usize,   // 远程连接数
    pub inhibitory_ratio: f32,      // 抑制单元比例
    pub rewiring_prob: f32,         // 小世界重连概率
    
    // ==================== 微单元动力学 ====================
    pub activation_decay: f32,      // 激活衰减
    pub energy_budget: f32,         // 能量预算
    pub prediction_error_gain: f32, // 预测误差增益
    
    // ==================== 可塑性 ====================
    pub hebbian_strength: f32,
    pub stdp_strength: f32,
    pub predictive_strength: f32,
    pub reward_mod_strength: f32,
    pub homeostasis_strength: f32,
    
    // ==================== 团簇 ====================
    pub cluster_threshold: f32,
    pub attractor_decay: f32,
    pub competition_strength: f32,
    
    // ==================== 全局广播 ====================
    pub workspace_k: usize,         // 广播竞争槽位数
    pub broadcast_window: usize,    // 广播窗口长度
    pub broadcast_sparsity: f32,    // 广播稀疏度
    
    // ==================== 记忆耦合 (护栏约束) ====================
    pub l1_enabled: bool,
    pub l2_enabled: bool,
    pub l3_enabled: bool,
    pub lineage_mutation_mu: f32,   // 默认 0.05
    pub l3_sampling_p: f32,         // 默认 0.01 (硬约束)
    pub max_distilled_lessons: usize, // 默认 5
    
    // ==================== 环境 ====================
    pub env_family: EnvironmentFamily,
    pub stress_profile: StressProfile,
    pub stress: StressProfileConfig,
    
    // ==================== 记录 ====================
    pub telemetry_stride: usize,    // 记录间隔
}

impl UniverseConfig {
    /// 生成配置哈希（用于唯一标识）
    pub fn config_hash(&self) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.family.hash(&mut hasher);
        self.n_units.hash(&mut hasher);
        self.local_degree.hash(&mut hasher);
        self.long_range_degree.hash(&mut hasher);
        self.inhibitory_ratio.to_bits().hash(&mut hasher);
        self.hebbian_strength.to_bits().hash(&mut hasher);
        self.predictive_strength.to_bits().hash(&mut hasher);
        self.workspace_k.hash(&mut hasher);
        self.broadcast_window.hash(&mut hasher);
        self.env_family.hash(&mut hasher);
        
        format!("{:016x}", hasher.finish())
    }
    
    /// 获取家族默认配置
    pub fn default_for_family(family: ArchitectureFamily, universe_id: u64, seed: u64) -> Self {
        match family {
            ArchitectureFamily::WormLike => Self::worm_like(universe_id, seed),
            ArchitectureFamily::OctopusLike => Self::octopus_like(universe_id, seed),
            ArchitectureFamily::PulseCentral => Self::pulse_central(universe_id, seed),
            ArchitectureFamily::ModularLattice => Self::modular_lattice(universe_id, seed),
            ArchitectureFamily::RandomSparse => Self::random_sparse(universe_id, seed),
        }
    }
    
    // ========== Family A: WormLike ==========
    fn worm_like(universe_id: u64, seed: u64) -> Self {
        Self {
            universe_id,
            seed,
            family: ArchitectureFamily::WormLike,
            n_units: 1024,
            ticks: 5000,
            local_degree: 6,
            long_range_degree: 1,
            inhibitory_ratio: 0.20,
            rewiring_prob: 0.02,
            activation_decay: 0.10,
            energy_budget: 1.00,
            prediction_error_gain: 0.25,
            hebbian_strength: 0.20,
            stdp_strength: 0.10,
            predictive_strength: 0.35,
            reward_mod_strength: 0.10,
            homeostasis_strength: 0.25,
            cluster_threshold: 0.55,
            attractor_decay: 0.08,
            competition_strength: 0.30,
            workspace_k: 2,
            broadcast_window: 8,
            broadcast_sparsity: 0.08,
            l1_enabled: true,
            l2_enabled: true,
            l3_enabled: true,
            lineage_mutation_mu: 0.05,
            l3_sampling_p: 0.01,  // 硬约束
            max_distilled_lessons: 5,
            env_family: EnvironmentFamily::StableLowStress,
            stress_profile: StressProfile::StableLowStress,
            stress: StressProfileConfig::default_for(StressProfile::StableLowStress),
            telemetry_stride: 10,
        }
    }
    
    // ========== Family B: OctopusLike ==========
    fn octopus_like(universe_id: u64, seed: u64) -> Self {
        Self {
            universe_id,
            seed,
            family: ArchitectureFamily::OctopusLike,
            n_units: 2048,
            ticks: 5000,
            local_degree: 10,
            long_range_degree: 2,
            inhibitory_ratio: 0.18,
            rewiring_prob: 0.05,
            activation_decay: 0.08,
            energy_budget: 1.05,
            prediction_error_gain: 0.30,
            hebbian_strength: 0.25,
            stdp_strength: 0.20,
            predictive_strength: 0.30,
            reward_mod_strength: 0.10,
            homeostasis_strength: 0.20,
            cluster_threshold: 0.50,
            attractor_decay: 0.06,
            competition_strength: 0.25,
            workspace_k: 3,
            broadcast_window: 6,
            broadcast_sparsity: 0.05,
            l1_enabled: true,
            l2_enabled: true,
            l3_enabled: true,
            lineage_mutation_mu: 0.05,
            l3_sampling_p: 0.01,
            max_distilled_lessons: 5,
            env_family: EnvironmentFamily::StableLowStress,
            stress_profile: StressProfile::StableLowStress,
            stress: StressProfileConfig::default_for(StressProfile::StableLowStress),
            telemetry_stride: 10,
        }
    }
    
    // ========== Family C: PulseCentral ==========
    fn pulse_central(universe_id: u64, seed: u64) -> Self {
        Self {
            universe_id,
            seed,
            family: ArchitectureFamily::PulseCentral,
            n_units: 2048,
            ticks: 5000,
            local_degree: 8,
            long_range_degree: 4,
            inhibitory_ratio: 0.22,
            rewiring_prob: 0.08,
            activation_decay: 0.12,
            energy_budget: 0.95,
            prediction_error_gain: 0.22,
            hebbian_strength: 0.18,
            stdp_strength: 0.22,
            predictive_strength: 0.20,
            reward_mod_strength: 0.15,
            homeostasis_strength: 0.30,
            cluster_threshold: 0.60,
            attractor_decay: 0.10,
            competition_strength: 0.40,
            workspace_k: 1,  // 强中心：只有一个广播槽
            broadcast_window: 12,
            broadcast_sparsity: 0.15,
            l1_enabled: true,
            l2_enabled: true,
            l3_enabled: true,
            lineage_mutation_mu: 0.05,
            l3_sampling_p: 0.01,
            max_distilled_lessons: 5,
            env_family: EnvironmentFamily::StableLowStress,
            stress_profile: StressProfile::StableLowStress,
            stress: StressProfileConfig::default_for(StressProfile::StableLowStress),
            telemetry_stride: 10,
        }
    }
    
    // ========== Family D: ModularLattice ==========
    fn modular_lattice(universe_id: u64, seed: u64) -> Self {
        Self {
            universe_id,
            seed,
            family: ArchitectureFamily::ModularLattice,
            n_units: 2048,
            ticks: 5000,
            local_degree: 8,
            long_range_degree: 1,
            inhibitory_ratio: 0.20,
            rewiring_prob: 0.00,  // 规则拓扑，不重连
            activation_decay: 0.09,
            energy_budget: 1.00,
            prediction_error_gain: 0.28,
            hebbian_strength: 0.20,
            stdp_strength: 0.15,
            predictive_strength: 0.28,
            reward_mod_strength: 0.12,
            homeostasis_strength: 0.25,
            cluster_threshold: 0.52,
            attractor_decay: 0.07,
            competition_strength: 0.28,
            workspace_k: 2,
            broadcast_window: 8,
            broadcast_sparsity: 0.06,
            l1_enabled: true,
            l2_enabled: true,
            l3_enabled: true,
            lineage_mutation_mu: 0.05,
            l3_sampling_p: 0.01,
            max_distilled_lessons: 5,
            env_family: EnvironmentFamily::StableLowStress,
            stress_profile: StressProfile::StableLowStress,
            stress: StressProfileConfig::default_for(StressProfile::StableLowStress),
            telemetry_stride: 10,
        }
    }
    
    // ========== Family E: RandomSparse ==========
    fn random_sparse(universe_id: u64, seed: u64) -> Self {
        Self {
            universe_id,
            seed,
            family: ArchitectureFamily::RandomSparse,
            n_units: 2048,
            ticks: 5000,
            local_degree: 5,
            long_range_degree: 3,
            inhibitory_ratio: 0.20,
            rewiring_prob: 0.20,  // 高重连 = 随机
            activation_decay: 0.10,
            energy_budget: 1.00,
            prediction_error_gain: 0.25,
            hebbian_strength: 0.15,
            stdp_strength: 0.15,
            predictive_strength: 0.25,
            reward_mod_strength: 0.10,
            homeostasis_strength: 0.25,
            cluster_threshold: 0.58,
            attractor_decay: 0.09,
            competition_strength: 0.32,
            workspace_k: 2,
            broadcast_window: 8,
            broadcast_sparsity: 0.10,
            l1_enabled: true,
            l2_enabled: true,
            l3_enabled: true,
            lineage_mutation_mu: 0.05,
            l3_sampling_p: 0.01,
            max_distilled_lessons: 5,
            env_family: EnvironmentFamily::StableLowStress,
            stress_profile: StressProfile::StableLowStress,
            stress: StressProfileConfig::default_for(StressProfile::StableLowStress),
            telemetry_stride: 10,
        }
    }
    
    /// 应用变体配置
    pub fn with_variant(
        &self,
        plasticity: PlasticityProfile,
        broadcast: BroadcastProfile,
        competition: CompetitionProfile,
        scale: ScaleProfile,
        env: EnvironmentFamily,
    ) -> Self {
        let mut config = self.clone();
        
        // 应用规模
        config.n_units = scale.n_units();
        
        // 应用可塑性变体
        match plasticity {
            PlasticityProfile::PredictiveHeavy => {
                config.predictive_strength += 0.10;
                config.hebbian_strength -= 0.05;
                config.reward_mod_strength -= 0.03;
            }
            PlasticityProfile::Balanced => {
                // 保持默认
            }
            PlasticityProfile::HebbianHeavy => {
                config.hebbian_strength += 0.10;
                config.predictive_strength -= 0.05;
                config.homeostasis_strength -= 0.03;
            }
        }
        
        // 应用广播变体
        match broadcast {
            BroadcastProfile::LowBroadcast => {
                config.broadcast_window = config.broadcast_window.saturating_sub(2);
                config.broadcast_sparsity -= 0.03;
                config.workspace_k = config.workspace_k.saturating_sub(1).max(1);
            }
            BroadcastProfile::MediumBroadcast => {
                // 保持默认
            }
        }
        
        // 应用竞争变体
        match competition {
            CompetitionProfile::LowCompetition => {
                config.competition_strength -= 0.08;
                config.cluster_threshold -= 0.03;
            }
            CompetitionProfile::HighCompetition => {
                config.competition_strength += 0.08;
                config.cluster_threshold += 0.03;
            }
        }
        
        // 应用环境（映射到对应的压力配置）
        config.env_family = env;
        config.stress_profile = env_to_stress_profile(env);
        
        // 确保参数在有效范围内
        config.clamp_parameters();
        
        config
    }
    
    /// 钳制参数到有效范围
    fn clamp_parameters(&mut self) {
        self.hebbian_strength = self.hebbian_strength.clamp(0.0, 1.0);
        self.predictive_strength = self.predictive_strength.clamp(0.0, 1.0);
        self.reward_mod_strength = self.reward_mod_strength.clamp(0.0, 1.0);
        self.homeostasis_strength = self.homeostasis_strength.clamp(0.0, 1.0);
        self.broadcast_sparsity = self.broadcast_sparsity.clamp(0.0, 1.0);
        self.competition_strength = self.competition_strength.clamp(0.0, 1.0);
        self.cluster_threshold = self.cluster_threshold.clamp(0.0, 1.0);
    }
}

/// 将EnvironmentFamily映射到StressProfile
fn env_to_stress_profile(env: EnvironmentFamily) -> StressProfile {
    match env {
        EnvironmentFamily::StableLowStress => StressProfile::StableLowStress,
        EnvironmentFamily::RegimeShiftModerate => StressProfile::RegimeShiftFrequent,
        EnvironmentFamily::FailureBurst => StressProfile::BossPressureHigh,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_default_configs() {
        for family in ArchitectureFamily::all() {
            let config = UniverseConfig::default_for_family(family, 0, 0);
            assert_eq!(config.family, family);
            assert_eq!(config.l3_sampling_p, 0.01); // 硬约束
            assert!(config.n_units > 0);
        }
    }
    
    #[test]
    fn test_variant_generation() {
        let base = UniverseConfig::default_for_family(ArchitectureFamily::WormLike, 0, 0);
        let variant = base.with_variant(
            PlasticityProfile::PredictiveHeavy,
            BroadcastProfile::LowBroadcast,
            CompetitionProfile::HighCompetition,
            ScaleProfile::Medium,
            EnvironmentFamily::FailureBurst,
        );
        
        assert_eq!(variant.n_units, 2048); // Medium scale
        assert_eq!(variant.env_family, EnvironmentFamily::FailureBurst);
        assert!(variant.predictive_strength > base.predictive_strength);
        assert!(variant.broadcast_window <= base.broadcast_window);
    }
    
    #[test]
    fn test_config_hash() {
        let config = UniverseConfig::default_for_family(ArchitectureFamily::WormLike, 1, 42);
        let hash1 = config.config_hash();
        
        let config2 = UniverseConfig::default_for_family(ArchitectureFamily::WormLike, 1, 42);
        let hash2 = config2.config_hash();
        
        assert_eq!(hash1, hash2);
        
        let config3 = UniverseConfig::default_for_family(ArchitectureFamily::OctopusLike, 1, 42);
        let hash3 = config3.config_hash();
        
        assert_ne!(hash1, hash3);
    }
}
