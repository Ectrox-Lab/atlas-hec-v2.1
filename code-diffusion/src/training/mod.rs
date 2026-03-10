//! Training module for Code-DNA Diffusion

use crate::data::{EditDNA, PatchCategory};
use crate::diffusion::{Diffusion, DiffusionConfig};
use crate::models::{UNet, UNetConfig};
use ndarray::{Array1, Array3};
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
            learning_rate: 0.0001,
            patience: 10,
            min_epochs: 20,
            log_interval: 10,
            checkpoint_interval: 50,
        }
    }
}

/// Training state
pub struct Trainer {
    diffusion: Diffusion,
    unet: UNet,
    config: TrainingConfig,
    optimizer: SimpleOptimizer,
    history: TrainingHistory,
}

/// Simplified SGD optimizer
pub struct SimpleOptimizer {
    learning_rate: f64,
}

impl SimpleOptimizer {
    pub fn new(learning_rate: f64) -> Self {
        Self { learning_rate }
    }
    
    /// Simple gradient descent step
    pub fn step(&self, params: &mut Array3<f64>, gradients: &Array3<f64>) {
        *params = &*params - &(gradients * self.learning_rate);
    }
}

/// Training history tracking
#[derive(Debug)]
pub struct TrainingHistory {
    pub train_losses: Vec<f64>,
    pub val_losses: Vec<f64>,
    pub best_val_loss: f64,
    pub best_epoch: usize,
}

impl Default for TrainingHistory {
    fn default() -> Self {
        Self {
            train_losses: vec![],
            val_losses: vec![],
            best_val_loss: f64::INFINITY,
            best_epoch: 0,
        }
    }
}

impl Trainer {
    pub fn new(diffusion: Diffusion, unet: UNet, config: TrainingConfig) -> Self {
        let optimizer = SimpleOptimizer::new(config.learning_rate);
        Self {
            diffusion,
            unet,
            config,
            optimizer,
            history: TrainingHistory::default(),
        }
    }
    
    /// Train on dataset
    pub fn train(&mut self, train_data: &[EditDNA], val_data: &[EditDNA]) -> &TrainingHistory {
        let mut patience_counter = 0;
        
        println!("Starting training for {} epochs", self.config.num_epochs);
        println!("Training samples: {}, Validation samples: {}", train_data.len(), val_data.len());
        
        for epoch in 0..self.config.num_epochs {
            // Training
            let train_loss = self.train_epoch(train_data);
            self.history.train_losses.push(train_loss);
            
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
            
            // Checkpoint saving
            if (epoch + 1) % self.config.checkpoint_interval == 0 {
                self.save_checkpoint(epoch + 1, val_loss);
            }
            
            // Early stopping check
            if val_loss < self.history.best_val_loss {
                self.history.best_val_loss = val_loss;
                self.history.best_epoch = epoch + 1;
                patience_counter = 0;
                // Save best model
                self.save_checkpoint(epoch + 1, val_loss);
            } else {
                patience_counter += 1;
            }
            
            // Early stopping
            if epoch >= self.config.min_epochs && patience_counter >= self.config.patience {
                println!(
                    "Early stopping at epoch {}. Best val_loss={:.6} at epoch {}",
                    epoch + 1,
                    self.history.best_val_loss,
                    self.history.best_epoch
                );
                break;
            }
        }
        
        &self.history
    }
    
    fn train_epoch(&mut self, data: &[EditDNA]) -> f64 {
        let mut total_loss = 0.0;
        let mut count = 0;
        
        // Process in batches
        for batch in data.chunks(self.config.batch_size) {
            let batch_loss = self.train_batch(batch);
            total_loss += batch_loss;
            count += 1;
        }
        
        total_loss / count as f64
    }
    
    fn train_batch(&mut self, batch: &[EditDNA]) -> f64 {
        let mut batch_loss = 0.0;
        
        for dna in batch {
            // Get tensor representation
            let x_start = dna.to_tensor().insert_axis(ndarray::Axis(0));
            let class = dna.condition as usize as f64;
            
            // Random timestep
            let t = rand::random::<usize>() % self.diffusion.timesteps();
            
            // Forward pass (simplified - no gradient computation yet)
            let loss = self.diffusion.p_losses(
                &x_start,
                t,
                &Array3::zeros((1, 1, 64)) // Placeholder for model prediction
            );
            
            batch_loss += loss;
        }
        
        batch_loss / batch.len() as f64
    }
    
    fn validate(&self, data: &[EditDNA]) -> f64 {
        let mut total_loss = 0.0;
        
        for dna in data.iter().take(100) { // Sample validation
            let x_start = dna.to_tensor().insert_axis(ndarray::Axis(0));
            let t = rand::random::<usize>() % self.diffusion.timesteps();
            
            let loss = self.diffusion.p_losses(&x_start, t, &Array3::zeros((1, 1, 64)));
            total_loss += loss;
        }
        
        total_loss / data.len().min(100) as f64
    }
    
    fn save_checkpoint(&self, epoch: usize, val_loss: f64) {
        let filename = format!("checkpoints/model_epoch{}_loss{:.6}.pt", epoch, val_loss);
        println!("Saving checkpoint: {}", filename);
        // In real implementation, save model weights here
    }
    
    pub fn history(&self) -> &TrainingHistory {
        &self.history
    }
}

/// Create toy dataset for testing
pub fn create_toy_dataset(size: usize) -> Vec<EditDNA> {
    use crate::data::EditToken;
    use rand::seq::SliceRandom;
    
    let tokens = vec![
        EditToken::AddIf,
        EditToken::InsertGuard,
        EditToken::ChangeConst,
        EditToken::RemoveCall,
        EditToken::WrapTry,
    ];
    
    let conditions = vec![
        PatchCategory::BugFix,
        PatchCategory::Performance,
        PatchCategory::Safety,
    ];
    
    let mut dataset = vec![];
    let mut rng = thread_rng();
    
    for _ in 0..size {
        let num_tokens = rand::random::<usize>() % 10 + 5;
        let sample_tokens: Vec<_> = (0..num_tokens)
            .map(|_| *tokens.choose(&mut rng).unwrap())
            .collect();
        
        let condition = *conditions.choose(&mut rng).unwrap();
        dataset.push(EditDNA::new(sample_tokens, condition));
    }
    
    dataset
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_trainer_creation() {
        let diffusion = Diffusion::new(DiffusionConfig::default());
        let unet = UNet::new(UNetConfig::default());
        let config = TrainingConfig::default();
        let trainer = Trainer::new(diffusion, unet, config);
        
        assert!(trainer.history().train_losses.is_empty());
    }
    
    #[test]
    fn test_toy_dataset() {
        let dataset = create_toy_dataset(10);
        assert_eq!(dataset.len(), 10);
    }
}
