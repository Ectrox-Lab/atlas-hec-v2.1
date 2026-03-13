//! Real gradient training with RealUNetFull
//! Replaces apply_noise() with true backprop

use crate::models::realunet_full::{RealUNetFull, FullGradient};
use crate::diffusion::{Diffusion, DiffusionConfig};
use ndarray::{Array3};
use rand::distributions::Distribution;
use rand::thread_rng;
use rand_distr::StandardNormal;

/// Real gradient trainer using RealUNetFull
pub struct RealGradientTrainer {
    diffusion: Diffusion,
    unet: RealUNetFull,
    learning_rate: f64,
}

impl RealGradientTrainer {
    pub fn new(diffusion: Diffusion, unet: RealUNetFull, learning_rate: f64) -> Self {
        Self {
            diffusion,
            unet,
            learning_rate,
        }
    }
    
    /// Single training step with real backprop
    pub fn train_step(&mut self, x_start: &Array3<f64>, t: usize) -> f64 {
        // Generate target noise
        let mut rng = thread_rng();
        let target_noise: Array3<f64> = Array3::from_shape_fn(
            x_start.raw_dim(),
            |_| StandardNormal.sample(&mut rng)
        );
        
        // Forward diffusion
        let x_noisy = self.diffusion.q_sample(x_start, t, Some(&target_noise));
        
        // Forward through network (with cache for backward)
        let noise_pred = self.unet.forward(&x_noisy);
        
        // Compute loss (MSE)
        let diff = &noise_pred - &target_noise;
        let loss = diff.mapv(|v| v * v).mean().unwrap();
        
        // Backward: compute gradients
        // dL/d(pred) = 2*(pred - target) / N
        let n = diff.len() as f64;
        let grad_output = diff.mapv(|v| 2.0 * v / n);
        
        let gradients = self.unet.backward(&grad_output);
        
        // Update parameters with gradients (real SGD)
        self.unet.update(&gradients, self.learning_rate);
        
        loss
    }
    
    /// Train for one epoch
    pub fn train_epoch(&mut self, data: &[Array3<f64>]) -> f64 {
        let mut total_loss = 0.0;
        
        for x_start in data {
            let t = rand::random::<usize>() % self.diffusion.timesteps();
            let loss = self.train_step(x_start, t);
            total_loss += loss;
        }
        
        total_loss / data.len() as f64
    }
}
