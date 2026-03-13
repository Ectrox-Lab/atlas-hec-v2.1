//! Bio-World v19 Core Components
//! 
//! Multi-agent simulation with:
//! - 50×50×16 3D grid
//! - Energy-based agents
//! - Population dynamics

pub mod agent;
pub mod grid;
pub mod population;

pub use agent::Agent;
pub use grid::{GridWorld, Position, Food, GRID_X, GRID_Y, GRID_Z};
pub use population::{PopulationDynamics, PopulationParams, PopulationStats};
