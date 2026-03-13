//! Hazard Rate Model
//! 
//! Extinction prediction and early warning signals

pub mod rate;

pub use rate::{HazardRateTracker, MultiUniverseHazard, HazardStats};
