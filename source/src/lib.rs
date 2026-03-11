pub mod mnist {
    pub mod loader;
}
pub mod mlp;

// PriorChannel: Post-Phase 7 Engineering Convergence
// FROZEN_STATE_v1: Generic prior channel only
pub mod prior_channel;
pub use prior_channel::{
    PriorChannel, PriorSample,
    sample_prior, prior_inject,
    PRIOR_SAMPLE_PROB, PRIOR_STRENGTH
};

// 重导出主要类型
pub use mnist::loader::MNISTDataset;
pub use mlp::MLPReadout;

// GridWorld模块
pub mod gridworld;
pub mod atlas_cuda_bridge;
pub mod hec_ffi;
pub mod sensory;

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
