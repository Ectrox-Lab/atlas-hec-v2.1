//! 001 Consistency Markers - Self-Model via Multi-Agent Coherence
//! 
//! Tests whether 32-bit consistency markers can function as self-model anchors.

pub mod marker;
pub mod environment;

pub use marker::{Marker, CoherenceTracker, ScheduledMarker};
pub use environment::{Agent, Environment, Action, Strategy, run_week1_experiment, ExperimentResult, run_timescale_comparison, run_ablation_test};
