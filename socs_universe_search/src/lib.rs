//! SOCS Universe Search Engine
//! 
//! 多元宇宙架构搜索：从简单局部规则出发，通过大规模并行探索，
//! 找出能涌现认知能力的结构组合。

// 核心模块 - Universe Search v0
pub mod universe_config;
pub mod stress_profile;
pub mod experiment_plan;
pub mod search_scheduler;
pub mod evaluation;
pub mod telemetry;
pub mod universe_runner;
pub mod config_generator;
pub mod consciousness_index;
pub mod cwci_report;

// 重新导出常用类型
pub use universe_config::{
    ArchitectureFamily, UniverseConfig, EnvironmentFamily,
    PlasticityProfile, BroadcastProfile, CompetitionProfile, ScaleProfile,
};
pub use evaluation::{DynamicsScores, EvaluationResult, DynamicPhenomena, TickSnapshot, CollapseSignature};
pub use stress_profile::{StressProfile, StressProfileConfig};
pub use consciousness_index::{ConsciousnessCapabilities, ConsciousnessLevel, CWCIEvaluation, evaluate_cwci};

// 类型别名（向后兼容）
pub type ParameterConfig = UniverseConfig;
pub type PlasticityFamily = PlasticityProfile;
pub type BroadcastFamily = BroadcastProfile;
pub type MemoryCoupling = ScaleProfile;

// SearchResult 类型
#[derive(Clone, Debug)]
pub struct SearchResult {
    pub universe_id: String,
    pub architecture_family: ArchitectureFamily,
    pub parameter_config: UniverseConfig,
    pub dynamics_scores: DynamicsScores,
    pub survival_time: u64,
    pub stability_rating: f32,
}

/// 搜索配置
#[derive(Clone, Debug)]
pub struct SearchConfig {
    pub parallel_universes: usize,
    pub max_ticks_per_universe: usize,
    pub pass_threshold: f32,
}

impl Default for SearchConfig {
    fn default() -> Self {
        Self {
            parallel_universes: 1,
            max_ticks_per_universe: 5000,
            pass_threshold: 0.5,
        }
    }
}
