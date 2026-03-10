//! 001 Consistency Markers - Self-Model via Multi-Agent Coherence
//! 
//! Tests whether 32-bit consistency markers can function as self-model anchors.

pub mod marker;
pub mod environment;

pub use marker::{Marker, CoherenceTracker, ScheduledMarker};
pub use environment::{Agent, Environment, Action, Strategy, run_week1_experiment, ExperimentResult, run_timescale_comparison, run_ablation_test, run_site_dissection_experiment, MarkerMode};
pub mod d4_analysis;
pub use d4_analysis::{run_d4_analysis, run_d4_metric_collection, compute_sub_metrics, export_to_csv, AgentCoherenceRecord, CoherenceSubMetrics};
pub mod d1_paired_seed;
pub use d1_paired_seed::{run_d1_validation, run_aa_test, AAResult};
