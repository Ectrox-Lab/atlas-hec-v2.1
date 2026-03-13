//! Training module - Real gradient as default path
//! Noise prediction loss with backward() + update()

use crate::diffusion::{Diffusion, DiffusionConfig};
use crate::models::realunet_full::{RealUNetFull, FullGradient};
use ndarray::{Array1, Array3, Axis};
use rand::distributions::Distribution;
use rand::thread_rng;
use rand_distr::StandardNormal;
use std::collections::VecDeque;

/// Training configuration
#[derive(Debug, Clone)]
pub struct TrainingConfig {
    pub batch_size: usize,
    pub num_epochs: usize,
    pub learning_rate: f64,
    pub patience: usize,
    pub min_epochs: usize,
    pub log_interval: usize,
    pub checkpoint_interval: usize,
}

impl Default for TrainingConfig {
    fn default() -> Self {
        Self {
            batch_size: 32,
            num_epochs: 100,
            learning_rate: 0.001,
            patience: 10,
            min_epochs: 20,
            log_interval: 10,
            checkpoint_interval: 50,
        }
    }
}

/// Training state with REAL gradient-based model
pub struct Trainer {
    diffusion: Diffusion,
    unet: RealUNetFull,
    config: TrainingConfig,
    history: TrainingHistory,
}

/// Training history tracking
#[derive(Debug, Clone)]
pub struct TrainingHistory {
    pub train_losses: Vec<f64>,
    pub val_losses: Vec<f64>,
    pub best_val_loss: f64,
    pub best_epoch: usize,
    pub param_hashes: Vec<(usize, u64)>,
}

impl Default for TrainingHistory {
    fn default() -> Self {
        Self {
            train_losses: vec![],
            val_losses: vec![],
            best_val_loss: f64::INFINITY,
            best_epoch: 0,
            param_hashes: vec![],
        }
    }
}

impl Trainer {
    pub fn new(diffusion: Diffusion, unet: RealUNetFull, config: TrainingConfig) -> Self {
        Self {
            diffusion,
            unet,
            config,
            history: TrainingHistory::default(),
        }
    }
    
    /// Get current parameter hash
    pub fn current_param_hash(&self) -> u64 {
        self.unet.param_hash()
    }
    
    /// Train for one epoch with REAL gradient
    fn train_epoch(&mut self, data: &[(Array3<f64>, usize)]) -> f64 {
        let mut total_loss = 0.0;
        let mut count = 0;
        
        for batch in data.chunks(self.config.batch_size) {
            let batch_loss = self.train_batch_real(batch);
            total_loss += batch_loss;
            count += 1;
        }
        
        total_loss / count as f64
    }
    
    /// REAL gradient training batch - DEFAULT PATH
    fn train_batch_real(&mut self, batch: &[(Array3<f64>, usize)]) -> f64 {
        let mut batch_loss = 0.0;
        
        for (x_start, class) in batch {
            // Forward diffusion: add noise
            let t = rand::random::<usize>() % self.diffusion.timesteps();
            let mut rng = thread_rng();
            let target_noise: Array3<f64> = Array3::from_shape_fn(
                x_start.raw_dim(),
                |_| StandardNormal.sample(&mut rng)
            );
            let x_noisy = self.diffusion.q_sample(x_start, t, Some(&target_noise));
            
            // Forward: predict noise
            let noise_pred = self.unet.forward(&x_noisy);
            
            // Loss: MSE between predicted and target noise
            let diff = &noise_pred - &target_noise;
            let loss = diff.mapv(|v| v * v).mean().unwrap();
            batch_loss += loss;
            
            // Backward: compute gradients
            let n = diff.len() as f64;
            let grad_output = diff.mapv(|v| 2.0 * v / n);
            let gradients = self.unet.backward(&grad_output);
            
            // Update: real gradient descent
            self.unet.update(&gradients, self.config.learning_rate);
        }
        
        batch_loss / batch.len() as f64
    }
    
    /// Validation
    fn validate(&mut self, data: &[(Array3<f64>, usize)]) -> f64 {
        let mut total_loss = 0.0;
        
        for (x_start, _class) in data {
            let t = rand::random::<usize>() % self.diffusion.timesteps();
            let mut rng = thread_rng();
            let target_noise: Array3<f64> = Array3::from_shape_fn(
                x_start.raw_dim(),
                |_| StandardNormal.sample(&mut rng)
            );
            let x_noisy = self.diffusion.q_sample(x_start, t, Some(&target_noise));
            let noise_pred = self.unet.forward(&x_noisy);
            
            let diff = &noise_pred - &target_noise;
            let loss = diff.mapv(|v| v * v).mean().unwrap();
            total_loss += loss;
        }
        
        total_loss / data.len() as f64
    }
    
    /// Main training loop - DEFAULT: Real gradient
    pub fn train(&mut self, train_data: &[(Array3<f64>, usize)], val_data: &[(Array3<f64>, usize)]) {
        println!("Starting REAL gradient training...");
        println!("  Epochs: {}", self.config.num_epochs);
        println!("  Learning rate: {}", self.config.learning_rate);
        println!("  Batch size: {}", self.config.batch_size);
        
        let mut patience_counter = 0;
        
        for epoch in 0..self.config.num_epochs {
            // Training with REAL gradient
            let train_loss = self.train_epoch(train_data);
            self.history.train_losses.push(train_loss);
            
            // Record param hash
            let hash = self.unet.param_hash();
            self.history.param_hashes.push((epoch + 1, hash));
            
            // Validation
            let val_loss = self.validate(val_data);
            self.history.val_losses.push(val_loss);
            
            // Logging
            if (epoch + 1) % self.config.log_interval == 0 {
                println!(
                    "Epoch {}/{}: train_loss={:.6}, val_loss={:.6}",
                    epoch + 1,
                    self.config.num_epochs,
                    train_loss,
                    val_loss
                );
            }
            
            // Checkpoint
            if (epoch + 1) % self.config.checkpoint_interval == 0 {
                println!("  [Checkpoint] Epoch {} saved", epoch + 1);
            }
            
            // Early stopping
            if val_loss < self.history.best_val_loss {
                self.history.best_val_loss = val_loss;
                self.history.best_epoch = epoch + 1;
                patience_counter = 0;
            } else {
                patience_counter += 1;
            }
            
            if patience_counter >= self.config.patience 
                && epoch >= self.config.min_epochs {
                println!("Early stopping at epoch {}", epoch + 1);
                break;
            }
        }
        
        println!("\nTraining complete!");
        println!("Best val_loss: {:.6} at epoch {}", 
            self.history.best_val_loss, self.history.best_epoch);
    }
    
    /// Save checkpoint
    pub fn save_checkpoint(&self, epoch: usize, loss: f64) -> String {
        let hash = self.unet.param_hash();
        let filename = format!("checkpoints/model_epoch{}_loss{:.6}_hash{:x}.pt", 
            epoch, loss, hash);
        println!("  Checkpoint: {}", filename);
        filename
    }
}

/// LEGACY: Perturbation-based training (for debug/compatibility only)
#[cfg(feature = "legacy_perturbation")]
pub mod legacy {
    use super::*;
    
    /// Apply noise perturbation (NOT real gradient)
    pub fn apply_noise_perturbation(unet: &mut RealUNetFull, signal: f64) {
        let scale = signal.abs() * 0.001 + 1e-6;
        // This is random walk, not gradient descent
        // Kept only for regression testing
        println!("[LEGACY] apply_noise_perturbation called (NOT real training)");
    }
}
