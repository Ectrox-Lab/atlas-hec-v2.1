//! 002 Soft Robot - Proprioceptive Self-Model
//! 
//! Tests whether predictive feedback improves body stability and self-boundary discrimination.

pub mod mesh;
pub mod predictor;
pub mod experiment;

pub use mesh::{SoftMesh, Node, Spring};
pub use predictor::{LinearPredictor, PredictiveController, ReactiveController};
pub use experiment::{run_week1_experiment, save_results, analyze_for_gate, Condition, run_single_shot_recovery_experiment, RecoveryMetrics};
