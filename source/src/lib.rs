pub mod mnist {
    pub mod loader;
}
pub mod mlp;

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
