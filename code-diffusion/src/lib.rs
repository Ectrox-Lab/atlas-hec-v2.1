//! Code-DNA Diffusion
//! 
//! A Rust implementation of conditional diffusion models for code patch generation.
//! Adapted from DNA-Diffusion for the Hyperbrain project.

pub mod diffusion;
pub mod models;
pub mod data;
pub mod sampling;
pub mod verification;
pub mod training;

pub use diffusion::{Diffusion, DiffusionConfig};
pub use models::{UNet, UNetConfig};
pub use data::{CodeDNAEncoder, ConditionLabel, EditDNA, EditToken};

use thiserror::Error;

#[derive(Error, Debug)]
pub enum CodeDiffusionError {
    #[error("Invalid token index: {0}")]
    InvalidToken(usize),
    
    #[error("Sequence length mismatch: expected {expected}, got {actual}")]
    SequenceLengthMismatch { expected: usize, actual: usize },
    
    #[error("Model error: {0}")]
    ModelError(String),
    
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Serialization error: {0}")]
    SerializationError(String),
}

pub type Result<T> = std::result::Result<T, CodeDiffusionError>;

/// Version of the library
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
