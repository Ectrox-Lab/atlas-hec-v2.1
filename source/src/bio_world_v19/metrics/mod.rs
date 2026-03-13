//! Bio-World v19 State Vector Metrics
//! 
//! Unified state: S(t) = [CDI, CI, r, N, E, h]
//! 
//! Sources:
//! - r, CI, P: from e1_critical_coupling/src/bin/e1_overnight_batch.rs
//! - CDI: from bio_superbrain_interface/lineage_adapter.rs

pub mod sync;
pub mod condensation;
pub mod percolation;

pub use sync::compute_sync_order_parameter;
pub use condensation::compute_condensation_index;
pub use percolation::compute_percolation_ratio;

/// Unified v19 state vector
#[derive(Clone, Copy, Debug, Default)]
pub struct StateVector {
    pub cdi: f64,    // Complexity-Degradation-Index
    pub ci: f64,     // Condensation Index
    pub r: f64,      // Synchronization order parameter
    pub n: usize,    // Population
    pub e: f64,      // Energy availability
    pub h: f64,      // Hazard rate
}

impl StateVector {
    pub fn new() -> Self {
        Self::default()
    }
    
    /// Export as CSV row
    pub fn to_csv(&self) -> String {
        format!("{},{},{},{},{},{}",
            self.cdi, self.ci, self.r, self.n, self.e, self.h
        )
    }
    
    /// CSV header
    pub fn csv_header() -> &'static str {
        "CDI,CI,r,N,E,h"
    }
}
