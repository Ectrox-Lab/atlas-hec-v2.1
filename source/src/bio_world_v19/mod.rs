//! Bio-World v19 - Unified Multi-Agent Evolution Framework
//! 
//! State vector: S(t) = [CDI, CI, r, N, E, h]
//! 
//! Components:
//! - metrics: r (sync), CI (condensation), P (percolation), CDI
//! - core: 50×50×16 grid, agents, population dynamics
//! - hazard: Extinction prediction and early warning

pub mod metrics;
pub mod core;
pub mod hazard;

pub use metrics::{StateVector, compute_sync_order_parameter, compute_condensation_index, compute_percolation_ratio};
pub use core::{GridWorld, Agent, Position, PopulationDynamics, PopulationParams, GRID_X, GRID_Y, GRID_Z};
pub use hazard::{HazardRateTracker, MultiUniverseHazard, HazardStats};

/// v19 version
pub const VERSION: &str = "v19.0-alpha";

/// Integration with bio_superbrain_interface
pub fn integrate_with_superbrain() -> bool {
    // Placeholder for actual integration
    true
}
