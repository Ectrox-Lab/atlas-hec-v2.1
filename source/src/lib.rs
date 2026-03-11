pub mod mnist {
    pub mod loader;
}
pub mod mlp;

// PriorChannel: Post-Phase 7 Engineering Convergence
// FROZEN_STATE_v1: Generic prior channel only
// Candidate 001: Multi-Agent Consistency Markers = MAINLINE DEFAULT
pub mod prior_channel;
pub use prior_channel::{
    PriorChannel, PriorSample,
    sample_prior, prior_inject,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH,
    // Candidate 001 Integration (Mainline Default)
    PriorChannelMarkerAdapter, Marker, MarkerScheduler, PolicyModulation,
    MainlinePriorChannel, ConstraintReport,
};

// 重导出主要类型
pub use mnist::loader::MNISTDataset;
pub use mlp::MLPReadout;

// GridWorld模块
pub mod gridworld;
pub mod atlas_cuda_bridge;
pub mod sensory;

// HEC Bridge (requires external library)
#[cfg(feature = "hec_bridge")]
pub mod hec_ffi;

// Self Kernel v0.1: 最小可验证自我核心
pub mod self_kernel;
pub use self_kernel::{
    SelfKernel, Identity, SelfState, 
    RuntimeSnapshot, RuntimeData,
    Episode, AutobiographicalMemory, 
    SelfReport, Goal, GoalVector, GoalStatus,
    SelfPredictor, PredictedState
};

// P2: Self Preservation Kernel
pub mod self_preservation;
pub use self_preservation::{
    SelfPreservationKernel, HomeostasisState,
    PreservationAction, PreservationPolicy,
    SurvivalRiskModel, SurvivalRiskEstimate,
    PreservationMetrics, ExperimentComparison
};

// P3: Runtime Integration (P2 验证的关键闭环)
pub mod p3_runtime_integration;
pub use p3_runtime_integration::{
    P3RuntimeIntegration, RuntimeParameters, P3Config,
    ParameterMappingConfig
};

// Bio-World × Superbrain Integration v0
// Open-world multi-agent adaptive intelligence
pub mod bio_superbrain_interface;
pub use bio_superbrain_interface::{
    CellAdapter, LineageAdapter, StrategyBridge,
    ExperimentAtoE, RunConfig,
    integration_health, HealthStatus,
};
