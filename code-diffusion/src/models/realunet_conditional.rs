//! Round 21: Task-Aligned Conditional Diffusion
//!
//! Minimal conditioning: timestep embedding + noise prediction objective

use ndarray::{Array1, Array2, Array3, Axis};
use rand::distributions::Distribution;
use rand::SeedableRng;
use rand::rngs::StdRng;
use rand_distr::StandardNormal;

/// RealUNet with timestep conditioning for noise prediction
pub struct RealUNetConditional {
    // Timestep embedding (simple sinusoidal)
    time_embed_dim: usize,
    
    // Layer 1: input + time_embed → hidden
    w1: Array2<f64>,
    b1: Array1<f64>,
    
    // Layer 2: hidden → hidden
    w2: Array2<f64>,
    b2: Array1<f64>,
    
    // Layer 3: hidden → output (noise prediction)
    w3: Array2<f64>,
    b3: Array1<f64>,
    
    // Dimensions
    input_dim: usize,
    hidden_dim: usize,
    
    // Cache for backward
    cache_x: Option<Array2<f64>>,
    cache_t_emb: Option<Array2<f64>>,  // timestep embedding
    cache_z1: Option<Array2<f64>>,
    cache_a1: Option<Array2<f64>>,
    cache_z2: Option<Array2<f64>>,
    cache_a2: Option<Array2<f64>>,
}

#[derive(Debug, Clone)]
pub struct ConditionalGradient {
    pub d_w1: Array2<f64>,
    pub d_b1: Array1<f64>,
    pub d_w2: Array2<f64>,
    pub d_b2: Array1<f64>,
    pub d_w3: Array2<f64>,
    pub d_b3: Array1<f64>,
    pub total_norm: f64,
}

impl RealUNetConditional {
    pub fn new(input_dim: usize, hidden_dim: usize, time_embed_dim: usize, seed: u64) -> Self {
        let mut rng = StdRng::seed_from_u64(seed);
        
        // Input dim includes time embedding concatenation
        let layer1_input = input_dim + time_embed_dim;
        
        let scale1 = (2.0 / (layer1_input + hidden_dim) as f64).sqrt();
        let scale2 = (2.0 / (hidden_dim + hidden_dim) as f64).sqrt();
        let scale3 = (2.0 / (hidden_dim + input_dim) as f64).sqrt();
        
        Self {
            time_embed_dim,
            
            w1: Self::init_matrix(&mut rng, hidden_dim, layer1_input, scale1),
            b1: Array1::zeros(hidden_dim),
            
            w2: Self::init_matrix(&mut rng, hidden_dim, hidden_dim, scale2),
            b2: Array1::zeros(hidden_dim),
            
            w3: Self::init_matrix(&mut rng, input_dim, hidden_dim, scale3),
            b3: Array1::zeros(input_dim),
            
            input_dim,
            hidden_dim,
            
            cache_x: None,
            cache_t_emb: None,
            cache_z1: None,
            cache_a1: None,
            cache_z2: None,
            cache_a2: None,
        }
    }
    
    fn init_matrix<R: rand::Rng>(rng: &mut R, rows: usize, cols: usize, scale: f64) -> Array2<f64> {
        Array2::from_shape_fn((rows, cols), |_| {
            let noise: f64 = StandardNormal.sample(rng);
            noise * scale
        })
    }
    
    /// Simple sinusoidal timestep embedding
    fn time_embedding(&self, t: usize, total_steps: usize) -> Array1<f64> {
        let mut embed = Array1::zeros(self.time_embed_dim);
        for i in 0..self.time_embed_dim {
            let freq = 10000_f64.powf(-(i as f64) / (self.time_embed_dim as f64));
            let phase = t as f64 / total_steps as f64 * std::f64::consts::PI * 2.0 * freq;
            embed[i] = if i % 2 == 0 { phase.sin() } else { phase.cos() };
        }
        embed
    }
    
    /// Forward: predict noise given x_t and timestep t
    pub fn forward(&mut self, x: &Array3<f64>, t: usize, total_steps: usize) -> Array3<f64> {
        let batch_size = x.shape()[0];
        let mut output = Array3::zeros((batch_size, 1, self.input_dim));
        
        // Flatten input
        let x_flat: Array2<f64> = Array2::from_shape_fn(
            (batch_size, self.input_dim),
            |(i, j)| x[[i, 0, j]]
        );
        
        // Timestep embedding
        let t_emb = self.time_embedding(t, total_steps);
        let t_emb_batch: Array2<f64> = Array2::from_shape_fn(
            (batch_size, self.time_embed_dim),
            |(_, j)| t_emb[j]
        );
        
        // Concatenate input + time embedding
        let combined = ndarray::concatenate(Axis(1), &[x_flat.view(), t_emb_batch.view()]).unwrap();
        
        // Layer 1
        let z1 = combined.dot(&self.w1.t()) + &self.b1;
        let a1 = relu(&z1);
        
        // Layer 2
        let z2 = a1.dot(&self.w2.t()) + &self.b2;
        let a2 = relu(&z2);
        
        // Layer 3: predict noise
        let noise_pred = a2.dot(&self.w3.t()) + &self.b3;
        
        // Store output
        for b in 0..batch_size {
            for j in 0..self.input_dim {
                output[[b, 0, j]] = noise_pred[[b, j]];
            }
        }
        
        // Cache
        self.cache_x = Some(x_flat);
        self.cache_t_emb = Some(t_emb_batch);
        self.cache_z1 = Some(z1);
        self.cache_a1 = Some(a1);
        self.cache_z2 = Some(z2);
        self.cache_a2 = Some(a2);
        
        output
    }
    
    /// Backward: compute gradients for noise prediction task
    pub fn backward(&self, grad_output_3d: &Array3<f64>) -> ConditionalGradient {
        let batch_size = grad_output_3d.shape()[0];
        
        let grad_output: Array2<f64> = Array2::from_shape_fn(
            (batch_size, self.input_dim),
            |(i, j)| grad_output_3d[[i, 0, j]]
        );
        
        let a2 = self.cache_a2.as_ref().expect("Forward first");
        let a1 = self.cache_a1.as_ref().expect("Forward first");
        let z2 = self.cache_z2.as_ref().expect("Forward first");
        let z1 = self.cache_z1.as_ref().expect("Forward first");
        let combined = ndarray::concatenate(
            Axis(1), 
            &[self.cache_x.as_ref().unwrap().view(), 
              self.cache_t_emb.as_ref().unwrap().view()]
        ).unwrap();
        
        // Layer 3
        let d_w3 = grad_output.t().dot(a2);
        let d_b3 = grad_output.sum_axis(Axis(0));
        let grad_a2 = grad_output.dot(&self.w3);
        
        // Layer 2
        let relu_deriv_z2 = z2.mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
        let grad_z2 = &grad_a2 * &relu_deriv_z2;
        let d_w2 = grad_z2.t().dot(a1);
        let d_b2 = grad_z2.sum_axis(Axis(0));
        let grad_a1 = grad_z2.dot(&self.w2);
        
        // Layer 1 (only backprop to input part, not time embedding)
        let relu_deriv_z1 = z1.mapv(|v| if v > 0.0 { 1.0 } else { 0.0 });
        let grad_z1 = &grad_a1 * &relu_deriv_z1;
        let d_w1 = grad_z1.t().dot(&combined);
        let d_b1 = grad_z1.sum_axis(Axis(0));
        
        let total_norm = (
            d_w1.mapv(|v| v * v).sum() +
            d_b1.mapv(|v| v * v).sum() +
            d_w2.mapv(|v| v * v).sum() +
            d_b2.mapv(|v| v * v).sum() +
            d_w3.mapv(|v| v * v).sum() +
            d_b3.mapv(|v| v * v).sum()
        ).sqrt();
        
        ConditionalGradient {
            d_w1, d_b1, d_w2, d_b2, d_w3, d_b3, total_norm
        }
    }
    
    pub fn update(&mut self, grad: &ConditionalGradient, lr: f64) {
        self.w1 = &self.w1 - lr * &grad.d_w1;
        self.b1 = &self.b1 - lr * &grad.d_b1;
        self.w2 = &self.w2 - lr * &grad.d_w2;
        self.b2 = &self.b2 - lr * &grad.d_b2;
        self.w3 = &self.w3 - lr * &grad.d_w3;
        self.b3 = &self.b3 - lr * &grad.d_b3;
    }
    
    pub fn param_hash(&self) -> u64 {
        let mut hash: u64 = 0xcbf29ce484222325;
        for &v in self.w1.iter().chain(self.b1.iter())
            .chain(self.w2.iter()).chain(self.b2.iter())
            .chain(self.w3.iter()).chain(self.b3.iter()) {
            hash ^= v.to_bits();
            hash = hash.wrapping_mul(0x100000001b3);
        }
        hash
    }
}

fn relu(x: &Array2<f64>) -> Array2<f64> {
    x.mapv(|v| v.max(0.0))
}
